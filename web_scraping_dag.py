from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

def run_script(script_path):
    exec(open(script_path).read())

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'web_scraping_dag',
    default_args=default_args,
    description='A DAG for web scraping and data cleaning',
    schedule_interval=timedelta(days=1),
)

script_paths = [
    'football_web_scraping_scripts/scraping_club_placing_data.py',
    'football_web_scraping_scripts/scraping_competition_data.py',
    'football_web_scraping_scripts/scraping_country_codes.py',
    'football_web_scraping_scripts/scraping_player_club_data.py',
    'football_web_scraping_scripts/scraping_transfer_market_data.py'
]

previous_task = None
for i, script_path in enumerate(script_paths):
    task = PythonOperator(
        task_id=f'run_script_{i+1}',
        python_callable=run_script,
        op_args=[script_path],
        dag=dag,
    )
    if previous_task:
        previous_task >> task
    previous_task = task
