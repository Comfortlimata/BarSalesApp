# 1. Database constraints and triggers
def create_audit_triggers():
    """Create database triggers to ensure audit trail integrity"""
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    # Prevent deletion of sales records
    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS prevent_sales_delete
        BEFORE DELETE ON sales
        BEGIN
            SELECT RAISE(ABORT, 'Sales records cannot be deleted for audit purposes');
        END
    ''')
    
    # Log all sales updates
    cur.execute('''
        CREATE TABLE IF NOT EXISTS sales_audit_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sale_id INTEGER,
            field_changed TEXT,
            old_value TEXT,
            new_value TEXT,
            changed_by TEXT,
            timestamp TEXT
        )
    ''')
    
    # Trigger for sales updates
    cur.execute('''
        CREATE TRIGGER IF NOT EXISTS sales_update_audit
        AFTER UPDATE ON sales
        FOR EACH ROW
        BEGIN
            INSERT INTO sales_audit_log (sale_id, field_changed, old_value, new_value, changed_by, timestamp)
            SELECT NEW.id, 'is_voided', OLD.is_voided, NEW.is_voided, NEW.authorized_by, datetime('now')
            WHERE OLD.is_voided != NEW.is_voided;
            
            INSERT INTO sales_audit_log (sale_id, field_changed, old_value, new_value, changed_by, timestamp)
            SELECT NEW.id, 'adjustment_type', OLD.adjustment_type, NEW.adjustment_type, NEW.authorized_by, datetime('now')
            WHERE OLD.adjustment_type != NEW.adjustment_type OR (OLD.adjustment_type IS NULL AND NEW.adjustment_type IS NOT NULL);
        END
    ''')
    
    conn.commit()
    conn.close()

# 2. Data validation functions
def validate_correction_integrity():
    """Validate that all corrections have proper authorization and audit trail"""
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    issues = []
    
    # Check for voids without supervisor authorization
    cur.execute('''
        SELECT id, item, total FROM sales 
        WHERE is_voided = 1 AND authorized_by IS NULL
    ''')
    unauthorized_voids = cur.fetchall()
    if unauthorized_voids:
        issues.append(f"Found {len(unauthorized_voids)} voided sales without supervisor authorization")
    
    # Check for refunds without corresponding correction records
    cur.execute('''
        SELECT s.id FROM sales s
        LEFT JOIN corrections c ON s.id = c.original_sale_id
        WHERE s.adjustment_type = 'REFUND' AND c.id IS NULL
    ''')
    missing_correction_records = cur.fetchall()
    if missing_correction_records:
        issues.append(f"Found {len(missing_correction_records)} refunds without correction records")
    
    # Check for negative sales without refund type
    cur.execute('''
        SELECT id, item, total FROM sales 
        WHERE total < 0 AND adjustment_type IS NULL
    ''')
    invalid_negatives = cur.fetchall()
    if invalid_negatives:
        issues.append(f"Found {len(invalid_negatives)} negative sales without refund classification")
    
    conn.close()
    return issues

# 3. Regular integrity checks
def schedule_integrity_checks():
    """Schedule regular integrity checks"""
    import threading
    import time
    
    def daily_integrity_check():
        while True:
            # Run at 2 AM daily
            now = datetime.now()
            if now.hour == 2 and now.minute == 0:
                issues = validate_correction_integrity()
                if issues:
                    # Log issues or send alerts
                    with open('integrity_issues.log', 'a') as f:
                        f.write(f"{datetime.now()}: {issues}\n")
            
            time.sleep(60)  # Check every minute
    
    # Run in background thread
    integrity_thread = threading.Thread(target=daily_integrity_check, daemon=True)
    integrity_thread.start()

# 4. Backup strategies
def create_audit_backup():
    """Create backup specifically for audit purposes"""
    import shutil
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"audit_backup_{timestamp}.db"
    
    try:
        shutil.copy2("bar_sales.db", f"backups/{backup_name}")
        return f"Audit backup created: {backup_name}"
    except Exception as e:
        return f"Backup failed: {str(e)}"

python schema_migration.py