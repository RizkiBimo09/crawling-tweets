import pandas as pd

# Read the first CSV file
df1 = pd.read_csv('D:\Work Area\Project\Tweet Crawler\output\Pendekar 3-4 Juni-tweets.csv')

# Read the second CSV file
df2 = pd.read_csv('D:\Work Area\Project\Tweet Crawler\output\Pendekar 5-6-tweets.csv')

# Concatenate the two dataframes
merged_df = pd.concat([df1, df2])

# Convert the 'date' column to datetime type
merged_df['created_at'] = pd.to_datetime(merged_df['created_at'])

# Sort the dataframe by the 'date' column in ascending order
sorted_df = merged_df.sort_values(by='created_at')

# Save the sorted dataframe to a new CSV file
sorted_df.to_csv('Pendekar-Raw.csv', index=False)
