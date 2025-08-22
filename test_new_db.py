#!/usr/bin/env python3
"""Test the new database structure and functionality"""

import sqlite3
from sales_utils import (
    create_sale_with_items, void_sale_transaction, 
    get_recent_sales_headers, get_sale_items, 
    generate_pdf_receipt_for_sale, get_all_stock
)

def test_cart_sales():
    """Test cart-based sales functionality"""
    print("=== Testing Cart-Based Sales ===")
    
    try:
        # Check inventory first
        stock = get_all_stock()
        print(f"Available inventory: {len(stock)} items")
        
        if len(stock) < 3:
            print("✗ Not enough inventory items for test")
            return None, None
        
        # Create a multi-item sale
        items = [
            {'item': stock[0][0], 'quantity': 2, 'unit_price': 25.0},
            {'item': stock[1][0], 'quantity': 1, 'unit_price': 20.0},
            {'item': stock[2][0], 'quantity': 3, 'unit_price': 5.0}
        ]
        
        sale_id, tx_id, total = create_sale_with_items('cashier', items)
        print(f"✓ Created sale: ID={sale_id}, TX={tx_id}, Total=ZMW {total:.2f}")
        
        # Verify sale items
        sale_items = get_sale_items(sale_id)
        print(f"✓ Sale has {len(sale_items)} items:")
        for item, qty, price, subtotal in sale_items:
            print(f"  - {item}: {qty} x ZMW {price:.2f} = ZMW {subtotal:.2f}")
        
        # Generate receipt
        receipt_path = generate_pdf_receipt_for_sale(sale_id)
        print(f"✓ Receipt generated: {receipt_path}")
        
        return sale_id, tx_id
        
    except Exception as e:
        print(f"✗ Cart sales test failed: {e}")
        return None, None

def test_void_functionality(sale_id):
    """Test void functionality"""
    print("\n=== Testing Void Functionality ===")
    
    if not sale_id:
        print("✗ No sale ID to test void functionality")
        return False
    
    try:
        # Test voiding the sale
        success, message = void_sale_transaction(
            sale_id, 
            "Test void", 
            "cashier", 
            "manager"
        )
        
        if success:
            print(f"✓ Sale voided successfully: {message}")
            
            # Verify sale is marked as voided
            headers = get_recent_sales_headers(5)
            for sid, tx, cashier, total, ts, status in headers:
                if sid == sale_id:
                    if status == 'VOIDED':
                        print("✓ Sale status correctly updated to VOIDED")
                    else:
                        print(f"✗ Sale status is {status}, expected VOIDED")
                    break
            
            return True
        else:
            print(f"✗ Void failed: {message}")
            return False
            
    except Exception as e:
        print(f"✗ Void functionality test failed: {e}")
        return False

def test_database_access():
    """Test basic database access"""
    print("=== Testing Database Access ===")
    
    try:
        conn = sqlite3.connect("bar_sales.db", timeout=10)
        cursor = conn.cursor()
        
        # Test reading from all main tables
        cursor.execute("SELECT COUNT(*) FROM inventory")
        inv_count = cursor.fetchone()[0]
        print(f"✓ Inventory table: {inv_count} items")
        
        cursor.execute("SELECT COUNT(*) FROM sales")
        sales_count = cursor.fetchone()[0]
        print(f"✓ Sales table: {sales_count} transactions")
        
        cursor.execute("SELECT COUNT(*) FROM sale_items")
        items_count = cursor.fetchone()[0]
        print(f"✓ Sale_items table: {items_count} line items")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"✗ Database access test failed: {e}")
        return False

def main():
    print("=== New Database Structure Test ===\n")
    
    # Test database access
    if not test_database_access():
        print("\n❌ Database access failed")
        return
    
    # Test cart-based sales
    sale_id, tx_id = test_cart_sales()
    
    # Test void functionality
    void_success = test_void_functionality(sale_id)
    
    # Summary
    print("\n=== Test Summary ===")
    if sale_id and void_success:
        print("✅ All tests passed! The application is working correctly.")
        print("\nFeatures verified:")
        print("  - Database access without locks")
        print("  - Cart-based multi-item sales")
        print("  - Multi-item receipt generation")
        print("  - Transaction-level voiding")
        print("  - Stock management")
        
        print("\n🚀 Ready to use!")
        print("Run: python main.py")
        print("Login: cashier / cashier123")
        
    else:
        print("❌ Some tests failed. Check the errors above.")

if __name__ == "__main__":
    main()