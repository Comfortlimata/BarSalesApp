import sqlite3
import hashlib
from datetime import datetime
from tkinter import messagebox

# Supervisor credentials
SUPERVISOR_PINS = {
    'manager': '1234',
    'supervisor': '5678'
}

def hash_pin(pin):
    """Hash supervisor PIN for security"""
    return hashlib.sha256(pin.encode()).hexdigest()

def verify_supervisor_pin(supervisor_name, pin):
    """Verify supervisor PIN"""
    if supervisor_name in SUPERVISOR_PINS:
        return SUPERVISOR_PINS[supervisor_name] == pin
    return False

def ensure_corrections_columns():
    """Ensure all required columns exist in the sales table"""
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    # Check if columns exist and add them if they don't
    columns_to_add = [
        ("is_voided", "INTEGER DEFAULT 0"),
        ("adjustment_type", "TEXT DEFAULT NULL"),
        ("reason", "TEXT DEFAULT NULL"),
        ("authorized_by", "TEXT DEFAULT NULL"),
        ("voided_at", "TEXT DEFAULT NULL"),
        ("original_sale_id", "INTEGER DEFAULT NULL")
    ]
    
    for column_name, column_def in columns_to_add:
        try:
            cur.execute(f"ALTER TABLE sales ADD COLUMN {column_name} {column_def}")
            print(f"Added column {column_name}")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                pass  # Column already exists
            else:
                print(f"Error adding {column_name}: {e}")
    
    # Create corrections table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS corrections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_sale_id INTEGER NOT NULL,
            correction_type TEXT NOT NULL,
            reason TEXT NOT NULL,
            requested_by TEXT NOT NULL,
            authorized_by TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            original_item TEXT NOT NULL,
            original_quantity INTEGER NOT NULL,
            original_price REAL NOT NULL,
            original_total REAL NOT NULL,
            correction_amount REAL NOT NULL
        )
    ''')
    
    # Create supervisor_sessions table if it doesn't exist
    cur.execute('''
        CREATE TABLE IF NOT EXISTS supervisor_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            supervisor_name TEXT NOT NULL,
            session_start TEXT NOT NULL,
            cashier_name TEXT NOT NULL,
            action_type TEXT NOT NULL
        )
    ''')
    
    conn.commit()
    conn.close()

def log_supervisor_session(supervisor_name, cashier_name, action_type):
    """Log supervisor authorization session"""
    ensure_corrections_columns()
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    cur.execute('''
        INSERT INTO supervisor_sessions 
        (supervisor_name, session_start, cashier_name, action_type)
        VALUES (?, ?, ?, ?)
    ''', (supervisor_name, datetime.now().isoformat(), cashier_name, action_type))
    conn.commit()
    conn.close()

def void_sale_item(sale_id, reason, cashier, supervisor_name, supervisor_pin):
    """Void a sale item before payment is processed"""
    if not verify_supervisor_pin(supervisor_name, supervisor_pin):
        return False, "Invalid supervisor credentials"
    
    ensure_corrections_columns()
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    try:
        # Get original sale details
        cur.execute("SELECT * FROM sales WHERE id = ?", (sale_id,))
        original_sale = cur.fetchone()
        
        if not original_sale:
            return False, "Sale not found"
        
        # Check if already voided
        cur.execute("SELECT COALESCE(is_voided, 0) FROM sales WHERE id = ?", (sale_id,))
        result = cur.fetchone()
        if result and result[0] == 1:
            return False, "Sale already voided"
        
        # Mark as voided
        cur.execute('''
            UPDATE sales SET 
            is_voided = 1, 
            adjustment_type = 'VOID',
            reason = ?,
            authorized_by = ?,
            voided_at = ?
            WHERE id = ?
        ''', (reason, supervisor_name, datetime.now().isoformat(), sale_id))
        
        # Log in corrections table
        cur.execute('''
            INSERT INTO corrections 
            (original_sale_id, correction_type, reason, requested_by, authorized_by, 
             timestamp, original_item, original_quantity, original_price, 
             original_total, correction_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (sale_id, 'VOID', reason, cashier, supervisor_name, 
              datetime.now().isoformat(), original_sale[2], original_sale[3], 
              original_sale[4], original_sale[5], -original_sale[5]))
        
        # Update stock (add back voided quantity) if function exists
        try:
            from sales_utils import update_stock
            update_stock(original_sale[2], original_sale[3])
        except:
            pass  # Stock update failed, but void still processed
        
        log_supervisor_session(supervisor_name, cashier, 'VOID')
        conn.commit()
        return True, "Item voided successfully"
        
    except Exception as e:
        conn.rollback()
        return False, f"Error voiding sale: {str(e)}"
    finally:
        conn.close()

