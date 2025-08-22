#!/usr/bin/env python3
"""
Comprehensive database lock fix for Bar Sales App
This script will:
1. Close any hanging database connections
2. Enable WAL mode for better concurrency
3. Optimize database settings
4. Test database accessibility
"""

import sqlite3
import os
import sys
import time
import subprocess

def kill_python_processes():
    """Kill any hanging Python processes that might be holding database locks"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.run(['taskkill', '/f', '/im', 'python.exe'], 
                         capture_output=True, text=True)
            subprocess.run(['taskkill', '/f', '/im', 'pythonw.exe'], 
                         capture_output=True, text=True)
        else:  # Unix/Linux/Mac
            subprocess.run(['pkill', '-f', 'python'], 
                         capture_output=True, text=True)
        print("✓ Killed any hanging Python processes")
        time.sleep(2)  # Wait for processes to fully terminate
    except Exception as e:
        print(f"Note: Could not kill processes: {e}")

def backup_database():
    """Create a backup of the current database"""
    db_path = "bar_sales.db"
    if os.path.exists(db_path):
        backup_path = f"bar_sales_backup_{int(time.time())}.db"
        try:
            import shutil
            shutil.copy2(db_path, backup_path)
            print(f"✓ Database backed up to: {backup_path}")
            return backup_path
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    return None

def fix_database_lock():
    """Fix database locking issues"""
    db_path = "bar_sales.db"
    
    print("=== Fixing Database Lock Issues ===\n")
    
    # Step 1: Kill hanging processes
    print("1. Terminating any hanging processes...")
    kill_python_processes()
    
    # Step 2: Backup database
    print("2. Creating database backup...")
    backup_path = backup_database()
    
    # Step 3: Check if database file is accessible
    print("3. Checking database file accessibility...")
    if not os.path.exists(db_path):
        print(f"✗ Database file {db_path} does not exist!")
        return False
    
    # Step 4: Try to access database with timeout
    print("4. Testing database access...")
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            conn = sqlite3.connect(db_path, timeout=30)
            conn.execute("BEGIN IMMEDIATE;")
            conn.rollback()
            conn.close()
            print(f"✓ Database accessible on attempt {attempt + 1}")
            break
        except sqlite3.OperationalError as e:
            if "database is locked" in str(e).lower():
                print(f"Attempt {attempt + 1}: Database still locked, waiting...")
                time.sleep(2)
                if attempt == max_attempts - 1:
                    print("✗ Database remains locked after all attempts")
                    return False
            else:
                print(f"✗ Database error: {e}")
                return False
        except Exception as e:
            print(f"✗ Unexpected error: {e}")
            return False
    
    # Step 5: Configure database for better concurrency
    print("5. Configuring database for better concurrency...")
    try:
        conn = sqlite3.connect(db_path, timeout=30)
        cursor = conn.cursor()
        
        # Enable WAL mode for better concurrency
        cursor.execute("PRAGMA journal_mode=WAL;")
        result = cursor.fetchone()
        print(f"   Journal mode set to: {result[0]}")
        
        # Set synchronous mode to NORMAL for better performance
        cursor.execute("PRAGMA synchronous=NORMAL;")
        
        # Increase cache size
        cursor.execute("PRAGMA cache_size=10000;")
        
        # Use memory for temporary storage
        cursor.execute("PRAGMA temp_store=memory;")
        
        # Set busy timeout
        cursor.execute("PRAGMA busy_timeout=30000;")
        
        # Enable memory mapping
        cursor.execute("PRAGMA mmap_size=268435456;")  # 256MB
        
        conn.commit()
        conn.close()
        print("✓ Database configuration updated")
        
    except Exception as e:
        print(f"✗ Failed to configure database: {e}")
        return False
    
    # Step 6: Test database operations
    print("6. Testing database operations...")
    try:
        conn = sqlite3.connect(db_path, timeout=10)
        cursor = conn.cursor()
        
        # Test read operation
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' LIMIT 1;")
        cursor.fetchone()
        
        # Test write operation
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER);")
        cursor.execute("DROP TABLE IF EXISTS test_table;")
        
        conn.commit()
        conn.close()
        print("✓ Database operations working correctly")
        
    except Exception as e:
        print(f"✗ Database operations failed: {e}")
        return False
    
    print("\n✅ Database lock issues have been resolved!")
    return True

def create_connection_manager():
    """Create a connection manager module to prevent future lock issues"""
    connection_manager_code = '''"""
Database connection manager to prevent locking issues
"""
import sqlite3
import threading
from contextlib import contextmanager

DB_NAME = "bar_sales.db"
_local = threading.local()

def get_connection():
    """Get a thread-local database connection"""
    if not hasattr(_local, 'connection'):
        _local.connection = sqlite3.connect(DB_NAME, timeout=30)
        # Configure connection
        _local.connection.execute("PRAGMA journal_mode=WAL")
        _local.connection.execute("PRAGMA synchronous=NORMAL")
        _local.connection.execute("PRAGMA busy_timeout=30000")
    return _local.connection

@contextmanager
def db_transaction():
    """Context manager for database transactions"""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        # Don't close the connection, just ensure it's committed/rolled back
        pass

def close_connection():
    """Close the thread-local connection"""
    if hasattr(_local, 'connection'):
        _local.connection.close()
        del _local.connection
'''
    
    try:
        with open('db_connection_manager.py', 'w') as f:
            f.write(connection_manager_code)
        print("✓ Created connection manager module")
    except Exception as e:
        print(f"Warning: Could not create connection manager: {e}")

def main():
    print("Bar Sales App - Database Lock Fix Tool")
    print("=" * 50)
    
    if fix_database_lock():
        create_connection_manager()
        print("\n🎉 Success! Your database is now ready to use.")
        print("\nNext steps:")
        print("1. Run: python main.py")
        print("2. The application should now work without database lock errors")
        print("3. If you still encounter issues, restart your computer and try again")
        
        # Test the application can start
        print("\n7. Testing application startup...")
        try:
            from sales_utils import init_db
            init_db()
            print("✓ Application initialization successful")
        except Exception as e:
            print(f"Warning: Application test failed: {e}")
            print("You may need to restart your computer")
    else:
        print("\n❌ Could not resolve database lock issues.")
        print("\nTroubleshooting steps:")
        print("1. Restart your computer")
        print("2. Make sure no other applications are using the database")
        print("3. Check if you have sufficient disk space")
        print("4. Run this script again after restart")

if __name__ == "__main__":
    main()