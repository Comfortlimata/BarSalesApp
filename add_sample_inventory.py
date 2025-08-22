#!/usr/bin/env python3
"""
Add sample inventory items for testing the cart system
"""

import sqlite3
from sales_utils import init_db, update_stock, set_item_prices, set_item_category

def add_sample_inventory():
    """Add sample inventory items for testing"""
    init_db()
    
    # Sample items with categories, prices, and stock
    sample_items = [
        # Beers
        ("Castle Lager", 50, "Beer", 8.0, 12.0),
        ("Mosi Lager", 45, "Beer", 7.5, 11.0),
        ("Zambezi Lager", 40, "Beer", 7.0, 10.5),
        ("Rhino Lager", 35, "Beer", 6.5, 10.0),
        
        # Soft Drinks
        ("Coca Cola", 60, "Soft Drink", 3.0, 5.0),
        ("Pepsi", 55, "Soft Drink", 3.0, 5.0),
        ("Fanta Orange", 50, "Soft Drink", 2.5, 4.5),
        ("Sprite", 45, "Soft Drink", 2.5, 4.5),
        ("7UP", 40, "Soft Drink", 2.5, 4.5),
        
        # Cigarettes
        ("Marlboro", 25, "Cigarettes", 15.0, 20.0),
        ("Embassy", 30, "Cigarettes", 12.0, 18.0),
        ("Dunhill", 20, "Cigarettes", 18.0, 25.0),
        
        # Snacks
        ("Peanuts", 100, "Snacks", 2.0, 4.0),
        ("Biltong", 50, "Snacks", 8.0, 15.0),
        ("Chips", 75, "Snacks", 3.0, 6.0),
        
        # Spirits
        ("Jameson Whiskey", 10, "Spirits", 120.0, 180.0),
        ("Smirnoff Vodka", 15, "Spirits", 100.0, 150.0),
        ("Captain Morgan Rum", 12, "Spirits", 110.0, 165.0),
    ]
    
    print("Adding sample inventory items...")
    
    for item_name, quantity, category, cost_price, sell_price in sample_items:
        try:
            # Add stock
            update_stock(item_name, quantity)
            
            # Set prices
            set_item_prices(item_name, cost_price, sell_price)
            
            # Set category
            set_item_category(item_name, category)
            
            print(f"✓ Added {item_name}: {quantity} units, ZMW {sell_price:.2f} each ({category})")
            
        except Exception as e:
            print(f"✗ Error adding {item_name}: {e}")
    
    print("\nSample inventory added successfully!")
    print("You can now test the cart system with these items.")

if __name__ == "__main__":
    add_sample_inventory()