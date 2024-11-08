from config import comp_dict_lst
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import re
import csv
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

class CompetitionDataScraper:
    def __init__(self, dict_list):
        self.dict_list = dict_list
        self.options = Options()
        self.options.headless = True
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        log_folder = 'logs'
        os.makedirs(log_folder, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'competition_scraping.log'),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized CompetitionDataScraper')

    def create_filename(self, url, id):
        match = re.search(r'/(\d{4}-\d{4})', url)
        if match:
            season = match.group(1).replace('-', '_')
            filename = f"{id}_{season}_raw.csv"
            return filename
        return None

    def scrape_page(self, url, class_id):
        self.driver.get(url)
        html = self.driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        table = soup.find('table', {'id': class_id})
        if not table:
            self.logger.warning(f'Table not found for {url} with id {class_id}')
            return None, None
        headers = table.find_all('th')
        header_labels = [header.get('aria-label') for header in headers if header.get('aria-label')]
        rows = table.find_all('tr')
        data = []
        for row in rows:
            league_name = row.find('th').text.strip()
            columns = row.find_all('td')
            row_data = [league_name] + [column.text.strip() for column in columns]
            data.append(row_data)
        return header_labels, data

    def scrape_competition_data(self):
        for entry in self.dict_list:
            url = entry["url"]
            class_id = entry["id"]
            header_labels, data = self.scrape_page(url, class_id)
            if header_labels and data:
                csv_name = self.create_filename(url, class_id)
                with open(csv_name, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(header_labels)
                    writer.writerows(data)
                self.logger.info(f'Data has been scraped and saved to {csv_name}')
                print(f'Data has been scraped and saved to {csv_name}')
            else:
                print("Table not found")
        self.driver.quit()
        self.logger.info('Finished scraping')

    def run(self):
        self.scrape_competition_data()

if __name__ == "__main__":
    dict_list = comp_dict_lst
    scraper = CompetitionDataScraper(dict_list)
    scraper.run()
