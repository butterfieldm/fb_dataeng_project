## Data Engineering Project (On-going)

Current development branch: MB-ML-Dev

This data engineering project was designed to test and use a range of fundamental data engineering principles and techniques.
The goal of the project was to practise and learn a range of practises that consist of but are not limited to:

- Data Modelling Techniques 
- Data Ingestion
- Database Management 
- Data Handling
- Data Cleansing
- Data Manipulation
- ETL processes
- Data Pipelines
- Data Warehousing

The steps followed to capture the relevant fundamentals include:

1. Automate Data Ingestion:
    * Write and schedule web scraping scripts using cron or Airflow.
2. Automate Data Cleaning:
    * Write Python scripts to clean the data and integrate them into an ETL pipeline.
3. Design Snowflake Schema:
    * Create a PostgreSQL database and define a snowflake schema.
4. ETL Process:
    * Develop ETL scripts to extract, transform, and load data into your PostgreSQL database.
    * Schedule these ETL jobs using Airflow.
5. Develop ML Model:
    * Develop a predicting machine learning model.
    * Use the cleaned and structured data for training and testing.
    * Save the trained model and predictions.
6. Store ML Output:
    * Write a script to save ML model predictions back into PostgreSQL.
7. Real-Time Processing:
    * Set up Spark Streaming and Kafka to process data in real-time.
    * Implement real-time cleaning and model prediction using streaming data.
8. Orchestrate with Airflow:
    * Define Airflow DAGs to schedule and manage the entire pipeline: data ingestion, ETL, ML, and streaming.
  

Script Purpose:

# config.py
Assigns all relevant values to parameters used throughout the ETL pipeline

# football_web_scraping_scripts
These classes access the relevant web pages required to scrape the necessary football data for model development
Data is consolidated into relevant datasets and stored in a PostgreSQL database

# football_data_cleansing.py
Reads the scraped data from the PostgreSQL raw data layer to perform various data cleansing for more managable and usabke data. 
This data is then ouputted to a staging layer in the same PostgreSQL database.

# main.py
Main control script, any changes that need to be made for a re-run should be editted here and in the config.py script.
This script will call all of the web-scraping, cleansing, manipulation and ML scripts.

# web_scraping_dag.py
Dag script to run the job when scheduled
