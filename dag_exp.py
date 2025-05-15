from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago
from ressources.test1_file import test1

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

task1 = PythonOperator(
    task_id='task1',
    python_callable=test1,
    dag=dag
)

task2 = PythonOperator(
    task_id='task2',
    python_callable=test2,
    dag=dag
)

task1 >> task2
