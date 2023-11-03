from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from tabulate import tabulate
from datetime import datetime
from bs4 import BeautifulSoup
import re
import time
import pandas as pd

# Setup the tweet page
def setup():
    driver = webdriver.Chrome()
    token = "37cb55005d42cbf4c699c9f6f1aa649384ddb750"

    driver.get("https://twitter.com") # Open tweet page
    driver.add_cookie({ # Bypass login with cookie auth_token
            'name': "auth_token",
            'value': token,
            'domain': "twitter.com",
            'path': "/",
            'expires': -1,
            'httpOnly': True,
            'secure': True,
            'sameSite': "Strict",
          })
    driver.get("https://twitter.com/explore")
  
    return driver

# Fill the search form
def search(currentDriver, keyword):
    inputContext = currentDriver.find_element(By.XPATH, "//input[@placeholder='Cari']")
    inputContext.clear()
    inputContext.send_keys(keyword)
    inputContext.send_keys(Keys.RETURN)

    current_url = currentDriver.current_url
    currentDriver.get(current_url + "&f=live")

    return currentDriver

def dataCrawler(currentPage, target_data):
    tweet_links = []
    created_ats = []
    usernames = []
    full_texts = []
    langs = []
    replys = []
    retweets = []
    likes = []
    views = []

    while len(tweet_links) < target_data:

        # Setup BS and find the divs
        page_source = currentPage.page_source
        soup = BeautifulSoup(page_source, "html.parser")
        divs = soup.find_all('article', class_="css-1dbjc4n r-1loqt21 r-18u37iz r-1ny4l3l r-1udh08x r-1qhn6m8 r-i023vh r-o7ynqc r-6416eg")

        # Start Crawling
        for div in divs:
            link_ele = div.find("a", class_="css-4rbku5 css-18t94o4 css-901oao r-1bwzh9t r-1loqt21 r-xoduu5 r-1q142lx r-1w6e6rj r-37j5jr r-a023e6 r-16dba41 r-9aw3ui r-rjixqe r-bcqeeo r-3s2u2q r-qvutc0")

            try:
                base = "https://twitter.com"
                link = link_ele.get("href")
                if base + link not in tweet_links:
                    tweet_links.append(base + link)

                    username = re.search(r"/([^/]+)/status", link).group(1)
                    usernames.append(username)

                    try:
                        ele_fulltext = div.find("div", class_="css-901oao css-cens5h r-1nao33i r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0")
                        text = ele_fulltext.getText()
                        full_texts.append(text)
                    except:
                        full_texts.append("")

                    ele_time = div.find("time")
                    created_at = ele_time.get("datetime")
                    datetime_obj = datetime.strptime(created_at, "%Y-%m-%dT%H:%M:%S.%fZ")
                    created_ats.append(datetime_obj)

                    ele_lang = div.find("div", class_="css-901oao css-cens5h r-1nao33i r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-bnwqim r-qvutc0")
                    lang = ele_lang.get("lang")
                    langs.append(lang)

                    ele_interactions = div.find("div", class_="css-1dbjc4n r-1kbdv8c r-18u37iz r-1wtj0ep r-1s2bzr4 r-1ye8kvj")
                    interactions = ele_interactions.find_all("div", class_="css-18t94o4 css-1dbjc4n r-1777fci r-bt1l66 r-1ny4l3l r-bztko3 r-lrvibr")

                    reply = interactions[0].get("aria-label")
                    reply = re.search(r'\d+', reply)[0]
                    replys.append(reply)

                    retweet = interactions[1].get("aria-label")
                    retweet = re.search(r'\d+', retweet)[0]
                    retweets.append(retweet)

                    like = interactions[2].get("aria-label")
                    like = re.search(r'\d+', like)[0]
                    likes.append(like)

                    try:
                        view = div.find("a", class_="css-4rbku5 css-18t94o4 css-1dbjc4n r-1loqt21 r-1777fci r-bt1l66 r-1ny4l3l r-bztko3 r-lrvibr")
                        view = view.get("aria-label")
                        view = re.search(r'\d+', view)[0]
                        views.append(view)
                    except:
                        views.append("0")
            except:
                pass

        print("Total tweets saved:", len(tweet_links))

        # Scroll by pressing the arrow-down key
        for _ in range(30):
            currentPage.find_element(By.TAG_NAME, "body").send_keys(Keys.ARROW_DOWN)
        time.sleep(1)

    if len(tweet_links) != target_data:
        print(f"Warning: Target data not reached. Only {len(tweet_links)} data collected.")
        target_data = len(tweet_links)

    data = {
        "tweet_links": tweet_links,
        "created_at": created_ats,
        "usernames": usernames,
        "full_text": full_texts,
        "language": langs,
        "reply": replys,
        "retweet": retweets,
        "like": likes,
        "view": views
    }

    return data

keyword = input("Input your search keyword: ")
target_data = 1500

# Counting
start_time = time.time()

browser = setup()
page = search(browser, keyword)
data = dataCrawler(page, target_data)

# Create a DataFrame from the dictionary
df = pd.DataFrame(data)

filename = input("Input File Names: ")

# Export the DataFrame to a CSV file
df.to_csv("output/" + filename + "-tweets.csv", index=False, mode="w")

print("Program took", time.time() - start_time, "seconds to run")

# Pause
input("Press any key to close...")
browser.quit()
