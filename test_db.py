#!/usr/bin/env python3
"""Test script to check database functionality and add sample inventory"""

import sqlite3
from sales_utils import init_db, update_stock, set_item_prices, set_item_category, get_all_stock

def test_database():
    print("Testing database functionality...")
    
    # Initialize database
    try:
        init_db()
        print("✓ Database initialized successfully")
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False
    
    # Test inventory operations
    try:
        # Add some sample inventory
        items = [
            ("Black Label", 50, 15.0, 25.0, "Beer"),
            ("Castle Lager", 30, 12.0, 20.0, "Beer"),
            ("Coca Cola", 100, 3.0, 5.0, "Soft Drink"),
            ("Cigarettes", 200, 8.0, 12.0, "Tobacco"),
            ("Pringles", 25, 5.0, 8.0, "Snacks")
        ]
        
        for item, qty, cost, sell, cat in items:
            update_stock(item, qty)
            set_item_prices(item, cost, sell)
            set_item_category(item, cat)
        
        print("✓ Sample inventory added successfully")
        
        # Check inventory
        stock = get_all_stock()
        print(f"✓ Current inventory: {len(stock)} items")
        for item, qty, cat in stock:
            print(f"  - {item}: {qty} units ({cat})")
            
    except Exception as e:
        print(f"✗ Inventory operations failed: {e}")
        return False
    
    # Test cart schema
    try:
        from sales_utils import ensure_cart_schema, get_recent_sales_headers
        ensure_cart_schema()
        print("✓ Cart schema ensured")
        
        headers = get_recent_sales_headers(5)
        print(f"✓ Recent sales headers: {len(headers)} transactions")
        
    except Exception as e:
        print(f"✗ Cart schema test failed: {e}")
        return False
    
    return True

def check_database_structure():
    print("\nChecking database structure...")
    conn = sqlite3.connect("bar_sales.db", timeout=10)
    cur = conn.cursor()
    
    try:
        # Check tables
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cur.fetchall()
        print(f"Tables: {[t[0] for t in tables]}")
        
        # Check sales table structure
        cur.execute("PRAGMA table_info(sales)")
        sales_cols = cur.fetchall()
        print(f"Sales table columns: {[col[1] for col in sales_cols]}")
        
        # Check if sale_items exists
        cur.execute("PRAGMA table_info(sale_items)")
        items_cols = cur.fetchall()
        if items_cols:
            print(f"Sale_items table columns: {[col[1] for col in items_cols]}")
        else:
            print("Sale_items table does not exist")
            
    except Exception as e:
        print(f"Error checking database structure: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== Database Test Script ===")
    
    check_database_structure()
    
    if test_database():
        print("\n✓ All tests passed! Database is working correctly.")
    else:
        print("\n✗ Some tests failed. Check the errors above.")
    
    print("\nYou can now run the main application with: python main.py")