from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.utils.dates import days_ago
from ressources.extraction import main as main_extraction
from ressources.staging import main as main_staging
from scripts.analyze_mart_reviews import main as main_analysis

# Default arguments for the DAG
default_args = {
    'owner': 'ahmed',
    'depends_on_past': False,
    'email': ['araji@insea.ac.ma'],
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

# Define the DAG
with DAG(
    'bank_reviews_etl',
    default_args=default_args,
    description='ETL complet pour les avis clients bancaires',
    schedule_interval='@daily',
    catchup=False,
    start_date=days_ago(2),
    tags=['csv', 'bank_reviews', 'etl', 'cleaning']
) as dag:

    extraction = PythonOperator(
        task_id='extraction',
        python_callable=main_extraction
    )

    staging = PythonOperator(
        task_id='staging',
        python_callable=main_staging
    )

    dbt_run = BashOperator(
        task_id='dbt_run',
        bash_command='cd ~/projets/dw/DBT/etl_dw && dbt run',
        env={
            'DBT_PROFILES_DIR': '/home/zakaria/.dbt',
        },
        append_env=True,
    )

    dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd ~/projets/dw/DBT/etl_dw && dbt test',
        env={
            'DBT_PROFILES_DIR': '/home/zakaria/.dbt',
        },
        append_env=True,
    )

    analysis = PythonOperator(
        task_id='analysis',
        python_callable=main_analysis
    )

    extraction >> staging >> dbt_run >> dbt_test >> analysis
