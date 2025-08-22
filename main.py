# main.py
import tkinter as tk
from tkinter import messagebox, ttk
from sales_utils import init_db, record_sale, generate_pdf_receipt, backup_today_sales, log_audit_event, export_all_sales_to_csv, get_all_stock
import sales_corrections  # Add this import
import os

# Hardcoded users and roles
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'cashier': {'password': 'cashier123', 'role': 'cashier'}
}

current_user = {'username': '', 'role': ''}

def restart_login():
    """Restart the login window"""
    global login_window, entry_username, entry_password
    login_window = tk.Tk()
    login_window.title("Login - Bar Sales App")
    login_window.geometry("400x300")
    login_window.configure(bg='#f0f0f0')

    # Login form
    login_frame = tk.Frame(login_window, bg='#f0f0f0')
    login_frame.pack(padx=20, pady=20)
    login_frame.grid_columnconfigure(1, weight=1)

    login_frame_label = tk.Label(login_frame, text="Please login to continue", 
                                font=("Arial", 12, "bold"), bg='#f0f0f0')
    login_frame_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

    label_username = tk.Label(login_frame, text="Username:", bg='#f0f0f0')
    label_username.grid(row=1, column=0, sticky="e", padx=(0, 10), pady=5)
    entry_username = tk.Entry(login_frame, font=('Arial', 10))
    entry_username.grid(row=1, column=1, pady=5, sticky='ew')

    label_password = tk.Label(login_frame, text="Password:", bg='#f0f0f0')
    label_password.grid(row=2, column=0, sticky="e", padx=(0, 10), pady=5)
    entry_password = tk.Entry(login_frame, show="*", font=('Arial', 10))
    entry_password.grid(row=2, column=1, pady=5, sticky='ew')

    login_btn = tk.Button(login_frame, text="Login", command=login, 
                         bg='#3498db', fg='white', font=('Arial', 10, 'bold'))
    login_btn.grid(row=3, column=0, columnspan=2, pady=10)

    # Bind Enter key to login
    entry_password.bind('<Return>', lambda event: login())
    
    login_window.mainloop()

def login():
    username = entry_username.get()
    password = entry_password.get()
    user = USERS.get(username)
    if user and user['password'] == password:
        current_user['username'] = username
        current_user['role'] = user['role']
        login_window.destroy()
        show_main_app()
        return
    # Check database users
    from sales_utils import get_user, check_password
    db_user = get_user(username)
    if db_user and check_password(password, db_user['password_hash']):
        current_user['username'] = username
        current_user['role'] = db_user['role']
        login_window.destroy()
        show_main_app()
    else:
        messagebox.showerror("Login Failed", "Invalid username or password.")

