#!/usr/bin/env python3
"""Simple database lock fix"""

import sqlite3
import os
import time

def fix_database():
    db_path = "bar_sales.db"
    
    print("Fixing database lock issue...")
    
    if not os.path.exists(db_path):
        print("Database file doesn't exist, creating new one...")
        # Initialize new database
        conn = sqlite3.connect(db_path, timeout=30)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.close()
        return True
    
    # Try to access database with increasing timeouts
    for timeout in [5, 10, 30, 60]:
        try:
            print(f"Attempting to connect with {timeout}s timeout...")
            conn = sqlite3.connect(db_path, timeout=timeout)
            
            # Enable WAL mode for better concurrency
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            conn.execute("PRAGMA busy_timeout=30000")
            conn.execute("PRAGMA cache_size=10000")
            
            # Test a simple operation
            conn.execute("SELECT 1")
            conn.commit()
            conn.close()
            
            print("✓ Database connection successful!")
            return True
            
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e):
                print(f"Database still locked, trying longer timeout...")
                time.sleep(2)
                continue
            else:
                print(f"Database error: {e}")
                return False
        except Exception as e:
            print(f"Unexpected error: {e}")
            return False
    
    print("Could not unlock database after all attempts")
    return False

if __name__ == "__main__":
    if fix_database():
        print("\n✅ Database is now accessible!")
        print("You can now run: python main.py")
    else:
        print("\n❌ Could not fix database lock")
        print("Try restarting your computer and run this script again")