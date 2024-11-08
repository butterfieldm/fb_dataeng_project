from config import seasons_list, placing_urls_dict
from bs4 import BeautifulSoup
import pandas as pd
import os
import csv
import logging
import glob
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class PlacingDataScraper:
    def __init__(self, seasons):
        self.seasons = seasons
        self.options = Options()
        self.options.headless = True
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        log_folder = 'logs'
        os.makedirs(log_folder, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'player_data_scraping.log'),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized PlayerDataScraper')

    def create_filename(self, url):
        name = url.split('/')[-1].replace('-', '_') + "_table_placings.csv"
        return name

    def scrape_placing_data(self):
        for data_dict in placing_urls_dict:
            for page, id in data_dict.items():
                print(page, id)
                csv_files = glob.glob(f'**.csv')
                csv_name = self.create_filename(page)

                if csv_name in csv_files:
                    print('Dataset already exists')

                else:
                    self.driver.get(page)
                    # Get the page source after JavaScript has rendered
                    html = self.driver.page_source
                    # Parse the HTML content with BeautifulSoup
                    soup = BeautifulSoup(html, 'html.parser')
                    # Find the table with the specified class
                    table = soup.find('table', id)
                    # Extract the data from the table
                    if table:
                        # Find the thead element
                        thead = table.find('thead')
                        # Extract column headers with aria-label

                        headers = thead.find_all('th')
                        header_labels = [header.get('aria-label', header.text).strip() for header in headers if header.get('aria-label', header.text).strip()]
                        # Use a set to remove duplicates, required due to multiple headers in the table across the web page
                        unique_header_labels = list(dict.fromkeys(header_labels))
                        # Removing unwanted blank fields scraped incorrectly
                        if 'Rank' in unique_header_labels:
                            filtered_lst = [header for header in header_labels if not (header.isdigit())][1:]
                        else:
                            filtered_lst = [header for header in header_labels if not (header.isdigit())]
                        rows = table.find_all('tr')
                        data = []
                        for row in rows:
                            columns = row.find_all('td')
                            row_data = [column.text for column in columns]
                            data.append(row_data)
                        # Write data to CSV
                        with open(csv_name, 'w', newline='', encoding='utf-8') as file:                  
                            writer = csv.writer(file)
                            # Write header labels first
                            writer.writerow(filtered_lst)
                            # Write the rest of the data
                            writer.writerows(data)
                        print(f'Data has been scraped and saved to {csv_name}')
                    else:
                        print("Table not found")

        self.driver.quit()
        self.logger.info('Finished scraping')

    def run(self):
        self.scrape_placing_data()

if __name__ == "__main__":
    seasons = seasons_list
    scraper = PlacingDataScraper(seasons)
    scraper.run()


