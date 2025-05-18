from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from ressources.extraction import main as main_extraction
from ressources.staging import main as main_staging

default_args = {
    'owner': 'ahmed',
    'depends_on_past': False,
    'email': ['araji@insea.ac.ma'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}



def test2(**context):
    print("Hello there 2")

dag = DAG(
    'test_DAG',
    default_args=default_args,
    description='Juste un test',
    schedule_interval='@daily',
    catchup=False,
    start_date=days_ago(2),
    tags=['csv', 'bank_reviews', 'etl', 'no_cleaning']
)

extraction = PythonOperator(
    task_id='extraction',
    python_callable=main_extraction,
    dag=dag
)

staging = PythonOperator(
    task_id='staging',
    python_callable=main_staging,
    dag=dag
)

dbt_run = BashOperator(
    task_id='dbt_run',
    bash_command='cd ~/projets/dw/DBT/etl_dw && dbt run',
    dag=dag,
    env={
        'DBT_PROFILES_DIR': '/home/zakaria/.dbt',
    },
    append_env=True,
)

extraction >> staging
