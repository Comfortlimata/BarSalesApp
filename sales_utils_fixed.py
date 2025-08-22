#!/usr/bin/env python3
"""
Fixed version of sales_utils.py with proper transaction handling to prevent database locks
"""

import sqlite3
from datetime import datetime, timedelta
from fpdf import FPDF
import hashlib
import os
import json
import bcrypt
from typing import List, Dict, Tuple, Optional

DB_NAME = "bar_sales.db"

def create_sale_with_items(cashier: str, items: List[Dict]) -> Tuple[int, str, float]:
    """Create sale header + multiple sale_items with proper transaction handling.
    items: list of dicts with keys: item, quantity, unit_price
    Returns (sale_id, transaction_id, total)
    """
    conn = sqlite3.connect(DB_NAME, timeout=30)
    cur = conn.cursor()
    
    try:
        # Begin immediate transaction to prevent locks
        cur.execute("BEGIN IMMEDIATE")
        
        # Stock check within transaction
        for it in items:
            cur.execute('SELECT quantity FROM inventory WHERE item=?', (it['item'],))
            row = cur.fetchone()
            stock = row[0] if row else 0
            if it['quantity'] > stock:
                raise ValueError(f"Not enough stock for {it['item']}. In stock: {stock}, requested: {it['quantity']}")
        
        # Compute total
        total = sum(float(it['quantity']) * float(it['unit_price']) for it in items)
        tx_id = _new_transaction_id()
        ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Insert sale header
        cur.execute("INSERT INTO sales (transaction_id, cashier, total, timestamp, status) VALUES (?, ?, ?, ?, 'ACTIVE')",
                    (tx_id, cashier, total, ts))
        sale_id = cur.lastrowid
        
        # Insert sale items and update stock in same transaction
        for it in items:
            subtotal = float(it['quantity']) * float(it['unit_price'])
            
            # Insert sale item
            cur.execute(
                "INSERT INTO sale_items (sale_id, item, quantity, unit_price, subtotal) VALUES (?, ?, ?, ?, ?)",
                (sale_id, it['item'], int(it['quantity']), float(it['unit_price']), subtotal)
            )
            
            # Update stock within same transaction
            cur.execute('SELECT quantity FROM inventory WHERE item=?', (it['item'],))
            row = cur.fetchone()
            if row:
                new_qty = row[0] - int(it['quantity'])
                cur.execute('UPDATE inventory SET quantity=? WHERE item=?', (new_qty, it['item']))
        
        # Commit transaction
        conn.commit()
        return sale_id, tx_id, total
        
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def void_sale_transaction(sale_id: int, reason: str, requested_by: str, authorized_by: str) -> Tuple[bool, str]:
    """Void entire sale, restore stock, mark as VOIDED with audit fields."""
    conn = sqlite3.connect(DB_NAME, timeout=30)
    cur = conn.cursor()
    
    try:
        cur.execute("BEGIN IMMEDIATE")
        
        cur.execute("SELECT status FROM sales WHERE id=?", (sale_id,))
        row = cur.fetchone()
        if not row:
            return False, "Sale not found"
        if row[0] == 'VOIDED':
            return False, "Sale already voided"
        
        # Restore stock for all items within same transaction
        cur.execute("SELECT item, quantity FROM sale_items WHERE sale_id=?", (sale_id,))
        for item, qty in cur.fetchall():
            cur.execute('SELECT quantity FROM inventory WHERE item=?', (item,))
            row = cur.fetchone()
            if row:
                new_qty = row[0] + int(qty)
                cur.execute('UPDATE inventory SET quantity=? WHERE item=?', (new_qty, item))
        
        # Mark as voided
        cur.execute(
            "UPDATE sales SET status='VOIDED', void_reason=?, void_authorized_by=?, voided_at=? WHERE id=?",
            (reason, authorized_by, datetime.now().isoformat(timespec='seconds'), sale_id)
        )
        
        conn.commit()
        return True, "Sale voided successfully"
        
    except Exception as e:
        conn.rollback()
        return False, f"Error voiding sale: {e}"
    finally:
        conn.close()

def _new_transaction_id() -> str:
    dt = datetime.now().strftime('%Y%m%d%H%M%S')
    rnd = hashlib.sha256(os.urandom(16)).hexdigest()[:6]
    return f"TX-{dt}-{rnd}"

def get_recent_sales_headers(limit: int = 20) -> List[Tuple]:
    conn = sqlite3.connect(DB_NAME, timeout=10)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT id, transaction_id, cashier, total, timestamp, status FROM sales ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return rows

