from football_web_scraping_scripts.scraping_player_club_data import PlayerClubScraping
from data_cleaning import clean_data
from transformations import transform_data
from config import seasons_list, urls_lst_dict

def main():

    def scraping_player_club_data():
        for season in seasons_list:
            for url_dict in urls_lst_dict:
                for page, table_ids in url_dict.items():
                    for table_id in table_ids:
                        # Scrape data
                        scraper = PlayerClubScraping(season)
                        scraper.run(page, table_id)
    
    def scraping_transfer_market_data():
                    
    

                    # Clean data
                    clean_data()

                    # Transform data
                    transform_data()

if __name__ == "__main__":
    main()
