import pandas as pd 
from sqlalchemy import create_engine, text 
import re 
import pycountry as pc 
import os 
from dotenv import load_dotenv 
from config import keyword_list

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

def extract_season_and_league(table_name): 
    """Extracts season and league from the table name.""" 
    season_match = re.search(r'(\d{4}_\d{4})', table_name) 
    season = season_match.group(1) if season_match else None 

    league_match = re.search(r'\d{4}_\d{4}_(.*?)_Stats', table_name) 
    league = league_match.group(1) if league_match else None 
    
    return season, league
def clean_dataframes(df, season, league, keyword):
    """Applies cleaning operations to the dataframe."""

    for keyword in keyword_list:

        df['League'] = league
        df['Season'] = season
        df['Squad'] = df['Squad'].apply(lambda x: re.sub(r'^[a-z]+\s+', '', x))
        df['Nation'] = df['Nation'].apply(lambda x: re.sub(r'^[a-z]+\s+', '', str(x)))

        if 'standard' in keyword:
            df['Minutes'] = df['Minutes'].astype(str).str.replace(',', '')
            df = df.dropna(how='all').drop('Matches', axis=1, errors='ignore')
            # Ensuring headers are the correct type
            for column in df.columns:
                if column in ('Player', 'Nation', 'Position', 'Squad', 'League', 'Season'):
                    df[column] = df[column].astype(str)
                elif column in ('Age', 'Year of birth', 'Matches Played', 'Starts', 'Minutes', 'Goals', 'Assists', 
                                'Goals + Assists', 'Non-Penalty Goals', 'Penalty Kicks Made', 'Penalty Kicks Attempted',
                                'Yellow Cards', 'Red Cards', 'Progressive Carries', 'Progressive Passes', 
                                'Progressive Passes Rec'):
                    df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
                else:
                    df[column] = pd.to_numeric(df[column], errors='coerce')

        else:
            # Ensuring headers are the correct type
             header_lst = list(df)
             for header in header_lst:
                if header in ('Player', 'Nation', 'Position', 'Squad', 'League', 'Season'):
                    df[header] = df[header].astype(str)
                if header in ('Age', 'Year of birth'):
                    df[header] = df[header].astype('Int64')

    return df

def process_db_tables(): 
    """Processes data from PostgreSQL tables and combines them into a single DataFrame.""" 
    final_df = pd.DataFrame() 
    with engine.connect() as conn: 
        # Get list of tables from the raw schema 
        result = conn.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'raw'")) 
        tables = result.fetchall() 
        for table in tables: 
            table_name = table[0] 
            season, league = extract_season_and_league(table_name) 
            # Read data from the PostgreSQL table 
            df = pd.read_sql_table(table_name, engine, schema='raw') 
            df = clean_dataframes(df, season, league) 
            final_df = pd.concat([final_df, df], ignore_index=True, sort=False) 
            print(f'Table: {table_name} concatenated to a combined dataframe') 

            return final_df 
        
def main(): 
    final_df = process_db_tables() 
    new_headers = [col.lower().replace(' ', '_') for col in final_df.columns] 
    final_df.columns = new_headers 
    # Write the cleaned DataFrame to the PostgreSQL database, schema 'staging' 
    final_df.to_sql('combined_player_stats_hist_cleaned', engine, schema='staging', if_exists='replace', index=False) 
    print("Data has been written to the staging schema in PostgreSQL")

    # For testing purposes
    # final_df.to_csv('staging_data/combined_player_stats_cleaned.csv', index=False) 

if __name__ == "__main__": 
    main()