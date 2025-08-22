import sqlite3
from datetime import datetime

def generate_sales_report_with_corrections(start_date, end_date):
    """Generate comprehensive sales report including corrections"""
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    # Original sales (excluding voids and refunds)
    cur.execute('''
        SELECT 
            DATE(timestamp) as sale_date,
            SUM(CASE WHEN is_voided = 0 AND adjustment_type IS NULL THEN total ELSE 0 END) as gross_sales,
            SUM(CASE WHEN adjustment_type = 'REFUND' THEN total ELSE 0 END) as refunds,
            SUM(CASE WHEN is_voided = 1 THEN total ELSE 0 END) as voided_sales,
            COUNT(CASE WHEN is_voided = 0 AND adjustment_type IS NULL THEN 1 END) as valid_transactions,
            COUNT(CASE WHEN adjustment_type = 'REFUND' THEN 1 END) as refund_transactions,
            COUNT(CASE WHEN is_voided = 1 THEN 1 END) as voided_transactions
        FROM sales 
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY DATE(timestamp)
        ORDER BY sale_date DESC
    ''', (start_date, end_date))
    
    daily_summary = cur.fetchall()
    
    # Detailed corrections
    cur.execute('''
        SELECT 
            c.timestamp,
            c.correction_type,
            c.reason,
            c.original_item,
            c.original_quantity,
            c.correction_amount,
            c.requested_by,
            c.authorized_by
        FROM corrections c
        WHERE DATE(c.timestamp) BETWEEN ? AND ?
        ORDER BY c.timestamp DESC
    ''', (start_date, end_date))
    
    corrections = cur.fetchall()
    conn.close()
    
    return {
        'daily_summary': daily_summary,
        'corrections': corrections
    }

def get_cashier_performance_with_corrections(start_date, end_date):
    """Get cashier performance including correction rates"""
    conn = sqlite3.connect("bar_sales.db")
    cur = conn.cursor()
    
    cur.execute('''
        SELECT 
            username,
            COUNT(CASE WHEN is_voided = 0 AND adjustment_type IS NULL THEN 1 END) as valid_sales,
            COUNT(CASE WHEN is_voided = 1 THEN 1 END) as voided_sales,
            COUNT(CASE WHEN adjustment_type = 'REFUND' THEN 1 END) as refunds,
            SUM(CASE WHEN is_voided = 0 AND adjustment_type IS NULL THEN total ELSE 0 END) as gross_sales,
            SUM(CASE WHEN adjustment_type = 'REFUND' THEN total ELSE 0 END) as refund_amount,
            SUM(total) as net_sales
        FROM sales 
        WHERE DATE(timestamp) BETWEEN ? AND ?
        GROUP BY username
        ORDER BY net_sales DESC
    ''', (start_date, end_date))
    
    results = cur.fetchall()
    conn.close()
    
    performance_data = []
    for row in results:
        username, valid, voided, refunds, gross, refund_amt, net = row
        total_transactions = valid + voided + refunds
        error_rate = ((voided + refunds) / total_transactions * 100) if total_transactions > 0 else 0
        
        performance_data.append({
            'cashier': username,
            'valid_sales': valid,
            'voided_sales': voided,
            'refunds': refunds,
            'total_transactions': total_transactions,
            'error_rate': round(error_rate, 2),
            'gross_sales': gross,
            'refund_amount': refund_amt,
            'net_sales': net
        })
    
    return performance_data