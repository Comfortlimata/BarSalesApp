# query_inventory.py
import sqlite3

def query_inventory():
    conn = sqlite3.connect('bar_sales.db')
    cur = conn.cursor()
    cur.execute('SELECT * FROM inventory')
    rows = cur.fetchall()
    if not rows:
        print('No items in inventory.')
    else:
        print('Inventory items:')
        for row in rows:
            print(row)
    conn.close()

if __name__ == '__main__':
    query_inventory()
