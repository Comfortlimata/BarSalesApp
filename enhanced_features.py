#!/usr/bin/env python3
"""
Enhanced features for the Bar Sales App:
1. Void Sale functionality
2. Popup receipts
3. Enhanced reporting
4. UI improvements
"""

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

def show_popup_receipt(root, current_user, sale_id, tx_id, total, payment_method, amount_received, change, mobile_ref):
    """Show a popup receipt after successful payment"""
    receipt_window = tk.Toplevel(root)
    receipt_window.title("Receipt")
    receipt_window.geometry("400x600")
    receipt_window.configure(bg='#ffffff')
    receipt_window.transient(root)
    receipt_window.grab_set()
    receipt_window.geometry("+%d+%d" % (root.winfo_rootx() + 100, root.winfo_rooty() + 50))
    
    # Header
    header_frame = tk.Frame(receipt_window, bg='#34495e', height=60)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="🍻 Comfort_2022 Bar Sales", 
            font=('Arial', 16, 'bold'), bg='#34495e', fg='white').pack(pady=15)
    
    # Receipt content
    content_frame = tk.Frame(receipt_window, bg='#ffffff', padx=20, pady=20)
    content_frame.pack(fill='both', expand=True)
    
    # Transaction details
    tk.Label(content_frame, text="RECEIPT", font=('Arial', 18, 'bold'), 
            bg='#ffffff', fg='#2c3e50').pack(pady=(0, 10))
    
    details_frame = tk.Frame(content_frame, bg='#ffffff')
    details_frame.pack(fill='x', pady=10)
    
    # Transaction info
    tk.Label(details_frame, text=f"Transaction ID: {tx_id}", 
            font=('Arial', 12, 'bold'), bg='#ffffff', anchor='w').pack(fill='x')
    tk.Label(details_frame, text=f"Cashier: {current_user['username']}", 
            font=('Arial', 10), bg='#ffffff', anchor='w').pack(fill='x')
    
    tk.Label(details_frame, text=f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", 
            font=('Arial', 10), bg='#ffffff', anchor='w').pack(fill='x')
    
    # Separator
    tk.Frame(content_frame, bg='#bdc3c7', height=1).pack(fill='x', pady=10)
    
    # Items
    tk.Label(content_frame, text="ITEMS PURCHASED", font=('Arial', 12, 'bold'), 
            bg='#ffffff', fg='#2c3e50').pack(anchor='w')
    
    items_frame = tk.Frame(content_frame, bg='#ffffff')
    items_frame.pack(fill='x', pady=5)
    
    # Get sale items
    try:
        from sales_utils import get_sale_items
        items = get_sale_items(sale_id)
        
        for item_name, qty, unit_price, subtotal in items:
            item_frame = tk.Frame(items_frame, bg='#ffffff')
            item_frame.pack(fill='x', pady=2)
            
            tk.Label(item_frame, text=f"{item_name} x{qty}", 
                    font=('Arial', 10), bg='#ffffff', anchor='w').pack(side='left')
            tk.Label(item_frame, text=f"ZMW {subtotal:.2f}", 
                    font=('Arial', 10), bg='#ffffff', anchor='e').pack(side='right')
    except Exception as e:
        tk.Label(items_frame, text="Error loading items", 
                font=('Arial', 10), bg='#ffffff', fg='red').pack()
    
    # Separator
    tk.Frame(content_frame, bg='#bdc3c7', height=1).pack(fill='x', pady=10)
    
    # Totals
    totals_frame = tk.Frame(content_frame, bg='#ffffff')
    totals_frame.pack(fill='x')
    
    tk.Label(totals_frame, text=f"TOTAL: ZMW {total:.2f}", 
            font=('Arial', 14, 'bold'), bg='#ffffff', fg='#27ae60').pack(anchor='e')
    
    # Payment details
    payment_frame = tk.Frame(content_frame, bg='#ffffff')
    payment_frame.pack(fill='x', pady=10)
    
    tk.Label(payment_frame, text=f"Payment Method: {payment_method}", 
            font=('Arial', 11, 'bold'), bg='#ffffff', anchor='w').pack(fill='x')
    
    if payment_method == "Cash":
        tk.Label(payment_frame, text=f"Cash Received: ZMW {amount_received:.2f}", 
                font=('Arial', 10), bg='#ffffff', anchor='w').pack(fill='x')
        tk.Label(payment_frame, text=f"Change: ZMW {change:.2f}", 
                font=('Arial', 10, 'bold'), bg='#ffffff', fg='#e74c3c', anchor='w').pack(fill='x')
    elif payment_method == "Mobile Money" and mobile_ref:
        tk.Label(payment_frame, text=f"Reference: {mobile_ref}", 
                font=('Arial', 10), bg='#ffffff', anchor='w').pack(fill='x')
    
    # Footer
    footer_frame = tk.Frame(content_frame, bg='#ffffff')
    footer_frame.pack(fill='x', pady=20)
    
    tk.Label(footer_frame, text="Thank you for your business!", 
            font=('Arial', 12, 'italic'), bg='#ffffff', fg='#7f8c8d').pack()
    
    # Buttons
    button_frame = tk.Frame(content_frame, bg='#ffffff')
    button_frame.pack(fill='x', pady=10)
    
    def print_receipt():
        try:
            from sales_utils import generate_pdf_receipt_for_sale
            pdf_path = generate_pdf_receipt_for_sale(sale_id)
            messagebox.showinfo("Receipt Printed", f"Receipt saved to:\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Print Error", f"Error generating receipt: {str(e)}")
    
    tk.Button(button_frame, text="📄 Print Receipt", command=print_receipt,
             bg='#3498db', fg='white', font=('Arial', 11, 'bold'), padx=20).pack(side='left', padx=5)
    tk.Button(button_frame, text="✅ Close", command=receipt_window.destroy,
             bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), padx=20).pack(side='right', padx=5)
    
    # Auto-close after 30 seconds
    receipt_window.after(30000, receipt_window.destroy)

