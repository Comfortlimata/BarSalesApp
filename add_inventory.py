#!/usr/bin/env python3
"""Add sample inventory to the bar sales database"""

from sales_utils import update_stock, set_item_prices, set_item_category

def add_sample_inventory():
    """Add sample beer and drink inventory"""
    
    # Sample inventory items: (name, quantity, cost_price, selling_price, category)
    items = [
        ('Mosi', 50, 12.0, 20.0, 'beer'),
        ('Zambezi', 45, 13.0, 22.0, 'beer'), 
        ('Rhino', 30, 14.0, 24.0, 'beer'),
        ('Black Label', 25, 15.0, 25.0, 'beer'),
        ('Castle', 40, 15.0, 25.0, 'beer'),
        ('Coca Cola', 60, 8.0, 15.0, 'soft drink'),
        ('Fanta', 55, 8.0, 15.0, 'soft drink'),
        ('Sprite', 50, 8.0, 15.0, 'soft drink'),
        ('Water', 100, 3.0, 8.0, 'soft drink'),
        ('Peanuts', 20, 5.0, 12.0, 'snacks'),
        ('Chips', 25, 6.0, 15.0, 'snacks'),
        ('Biltong', 15, 20.0, 35.0, 'snacks')
    ]
    
    print("Adding sample inventory...")
    
    for item, qty, cost, sell, cat in items:
        try:
            # Update stock (this will create the item if it doesn't exist)
            update_stock(item, qty)
            
            # Set prices
            set_item_prices(item, cost, sell)
            
            # Set category
            set_item_category(item, cat)
            
            print(f'✓ Added {item}: {qty} units at ZMW {sell} ({cat})')
            
        except Exception as e:
            print(f'✗ Error adding {item}: {e}')
    
    print("\nSample inventory added successfully!")
    print("The cashier dashboard should now show items in the dropdown.")

if __name__ == "__main__":
    add_sample_inventory()