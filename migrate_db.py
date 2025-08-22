import sqlite3

def migrate_database():
    print("Starting database migration...")
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    try:
        # Add new columns to sales table
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
                print(f"✓ Added column {column_name}")
            except sqlite3.OperationalError as e:
                if "duplicate column name" in str(e):
                    print(f"- Column {column_name} already exists")
                else:
                    print(f"✗ Error adding {column_name}: {e}")
        
        # Create corrections table
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
        print("✓ Created corrections table")
        
        # Create supervisor_sessions table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS supervisor_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supervisor_name TEXT NOT NULL,
                session_start TEXT NOT NULL,
                cashier_name TEXT NOT NULL,
                action_type TEXT NOT NULL
            )
        ''')
        print("✓ Created supervisor_sessions table")
        
        conn.commit()
        print("✓ Database migration completed successfully!")
        
    except Exception as e:
        print(f"✗ Migration error: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()