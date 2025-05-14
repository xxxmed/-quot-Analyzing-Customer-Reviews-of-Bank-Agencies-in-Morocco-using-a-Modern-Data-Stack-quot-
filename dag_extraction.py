from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
import pandas as pd
import os
import logging
import glob

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default arguments for the DAG
default_args = {
    'owner': 'ahmed',
    'depends_on_past': False,
    'email': ['araji@insea.ac.ma'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 0,
    'retry_delay': timedelta(minutes=5),
}

# DAG configuration
dag = DAG(
    'bank_reviews_csv_to_db_simple',
    default_args=default_args,
    description='Extract bank reviews from CSV files and load to database (no cleaning)',
    schedule_interval='@daily',
    catchup=False,
    tags=['csv', 'bank_reviews', 'etl', 'no_cleaning']
)

# Configuration constants
POSTGRES_CONN_ID = 'postgres_default'
CSV_INPUT_DIR = '{{ var.value.CSV_INPUT_DIR }}'  # Set this in Airflow Variables
PROCESSED_DIR = '{{ var.value.PROCESSED_DIR }}'  # Where to move processed files


def create_bank_reviews_table(**context):
    """Create the bank_reviews table if it doesn't exist"""
    logger.info("Creating/checking bank_reviews table...")
    
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    
    # Simple table structure - adjust columns as needed for your CSV
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS bank_reviews (
        id SERIAL PRIMARY KEY,
        bank_name TEXT,
        branch_name TEXT,
        location TEXT,
        review_text TEXT,
        rating TEXT,
        review_date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    
    try:
        hook.run(create_table_sql)
        logger.info("Bank reviews table created/verified successfully")
    except Exception as e:
        logger.error(f"Error creating table: {e}")
        raise


def load_csv_to_database(**context):
    """Load CSV files directly to database without cleaning"""
    input_dir = context['params']['csv_input_dir']
    logger.info(f"Looking for CSV files in {input_dir}")
    
    # Find all CSV files
    csv_pattern = os.path.join(input_dir, "*.csv")
    csv_files = glob.glob(csv_pattern)
    
    if not csv_files:
        logger.info("No CSV files found")
        return 0
    
    hook = PostgresHook(postgres_conn_id=POSTGRES_CONN_ID)
    total_loaded = 0
    processed_files = []
    
    for file_path in csv_files:
        logger.info(f"Processing CSV file: {file_path}")
        
        try:
            # Read CSV file as-is
            df = pd.read_csv(file_path)
            
            # Get the column names from CSV
            logger.info(f"CSV columns: {df.columns.tolist()}")
            
            # Load directly to database
            engine = hook.get_sqlalchemy_engine()
            
            # Insert all data as-is
            rows_inserted = df.to_sql(
                name='bank_reviews',
                con=engine,
                if_exists='append',
                index=False,
                method='multi'
            )
            
            total_loaded += len(df)
            processed_files.append(file_path)
            logger.info(f"Loaded {len(df)} rows from {file_path}")
            
        except Exception as e:
            logger.error(f"Error processing {file_path}: {e}")
            continue
    
    logger.info(f"Total rows loaded: {total_loaded}")
    
    # Store processed files for cleanup
    context['task_instance'].xcom_push(key='processed_files', value=processed_files)
    return total_loaded


def move_processed_files(**context):
    """Move processed CSV files to the processed directory"""
    task_instance = context['task_instance']
    processed_files = task_instance.xcom_pull(task_ids='load_csv_to_database', key='processed_files')
    processed_dir = context['params']['processed_dir']
    
    if not processed_files:
        logger.info("No files to move")
        return
    
    # Create processed directory if it doesn't exist
    os.makedirs(processed_dir, exist_ok=True)
    
    moved_files = []
    for file_path in processed_files:
        try:
            filename = os.path.basename(file_path)
            # Add timestamp to avoid conflicts
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            new_filename = f"{timestamp}_{filename}"
            new_path = os.path.join(processed_dir, new_filename)
            
            # Move file
            os.rename(file_path, new_path)
            moved_files.append((file_path, new_path))
            logger.info(f"Moved {file_path} to {new_path}")
            
        except Exception as e:
            logger.error(f"Error moving {file_path}: {e}")
    
    return moved_files


# Define tasks
create_table_task = PythonOperator(
    task_id='create_bank_reviews_table',
    python_callable=create_bank_reviews_table,
    dag=dag
)

load_csv_task = PythonOperator(
    task_id='load_csv_to_database',
    python_callable=load_csv_to_database,
    params={
        'csv_input_dir': CSV_INPUT_DIR,
    },
    dag=dag
)

move_files_task = PythonOperator(
    task_id='move_processed_files',
    python_callable=move_processed_files,
    params={
        'processed_dir': PROCESSED_DIR,
    },
    dag=dag
)

# Set task dependencies
create_table_task >> load_csv_task >> move_files_task