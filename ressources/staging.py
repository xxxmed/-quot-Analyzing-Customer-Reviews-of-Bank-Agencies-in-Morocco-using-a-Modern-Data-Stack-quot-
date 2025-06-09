import pandas as pd
import psycopg2
import os
from dotenv import load_dotenv

# Get the absolute path to the project root directory
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Load environment variables from .env file in project root
load_dotenv(os.path.join(project_root, '.env'))

def staging_data():
    # Construct the path to the CSV file
    csv_path = os.path.join(project_root, "bank_reviews_data", "all_bank_reviews.csv")
    
    # Read CSV with explicit encoding and error handling
    df = pd.read_csv(csv_path, encoding='utf-8')

    # Database connection parameters
    conn = psycopg2.connect(
        dbname="DataWare",
        user="ahmed",
        password=os.getenv('DB_PASSWORD'),
        host="localhost",
        port="5432"
    )
    cur = conn.cursor()

    # Insert data into the table
    for _, row in df.iterrows():
        columns = ', '.join([f'"{col}"' for col in df.columns])
        values_placeholders = ', '.join(['%s'] * len(df.columns))
        insert_query = f'INSERT INTO bank_reviews ({columns}) VALUES ({values_placeholders})'
        cur.execute(insert_query, tuple(row.astype(str)))
    conn.commit()

    cur.close()
    conn.close()

if __name__ == "__main__":
    staging_data()
