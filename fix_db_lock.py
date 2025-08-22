#!/usr/bin/env python3
"""Fix database locking issues by enabling WAL mode and proper connection handling"""

import sqlite3
import os

def fix_database_locking():
    db_path = "bar_sales.db"
    
    if not os.path.exists(db_path):
        print("Database file does not exist")
        return False
    
    try:
        # Connect with timeout and enable WAL mode
        conn = sqlite3.connect(db_path, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=memory")
        conn.execute("PRAGMA mmap_size=268435456")  # 256MB
        conn.commit()
        conn.close()
        
        print("✓ Database configured for better concurrency")
        return True
        
    except Exception as e:
        print(f"✗ Failed to configure database: {e}")
        return False

def test_database_access():
    """Test if database can be accessed without locking"""
    try:
        conn = sqlite3.connect("bar_sales.db", timeout=10)
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM sales")
        count = cur.fetchone()[0]
        conn.close()
        print(f"✓ Database accessible, {count} sales records")
        return True
    except Exception as e:
        print(f"✗ Database access failed: {e}")
        return False

if __name__ == "__main__":
    print("=== Database Lock Fix ===")
    
    if fix_database_locking():
        if test_database_access():
            print("✓ Database is now properly configured and accessible")
        else:
            print("✗ Database still has access issues")
    else:
        print("✗ Failed to fix database configuration")