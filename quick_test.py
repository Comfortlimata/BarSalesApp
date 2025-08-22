#!/usr/bin/env python3
"""Quick test to verify the application functionality without database conflicts"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("=== Testing Imports ===")
    
    try:
        from sales_utils import (
            init_db, create_sale_with_items, void_sale_transaction, 
            get_recent_sales_headers, get_sale_items, generate_pdf_receipt_for_sale
        )
        print("✓ sales_utils imports successful")
    except Exception as e:
        print(f"✗ sales_utils import failed: {e}")
        return False
    
    try:
        from sales_corrections import verify_supervisor_pin
        print("✓ sales_corrections imports successful")
    except Exception as e:
        print(f"✗ sales_corrections import failed: {e}")
        return False
    
    try:
        import tkinter as tk
        from tkinter import ttk
        print("✓ tkinter imports successful")
    except Exception as e:
        print(f"✗ tkinter import failed: {e}")
        return False
    
    return True

def test_supervisor_pins():
    """Test supervisor PIN verification"""
    print("\n=== Testing Supervisor PINs ===")
    
    try:
        from sales_corrections import verify_supervisor_pin
        
        # Test valid PINs
        if verify_supervisor_pin('manager', '1234'):
            print("✓ Manager PIN (1234) verification works")
        else:
            print("✗ Manager PIN (1234) verification failed")
            return False
        
        if verify_supervisor_pin('supervisor', '5678'):
            print("✓ Supervisor PIN (5678) verification works")
        else:
            print("✗ Supervisor PIN (5678) verification failed")
            return False
        
        # Test invalid PIN
        if not verify_supervisor_pin('manager', '0000'):
            print("✓ Invalid PIN correctly rejected")
        else:
            print("✗ Invalid PIN was accepted")
            return False
        
        return True
        
    except Exception as e:
        print(f"✗ Supervisor PIN test failed: {e}")
        return False

def test_file_structure():
    """Test if all required files exist"""
    print("\n=== Testing File Structure ===")
    
    required_files = [
        'main.py',
        'sales_utils.py', 
        'sales_corrections.py',
        'bar_sales.db'
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
        else:
            print(f"✓ {file} exists")
    
    if missing_files:
        print(f"✗ Missing files: {missing_files}")
        return False
    
    return True

def test_database_schema():
    """Test database schema without locking"""
    print("\n=== Testing Database Schema ===")
    
    try:
        import sqlite3
        
        # Quick read-only check
        conn = sqlite3.connect("bar_sales.db", timeout=5)
        cur = conn.cursor()
        
        # Check if cart tables exist
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name IN ('sales', 'sale_items')")
        tables = [row[0] for row in cur.fetchall()]
        
        if 'sales' in tables and 'sale_items' in tables:
            print("✓ Cart-based tables exist")
        else:
            print(f"✗ Missing cart tables. Found: {tables}")
            conn.close()
            return False
        
        # Check sales table structure
        cur.execute("PRAGMA table_info(sales)")
        sales_cols = [col[1] for col in cur.fetchall()]
        
        required_cols = ['transaction_id', 'cashier', 'status']
        missing_cols = [col for col in required_cols if col not in sales_cols]
        
        if missing_cols:
            print(f"✗ Missing sales columns: {missing_cols}")
            conn.close()
            return False
        else:
            print("✓ Sales table has correct structure")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database schema test failed: {e}")
        return False

def main():
    print("=== Quick Application Test ===\n")
    
    tests = [
        ("File Structure", test_file_structure),
        ("Imports", test_imports),
        ("Database Schema", test_database_schema),
        ("Supervisor PINs", test_supervisor_pins)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n❌ {test_name} test failed")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total} tests")
    
    if passed == total:
        print("✅ All tests passed! The application should work correctly.")
        print("\nTo use the application:")
        print("1. Run: python main.py")
        print("2. Login as cashier (username: cashier, password: cashier123)")
        print("3. Use 'Add Item' to select products and add to cart")
        print("4. Click 'CHECKOUT' to complete multi-item sales")
        print("5. Use 'VOID ITEM' with supervisor PIN (manager: 1234, supervisor: 5678)")
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()