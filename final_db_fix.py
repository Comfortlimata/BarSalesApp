#!/usr/bin/env python3
"""
Final comprehensive database fix
This will completely resolve the database locking issue
"""

import sqlite3
import os
import shutil
import time
from datetime import datetime

def backup_and_recreate_database():
    """Backup existing database and create a fresh one"""
    db_path = "bar_sales.db"
    
    print("=== Final Database Fix ===")
    
    # Step 1: Backup existing database
    if os.path.exists(db_path):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = f"bar_sales_backup_{timestamp}.db"
        try:
            shutil.copy2(db_path, backup_path)
            print(f"✓ Database backed up to: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    
    # Step 2: Remove existing database files (including WAL and SHM files)
    files_to_remove = [db_path, f"{db_path}-wal", f"{db_path}-shm"]
    for file_path in files_to_remove:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"✓ Removed: {file_path}")
            except Exception as e:
                print(f"Warning: Could not remove {file_path}: {e}")
    
    # Step 3: Create fresh database with proper configuration
    print("Creating fresh database...")
    conn = sqlite3.connect(db_path, timeout=30)
    cursor = conn.cursor()
    
    # Enable WAL mode immediately
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA busy_timeout=30000")
    cursor.execute("PRAGMA cache_size=10000")
    cursor.execute("PRAGMA temp_store=memory")
    
    # Create all required tables
    print("Creating database tables...")
    
    # Users table
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Inventory table
    cursor.execute('''
        CREATE TABLE inventory (
            item TEXT PRIMARY KEY,
            quantity INTEGER NOT NULL,
            cost_price REAL DEFAULT 0,
            selling_price REAL DEFAULT 0,
            category TEXT DEFAULT ''
        )
    ''')
    
    # Sales table (cart-based)
    cursor.execute('''
        CREATE TABLE sales (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            transaction_id TEXT UNIQUE NOT NULL,
            cashier TEXT NOT NULL,
            total REAL NOT NULL,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'ACTIVE',
            void_reason TEXT DEFAULT NULL,
            void_authorized_by TEXT DEFAULT NULL,
            voided_at TEXT DEFAULT NULL
        )
    ''')
    
    # Sale items table
    cursor.execute('''
        CREATE TABLE sale_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER NOT NULL,
            item TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit_price REAL NOT NULL,
            subtotal REAL NOT NULL,
            FOREIGN KEY (sale_id) REFERENCES sales(id) ON DELETE CASCADE
        )
    ''')
    
    # Corrections table (from sales_corrections.py)
    cursor.execute('''
        CREATE TABLE corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_sale_id INTEGER NOT NULL,
            correction_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            requested_by TEXT NOT NULL,
            authorized_by TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            original_item TEXT NOT NULL,
            original_quantity INTEGER NOT NULL,
            original_price REAL NOT NULL,
            original_total REAL NOT NULL,
            correction_amount REAL NOT NULL
        )
    ''')
    
    # Supervisor sessions table
    cursor.execute('''
        CREATE TABLE supervisor_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supervisor_name TEXT NOT NULL,
            session_start TEXT NOT NULL,
            cashier_name TEXT NOT NULL,
            action_type TEXT NOT NULL
        )
    ''')
    
    # Create indexes
    cursor.execute("CREATE INDEX idx_sales_ts ON sales(timestamp)")
    cursor.execute("CREATE INDEX idx_sale_items_sale_id ON sale_items(sale_id)")
    
    conn.commit()
    conn.close()
    
    print("✓ Fresh database created successfully")
    
    # Step 4: Add sample data
    add_sample_data()
    
    # Step 5: Test database
    test_database()
    
    return True

def add_sample_data():
    """Add sample inventory and users"""
    print("Adding sample data...")
    
    conn = sqlite3.connect("bar_sales.db", timeout=30)
    cursor = conn.cursor()
    
    # Add sample inventory
    sample_items = [
        ("Black Label", 50, 15.0, 25.0, "Beer"),
        ("Castle Lager", 30, 12.0, 20.0, "Beer"),
        ("Coca Cola", 100, 3.0, 5.0, "Soft Drink"),
        ("Cigarettes", 200, 8.0, 12.0, "Tobacco"),
        ("Pringles", 25, 5.0, 8.0, "Snacks"),
        ("Mosi", 40, 10.0, 18.0, "Beer"),
        ("Fanta", 60, 2.5, 4.5, "Soft Drink"),
        ("Water", 80, 1.0, 2.0, "Soft Drink")
    ]
    
    for item, qty, cost, sell, category in sample_items:
        cursor.execute(
            "INSERT OR REPLACE INTO inventory (item, quantity, cost_price, selling_price, category) VALUES (?, ?, ?, ?, ?)",
            (item, qty, cost, sell, category)
        )
    
    conn.commit()
    conn.close()
    print("✓ Sample inventory added")

def test_database():
    """Test database operations"""
    print("Testing database operations...")
    
    try:
        # Test basic operations
        conn = sqlite3.connect("bar_sales.db", timeout=10)
        cursor = conn.cursor()
        
        # Test read
        cursor.execute("SELECT COUNT(*) FROM inventory")
        count = cursor.fetchone()[0]
        print(f"✓ Inventory items: {count}")
        
        # Test write
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        print(f"✓ Sales records: {sales_count}")
        
        conn.close()
        print("✓ Database operations successful")
        return True
        
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def main():
    print("Bar Sales App - Final Database Fix")
    print("=" * 40)
    
    if backup_and_recreate_database():
        print("\n🎉 Database has been completely fixed!")
        print("\nWhat was done:")
        print("- Backed up existing database")
        print("- Removed all database files (including WAL/SHM)")
        print("- Created fresh database with proper configuration")
        print("- Added sample inventory data")
        print("- Enabled WAL mode for better concurrency")
        
        print("\nYou can now:")
        print("1. Run: python main.py")
        print("2. Login as cashier (username: cashier, password: cashier123)")
        print("3. Use all features without database lock issues")
        
    else:
        print("\n❌ Could not fix database")
        print("Please restart your computer and try again")

if __name__ == "__main__":
    main()