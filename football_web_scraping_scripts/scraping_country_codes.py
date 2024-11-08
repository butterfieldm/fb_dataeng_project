import pandas as pd
import requests
from bs4 import BeautifulSoup

url = 'https://en.wikipedia.org/wiki/List_of_FIFA_country_codes' # URL of the Wikipedia page
response = requests.get(url) # Send a request to fetch the HTML content
soup = BeautifulSoup(response.text, 'html.parser')
tables = soup.find_all('table', {'class': 'wikitable'}) # Find all tables on the page
final_df = pd.DataFrame() # Initialize an empty DataFrame

# Loop through all tables and concatenate each to the final DataFrame
for table in tables:
    df = pd.read_html(str(table))[0]
    final_df = pd.concat([final_df, df], ignore_index=True)

# Save the final concatenated DataFrame to a CSV file
final_df.to_csv('raw_data/nation_raw_data/fifa_country_codes.csv', index=False)
print("Country Code Raw Table saved to CSV file.")
