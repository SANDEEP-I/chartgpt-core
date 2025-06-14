# backend/scripts/generate_mock_data.py

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

CUSTOMER_NAMES = [
    "Alice", "Bob", "Charlie", "Dana", "Eli", "Faye", "George", "Helen",
    "Ian", "Julia", "Kevin", "Lara", "Mike", "Nina", "Oscar", "Priya", "Quinn", "Ravi", "Sara", "Tom"
]

REGIONS = ["North", "South", "East", "West"]

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

def create_tables(cur):
    cur.execute("""
        CREATE TABLE IF NOT EXISTS customers (
            customer_id SERIAL PRIMARY KEY,
            customer_name TEXT NOT NULL,
            region TEXT NOT NULL
        );
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            customer_id INT REFERENCES customers(customer_id),
            product_name TEXT NOT NULL,
            quantity INT NOT NULL,
            price NUMERIC(10,2) NOT NULL,
            order_date DATE NOT NULL
        );
    """)

def populate_customers(cur):
    cur.execute("DELETE FROM orders;")  # Clear dependent orders first
    cur.execute("DELETE FROM customers;")

    for name in CUSTOMER_NAMES:
        region = random.choice(REGIONS)
        cur.execute("INSERT INTO customers (customer_name, region) VALUES (%s, %s);", (name, region))

def populate_orders(cur, num_orders=200):
    cur.execute("SELECT customer_id FROM customers;")
    customer_ids = [row[0] for row in cur.fetchall()]
    start_date = datetime(2024, 1, 1)

    for _ in range(num_orders):
        customer_id = random.choice(customer_ids)
        product, category, min_price, max_price = random.choice(PRODUCTS)
        quantity = random.randint(1, 10)
        price = round(random.uniform(min_price, max_price), 2)
        days_offset = random.randint(0, 150)
        order_date = start_date + timedelta(days=days_offset)

        cur.execute("""
            INSERT INTO orders (customer_id, product_name, quantity, price, order_date)
            VALUES (%s, %s, %s, %s, %s);
        """, (customer_id, product, quantity, price, order_date.date()))

def main():
    conn = psycopg2.connect(**DB_PARAMS)
    cur = conn.cursor()

    create_tables(cur)
    populate_customers(cur)
    populate_orders(cur)

    conn.commit()
    cur.close()
    conn.close()

    print("✅ Successfully generated mock customers and orders with relationships.")

if __name__ == "__main__":
    main()
