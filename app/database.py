import sqlite3
from pathlib import Path
from dotenv import load_dotenv
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "db" / "shopstream.db"

def create_database():

    connection = sqlite3.connect(DB_PATH)

    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
        order_id TEXT PRIMARY KEY,
        customer_name TEXT NOT NULL,
        product TEXT NOT NULL,
        status TEXT NOT NULL
        );
        """
    )

    cursor.execute(
        """
        INSERT INTO orders (order_id, customer_name, product, status) VALUES
    ('ORD1001', 'Arun Kumar', 'Wireless Headphones', 'Shipped'),
    ('ORD1002', 'Priya Sharma', 'Smart Watch', 'Delivered'),
    ('ORD1003', 'Rahul Kumar', 'Laptop Backpack', 'Processing'),
    ('ORD1004', 'Sneha Raj', 'Bluetooth Speaker', 'Out for Delivery'),
    ('ORD1005', 'Vikram Singh', 'Mechanical Keyboard', 'Cancelled');
        """
    )

# if __name__ == "__main__":
#     create_database()