def process_refund(original_sale_id, refund_quantity, reason, cashier, supervisor_name, supervisor_pin):
    """Process refund as negative entry after payment"""
    if not verify_supervisor_pin(supervisor_name, supervisor_pin):
        return False, "Invalid supervisor credentials"
    
    ensure_corrections_columns()
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    try:
        # Get original sale details
        cur.execute("SELECT * FROM sales WHERE id = ?", (original_sale_id,))
        original_sale = cur.fetchone()
        
        if not original_sale:
            return False, "Original sale not found"
        
        if refund_quantity > original_sale[3]:
            return False, "Cannot refund more than original quantity"
        
        # Calculate refund amount
        refund_total = (original_sale[4] * refund_quantity)
        
        # Create negative entry
        cur.execute('''
            INSERT INTO sales 
            (username, item, quantity, price_per_unit, total, timestamp, 
             adjustment_type, reason, authorized_by, original_sale_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (cashier, original_sale[2], -refund_quantity, original_sale[4], 
              -refund_total, datetime.now().isoformat(), 'REFUND', reason, 
              supervisor_name, original_sale_id))
        
        refund_id = cur.lastrowid
        
        # Log in corrections table
        cur.execute('''
            INSERT INTO corrections 
            (original_sale_id, correction_type, reason, requested_by, authorized_by, 
             timestamp, original_item, original_quantity, original_price, 
             original_total, correction_amount)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (original_sale_id, 'REFUND', reason, cashier, supervisor_name, 
              datetime.now().isoformat(), original_sale[2], refund_quantity, 
              original_sale[4], original_sale[5], -refund_total))
        
        # Update stock (add back refunded quantity) if function exists
        try:
            from sales_utils import update_stock
            update_stock(original_sale[2], refund_quantity)
        except:
            pass  # Stock update failed, but refund still processed
        
        log_supervisor_session(supervisor_name, cashier, 'REFUND')
        conn.commit()
        return True, f"Refund processed successfully. Refund ID: {refund_id}"
        
    except Exception as e:
        conn.rollback()
        return False, f"Error processing refund: {str(e)}"
    finally:
        conn.close()

def get_recent_sales(cashier, limit=20):
    """Get recent sales for void/refund selection"""
    ensure_corrections_columns()
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    try:
        cur.execute('''
            SELECT id, item, quantity, price_per_unit, total, timestamp, 
                   COALESCE(is_voided, 0) as is_voided,
                   COALESCE(adjustment_type, '') as adjustment_type
            FROM sales 
            WHERE username = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (cashier, limit))
    except sqlite3.OperationalError:
        # Fallback if columns don't exist
        cur.execute('''
            SELECT id, item, quantity, price_per_unit, total, timestamp, 
                   0 as is_voided, '' as adjustment_type
            FROM sales 
            WHERE username = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (cashier, limit))
    
    sales = cur.fetchall()
    conn.close()
    return sales

def get_correction_report(start_date, end_date):
    """Generate correction report"""
    ensure_corrections_columns()
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    # Get all corrections in date range
    cur.execute('''
        SELECT c.*, s.timestamp as original_timestamp
        FROM corrections c
        JOIN sales s ON c.original_sale_id = s.id
        WHERE DATE(c.timestamp) BETWEEN ? AND ?
        ORDER BY c.timestamp DESC
    ''', (start_date, end_date))
    
    corrections = cur.fetchall()
    conn.close()
    return corrections

# Initialize corrections on import
if __name__ != "__main__":
    ensure_corrections_columns()