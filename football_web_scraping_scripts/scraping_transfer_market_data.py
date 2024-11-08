from config import int_rank_lst, club_rnk_cols
import requests
from bs4 import BeautifulSoup
import pandas as pd
import os
import logging
import csv

class TransfermarktScraper:
    def __init__(self, market_value_dict):
        self.market_value_dict = market_value_dict
        log_folder = 'logs'
        os.makedirs(log_folder, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'transfermarkt_scraping.log'),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized TransfermarktScraper')

    def scrape_page(self, url):
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "items"})

        players = []
        ages = []
        dates = []
        record_values = []
        if table:
            for row in table.find_all("tr")[1:]:  # Skip the header row
                try:
                    player = row.select_one('td:nth-of-type(2) .hauptlink')
                    player_text = player.text.strip() if player else 'N/A'
                    if player_text in players:
                        continue  # Skip duplicates
                    players.append(player_text)
                except AttributeError:
                    players.append(None)
                try:
                    age = row.select_one('td:nth-of-type(5)')
                    age_text = age.text.strip() if age else 'N/A'
                    ages.append(age_text)
                except AttributeError:
                    ages.append(None)
                try:
                    date = row.select_one('td:nth-of-type(6)')
                    date_text = date.text.strip() if date else 'N/A'
                    dates.append(date_text)
                except AttributeError:
                    dates.append(None)
                try:
                    record_mv = row.select_one('td:nth-of-type(7)')
                    record_mv_text = record_mv.text.strip() if record_mv else 'N/A'
                    record_values.append(record_mv_text)
                except AttributeError:
                    record_values.append(None)
        return players, ages, dates, record_values

    def scrape_market_values(self):
        for url, csv_file in self.market_value_dict.items():
            all_players = []
            all_ages = []
            all_dates = []
            all_record_values = []
            players, ages, dates, record_values = self.scrape_page(url)
            all_players.extend(players)
            all_ages.extend(ages)
            all_dates.extend(dates)
            all_record_values.extend(record_values)
            for page in range(2, 21):
                next_page_url = f"{url}&page={page}"
                players, ages, dates, record_values = self.scrape_page(next_page_url)
                if not players:  # If no players are found, break the loop
                    break
                all_players.extend(players)
                all_ages.extend(ages)
                all_dates.extend(dates)
                all_record_values.extend(record_values)
            df = pd.DataFrame({
                "Player": all_players,
                "Age": all_ages,
                "Date": all_dates,
                "Record MV": all_record_values
            })
            df.to_csv(csv_file, index=False)
            self.logger.info(f'Data has been scraped and saved to {csv_file}')
            print(f'Data has been scraped and saved to {csv_file}')

if __name__ == "__main__":
    mrkt_value_dict = {
    "https://www.transfermarkt.com/spieler-statistik/rekordmarktwerte/marktwertetop?position=Abwehr&land_id=0&plus=1": "def_transfer_values_raw.csv",
    "https://www.transfermarkt.com/spieler-statistik/rekordmarktwerte/marktwertetop?position=Mittelfeld&land_id=0&plus=1": "mid_transfer_values_raw.csv",
    "https://www.transfermarkt.com/spieler-statistik/rekordmarktwerte/marktwertetop?position=Sturm&land_id=0&plus=1": "atck_transfer_values_raw.csv",
    "https://www.transfermarkt.com/spieler-statistik/rekordmarktwerte/marktwertetop?position=Torwart&land_id=0&plus=1": "gkp_transfer_values_raw.csv"
    }
    scraper = TransfermarktScraper(mrkt_value_dict)
    scraper.scrape_market_values()  # Add this line to call the method



class InternationalRankingScraper:

    def __init__(self, urls):
        self.urls = urls
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        log_folder = 'logs'
        os.makedirs(log_folder, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'international_ranking_scraping.log'),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized InternationalRankingScraper')

    def scrape_page(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "items"})

        data = []
        if table:
            for row in table.find_all('tr', class_=['odd', 'even']):
                try:
                    rank = row.find('td', class_='zentriert cp').text.strip().split()[0]
                    previous_rank = row.find('span', class_='icons_sprite')['title'].split(': ')[1]
                    nation = row.find('a', title=True)['title']
                    confederation = row.find_all('td', class_='zentriert')[1].text.strip()
                    points = row.find('td', class_='zentriert hauptlink').text.strip()
                    data.append([rank, previous_rank, nation, confederation, points])
                except (AttributeError, IndexError) as e:
                    self.logger.warning(f"Error parsing row: {e}")
        return data

    def scrape_rankings(self):
        for url in self.urls:
            dt = url[-10:]
            all_teams = []
            data = self.scrape_page(url)
            all_teams.extend(data)
            for num in range(2, 10):
                try:
                    next_page_url = f"https://www.transfermarkt.co.uk/statistik/weltrangliste/statistik/stat/ajax/yw1/datum/{dt}/plus/0/galerie/0/page/{num}"
                    data = self.scrape_page(next_page_url)
                    all_teams.extend(data)
                except Exception as e:
                    self.logger.warning(f"Error: Page Not Found")
                    break
            df = pd.DataFrame(all_teams, columns=['nation_rank', 'nation_prev_rank', 'nation', 'confederation', 'points'])
            df.to_csv(f'nation_rank_data_{dt}_raw.csv', index=False)
            self.logger.info(f'Data has been scraped and saved to nation_rank_data_{dt}_raw.csv')
            print(f'Data has been scraped and saved to nation_rank_data_{dt}_raw.csv')

if __name__ == "__main__":
    url_lst = int_rank_lst
    scraper = InternationalRankingScraper(url_lst)
    scraper.scrape_rankings()


class ClubRankingScraper:

    def __init__(self):
        self.base_url = "https://www.transfermarkt.co.uk/statistik/klubrangliste"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
        }
        log_folder = 'logs'
        os.makedirs(log_folder, exist_ok=True)
        logging.basicConfig(
            filename=os.path.join(log_folder, 'club_ranking_scraping.log'),
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.logger.info('Initialized ClubRankingScraper')

    def scrape_page(self, url):
        response = requests.get(url, headers=self.headers)
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "items"})

        data = []
        if table:
            for row in table.find_all('tr', class_=['odd', 'even']):
                try:
                    club_name = row.find('a', title=True)['title']
                    country_name = row.find('img', class_='flaggenrahmen')['title']
                    values = [td.text.strip() for td in row.find_all('td', class_='rechts')]
                    overall = values.pop()
                    data.append([club_name, country_name] + values + [overall])
                except (AttributeError, IndexError) as e:
                    self.logger.warning(f"Error parsing row: {e}")
        return data

    def scrape_rankings(self):
        all_teams = []
        data = self.scrape_page(self.base_url)
        all_teams.extend(data)
        for page in range(2, 23):
            next_page_url = f"{self.base_url}?page={page}"
            data = self.scrape_page(next_page_url)
            all_teams.extend(data)

        df = pd.DataFrame(all_teams, columns=club_rnk_cols)
        df.to_csv('club_rank_data.csv', index=False)
        self.logger.info('Data has been scraped and saved to club_rank_data.csv')
        print('Data has been scraped and saved to club_rank_data.csv')

if __name__ == "__main__":
    scraper = ClubRankingScraper()
    scraper.scrape_rankings()

