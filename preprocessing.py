import pandas as pd
import numpy as np
import re

df = pd.read_csv('movies.csv')

df['title'] = df['title'].apply(lambda x: ' '.join(x.split()[1:]) if pd.notnull(x) else x)
df['parental_guide'] = df['parental_guide'].replace([None, '', 'Not Rated'], 'Unrated')


def duration_to_minutes(duration_str):
    if pd.isnull(duration_str):
        return None
    hours, minutes = 0, 0
    match = re.search(r'(\d+)h', duration_str)
    if match:
        hours = int(match.group(1))
    match = re.search(r'(\d+)m', duration_str)
    if match:
        minutes = int(match.group(1))
    return hours * 60 + minutes


# Apply the function to the 'duration' column
df['duration'] = df['duration'].apply(duration_to_minutes)
placeholder_value = 0  # or -1, or any other value you choose
df['gross_usa'] = df['gross_usa'].str.replace('[$,]', '', regex=True)
df['gross_usa'] = pd.to_numeric(df['gross_usa'], errors='coerce')
df['gross_usa'].fillna(placeholder_value, inplace=True)
df.to_csv('modified_movies.csv', index=False)
