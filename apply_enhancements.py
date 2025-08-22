#!/usr/bin/env python3
"""
Apply enhancements to main.py:
1. Add popup receipt function
2. Replace success message with popup receipt
3. Add enhanced reporting
"""

def apply_enhancements():
    # Read the current main.py
    with open('main.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add popup receipt function before create_cashier_interface
    popup_receipt_function = '''
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
    
    from datetime import datetime
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
            messagebox.showinfo("Receipt Printed", f"Receipt saved to:\\n{pdf_path}")
        except Exception as e:
            messagebox.showerror("Print Error", f"Error generating receipt: {str(e)}")
    
    tk.Button(button_frame, text="📄 Print Receipt", command=print_receipt,
             bg='#3498db', fg='white', font=('Arial', 11, 'bold'), padx=20).pack(side='left', padx=5)
    tk.Button(button_frame, text="✅ Close", command=receipt_window.destroy,
             bg='#27ae60', fg='white', font=('Arial', 11, 'bold'), padx=20).pack(side='right', padx=5)
    
    # Auto-close after 30 seconds
    receipt_window.after(30000, receipt_window.destroy)

'''
    
    # Insert the popup receipt function before create_cashier_interface
    if 'def show_popup_receipt(' not in content:
        content = content.replace(
            'def create_cashier_interface(main_frame, root):',
            popup_receipt_function + '\ndef create_cashier_interface(main_frame, root):'
        )
        print("✓ Added popup receipt function")
    else:
        print("✓ Popup receipt function already exists")
    
    # Replace the success message with popup receipt call
    old_success_block = '''messagebox.showinfo("Success", success_msg)
                payment_dialog.destroy()
                clear_cart()
                update_summary()
                refresh_recent_sales()'''
    
    new_success_block = '''# Show popup receipt instead of simple message
                payment_dialog.destroy()
                show_popup_receipt(root, current_user, sale_id, tx_id, total, payment_method, 
                                 received if payment_method == "Cash" else total_amount,
                                 change if payment_method == "Cash" else 0,
                                 mobile_ref.get() if payment_method == "Mobile Money" else None)
                
                clear_cart()
                update_summary()
                refresh_recent_sales()'''
    
    if old_success_block in content:
        content = content.replace(old_success_block, new_success_block)
        print("✓ Replaced success message with popup receipt")
    else:
        print("✗ Could not find success message block to replace")
    
    # Write the enhanced main.py
    with open('main.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✓ Enhancements applied to main.py")

if __name__ == "__main__":
    apply_enhancements()