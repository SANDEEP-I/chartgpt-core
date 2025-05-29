# backend/scripts/generate_mock_orders.py

import os
import random
from datetime import datetime, timedelta
import psycopg2
from dotenv import load_dotenv

# Load .env variables
load_dotenv()

DB_PARAMS = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", 5432),
    "dbname": os.getenv("DB_NAME", "chartgpt"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD")
}

CUSTOMERS = [
    "Alice", "Bob", "Charlie", "Dana", "Eli", "Faye", "George", "Helen", "Ian", "Julia",
    "Kevin", "Lara", "Mike", "Nina", "Oscar", "Priya", "Quinn", "Ravi", "Sara", "Tom"
]

PRODUCTS = [
    ("Laptop", "Electronics", 900, 1500),
    ("Monitor", "Electronics", 150, 300),
    ("Mouse", "Accessories", 10, 50),
    ("Keyboard", "Accessories", 30, 100),
    ("Docking Station", "Accessories", 100, 250),
    ("Webcam", "Accessories", 50, 150),
    ("Chair", "Furniture", 150, 400),
    ("Desk", "Furniture", 200, 600)
]

REGIONS = ["North", "South", "East", "West"]

def generate_mock_data(num_rows=200):
    data = []
    start_date = datetime(2024, 1, 1)
    for _ in range(num_rows):
        customer = random.choice(CUSTOMERS)
        product, category, min_price, max_price = random.choice(PRODUCTS)
        quantity = random.randint(1, 10)
        price = round(random.uniform(min_price, max_price), 2)
        days_offset = random.randint(0, 150)
        order_date = start_date + timedelta(days=days_offset)
        region = random.choice(REGIONS)
        data.append((customer, product, quantity, price, order_date.date(), region))
    return data

def insert_data():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_name TEXT NOT NULL,
            product_name TEXT NOT NULL,
            quantity INT NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            order_date DATE NOT NULL,
            region TEXT NOT NULL
        );
    """)

    mock_data = generate_mock_data()
    cur.executemany("""
        INSERT INTO orders (customer_name, product_name, quantity, price, order_date, region)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, mock_data)

    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ Inserted {len(mock_data)} rows into orders table.")

if __name__ == "__main__":
    insert_data()
