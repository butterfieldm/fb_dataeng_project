import re
from sqlalchemy import create_engine, inspect
import os
from dotenv import load_dotenv

############################################# User input section #####################################################

# Enter start and end seasons in the form YYYY-YYYY (e.g., '2021-2022')
start_season = '2022-2023'
end_season = '2022-2023'

# Enter keywords in the list to scrape that category of data, data available: 'standard','keeper','shooting','misc'
# keyword_list = ['standard','keeper','shooting','misc']
keyword_list = ['standard']

# Add more leagues as needed from: https://fbref.com/en/ -> Competitions -> Select Competition -> Select a season for an example
# Must be in the form '{country 3 letter football code}: {link to the compeition ending in -Stats with season and the key word parameter added}'
base_urls = {'spa': 'https://fbref.com/en/comps/12/{season}/{keyword}/{season}-La-Liga-Stats',
            #  'fra': 'https://fbref.com/en/comps/13/{season}/{keyword}/{season}-Ligue-1-Stats',
            #  'eng': 'https://fbref.com/en/comps/9/{season}/{keyword}/{season}-Premier-League-Stats',
            #  'ger': 'https://fbref.com/en/comps/20/{season}/{keyword}/{season}-Bundesliga-Stats',
            #  'por': 'https://fbref.com/en/comps/32/{season}/{keyword}/{season}-Primeira-Liga-Stats',
            #  'ita': 'https://fbref.com/en/comps/11/{season}/{keyword}/{season}-Serie-A-Stats',
            #  'bul': 'https://fbref.com/en/comps/67/{season}/{keyword}/{season}-Bulgarian-First-League-Stats',
            #  'aus': 'https://fbref.com/en/comps/56/{season}/{keyword}/{season}-Austrian-Bundesliga-Stats',
            #  'dan': 'https://fbref.com/en/comps/50/{season}/{keyword}/{season}-Danish-Superliga-Stats',
            #  'bel': 'https://fbref.com/en/comps/37/{season}/{keyword}/{season}-Belgian-Pro-League-Stats',
            #  'gre': 'https://fbref.com/en/comps/27/{season}/{keyword}/{season}-Super-League-Greece-Stats',
            #  'net': 'https://fbref.com/en/comps/23/{season}/{keyword}/{season}-Eredivisie-Stats',
            #  'pol': 'https://fbref.com/en/comps/36/{season}/{keyword}/{season}-Ekstraklasa-Stats',
            #  'ser': 'https://fbref.com/en/comps/54/{season}/{keyword}/{season}-Serbian-SuperLiga-Stats',
             'tur': 'https://fbref.com/en/comps/26/{season}/{keyword}/{season}-Super-Lig-Stats'}

# Add more date urls where required by visiting 'https://www.transfermarkt.co.uk/statistik/weltrangliste/statistik/stat/plus/0/galerie/0?datum=2024-09-19'
# Click the drop down menu for the date, click the date, add it to the list below. 
# For reference Sep was chosen as a single point in time at the start of each season
int_rank_lst = ['https://www.transfermarkt.co.uk/statistik/weltrangliste/statistik/stat/plus/0/galerie/0?datum=2024-09-19',
                'https://www.transfermarkt.co.uk/statistik/weltrangliste/statistik/stat/plus/0/galerie/0?datum=2023-09-21',
                'https://www.transfermarkt.co.uk/statistik/weltrangliste/statistik/stat/plus/0/galerie/0?datum=2022-09-20']

# Check https://www.transfermarkt.co.uk/statistik/klubrangliste for the seasons available as it updates yearly and edit the col list below
club_rnk_cols =['Club Name', 'Country', '20/21', '21/22', '22/23', '23/24', '24/25', 'Overall'] 

################# End of user input section ##########################

def generate_season_list(start_season, end_season):
    start_year = int(start_season.split('-')[0])
    end_year = int(end_season.split('-')[1])
    seasons_list = [f"{year}-{year + 1}" for year in range(start_year, end_year)]
    return seasons_list

def generate_keyword_dict(keyword_list):
    keywords = {}
    for keyword in keyword_list:
        keywords[keyword] = (f'stats_squads_{keyword}_for', f'stats_{keyword}')
    return keywords

def generate_urls_lst(seasons_list, keywords, base_urls):
    lst_of_dicts = []
    for season in seasons_list:
        for keyword, ids in keywords.items():
            team_id = {'id': {ids[0]}}
            player_id = {'id': {ids[1]}}
            urls = {league: url.format(season=season, keyword=keyword) for league, url in base_urls.items()}  
            lst_of_dicts.append({url: [team_id, player_id] for url in urls.values()})
    return lst_of_dicts 

def generate_placing_urls(base_urls, seasons_list):
    placing_lst_dicts = []
    url_list = [url for url in base_urls.values()]
    for season in seasons_list:
        for url in url_list:
            match = re.search(r'comps/(\d+)/', url)
            if match:
                league_id = match.group(1)
                team_league_id = {'id': f'results{season}{league_id}1_overall'}
                dict_ = {url: team_league_id}
                placing_lst_dicts.append(dict_)
    return placing_lst_dicts

def generate_comp_dicts(season_list):
    comp_dict_list = []
    for season in season_list:
        intl_comp = {"url": f"https://fbref.com/en/comps/season/{season}", 'id': "comps_intl_club_cup"}
        club_comp = {"url": f"https://fbref.com/en/comps/season/{season}", 'id': "comps_fa_club_cup"}
        fa_comp = {"url": f"https://fbref.com/en/comps/season/{season}", 'id': "comps_1_fa_club_league_senior"}

        comp_dict_list.append(intl_comp)
        comp_dict_list.append(club_comp)
        comp_dict_list.append(fa_comp)
    return comp_dict_list

def generate_existing_table_list():

    # Load environment variables from .env file
    load_dotenv()
    # Database connection details
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_name = os.getenv('DB_NAME')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    DB_CONNECTION_STRING = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
    # Create engine
    engine = create_engine(DB_CONNECTION_STRING)

    # Function to list all tables in all schemas
    def list_all_tables():
        inspector = inspect(engine)
        schemas = inspector.get_schema_names()
        all_tables = {}

        for schema in schemas:
            if schema not in ['pg_catalog', 'information_schema']:
                tables = inspector.get_table_names(schema=schema)
                all_tables[schema] = tables

        return all_tables

    # Get the list of all tables
    tables = list_all_tables()

    return tables


seasons_list = generate_season_list(start_season, end_season)
keywords_dict = generate_keyword_dict(keyword_list)
urls_lst_dict = generate_urls_lst(seasons_list, keywords_dict, base_urls)
placing_urls_dict = generate_placing_urls(base_urls, seasons_list)
comp_dict_lst = generate_comp_dicts(seasons_list)
existing_tables = generate_existing_table_list()

