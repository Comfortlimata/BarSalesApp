 # database.py

import sqlite3
import os

DB_NAME = "bar_sales.db"

def connect_db():
    """Connect to SQLite DB and return the connection."""
    return sqlite3.connect(DB_NAME)

def initialize_database():
    """Create the sales table if it doesn't exist."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price_per_unit REAL NOT NULL,
            total REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def fetch_all_sales():
    """Retrieve all sales records from the database."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM sales")
    records = cur.fetchall()
    conn.close()
    return records

def get_sales_summary():
    """Get the total sales made (sum of totals)."""
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("SELECT SUM(total) FROM sales")
    result = cur.fetchone()
    conn.close()
    return result[0] if result and result[0] else 0.0
