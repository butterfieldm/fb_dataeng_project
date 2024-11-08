from dotenv import load_dotenv
import subprocess
import os
from sqlalchemy import create_engine
import pandas as pd
import glob
from config import seasons_list

# Load environment variables from .env file load_dotenv()
load_dotenv()

# Database connection details
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')
db_host = os.getenv('DB_HOST')
db_port = os.getenv('DB_PORT')
DB_CONNECTION_STRING = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

# Function to check if PostgreSQL server is running
def is_postgres_running():
    try:
        # Check if there are any processes listening on the PostgreSQL port
        output = subprocess.check_output(f'lsof -i :{db_port}', shell=True, stderr=subprocess.STDOUT)
        return "LISTEN" in output.decode('utf-8')
    except subprocess.CalledProcessError:
        return False

# Function to start PostgreSQL server if it's not running
def start_postgres():
    if not is_postgres_running():
        print("PostgreSQL server is not running. Starting server...")
        try:
            subprocess.check_call(f'pg_ctl -D "/Users/michaelbutterfield/Library/Application Support/Postgres/var-17" start', shell=True)
            print("PostgreSQL server started.")
        except subprocess.CalledProcessError as e:
            print(f"Failed to start PostgreSQL server: {e}")

# Function to check and create schema
def check_and_create_schema(schema_name):
    with engine.connect() as conn:
        conn.execute(f"CREATE SCHEMA IF NOT EXISTS {schema_name}")

# Function to upload raw data to the raw schema
def upload_raw_data(file_path, table_name):
    last_season = seasons_list[-1]
    for season in seasons_list:
        df = pd.read_csv(file_path)
        if season == last_season:
            df.to_sql(table_name, engine, schema='raw', if_exists='replace', index=False) # This will be the current season, we replace for updates
        else:
            try: 
                df.to_sql(table_name, engine, schema='raw', if_exists='fail', index=False) 
                print(f"Uploaded {file_path} to {table_name} table.") 
            except ValueError as e: 
                if 'already exists' in str(e): 
                    print(f"Table {table_name} already exists. Skipping {file_path}.") 
                else: 
                    raise

        os.remove(file_path)  # Optionally delete the local file after uploading

# Start PostgreSQL server if not running
start_postgres()

# Create engine
engine = create_engine(DB_CONNECTION_STRING)

# Check and create schemas
schemas = ['raw', 'staging', 'curated']
for schema in schemas:
    check_and_create_schema(schema)

# Use glob to list all CSV files in the data/raw directory 
csv_files = glob.glob('data/raw/*.csv') 

# Loop through each CSV file and upload it 
for csv_file in csv_files: 
    upload_raw_data(csv_file)