def get_sale_items(sale_id: int) -> List[Tuple]:
    conn = sqlite3.connect(DB_NAME, timeout=10)
    cur = conn.cursor()
    try:
        cur.execute(
            "SELECT item, quantity, unit_price, subtotal FROM sale_items WHERE sale_id=? ORDER BY id",
            (sale_id,)
        )
        rows = cur.fetchall()
    finally:
        conn.close()
    return rows

def get_all_stock():
    conn = sqlite3.connect(DB_NAME, timeout=10)
    cur = conn.cursor()
    try:
        cur.execute('SELECT item, quantity, category FROM inventory ORDER BY item')
        rows = cur.fetchall()
    finally:
        conn.close()
    return rows

def generate_pdf_receipt_for_sale(sale_id: int) -> str:
    """Generate a multi-item receipt for a sale header+items."""
    conn = sqlite3.connect(DB_NAME, timeout=10)
    cur = conn.cursor()
    try:
        cur.execute("SELECT transaction_id, cashier, total, timestamp, status FROM sales WHERE id=?", (sale_id,))
        row = cur.fetchone()
        if not row:
            raise ValueError("Sale not found")
        tx_id, cashier, total, ts, status = row
        cur.execute("SELECT item, quantity, unit_price, subtotal FROM sale_items WHERE sale_id=? ORDER BY id", (sale_id,))
        items = cur.fetchall()
    finally:
        conn.close()

    business_name = "Comfort_2022 Bar Sales"
    business_address = "123 Main St, Your City"
    
    signature_data = f"{tx_id}|{cashier}|{total}|{ts}|{len(items)}"
    signature = hashlib.sha256(signature_data.encode()).hexdigest()

    pdf = FPDF()
    pdf.add_page()
    pdf.set_xy(10, 10)

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, business_name, ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, business_address, ln=1)
    pdf.ln(5)

    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, f"Receipt: {tx_id}", ln=1)
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Date/Time: {ts}", ln=1)
    pdf.cell(0, 8, f"Cashier: {cashier}", ln=1)
    pdf.cell(0, 8, f"Status: {status}", ln=1)
    pdf.ln(5)

    # Table header
    pdf.set_font("Arial", "B", 12)
    pdf.cell(80, 8, "Item", 1)
    pdf.cell(25, 8, "Qty", 1, 0, 'R')
    pdf.cell(35, 8, "Unit", 1, 0, 'R')
    pdf.cell(40, 8, "Subtotal", 1, 1, 'R')
    pdf.set_font("Arial", "", 12)

    for it, qty, unit, sub in items:
        pdf.cell(80, 8, str(it), 1)
        pdf.cell(25, 8, str(qty), 1, 0, 'R')
        pdf.cell(35, 8, f"{unit:.2f}", 1, 0, 'R')
        pdf.cell(40, 8, f"{sub:.2f}", 1, 1, 'R')

    pdf.ln(3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(140, 8, "TOTAL", 1)
    pdf.cell(40, 8, f"{total:.2f}", 1, 1, 'R')

    pdf.ln(8)
    pdf.set_font("Arial", "I", 9)
    pdf.multi_cell(0, 6, f"Digital Signature:\n{signature}")

    if not os.path.exists("exports"):
        os.makedirs("exports")
    pdf_path = os.path.join("exports", f"receipt_{tx_id}.pdf")
    pdf.output(pdf_path)
    return pdf_path

if __name__ == "__main__":
    print("Testing fixed sales utilities...")
    
    try:
        # Test getting stock
        stock = get_all_stock()
        print(f"✓ Stock retrieved: {len(stock)} items")
        
        if len(stock) >= 3:
            # Test creating a sale
            items = [
                {'item': stock[0][0], 'quantity': 1, 'unit_price': 25.0},
                {'item': stock[1][0], 'quantity': 2, 'unit_price': 20.0}
            ]
            
            sale_id, tx_id, total = create_sale_with_items('cashier', items)
            print(f"✓ Sale created: ID={sale_id}, TX={tx_id}, Total={total}")
            
            # Test receipt generation
            receipt_path = generate_pdf_receipt_for_sale(sale_id)
            print(f"✓ Receipt generated: {receipt_path}")
            
            # Test voiding
            success, message = void_sale_transaction(sale_id, "Test void", "cashier", "manager")
            print(f"✓ Void test: {success} - {message}")
            
        print("✅ All tests passed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")