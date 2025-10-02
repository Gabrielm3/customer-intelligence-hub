import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

def get_database_connection():
    """Create database connection using environment variables"""
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        host = os.getenv('POSTGRES_HOST', 'localhost')
        port = os.getenv('POSTGRES_PORT', '5432')
        database = os.getenv('POSTGRES_DB', 'crm_database')
        user = os.getenv('POSTGRES_USER', 'crm_user')
        password = os.getenv('POSTGRES_PASSWORD', 'crm_password')
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    return create_engine(database_url)

def import_csv_to_table(csv_file, table_name, engine):
    try:
        print(f"Importing {csv_file} to {table_name}...")
        df = pd.read_csv(csv_file)
        
        if table_name == 'customers':
            df.columns = ['customer_id', 'country', 'name', 'email']
        elif table_name == 'transactions':
            df.columns = ['invoice', 'invoice_date', 'stock_code', 'quantity', 'price', 'total_price', 'customer_id']
         
            df['invoice_date'] = pd.to_datetime(df['invoice_date'])
        elif table_name == 'items':
            df.columns = ['stock_code', 'description', 'price']
        elif table_name == 'rfm':
            df.columns = ['customer_id', 'recency', 'frequency', 'monetary', 'r', 'f', 'm', 'rfm_score', 'segment']
        
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text(f"TRUNCATE TABLE {table_name} CASCADE"))
            conn.commit()
        
        df.to_sql(table_name, engine, if_exists='append', index=False, method='multi')
        print(f" Successfully imported {len(df)} rows to {table_name}")
        
    except Exception as e:
        print(f" Error importing {csv_file}: {str(e)}")

def main():
    try:
        engine = get_database_connection()
        
        csv_files = [
            ('data/customers.csv', 'customers'),
            ('data/items.csv', 'items'),
            ('data/transactions.csv', 'transactions'),
            ('data/rfm.csv', 'rfm')
        ]
        
        for csv_file, table_name in csv_files:
            if os.path.exists(csv_file):
                import_csv_to_table(csv_file, table_name, engine)
            else:
                print(f"  File not found: {csv_file}")
        
        print("\n completed!")
        
        with engine.connect() as conn:
            for _, table_name in csv_files:
                try:
                    from sqlalchemy import text
                    result = conn.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
                    count = result.fetchone()[0]
                    print(f" {table_name}: {count} records")
                except Exception as e:
                    print(f" Error counting {table_name}: {str(e)}")
                    
    except Exception as e:
        print(f" Database connection error: {str(e)}")

if __name__ == "__main__":
    main()