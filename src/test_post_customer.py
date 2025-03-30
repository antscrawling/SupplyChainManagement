import json
import requests
from pathlib import Path
import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import psycopg2

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': 5432,  # Default PostgreSQL port
    'user': 'postgres',
    'password': 'postgres',
    'database': 'supplychain_db'
}

DB_URL = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"

def test_db_connection():
    """Test database connection before proceeding"""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        conn.close()
        return True
    except psycopg2.Error as e:
        print(f"Database Connection Error: {e}")
        return False

def get_db_session():
    if not test_db_connection():
        raise ConnectionError("Cannot connect to database")
    
    engine = create_engine(DB_URL)
    Session = sessionmaker(bind=engine)
    return Session()

def post_customers():
    # Read customer data
    myfile = Path(__file__).parent / 'customer.json'
    with open(myfile, 'r') as f:
        mylist = json.load(f)
        assert isinstance(mylist, list), "mylist should be a list"

    # API endpoint configuration
    url = "http://0.0.0.0:8000/customers/batch"
    headers = {
        "accept": "application/json",
        "Content-Type": "application/json"
    }

    # Send POST request
    try:
        response = requests.post(url, headers=headers, json=mylist)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")

        # Query database after successful POST
        session = get_db_session()
        
        # Example queries
        queries = {
            "Total Customers": """
                SELECT COUNT(*) as total_customers 
                FROM customers
            """,
            "Customers by Type": """
                SELECT customer_type, COUNT(*) as count 
                FROM customers 
                GROUP BY customer_type
            """,
            "Recent Customers": """
                SELECT company_name, customer_type, registration_date 
                FROM customers 
                WHERE registration_date >= NOW() - INTERVAL '24 hours'
                ORDER BY registration_date DESC 
                LIMIT 5
            """,
            "Credit Analysis": """
                SELECT 
                    customer_type,
                    COUNT(*) as count,
                    AVG(credit_score) as avg_credit_score,
                    AVG(approved_credit_limit) as avg_credit_limit
                FROM customers 
                GROUP BY customer_type
            """
        }

        # Execute and print queries
        for title, query in queries.items():
            print(f"\n=== {title} ===")
            result = session.execute(text(query))
            for row in result:
                print(row)

    except requests.exceptions.RequestException as e:
        print(f"API Error: {e}")
    except Exception as e:
        print(f"Database Error: {e}")
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    post_customers()