def show_main_app():
    root = tk.Tk()
    root.title("🍻 Bar Sales – Comfort_2022")
    root.geometry("900x700")
    root.configure(bg='#ecf0f1')
    
    # Enhanced header with gradient-like effect
    header_frame = tk.Frame(root, bg='#34495e', height=70)
    header_frame.pack(fill='x')
    header_frame.pack_propagate(False)
    
    # Add a subtle separator line
    separator = tk.Frame(root, bg='#bdc3c7', height=2)
    separator.pack(fill='x')
    
    # User info with better styling
    user_frame = tk.Frame(header_frame, bg='#34495e')
    user_frame.pack(fill='x', padx=25, pady=15)
    
    # Welcome message with icon
    welcome_text = f"👋 Welcome, {current_user['username'].title()} ({current_user['role'].title()})"
    tk.Label(user_frame, text=welcome_text, 
             bg='#34495e', fg='#ecf0f1', font=('Arial', 14, 'bold')).pack(side='left')
    
    # --- Session Timeout (Fixed) ---
    SESSION_TIMEOUT_MS = 10 * 60 * 1000  # 10 minutes in milliseconds
    timeout_timer = {'id': None, 'active': True}  # Use dict instead of list

    def logout_due_to_timeout():
        if not timeout_timer['active']:
            return
        try:
            if root.winfo_exists():  # Check if window still exists
                messagebox.showwarning("Session Timeout", "You have been logged out due to inactivity.")
                cleanup_and_logout()
        except tk.TclError:
            pass  # Window already destroyed

    def reset_timeout(event=None):
        if not timeout_timer['active']:
            return
        try:
            if timeout_timer['id'] and root.winfo_exists():
                root.after_cancel(timeout_timer['id'])
            if root.winfo_exists():
                timeout_timer['id'] = root.after(SESSION_TIMEOUT_MS, logout_due_to_timeout)
        except tk.TclError:
            pass  # Window already destroyed

    def cleanup_and_logout():
        timeout_timer['active'] = False
        if timeout_timer['id']:
            try:
                root.after_cancel(timeout_timer['id'])
            except tk.TclError:
                pass
        try:
            root.destroy()
        except tk.TclError:
            pass
        restart_login()
    
    # Logout button with better styling
    def logout():
        cleanup_and_logout()
    
    logout_btn = tk.Button(user_frame, text="🚪 Logout", command=logout, 
                          bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                          padx=20, pady=5, relief='raised', bd=2, cursor='hand2')
    logout_btn.pack(side='right')
    
    # Hover effect for logout button
    def on_logout_enter(e):
        logout_btn.config(bg='#c0392b')
    def on_logout_leave(e):
        logout_btn.config(bg='#e74c3c')
    logout_btn.bind('<Enter>', on_logout_enter)
    logout_btn.bind('<Leave>', on_logout_leave)

    # Main content with padding
    main_frame = tk.Frame(root, bg='#ecf0f1')
    main_frame.pack(fill='both', expand=True, padx=25, pady=25)

    # Bind all user activity to reset the timer
    def bind_timeout_reset(widget):
        widget.bind('<Key>', reset_timeout)
        widget.bind('<Button>', reset_timeout)
        widget.bind('<Motion>', reset_timeout)
        for child in widget.winfo_children():
            bind_timeout_reset(child)
    
    # Bind timeout reset to all widgets
    bind_timeout_reset(root)
    reset_timeout()
    
    # Handle window close event
    def on_window_close():
        cleanup_and_logout()
    
    root.protocol("WM_DELETE_WINDOW", on_window_close)
    # --- End Session Timeout ---

    if current_user['role'] == 'cashier':
        create_cashier_interface(main_frame, root)

    elif current_user['role'] == 'admin':
        # Admin: View sales log, dashboard, export, user management
        def view_sales():
            import sqlite3
            from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
            win = Toplevel(root)
            win.title("All Sales Log")
            txt = Text(win, width=80, height=20)
            txt.pack(side="left", fill="both", expand=True)
            scrollbar = Scrollbar(win, command=txt.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            txt.config(yscrollcommand=scrollbar.set)
            conn = sqlite3.connect("bar_sales.db")
            cur = conn.cursor()
            cur.execute("""
                SELECT s.cashier, si.item, si.quantity, si.unit_price, si.subtotal, s.timestamp 
                FROM sales s 
                JOIN sale_items si ON s.id = si.sale_id 
                WHERE s.status != 'VOIDED'
                ORDER BY s.timestamp DESC
            """)
            rows = cur.fetchall()
            conn.close()
            txt.insert(END, f"{'User':<10} {'Item':<15} {'Qty':<5} {'Unit Price':<10} {'Total':<10} {'Time':<20}\n")
            txt.insert(END, "-"*75+"\n")
            for row in rows:
                txt.insert(END, f"{row[0]:<10} {row[1]:<15} {row[2]:<5} {row[3]:<10.2f} {row[4]:<10.2f} {row[5]:<20}\n")
            txt.config(state="disabled")

        def user_management():
            import sqlite3
            from tkinter import Toplevel, Frame, Label, Entry, Button, Listbox, Scrollbar, StringVar, OptionMenu, messagebox, simpledialog, END, SINGLE
            import sales_utils

            def refresh_user_list():
                user_list.delete(0, END)
                conn = sqlite3.connect("bar_sales.db")
                cur = conn.cursor()
                cur.execute("SELECT username, role FROM users ORDER BY username")
                for row in cur.fetchall():
                    user_list.insert(END, f"{row[0]} ({row[1]})")
                conn.close()

            def add_user():
                def save_new_user():
                    uname = entry_uname.get().strip()
                    pwd = entry_pwd.get()
                    role = role_var.get()
                    if not uname or not pwd:
                        messagebox.showerror("Error", "Username and password required.")
                        return
                    if sales_utils.get_user(uname):
                        messagebox.showerror("Error", "Username already exists.")
                        return
                    if sales_utils.create_user(uname, pwd, role):
                        messagebox.showinfo("Success", f"User '{uname}' added.")
                        win_add.destroy()
                        refresh_user_list()
                    else:
                        messagebox.showerror("Error", "Failed to add user.")
                win_add = Toplevel(win_um)
                win_add.title("Add User")
                Label(win_add, text="Username:").grid(row=0, column=0)
                entry_uname = Entry(win_add)
                entry_uname.grid(row=0, column=1)
                Label(win_add, text="Password:").grid(row=1, column=0)
                entry_pwd = Entry(win_add, show="*")
                entry_pwd.grid(row=1, column=1)
                Label(win_add, text="Role:").grid(row=2, column=0)
                role_var = StringVar(win_add)
                role_var.set("cashier")
                OptionMenu(win_add, role_var, "admin", "cashier").grid(row=2, column=1)
                Button(win_add, text="Save", command=save_new_user).grid(row=3, column=0, columnspan=2, pady=5)

            def edit_user():
                sel = user_list.curselection()
                if not sel:
                    messagebox.showerror("Error", "Select a user to edit.")
                    return
                uname = user_list.get(sel[0]).split()[0]
                user = sales_utils.get_user(uname)
                if not user:
                    messagebox.showerror("Error", "User not found.")
                    return
                def save_edit_user():
                    new_pwd = entry_pwd.get()
                    new_role = role_var.get()
                    conn = sqlite3.connect("bar_sales.db")
                    cur = conn.cursor()
                    if new_pwd:
                        new_hash = sales_utils.hash_password(new_pwd)
                        cur.execute("UPDATE users SET password_hash=?, role=? WHERE username=?", (new_hash, new_role, uname))
                    else:
                        cur.execute("UPDATE users SET role=? WHERE username=?", (new_role, uname))
                    conn.commit()
                    conn.close()
                    messagebox.showinfo("Success", f"User '{uname}' updated.")
                    win_edit.destroy()
                    refresh_user_list()
                win_edit = Toplevel(win_um)
                win_edit.title(f"Edit User: {uname}")
                Label(win_edit, text="New Password (leave blank to keep current):").grid(row=0, column=0)
                entry_pwd = Entry(win_edit, show="*")
                entry_pwd.grid(row=0, column=1)
                Label(win_edit, text="Role:").grid(row=1, column=0)
                role_var = StringVar(win_edit)
                role_var.set(user['role'])
                OptionMenu(win_edit, role_var, "admin", "cashier").grid(row=1, column=1)
                Button(win_edit, text="Save", command=save_edit_user).grid(row=2, column=0, columnspan=2, pady=5)

            def delete_user():
                sel = user_list.curselection()
                if not sel:
                    messagebox.showerror("Error", "Select a user to delete.")
                    return
                uname = user_list.get(sel[0]).split()[0]
                if uname == current_user['username']:
                    messagebox.showerror("Error", "You cannot delete the currently logged-in user.")
                    return
                # Prevent deleting last admin
                conn = sqlite3.connect("bar_sales.db")
                cur = conn.cursor()
                cur.execute("SELECT COUNT(*) FROM users WHERE role='admin'")
                admin_count = cur.fetchone()[0]
                if admin_count <= 1:
                    cur.execute("SELECT role FROM users WHERE username=?", (uname,))
                    if cur.fetchone()[0] == 'admin':
                        conn.close()
                        messagebox.showerror("Error", "Cannot delete the last admin user.")
                        return
                cur.execute("DELETE FROM users WHERE username=?", (uname,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", f"User '{uname}' deleted.")
                refresh_user_list()

            win_um = Toplevel(root)
            win_um.title("User Management")
            frame = Frame(win_um)
            frame.pack(padx=10, pady=10)
            user_list = Listbox(frame, width=30, height=10, selectmode=SINGLE)
            user_list.grid(row=0, column=0, rowspan=4)
            scrollbar = Scrollbar(frame, command=user_list.yview)
            scrollbar.grid(row=0, column=1, rowspan=4, sticky='ns')
            user_list.config(yscrollcommand=scrollbar.set)
            Button(frame, text="Add User", command=add_user).grid(row=0, column=2, padx=5)
            Button(frame, text="Edit User", command=edit_user).grid(row=1, column=2, padx=5)
            Button(frame, text="Delete User", command=delete_user).grid(row=2, column=2, padx=5)
            Button(frame, text="Refresh", command=refresh_user_list).grid(row=3, column=2, padx=5)
            refresh_user_list()

        def dashboard_prompt():
            from tkinter.simpledialog import askstring
            pw = askstring("Dashboard Access", "Enter admin password:", show="*")
            if pw == USERS['admin']['password']:
                # Notify admin if today's sales are below average
                import sqlite3
                from datetime import datetime, timedelta
                import matplotlib
                matplotlib.use('TkAgg')
                from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
                import matplotlib.pyplot as plt
                conn = sqlite3.connect('bar_sales.db')
                cur = conn.cursor()
                today = datetime.now().strftime('%Y-%m-%d')
                # 7-day sales
                cur.execute("SELECT DATE(timestamp), SUM(total) FROM sales WHERE status != 'VOIDED' GROUP BY DATE(timestamp) ORDER BY DATE(timestamp) DESC LIMIT 7")
                rows = cur.fetchall()[::-1]
                dates = [r[0] for r in rows]
                totals = [r[1] for r in rows]
                # Top items
                cur.execute("SELECT si.item, SUM(si.quantity) as qty FROM sales s JOIN sale_items si ON s.id = si.sale_id WHERE s.status != 'VOIDED' GROUP BY si.item ORDER BY qty DESC LIMIT 5")
                item_rows = cur.fetchall()
                items = [r[0] for r in item_rows]
                qtys = [r[1] for r in item_rows]
                # Sales by user
                cur.execute("SELECT cashier, SUM(total) FROM sales WHERE status != 'VOIDED' GROUP BY cashier ORDER BY SUM(total) DESC")
                user_rows = cur.fetchall()
                users = [r[0] for r in user_rows]
                user_totals = [r[1] for r in user_rows]
                # Sales by hour
                cur.execute("SELECT strftime('%H', timestamp) as hour, SUM(total) FROM sales WHERE status != 'VOIDED' GROUP BY hour ORDER BY hour")
                hour_rows = cur.fetchall()
                hours = [r[0] for r in hour_rows]
                hour_totals = [r[1] for r in hour_rows]
                conn.close()
                # Show warning if sales are low
                if rows:
                    avg = sum(totals) / len(totals)
                    cur_total = totals[-1] if dates and dates[-1] == today else 0
                    if cur_total < 0.5 * avg:
                        messagebox.showwarning('Low Sales Alert', f"Today's sales (ZMW {cur_total:.2f}) are below 50% of the recent average (ZMW {avg:.2f})!")
                log_audit_event(f"Dashboard opened by {current_user['username']}")
                # Analytics window
                dash = tk.Toplevel()
                dash.title("Sales Analytics Dashboard")
                fig, axs = plt.subplots(2, 2, figsize=(12, 8))
                # 7-day sales chart
                axs[0,0].bar(dates, totals, color='skyblue')
                axs[0,0].set_title('Daily Sales (Last 7 Days)')
                axs[0,0].set_ylabel('Total Sales (ZMW)')
                axs[0,0].set_xlabel('Date')
                axs[0,0].tick_params(axis='x', rotation=30)
                # Top items chart
                axs[0,1].bar(items, qtys, color='orange')
                axs[0,1].set_title('Top 5 Selling Items')
                axs[0,1].set_ylabel('Quantity Sold')
                axs[0,1].set_xlabel('Item')
                axs[0,1].tick_params(axis='x', rotation=30)
                # Sales by user chart
                axs[1,0].bar(users, user_totals, color='green')
                axs[1,0].set_title('Sales by User')
                axs[1,0].set_ylabel('Total Sales (ZMW)')
                axs[1,0].set_xlabel('User')
                axs[1,0].tick_params(axis='x', rotation=30)
                # Sales by hour chart
                axs[1,1].bar(hours, hour_totals, color='purple')
                axs[1,1].set_title('Sales by Hour')
                axs[1,1].set_ylabel('Total Sales (ZMW)')
                axs[1,1].set_xlabel('Hour (24h)')
                axs[1,1].tick_params(axis='x', rotation=0)
                plt.tight_layout()
                canvas = FigureCanvasTkAgg(fig, master=dash)
                canvas.draw()
                canvas.get_tk_widget().pack(fill='both', expand=True)
                # Show remaining stock below charts
                stock_list = get_all_stock()
                stock_text = "\n".join([f"{item} ({cat}): {qty}" for item, qty, cat in stock_list])
                import tkinter.scrolledtext as st
                stock_label = tk.Label(dash, text="\nCurrent Stock:", font=("Arial", 12, "bold"))
                stock_label.pack(anchor='w', padx=10, pady=(10,0))
                stock_box = st.ScrolledText(dash, height=8, width=40, font=("Consolas", 10))
                stock_box.pack(fill='x', padx=10, pady=(0,10))
                stock_box.insert('end', stock_text)
                stock_box.config(state='disabled')
            else:
                messagebox.showerror("Access Denied", "Incorrect password.")

        def export_all_sales():
            import sqlite3
            from tkinter import Toplevel, Label, Button, Checkbutton, IntVar, messagebox, StringVar, OptionMenu
            from tkcalendar import DateEntry
            from datetime import datetime, timedelta
            win = Toplevel(root)
            win.title("Export All Sales - Options")
            # Get min/max dates from sales
            conn = sqlite3.connect('bar_sales.db')
            cur = conn.cursor()
            cur.execute('SELECT MIN(DATE(timestamp)), MAX(DATE(timestamp)) FROM sales')
            min_date, max_date = cur.fetchone()
            if not min_date:
                min_date = max_date = datetime.now().strftime('%Y-%m-%d')
            # Date pickers
            Label(win, text="Start Date:").grid(row=0, column=0)
            entry_start = DateEntry(win, date_pattern='yyyy-mm-dd')
            entry_start.set_date(min_date)
            entry_start.grid(row=0, column=1)
            Label(win, text="End Date:").grid(row=1, column=0)
            entry_end = DateEntry(win, date_pattern='yyyy-mm-dd')
            entry_end.set_date(max_date)
            entry_end.grid(row=1, column=1)
            # Preset range buttons
            def set_this_month():
                today = datetime.now()
                entry_start.set_date(today.replace(day=1))
                entry_end.set_date(today)
            def set_last_7_days():
                today = datetime.now()
                entry_start.set_date(today - timedelta(days=6))
                entry_end.set_date(today)
            Button(win, text="This Month", command=set_this_month).grid(row=0, column=2, padx=5)
            Button(win, text="Last 7 Days", command=set_last_7_days).grid(row=1, column=2, padx=5)
            # Get columns from sales table
            cur.execute('PRAGMA table_info(sales)')
            columns = [row[1] for row in cur.fetchall()]
            conn.close()
            col_vars = {col: IntVar(value=1) for col in columns}
            Label(win, text="Select columns to export:").grid(row=2, column=0, columnspan=3)
            for i, col in enumerate(columns):
                Checkbutton(win, text=col, variable=col_vars[col]).grid(row=3+i, column=0, columnspan=3, sticky='w')
            # Export format dropdown
            Label(win, text="Export Format:").grid(row=3+len(columns), column=0)
            format_var = StringVar(win)
            format_var.set("CSV")
            OptionMenu(win, format_var, "CSV", "Excel").grid(row=3+len(columns), column=1)
            def do_export():
                start = entry_start.get_date().strftime('%Y-%m-%d')
                end = entry_end.get_date().strftime('%Y-%m-%d')
                selected_cols = [col for col, var in col_vars.items() if var.get()]
                if not selected_cols:
                    messagebox.showerror("Error", "Select at least one column.")
                    return
                export_format = format_var.get()
                csv_path = export_all_sales_to_csv(start, end, selected_cols, export_format)
                log_audit_event(f"All sales exported by {current_user['username']} to {csv_path} (filtered, {export_format})")
                messagebox.showinfo("Export All Sales", f"All sales exported to:\n{csv_path}")
                win.destroy()
            Button(win, text="Export", command=do_export).grid(row=4+len(columns), column=0, columnspan=3, pady=10)

        def add_stock():
            import sqlite3
            from tkinter import Toplevel, Label, Entry, Button, messagebox, Listbox, END, StringVar
            win = Toplevel(root)
            win.title("Add/Restock/Edit/Delete Item")
            Label(win, text="Item Name:").grid(row=0, column=0)
            entry_item = Entry(win)
            entry_item.grid(row=0, column=1)
            Label(win, text="Quantity to Add:").grid(row=1, column=0)
            entry_qty = Entry(win)
            entry_qty.grid(row=1, column=1)
            Label(win, text="Cost Price (optional):").grid(row=2, column=0)
            entry_cost = Entry(win)
            entry_cost.grid(row=2, column=1)
            Label(win, text="Selling Price (optional):").grid(row=3, column=0)
            entry_sell = Entry(win)
            entry_sell.grid(row=3, column=1)
            Label(win, text="Category:").grid(row=4, column=0)
            from sales_utils import set_item_category, get_item_category
            category_var = StringVar(win)
            category_var.set("")
            entry_cat = Entry(win, textvariable=category_var)
            entry_cat.grid(row=4, column=1)
            # Listbox for existing items
            Label(win, text="Existing Items:").grid(row=0, column=2, padx=(20,0))
            item_list = Listbox(win, width=25, height=8)
            item_list.grid(row=1, column=2, rowspan=5, padx=(20,0))
            from sales_utils import get_all_stock, delete_item, get_item_prices
            for item, qty, cat in get_all_stock():
                item_list.insert(END, f"{item} ({qty}) [{cat}]")
            def on_select(event):
                sel = item_list.curselection()
                if sel:
                    name = item_list.get(sel[0]).split(' (')[0]
                    entry_item.delete(0, END)
                    entry_item.insert(0, name)
                    # Optionally fill in prices and category
                    prices = get_item_prices(name)
                    if prices:
                        entry_cost.delete(0, END)
                        entry_cost.insert(0, str(prices[0]))
                        entry_sell.delete(0, END)
                        entry_sell.insert(0, str(prices[1]))
                    cat = get_item_category(name)
                    category_var.set(cat)
            item_list.bind('<<ListboxSelect>>', on_select)
            def do_add():
                item = entry_item.get().strip()
                try:
                    qty = int(entry_qty.get())
                    if qty < 0:
                        raise ValueError
                except Exception:
                    messagebox.showerror("Error", "Enter a valid (zero or positive) quantity.")
                    return
                try:
                    cost = float(entry_cost.get()) if entry_cost.get().strip() else None
                except Exception:
                    messagebox.showerror("Error", "Invalid cost price.")
                    return
                try:
                    sell = float(entry_sell.get()) if entry_sell.get().strip() else None
                except Exception:
                    messagebox.showerror("Error", "Invalid selling price.")
                    return
                cat = category_var.get().strip()
                from sales_utils import update_stock, set_item_prices
                update_stock(item, qty)
                if cost is not None or sell is not None:
                    set_item_prices(item, cost, sell)
                if cat:
                    set_item_category(item, cat)
                messagebox.showinfo("Success", f"Updated '{item}' (added {qty}).")
                win.destroy()
            def do_delete():
                item = entry_item.get().strip()
                if not item:
                    messagebox.showerror("Error", "Enter/select an item to delete.")
                    return
                if messagebox.askyesno("Delete Item", f"Are you sure you want to delete '{item}' from inventory?"):
                    delete_item(item)
                    messagebox.showinfo("Deleted", f"'{item}' deleted from inventory.")
                    win.destroy()
            Button(win, text="Save", command=do_add).grid(row=6, column=0, columnspan=2, pady=10)
            Button(win, text="Delete Item", command=do_delete).grid(row=6, column=2, pady=10)
            # Sales history for selected item
            def show_item_sales():
                sel = item_list.curselection()
                if not sel:
                    messagebox.showerror("Error", "Select an item to view sales history.")
                    return
                name = item_list.get(sel[0]).split(' (')[0]
                from sales_utils import get_sales_history_for_item
                sales = get_sales_history_for_item(name)
                from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
                win_hist = Toplevel(win)
                win_hist.title(f"Sales History for {name}")
                txt = Text(win_hist, width=80, height=20)
                txt.pack(side="left", fill="both", expand=True)
                scrollbar = Scrollbar(win_hist, command=txt.yview)
                scrollbar.pack(side=RIGHT, fill=Y)
                txt.config(yscrollcommand=scrollbar.set)
                txt.insert(END, f"{'Date':<20} {'User':<10} {'Qty':<5} {'Price':<10} {'Total':<10}\n")
                txt.insert(END, "-"*60+"\n")
                for row in sales:
                    txt.insert(END, f"{row[0]:<20} {row[1]:<10} {row[2]:<5} {row[3]:<10.2f} {row[4]:<10.2f}\n")
                txt.config(state="disabled")
            Button(win, text="Sales History", command=show_item_sales).grid(row=7, column=0, columnspan=3, pady=5)

        # Advanced stock analytics on dashboard
        def show_stock_analytics():
            from sales_utils import get_all_stock, get_item_prices
            stock_list = get_all_stock()
            total_cost = 0
            total_sell = 0
            
            for item, qty, cat in stock_list:  # Fixed: unpack 3 values
                prices = get_item_prices(item)
                if prices:
                    cost, sell = prices
                    total_cost += (cost or 0) * qty
                    total_sell += (sell or 0) * qty
            
            profit = total_sell - total_cost
            messagebox.showinfo("Stock Analytics", 
                               f"Total Stock Value (Cost): ZMW {total_cost:.2f}\n"
                               f"Total Stock Value (Sell): ZMW {total_sell:.2f}\n"
                               f"Potential Profit: ZMW {profit:.2f}")

        def show_low_stock_alerts():
            from tkinter import messagebox
            from sales_utils import get_all_stock
            low_stock_items = []
            for item, qty, cat in get_all_stock():
                if qty <= 5:  # Threshold for low stock
                    low_stock_items.append(f"{item} ({qty}) [{cat}]")
            if low_stock_items:
                messagebox.showwarning("Low Stock Alert", "Low stock for:\n" + "\n".join(low_stock_items))
            else:
                messagebox.showinfo("Low Stock Alert", "All items are sufficiently stocked.")

        def export_stock_report():
            import csv
            import os
            from datetime import datetime
            from sales_utils import get_all_stock
            
            # Create exports directory if it doesn't exist
            if not os.path.exists('exports'):
                os.makedirs('exports')
            
            stock_list = get_all_stock()
            today = datetime.now().strftime('%Y-%m-%d')
            path = f"exports/stock_report_{today}.csv"
            
            try:
                with open(path, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Item', 'Quantity', 'Category'])
                    for item, qty, cat in stock_list:  # Fixed: unpack 3 values
                        writer.writerow([item, qty, cat])
                messagebox.showinfo("Export Stock Report", f"Stock report exported to:\n{path}")
            except Exception as e:
                messagebox.showerror("Export Error", f"Failed to export stock report:\n{str(e)}")

        # Admin control panel
        admin_frame = tk.LabelFrame(main_frame, text="Admin Control Panel", font=('Arial', 12, 'bold'), 
                                   bg='#f0f0f0', padx=20, pady=20)
        admin_frame.pack(fill='both', expand=True)
        
        # Row 1: Sales and Dashboard
        row1_frame = tk.Frame(admin_frame, bg='#f0f0f0')
        row1_frame.pack(fill='x', pady=(0, 10))
        
        tk.Button(row1_frame, text="View All Sales", command=view_sales, 
                 bg='#3498db', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Button(row1_frame, text="Analytics Dashboard", command=dashboard_prompt, 
                 bg='#9b59b6', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(row1_frame, text="User Management", command=user_management, 
                 bg='#e67e22', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Row 2: Export functions
        row2_frame = tk.Frame(admin_frame, bg='#f0f0f0')
        row2_frame.pack(fill='x', pady=(0, 10))
        
        tk.Button(row2_frame, text="Export All Sales", command=export_all_sales, 
                 bg='#27ae60', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Button(row2_frame, text="Export Stock Report", command=export_stock_report, 
                 bg='#16a085', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        # Row 3: Inventory management
        row3_frame = tk.Frame(admin_frame, bg='#f0f0f0')
        row3_frame.pack(fill='x', pady=(0, 10))
        
        tk.Button(row3_frame, text="Add/Edit Stock", command=add_stock, 
                 bg='#f39c12', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=(0, 5))
        tk.Button(row3_frame, text="Check Low Stock", command=show_low_stock_alerts, 
                 bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=5)
        tk.Button(row3_frame, text="Stock Analytics", command=show_stock_analytics, 
                 bg='#34495e', fg='white', font=('Arial', 10, 'bold'), pady=8).pack(side='left', fill='x', expand=True, padx=(5, 0))

        
        # Row 4: Enhanced reporting
        row4_frame = tk.Frame(admin_frame, bg='#f0f0f0')
        row4_frame.pack(fill='x', pady=(10, 0))
        
        def show_enhanced_reports():
            """Show enhanced reporting dashboard"""
            from enhanced_features import show_enhanced_admin_reports
            show_enhanced_admin_reports(root, current_user)
        
        tk.Button(row4_frame, text="📊 Enhanced Reports Dashboard", command=show_enhanced_reports, 
                 bg='#8e44ad', fg='white', font=('Arial', 12, 'bold'), pady=12).pack(fill='x', padx=50)

    root.mainloop()


def show_popup_receipt(root, current_user, sale_id, tx_id, total, payment_method, amount_received, change, mobile_ref, cart_items=None):
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
        
        if items:
            for item_name, qty, unit_price, subtotal in items:
                item_frame = tk.Frame(items_frame, bg='#ffffff')
                item_frame.pack(fill='x', pady=2)
                
                tk.Label(item_frame, text=f"{item_name} x{qty}", 
                        font=('Arial', 10), bg='#ffffff', anchor='w').pack(side='left')
                tk.Label(item_frame, text=f"ZMW {subtotal:.2f}", 
                        font=('Arial', 10), bg='#ffffff', anchor='e').pack(side='right')
        elif cart_items:
            # Fallback: display items from cart if database retrieval failed
            for item in cart_items:
                item_frame = tk.Frame(items_frame, bg='#ffffff')
                item_frame.pack(fill='x', pady=2)
                
                subtotal = float(item['quantity']) * float(item['unit_price'])
                tk.Label(item_frame, text=f"{item['item']} x{item['quantity']}", 
                        font=('Arial', 10), bg='#ffffff', anchor='w').pack(side='left')
                tk.Label(item_frame, text=f"ZMW {subtotal:.2f}", 
                        font=('Arial', 10), bg='#ffffff', anchor='e').pack(side='right')
        else:
            # Final fallback
            tk.Label(items_frame, text="Transaction completed successfully", 
                    font=('Arial', 10), bg='#ffffff', fg='#27ae60').pack()
    except Exception as e:
        tk.Label(items_frame, text=f"Error loading items: {str(e)}", 
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


def create_cashier_interface(main_frame, root):
    """Redesigned cashier interface with visual item buttons and streamlined workflow"""
    
    # Main container with split design
    main_container = tk.Frame(main_frame, bg='#ecf0f1')
    main_container.pack(fill='both', expand=True)
    
    # Left panel for categories and items (70% width)
    left_panel = tk.Frame(main_container, bg='#ffffff')
    left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
    
    # Right panel for cart (30% width)
    right_panel = tk.Frame(main_container, bg='#ffffff', width=300)
    right_panel.pack(side='right', fill='both', expand=False, padx=(10, 0))
    right_panel.pack_propagate(False)
    
    # Cart data
    cart = []  # list of dicts: {item, quantity, unit_price, notes}
    
    # ---------- LEFT PANEL (ITEMS) ----------
    
    # Category tabs at the top
    category_frame = tk.Frame(left_panel, bg='#34495e', height=50)
    category_frame.pack(fill='x')
    
    # Item grid area
    items_frame = tk.Frame(left_panel, bg='#ffffff', padx=10, pady=10)
    items_frame.pack(fill='both', expand=True)
    
    # Fetch all available categories
    try:
        from sales_utils import get_categories
        all_categories = get_categories()
        if not all_categories:
            all_categories = ["Drinks", "Food", "Other"]
    except Exception as e:
        print(f"Error loading categories: {e}")
        all_categories = ["Drinks", "Food", "Other"]
    
    # Add "All Items" as the first category
    all_categories.insert(0, "All Items")
    
    # Category selection
    selected_category = tk.StringVar()
    selected_category.set("All Items")
    
    # Create category buttons
    category_buttons = []
    for i, category in enumerate(all_categories):
        btn = tk.Button(category_frame, text=category, bg='#34495e', fg='#ecf0f1',
                       font=('Arial', 11, 'bold'), bd=0, padx=15, relief='flat',
                       activebackground='#2c3e50', activeforeground='#ffffff')
        btn.pack(side='left')
        category_buttons.append(btn)
    
    # Function to populate items based on category
    def populate_items(category):
        # Clear existing items
        for widget in items_frame.winfo_children():
            widget.destroy()
        
        # Get items from inventory
        try:
            if category == "All Items":
                items = get_all_stock()
            else:
                # Filter items by category
                items = [item for item in get_all_stock() if item[2] == category]
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load inventory: {str(e)}")
            return
        
        # Create item grid with 4 items per row
        cols = 4
        for i, (item, qty, cat) in enumerate(items):
            if qty <= 0:  # Skip out-of-stock items
                continue
                
            # Get price
            try:
                from sales_utils import get_item_prices
                prices = get_item_prices(item)
                if prices:
                    _, sell_price = prices
                    price_display = f"{sell_price:.2f}" if sell_price else "N/A"
                else:
                    price_display = "N/A"
                    sell_price = 0
            except Exception as e:
                price_display = "N/A"
                sell_price = 0
                
            # Calculate position in grid
            row, col = divmod(i, cols)
            
            # Item frame
            item_frame = tk.Frame(items_frame, bg='#f0f3f4', width=150, height=120, 
                               relief='raised', bd=1)
            item_frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
            item_frame.grid_propagate(False)  # Maintain fixed size
            
            # Item name with wrapping
            name_label = tk.Label(item_frame, text=item, bg='#f0f3f4', fg='#2c3e50', 
                               font=('Arial', 11, 'bold'), wraplength=140)
            name_label.pack(pady=(15, 5))
            
            # Price and stock
            price_label = tk.Label(item_frame, text=f"ZMW {price_display}", bg='#f0f3f4',
                               fg='#27ae60', font=('Arial', 10))
            price_label.pack()
            
            stock_label = tk.Label(item_frame, text=f"Stock: {qty}", bg='#f0f3f4',
                               fg='#7f8c8d', font=('Arial', 9))
            stock_label.pack()
            
            # Make the entire frame clickable
            def make_click_handler(item_name=item, unit_price=sell_price):
                return lambda e: show_quantity_dialog(item_name, unit_price)
            
            item_frame.bind("<Button-1>", make_click_handler())
            name_label.bind("<Button-1>", make_click_handler())
            price_label.bind("<Button-1>", make_click_handler())
            stock_label.bind("<Button-1>", make_click_handler())
            
        # Configure grid to expand
        for i in range(cols):
            items_frame.grid_columnconfigure(i, weight=1)
    
    # Set up category button clicks
    def make_category_handler(category, button):
        def handler():
            selected_category.set(category)
            for b in category_buttons:
                b.configure(bg='#34495e', fg='#ecf0f1')
            button.configure(bg='#ecf0f1', fg='#34495e')
            populate_items(category)
        return handler
    
    for i, cat in enumerate(all_categories):
        category_buttons[i].config(command=make_category_handler(cat, category_buttons[i]))
    
    # Search box at the bottom of left panel
    search_frame = tk.Frame(left_panel, bg='#ffffff', pady=10)
    search_frame.pack(fill='x')
    
    search_var = tk.StringVar()
    search_entry = tk.Entry(search_frame, textvariable=search_var, font=('Arial', 12),
                         width=25)
    search_entry.pack(side='left', padx=(10, 5))
    
    search_btn = tk.Button(search_frame, text="🔍 Search", font=('Arial', 10, 'bold'),
                        bg='#3498db', fg='white', command=lambda: search_items())
    search_btn.pack(side='left')
    
    def search_items(*args):
        search_text = search_var.get().strip().lower()
        if search_text:
            # Clear existing items
            for widget in items_frame.winfo_children():
                widget.destroy()
            
            # Search in inventory
            try:
                all_items = get_all_stock()
                matching_items = [(item, qty, cat) for item, qty, cat in all_items 
                                if search_text in item.lower()]
                
                # Display matching items
                cols = 4
                for i, (item, qty, cat) in enumerate(matching_items):
                    if qty <= 0:  # Skip out-of-stock items
                        continue
                        
                    # Get price
                    try:
                        from sales_utils import get_item_prices
                        prices = get_item_prices(item)
                        if prices:
                            _, sell_price = prices
                            price_display = f"{sell_price:.2f}" if sell_price else "N/A"
                        else:
                            price_display = "N/A"
                            sell_price = 0
                    except:
                        price_display = "N/A"
                        sell_price = 0
                        
                    # Calculate position in grid
                    row, col = divmod(i, cols)
                    
                    # Item frame
                    item_frame = tk.Frame(items_frame, bg='#f0f3f4', width=150, height=120, 
                                      relief='raised', bd=1)
                    item_frame.grid(row=row, column=col, padx=8, pady=8, sticky='nsew')
                    item_frame.grid_propagate(False)  # Maintain fixed size
                    
                    # Item name with wrapping
                    name_label = tk.Label(item_frame, text=item, bg='#f0f3f4', fg='#2c3e50', 
                                      font=('Arial', 11, 'bold'), wraplength=140)
                    name_label.pack(pady=(15, 5))
                    
                    # Price and stock
                    price_label = tk.Label(item_frame, text=f"ZMW {price_display}", bg='#f0f3f4',
                                      fg='#27ae60', font=('Arial', 10))
                    price_label.pack()
                    
                    stock_label = tk.Label(item_frame, text=f"Stock: {qty}", bg='#f0f3f4',
                                      fg='#7f8c8d', font=('Arial', 9))
                    stock_label.pack()
                    
                    # Make the entire frame clickable
                    def make_click_handler(item_name=item, unit_price=sell_price):
                        return lambda e: show_quantity_dialog(item_name, unit_price)
                    
                    item_frame.bind("<Button-1>", make_click_handler())
                    name_label.bind("<Button-1>", make_click_handler())
                    price_label.bind("<Button-1>", make_click_handler())
                    stock_label.bind("<Button-1>", make_click_handler())
                
                # Configure grid to expand
                for i in range(cols):
                    items_frame.grid_columnconfigure(i, weight=1)
            except Exception as e:
                messagebox.showerror("Search Error", f"Error searching items: {str(e)}")
    
    search_var.trace("w", search_items)
    search_entry.bind("<Return>", lambda e: search_items())
    
    # ---------- RIGHT PANEL (CART) ----------
    
    # Cart section on the right
    cart_label = tk.Label(right_panel, text="Current Order", font=('Arial', 14, 'bold'), 
                        bg='#ffffff', fg='#2c3e50')
    cart_label.pack(pady=(10, 5), anchor='w')
    
    # Cart treeview
    cart_columns = ("Item", "Qty", "Price", "Total")
    cart_tree = ttk.Treeview(right_panel, columns=cart_columns, show='headings', height=12)
    cart_tree.pack(fill='both', expand=True, padx=5, pady=5)
    
    for c in cart_columns:
        cart_tree.heading(c, text=c)
        if c == "Item":
            cart_tree.column(c, width=120, stretch=True)
        elif c == "Qty":
            cart_tree.column(c, width=40, anchor='center', stretch=False)
        elif c == "Price":
            cart_tree.column(c, width=60, anchor='e', stretch=False)
        else:
            cart_tree.column(c, width=60, anchor='e', stretch=False)
    
    # Add scrollbar
    cart_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=cart_tree.yview)
    cart_scroll.pack(side='right', fill='y')
    cart_tree.configure(yscrollcommand=cart_scroll.set)
    
    # Cart functions
    def refresh_cart_tree():
        """Update the cart display and buttons"""
        for i in cart_tree.get_children():
            cart_tree.delete(i)
            
        for it in cart:
            subtotal = float(it['quantity']) * float(it['unit_price'])
            cart_tree.insert('', 'end', values=(it['item'], it['quantity'], 
                                              f"{float(it['unit_price']):.2f}", 
                                              f"{subtotal:.2f}"))
        
        # Update total
        cart_total = sum(float(it['quantity']) * float(it['unit_price']) for it in cart)
        total_label.config(text=f"Total: ZMW {cart_total:.2f}")
        
        # Enable/disable buttons
        if cart:
            payment_btn.config(state='normal')
            void_btn.config(state='normal')
            clear_btn.config(state='normal')
            remove_btn.config(state='normal')
        else:
            payment_btn.config(state='disabled')
            void_btn.config(state='disabled')
            clear_btn.config(state='disabled')
            remove_btn.config(state='disabled')
    
    def add_to_cart(item_name, quantity, unit_price, notes=""):
        """Add item to cart, merging with existing items if needed"""
        # Check if item exists
        for it in cart:
            if it['item'] == item_name and abs(float(it['unit_price']) - float(unit_price)) < 0.01:
                it['quantity'] += quantity
                if notes and not it.get('notes'):
                    it['notes'] = notes
                refresh_cart_tree()
                return
        
        # Add new item
        cart.append({
            'item': item_name,
            'quantity': quantity,
            'unit_price': unit_price,
            'notes': notes
        })
        refresh_cart_tree()
    
    def remove_from_cart():
        """Remove selected item from cart"""
        sel = cart_tree.selection()
        if not sel:
            messagebox.showinfo("Remove Item", "Please select an item to remove")
            return
            
        idx = cart_tree.index(sel[0])
        cart.pop(idx)
        refresh_cart_tree()
    
    def clear_cart():
        """Clear all items from cart"""
        if not cart:
            return
            
        if messagebox.askyesno("Clear Order", "Are you sure you want to clear the entire order?"):
            cart.clear()
            refresh_cart_tree()
    
    # Total amount
    total_label = tk.Label(right_panel, text="Total: ZMW 0.00", font=('Arial', 14, 'bold'),
                         bg='#ffffff', fg='#27ae60')
    total_label.pack(pady=(5, 10))
    
    # Action buttons
    action_frame = tk.Frame(right_panel, bg='#ffffff')
    action_frame.pack(fill='x', pady=(0, 10))
    
    # Button to remove selected item
    remove_btn = tk.Button(action_frame, text="❌ Remove", command=remove_from_cart,
                         bg='#e74c3c', fg='white', font=('Arial', 10, 'bold'),
                         padx=10, pady=5, state='disabled')
    remove_btn.pack(side='left', padx=5)
    
    # Button to clear cart
    clear_btn = tk.Button(action_frame, text="🗑️ Clear All", command=clear_cart,
                        bg='#95a5a6', fg='white', font=('Arial', 10, 'bold'),
                        padx=10, pady=5, state='disabled')
    clear_btn.pack(side='left', padx=5)
    
    # Button to process payment
    payment_btn = tk.Button(right_panel, text="💰 PROCESS PAYMENT", command=lambda: process_payment(),
                         bg='#27ae60', fg='white', font=('Arial', 12, 'bold'),
                         padx=20, pady=10, state='disabled')
    payment_btn.pack(fill='x', padx=5, pady=(5, 10))
    
    # Button to void current order
    void_btn = tk.Button(right_panel, text="❌ VOID ORDER", command=lambda: void_order(),
                       bg='#c0392b', fg='white', font=('Arial', 12, 'bold'),
                       padx=20, pady=10, state='disabled')
    void_btn.pack(fill='x', padx=5, pady=(0, 10))
    
    # Hover effects for buttons
    def add_hover_effect(button, normal_color, hover_color):
        """Add hover effect to a button"""
        def on_enter(e):
            button.config(bg=hover_color)
        def on_leave(e):
            button.config(bg=normal_color)
        button.bind("<Enter>", on_enter)
        button.bind("<Leave>", on_leave)
    
    add_hover_effect(remove_btn, '#e74c3c', '#c0392b')
    add_hover_effect(clear_btn, '#95a5a6', '#7f8c8d')
    add_hover_effect(payment_btn, '#27ae60', '#2ecc71')
    add_hover_effect(void_btn, '#c0392b', '#e74c3c')
    add_hover_effect(search_btn, '#3498db', '#2980b9')
    
    # ---------- DIALOGS ----------
    
    # Quantity dialog
    def show_quantity_dialog(item_name, unit_price):
        """Show dialog to select quantity and add to cart"""
        dialog = tk.Toplevel(root)
        dialog.title(f"Add {item_name}")
        dialog.geometry("300x250")
        dialog.configure(bg='#ffffff')
        dialog.transient(root)
        dialog.grab_set()
        
        # Center the dialog
        dialog.geometry("+%d+%d" % (root.winfo_rootx() + 100, root.winfo_rooty() + 100))
        
        # Item info
        tk.Label(dialog, text=item_name, font=('Arial', 14, 'bold'), 
                bg='#ffffff', fg='#2c3e50').pack(pady=(15, 10))
        
        tk.Label(dialog, text=f"ZMW {unit_price:.2f}", font=('Arial', 12),
                bg='#ffffff', fg='#27ae60').pack(pady=(0, 15))
        
        # Quantity frame
        qty_frame = tk.Frame(dialog, bg='#ffffff')
        qty_frame.pack(pady=10)
        
        qty_var = tk.StringVar(value="1")
        
        def validate_qty(P):
            """Validate quantity - only allow positive integers"""
            if P == "":
                return True
            try:
                val = int(P)
                return val > 0
            except ValueError:
                return False
        
        vcmd = (dialog.register(validate_qty), '%P')
        
        # Decrease quantity button
        dec_btn = tk.Button(qty_frame, text="-", font=('Arial', 16, 'bold'), 
                          bg='#e74c3c', fg='white', width=2, command=lambda: update_qty(-1))
        dec_btn.pack(side='left', padx=(0, 5))
        
        # Quantity entry
        qty_entry = tk.Entry(qty_frame, textvariable=qty_var, font=('Arial', 14), 
                           width=4, justify='center', validate='key', validatecommand=vcmd)
        qty_entry.pack(side='left')
        
        # Increase quantity button
        inc_btn = tk.Button(qty_frame, text="+", font=('Arial', 16, 'bold'), 
                          bg='#27ae60', fg='white', width=2, command=lambda: update_qty(1))
        inc_btn.pack(side='left', padx=(5, 0))
        
        def update_qty(delta):
            """Update quantity by delta"""
            try:
                current = int(qty_var.get() or "1")
                new_val = current + delta
                if new_val > 0:
                    qty_var.set(str(new_val))
            except ValueError:
                qty_var.set("1")
        
        # Notes field
        tk.Label(dialog, text="Notes (optional):", bg='#ffffff', anchor='w').pack(anchor='w', padx=20)
        notes_entry = tk.Entry(dialog, font=('Arial', 11), width=30)
        notes_entry.pack(padx=20, pady=(0, 10), fill='x')
        
        # Buttons
        btn_frame = tk.Frame(dialog, bg='#ffffff')
        btn_frame.pack(pady=15)
        
        cancel_btn = tk.Button(btn_frame, text="Cancel", command=dialog.destroy,
                              bg='#95a5a6', fg='white', font=('Arial', 11))
        cancel_btn.pack(side='left', padx=10)
        
        def add_and_close():
            """Add item to cart and close dialog"""
            try:
                quantity = int(qty_var.get() or "1")
                notes = notes_entry.get().strip()
                add_to_cart(item_name, quantity, unit_price, notes)
                dialog.destroy()
            except ValueError:
                messagebox.showerror("Error", "Please enter a valid quantity")
        
        add_btn = tk.Button(btn_frame, text="Add to Order", command=add_and_close,
                         bg='#3498db', fg='white', font=('Arial', 11, 'bold'))
        add_btn.pack(side='left', padx=10)
        
        # Add hover effects
        add_hover_effect(dec_btn, '#e74c3c', '#c0392b')
        add_hover_effect(inc_btn, '#27ae60', '#2ecc71')
        add_hover_effect(add_btn, '#3498db', '#2980b9')
        add_hover_effect(cancel_btn, '#95a5a6', '#7f8c8d')
        
        # Select all text when focusing on qty entry
        qty_entry.bind("<FocusIn>", lambda e: qty_entry.selection_range(0, tk.END))
        qty_entry.focus_set()
        
        # Bind Enter key to add
        qty_entry.bind("<Return>", lambda e: add_and_close())
        notes_entry.bind("<Return>", lambda e: add_and_close())
    
    # Process payment
    def process_payment():
        """Process payment for items in cart"""
        if not cart:
            return
        
        try:
            total_amount = sum(float(it['quantity']) * float(it['unit_price']) for it in cart)
        except:
            total_amount = 0.0
        
        # Payment dialog
        payment_dialog = tk.Toplevel(root)
        payment_dialog.title("Process Payment")
        payment_dialog.geometry("400x350")
        payment_dialog.configure(bg='#f8f9fa')
        payment_dialog.transient(root)
        payment_dialog.grab_set()
        
        # Center the dialog
        payment_dialog.geometry("+%d+%d" % (root.winfo_rootx() + 50, root.winfo_rooty() + 50))
        
        # Header
        tk.Label(payment_dialog, text="💳 Process Payment", font=('Arial', 16, 'bold'), 
                bg='#f8f9fa', fg='#2c3e50').pack(pady=15)
        
        # Total display
        tk.Label(payment_dialog, text=f"Total Amount: ZMW {total_amount:.2f}", 
                font=('Arial', 14, 'bold'), bg='#f8f9fa', fg='#27ae60').pack(pady=10)
        
        # Payment type selection
        payment_type = tk.StringVar(value="Cash")
        
        payment_frame = tk.LabelFrame(payment_dialog, text="Payment Method", 
                                    font=('Arial', 12, 'bold'), bg='#f8f9fa', padx=20, pady=15)
        payment_frame.pack(fill='x', padx=20, pady=10)
        
        tk.Radiobutton(payment_frame, text="💵 Cash", variable=payment_type, value="Cash",
                      bg='#f8f9fa', font=('Arial', 11)).pack(anchor='w', pady=2)
        tk.Radiobutton(payment_frame, text="📱 Mobile Money", variable=payment_type, value="Mobile Money",
                      bg='#f8f9fa', font=('Arial', 11)).pack(anchor='w', pady=2)
        tk.Radiobutton(payment_frame, text="💳 Card/Other", variable=payment_type, value="Card",
                      bg='#f8f9fa', font=('Arial', 11)).pack(anchor='w', pady=2)
        
        # Dynamic input fields
        input_frame = tk.Frame(payment_dialog, bg='#f8f9fa')
        input_frame.pack(fill='x', padx=20, pady=10)
        
        # Variables for inputs
        cash_received = tk.StringVar()
        mobile_ref = tk.StringVar()
        
        # Input widgets (initially hidden)
        cash_label = tk.Label(input_frame, text="Cash Received (ZMW):", bg='#f8f9fa', font=('Arial', 11))
        cash_entry = tk.Entry(input_frame, textvariable=cash_received, font=('Arial', 11), width=20)
        
        mobile_label = tk.Label(input_frame, text="Transaction Reference:", bg='#f8f9fa', font=('Arial', 11))
        mobile_entry = tk.Entry(input_frame, textvariable=mobile_ref, font=('Arial', 11), width=25)
        
        change_label = tk.Label(input_frame, text="", bg='#f8f9fa', font=('Arial', 12, 'bold'), fg='#e74c3c')
        
        def update_payment_fields(*args):
            # Hide all fields first
            for widget in [cash_label, cash_entry, mobile_label, mobile_entry, change_label]:
                widget.pack_forget()
            
            if payment_type.get() == "Cash":
                cash_label.pack(anchor='w', pady=(5,2))
                cash_entry.pack(anchor='w', pady=(0,5))
                change_label.pack(anchor='w', pady=5)
                cash_entry.focus_set()
            elif payment_type.get() == "Mobile Money":
                mobile_label.pack(anchor='w', pady=(5,2))
                mobile_entry.pack(anchor='w', pady=(0,5))
                mobile_entry.focus_set()
            validate_input()
        
        def calculate_change(*args):
            if payment_type.get() == "Cash":
                try:
                    received = float(cash_received.get() or '0')
                    change = received - total_amount
                    if change >= 0:
                        change_label.config(text=f"Change: ZMW {change:.2f}", fg='#27ae60')
                    else:
                        change_label.config(text=f"Insufficient: ZMW {abs(change):.2f} short", fg='#e74c3c')
                except ValueError:
                    change_label.config(text="", fg='#e74c3c')
            validate_input()
        
        # Buttons
        button_frame = tk.Frame(payment_dialog, bg='#f8f9fa')
        button_frame.pack(pady=20)
        
        complete_btn = tk.Button(button_frame, text="💳 Complete Payment", command=lambda: None,
                              bg='#27ae60', fg='white', font=('Arial', 12, 'bold'), padx=20, pady=8, state='disabled')
        complete_btn.pack(side='left', padx=5)
        
        cancel_btn = tk.Button(button_frame, text="Cancel", command=payment_dialog.destroy,
                             bg='#6c757d', fg='white', font=('Arial', 12, 'bold'), padx=20, pady=8)
        cancel_btn.pack(side='left', padx=5)
        
        def validate_input(*args):
            method = payment_type.get()
            if method == "Cash":
                try:
                    received = float(cash_received.get() or '0')
                    complete_btn.config(state='normal' if received >= total_amount else 'disabled')
                except ValueError:
                    complete_btn.config(state='disabled')
            elif method == "Mobile Money":
                complete_btn.config(state='normal' if mobile_ref.get().strip() else 'disabled')
            else:
                complete_btn.config(state='normal')
        
        def finalize_payment():
            payment_method = payment_type.get()
            
            # Validation based on payment type
            if payment_method == "Cash":
                try:
                    received = float(cash_received.get() or '0')
                    if received < total_amount:
                        messagebox.showerror("Error", "Insufficient cash received")
                        return
                    change = received - total_amount
                except ValueError:
                    messagebox.showerror("Error", "Please enter a valid cash amount")
                    return
            elif payment_method == "Mobile Money":
                if not mobile_ref.get().strip():
                    messagebox.showerror("Error", "Please enter transaction reference")
                    return
                received = total_amount
                change = 0
            else:
                received = total_amount
                change = 0
            
            # Process the sale
            try:
                from sales_utils import create_sale_with_items, log_audit_event
                from datetime import datetime
                
                # Prepare cart items for the cart-based system
                cart_items = []
                for item in cart:
                    cart_items.append({
                        'item': item['item'],
                        'quantity': item['quantity'],
                        'unit_price': item['unit_price']
                    })
                
                # Create the sale using the cart-based system
                sale_id, tx_id, total = create_sale_with_items(current_user['username'], cart_items)
                
                # Log the transaction
                log_audit_event(f"Payment processed by {current_user['username']} TX={tx_id} Method={payment_method} Total={total}")
                
                # Show receipt
                payment_dialog.destroy()
                show_popup_receipt(
                    root, current_user, sale_id, tx_id, total, payment_method, 
                    received, change,
                    mobile_ref.get() if payment_method == "Mobile Money" else None,
                    cart_items=cart  # Pass cart items for fallback display
                )
                
                # Clear cart and refresh
                cart.clear()
                refresh_cart_tree()
                
            except Exception as e:
                messagebox.showerror("Payment Error", f"Error processing payment: {str(e)}")
                print(f"Payment error: {e}")
        
        # Update the complete button command
        complete_btn.config(command=finalize_payment)
        
        # Set up trace callbacks
        payment_type.trace('w', update_payment_fields)
        cash_received.trace('w', calculate_change)
        mobile_ref.trace('w', validate_input)
        
        # Initialize fields
        update_payment_fields()
        
        # Add hover effects
        add_hover_effect(complete_btn, '#27ae60', '#2ecc71')
        add_hover_effect(cancel_btn, '#6c757d', '#5d6d7e')
    
    # Void order
    def void_order():
        """Void the current order"""
        if not cart:
            return
        
        if messagebox.askyesno("Void Order", "Are you sure you want to void this entire order?"):
            from sales_utils import log_audit_event
            
            # Log the void action
            cart_items = ", ".join([f"{it['item']} x{it['quantity']}" for it in cart])
            log_audit_event(f"Order voided by {current_user['username']} - Items: {cart_items}")
            
            # Clear cart
            cart.clear()
            refresh_cart_tree()
            messagebox.showinfo("Order Voided", "The order has been voided and logged.")
    
    # ---------- KEYBOARD SHORTCUTS ----------
    
    def handle_key(event):
        """Handle keyboard shortcuts"""
        # + key for search
        if event.char == "+":
            search_entry.focus_set()
        # p key for payment
        elif event.char == "p" and cart:
            process_payment()
        # v key for void
        elif event.char == "v" and cart:
            void_order()
        # Delete key for removing selected item
        elif event.keysym == "Delete" and cart:
            remove_from_cart()
    
    root.bind("<Key>", handle_key)
    
    # Load initial category
    category_buttons[0].configure(bg='#ecf0f1', fg='#34495e')
    populate_items("All Items")

# --- App Start ---
if not os.path.exists('bar_sales.db'):
    from tkinter import Tk
    warn_root = Tk()
    warn_root.withdraw()
    messagebox.showwarning('Database Missing', 'Warning: bar_sales.db was missing! A new database will be created.')
    log_audit_event('WARNING: bar_sales.db was missing on app start. New database created.')
    warn_root.destroy()

init_db()
backup_today_sales()

import atexit
def on_app_close():
    backup_today_sales()
    log_audit_event('App closed and daily backup created.')
atexit.register(on_app_close)

login_window = tk.Tk()
login_window.title("Login - Bar Sales App")

# Login form
login_frame = tk.Frame(login_window)
login_frame.pack(padx=20, pady=20)

login_frame.grid_columnconfigure(1, weight=1)

login_frame_label = tk.Label(login_frame, text="Please login to continue", font=("Arial", 12, "bold"))
login_frame_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

label_username = tk.Label(login_frame, text="Username:")
label_username.grid(row=1, column=0, sticky="e")
entry_username = tk.Entry(login_frame)
entry_username.grid(row=1, column=1)

label_password = tk.Label(login_frame, text="Password:")
label_password.grid(row=2, column=0, sticky="e")
entry_password = tk.Entry(login_frame, show="*")
entry_password.grid(row=2, column=1)

login_btn = tk.Button(login_frame, text="Login", command=login)
login_btn.grid(row=3, column=0, columnspan=2, pady=10)

login_window.mainloop()
