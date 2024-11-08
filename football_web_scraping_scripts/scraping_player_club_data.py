from config import seasons_list
from bs4 import BeautifulSoup
import pandas as pd
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import re
import logging
import csv

class PlayerClubScraping:

    def __init__(self, season):
        self.options = Options()
        self.options.headless = True
        self.service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=self.service, options=self.options)
        self.season = season
        log_folder = 'logs'
        os.makedirs(log_folder, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'playerclubscraping.log'),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized FootballScraper')

    def create_filename(self, url, table_id):
        match = re.search(r'/(\d{4}-\d{4})/([^/]+)/(\d{4}-\d{4}-[^/]+)', url)
        table_id_match = re.search(r"'id': {'([^']*)'}", str(table_id))
        if match and table_id_match:
            category = match.group(2).title()
            stats = match.group(3).replace('-', '_')[:-6]
            table = table_id_match.group(1)
            table_type = 'Player' if '_for' not in table else 'Team'
            filename = f"{stats}_{category}_{table_type}.csv"
            return filename
        return None

    def scrape_page(self, page, table_id):
        try:
            self.logger.info(f'Scraping page: {page} with id: {table_id}')
            self.driver.get(page)
            html = self.driver.page_source
            soup = BeautifulSoup(html, 'html.parser')
            table = soup.find('table', {'id': table_id})
            if not table:
                self.logger.warning('Table not found')
                return
            thead = table.find('thead')
            headers = thead.find_all('th')
            header_labels = [header.get('aria-label', header.text).strip() for header in headers if header.get('aria-label', header.text).strip()]
            unique_header_labels = list(dict.fromkeys(header_labels))
            if 'Rk' in unique_header_labels:
                filtered_headers = [header for header in header_labels if not header.isdigit()][1:]
            else:
                filtered_headers = [header for header in header_labels if not header.isdigit()]
            if '/stats/' in page and 'npxG + xAG/90' not in filtered_headers:
                if 'Matches' in filtered_headers:
                    filtered_headers.remove('Matches')
                    filtered_headers[-1] = 'npxG + xAG/90'
                    filtered_headers.append('Matches')
                else:
                    filtered_headers[-1] = 'npxG + xAG/90'

            rows = table.find_all('tr')
            data = []
            for row in rows:
                columns = row.find_all('td')
                row_data = [column.text for column in columns]
                data.append(row_data)

            filename = self.create_filename(page, table_id)
            if filename:
                with open(filename, 'w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(filtered_headers)
                    writer.writerows(data)
                self.logger.info(f'Data has been scraped and saved to {filename}')
        except Exception as e:
            self.logger.error(f'Error scraping page {page} with id {table_id}: {e}', exc_info=True)
        finally:
            self.driver.quit()

    def run(self, page, table_id):
        self.scrape_page(page, table_id)

if __name__ == "__main__":
    page = 'your_page_url'
    table_id = {'id': 'your_table_id'}
    scraper = PlayerClubScraping(seasons_list)
    scraper.run(page, table_id)