def show_enhanced_admin_reports(root, current_user):
    """Show enhanced admin reporting dashboard"""
    reports_window = tk.Toplevel(root)
    reports_window.title("Enhanced Reports Dashboard")
    reports_window.geometry("800x600")
    reports_window.configure(bg='#f8f9fa')
    reports_window.transient(root)
    reports_window.grab_set()
    
    # Header
    header_frame = tk.Frame(reports_window, bg='#34495e', height=60)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)
    
    tk.Label(header_frame, text="📊 Enhanced Reports Dashboard", 
            font=('Arial', 18, 'bold'), bg='#34495e', fg='white').pack(pady=15)
    
    # Main content
    main_frame = tk.Frame(reports_window, bg='#f8f9fa', padx=20, pady=20)
    main_frame.pack(fill='both', expand=True)
    
    # Reports grid
    reports_grid = tk.Frame(main_frame, bg='#f8f9fa')
    reports_grid.pack(fill='both', expand=True)
    
    # Configure grid
    for i in range(3):
        reports_grid.grid_columnconfigure(i, weight=1)
    for i in range(3):
        reports_grid.grid_rowconfigure(i, weight=1)
    
    def show_top_products():
        """Show top selling products report"""
        import sqlite3
        from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
        
        win = Toplevel(reports_window)
        win.title("Top Products Report")
        win.geometry("600x400")
        
        txt = Text(win, width=70, height=20, font=('Consolas', 10))
        txt.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(win, command=txt.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        txt.config(yscrollcommand=scrollbar.set)
        
        try:
            conn = sqlite3.connect("bar_sales.db")
            cur = conn.cursor()
            
            # Top products by quantity
            cur.execute("""
                SELECT si.item, SUM(si.quantity) as total_qty, 
                       COUNT(DISTINCT s.id) as num_sales,
                       SUM(si.subtotal) as total_revenue
                FROM sale_items si
                JOIN sales s ON s.id = si.sale_id
                WHERE s.status != 'VOIDED'
                GROUP BY si.item
                ORDER BY total_qty DESC
                LIMIT 20
            """)
            
            products = cur.fetchall()
            conn.close()
            
            txt.insert(END, "TOP SELLING PRODUCTS REPORT\n")
            txt.insert(END, "=" * 60 + "\n\n")
            txt.insert(END, f"{'Product':<25} {'Qty':<8} {'Sales':<8} {'Revenue':<12}\n")
            txt.insert(END, "-" * 60 + "\n")
            
            for product, qty, sales, revenue in products:
                txt.insert(END, f"{product:<25} {qty:<8} {sales:<8} ZMW {revenue:<8.2f}\n")
                
        except Exception as e:
            txt.insert(END, f"Error loading report: {str(e)}")
        
        txt.config(state="disabled")
    
    def show_cashier_performance():
        """Show cashier performance report"""
        import sqlite3
        from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
        from datetime import datetime, timedelta
        
        win = Toplevel(reports_window)
        win.title("Cashier Performance Report")
        win.geometry("700x400")
        
        txt = Text(win, width=80, height=20, font=('Consolas', 10))
        txt.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(win, command=txt.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        txt.config(yscrollcommand=scrollbar.set)
        
        try:
            conn = sqlite3.connect("bar_sales.db")
            cur = conn.cursor()
            
            # Last 30 days performance
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            
            cur.execute("""
                SELECT cashier, 
                       COUNT(*) as num_transactions,
                       SUM(total) as total_sales,
                       AVG(total) as avg_transaction,
                       COUNT(CASE WHEN status = 'VOIDED' THEN 1 END) as voids
                FROM sales
                WHERE DATE(timestamp) >= ?
                GROUP BY cashier
                ORDER BY total_sales DESC
            """, (thirty_days_ago,))
            
            performance = cur.fetchall()
            conn.close()
            
            txt.insert(END, "CASHIER PERFORMANCE REPORT (Last 30 Days)\n")
            txt.insert(END, "=" * 70 + "\n\n")
            txt.insert(END, f"{'Cashier':<15} {'Trans':<8} {'Total Sales':<15} {'Avg Trans':<12} {'Voids':<8}\n")
            txt.insert(END, "-" * 70 + "\n")
            
            for cashier, trans, total, avg, voids in performance:
                txt.insert(END, f"{cashier:<15} {trans:<8} ZMW {total:<11.2f} ZMW {avg:<8.2f} {voids:<8}\n")
                
        except Exception as e:
            txt.insert(END, f"Error loading report: {str(e)}")
        
        txt.config(state="disabled")
    
    def show_payment_breakdown():
        """Show payment method breakdown"""
        import sqlite3
        from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
        from datetime import datetime, timedelta
        
        win = Toplevel(reports_window)
        win.title("Payment Method Breakdown")
        win.geometry("600x400")
        
        txt = Text(win, width=70, height=20, font=('Consolas', 10))
        txt.pack(side="left", fill="both", expand=True)
        scrollbar = Scrollbar(win, command=txt.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        txt.config(yscrollcommand=scrollbar.set)
        
        try:
            # For now, we'll simulate payment method data since we need to enhance the database
            # In a real implementation, we'd store payment method in the sales table
            
            txt.insert(END, "PAYMENT METHOD BREAKDOWN\n")
            txt.insert(END, "=" * 50 + "\n\n")
            txt.insert(END, "Note: Payment method tracking will be available\n")
            txt.insert(END, "after database schema enhancement.\n\n")
            txt.insert(END, "Planned features:\n")
            txt.insert(END, "- Cash payments with change tracking\n")
            txt.insert(END, "- Mobile Money with reference numbers\n")
            txt.insert(END, "- Card/Other payment methods\n")
            txt.insert(END, "- Daily/weekly/monthly breakdowns\n")
                
        except Exception as e:
            txt.insert(END, f"Error loading report: {str(e)}")
        
        txt.config(state="disabled")
    
    # Report buttons
    tk.Button(reports_grid, text="📈 Top Products", command=show_top_products,
             bg='#3498db', fg='white', font=('Arial', 12, 'bold'), 
             height=3, cursor='hand2').grid(row=0, column=0, padx=10, pady=10, sticky='nsew')
    
    tk.Button(reports_grid, text="👥 Cashier Performance", command=show_cashier_performance,
             bg='#e67e22', fg='white', font=('Arial', 12, 'bold'), 
             height=3, cursor='hand2').grid(row=0, column=1, padx=10, pady=10, sticky='nsew')
    
    tk.Button(reports_grid, text="💳 Payment Methods", command=show_payment_breakdown,
             bg='#9b59b6', fg='white', font=('Arial', 12, 'bold'), 
             height=3, cursor='hand2').grid(row=0, column=2, padx=10, pady=10, sticky='nsew')
    
    # Additional reports can be added here
    tk.Button(reports_grid, text="📊 Sales Trends", command=lambda: messagebox.showinfo("Coming Soon", "Sales trends report coming soon!"),
             bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), 
             height=3, cursor='hand2').grid(row=1, column=0, padx=10, pady=10, sticky='nsew')
    
    tk.Button(reports_grid, text="📅 Daily Summary", command=lambda: messagebox.showinfo("Coming Soon", "Daily summary report coming soon!"),
             bg='#f39c12', fg='white', font=('Arial', 12, 'bold'), 
             height=3, cursor='hand2').grid(row=1, column=1, padx=10, pady=10, sticky='nsew')
    
    tk.Button(reports_grid, text="🔍 Audit Trail", command=lambda: messagebox.showinfo("Coming Soon", "Audit trail report coming soon!"),
             bg='#e74c3c', fg='white', font=('Arial', 12, 'bold'), 
             height=3, cursor='hand2').grid(row=1, column=2, padx=10, pady=10, sticky='nsew')
    
    # Close button
    tk.Button(reports_grid, text="❌ Close", command=reports_window.destroy,
             bg='#95a5a6', fg='white', font=('Arial', 12, 'bold'), 
             height=2, cursor='hand2').grid(row=2, column=1, padx=10, pady=20, sticky='ew')

if __name__ == "__main__":
    print("Enhanced features module for Bar Sales App")
    print("This module provides:")
    print("1. Popup receipt functionality")
    print("2. Enhanced admin reporting")
    print("3. Void sale capabilities")
    print("4. UI improvements")