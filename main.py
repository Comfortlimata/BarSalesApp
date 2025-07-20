# main.py
import tkinter as tk
from tkinter import messagebox
from sales_utils import init_db, record_sale, generate_pdf_receipt, backup_today_sales, log_audit_event, export_all_sales_to_csv, get_all_stock
import os

# Hardcoded users and roles
USERS = {
    'admin': {'password': 'admin123', 'role': 'admin'},
    'cashier': {'password': 'cashier123', 'role': 'cashier'}
}

current_user = {'username': '', 'role': ''}

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
    root.title("Bar Sales – Comfort_2022")

    # --- Session Timeout ---
    import threading
    SESSION_TIMEOUT_MS = 10 * 60 * 1000  # 10 minutes in milliseconds
    timeout_timer = [None]

    def logout_due_to_timeout():
        messagebox.showwarning("Session Timeout", "You have been logged out due to inactivity.")
        root.destroy()
        # Show login window again
        global login_window
        login_window = tk.Tk()
        login_window.title("Login - Bar Sales App")
        # (recreate login form below)
        login_frame = tk.Frame(login_window)
        login_frame.pack(padx=20, pady=20)
        login_frame.grid_columnconfigure(1, weight=1)
        login_frame_label = tk.Label(login_frame, text="Please login to continue", font=("Arial", 12, "bold"))
        login_frame_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        label_username = tk.Label(login_frame, text="Username:")
        label_username.grid(row=1, column=0, sticky="e")
        global entry_username, entry_password
        entry_username = tk.Entry(login_frame)
        entry_username.grid(row=1, column=1)
        label_password = tk.Label(login_frame, text="Password:")
        label_password.grid(row=2, column=0, sticky="e")
        entry_password = tk.Entry(login_frame, show="*")
        entry_password.grid(row=2, column=1)
        login_btn = tk.Button(login_frame, text="Login", command=login)
        login_btn.grid(row=3, column=0, columnspan=2, pady=10)
        login_window.mainloop()

    def reset_timeout(event=None):
        if timeout_timer[0]:
            root.after_cancel(timeout_timer[0])
        timeout_timer[0] = root.after(SESSION_TIMEOUT_MS, logout_due_to_timeout)

    # Bind all user activity to reset the timer
    root.bind_all('<Any-KeyPress>', reset_timeout)
    root.bind_all('<Any-Button>', reset_timeout)
    reset_timeout()
    # --- End Session Timeout ---

    tk.Label(root, text=f"Logged in as: {current_user['username']} ({current_user['role']})").grid(row=0, column=0, columnspan=2)

    if current_user['role'] == 'cashier':
        # Sales entry form for cashier only
        tk.Label(root, text="Item:").grid(row=1, column=0)
        entry_item = tk.Entry(root)
        entry_item.grid(row=1, column=1)

        tk.Label(root, text="Quantity:").grid(row=2, column=0)
        entry_quantity = tk.Entry(root)
        entry_quantity.grid(row=2, column=1)

        tk.Label(root, text="Price per Unit:").grid(row=3, column=0)
        entry_price = tk.Entry(root)
        entry_price.grid(row=3, column=1)

        def submit_sale():
            import uuid
            from datetime import datetime
            item = entry_item.get()
            try:
                quantity = int(entry_quantity.get())
                price = float(entry_price.get())
                total = record_sale(current_user['username'], item, quantity, price)
                # Generate unique receipt ID
                receipt_id = str(uuid.uuid4())[:8]
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                pdf_path = generate_pdf_receipt(receipt_id, current_user['username'], item, quantity, price, total, timestamp)
                log_audit_event(f"Sale recorded by {current_user['username']}: {item} x{quantity} at {price} (Total: {total})")
                messagebox.showinfo("Success", f"Sale Recorded!\nTotal: ZMW {total}\nReceipt saved: {pdf_path}")
                entry_item.delete(0, tk.END)
                entry_quantity.delete(0, tk.END)
                entry_price.delete(0, tk.END)
                update_summary()
            except ValueError:
                messagebox.showerror("Error", "Enter valid numeric values for quantity and price.")

        submit_btn = tk.Button(root, text="Record Sale", command=submit_sale)
        submit_btn.grid(row=4, column=0, columnspan=2)

        # My Sales button
        def view_my_sales():
            import sqlite3
            from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
            win = Toplevel(root)
            win.title("My Sales Log")
            txt = Text(win, width=80, height=20)
            txt.pack(side="left", fill="both", expand=True)
            scrollbar = Scrollbar(win, command=txt.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            txt.config(yscrollcommand=scrollbar.set)
            conn = sqlite3.connect("bar_sales.db")
            cur = conn.cursor()
            cur.execute("SELECT item, quantity, price_per_unit, total, timestamp FROM sales WHERE username=? ORDER BY timestamp DESC", (current_user['username'],))
            rows = cur.fetchall()
            conn.close()
            txt.insert(END, f"{'Item':<15} {'Qty':<5} {'Unit Price':<10} {'Total':<10} {'Time':<20}\n")
            txt.insert(END, "-"*65+"\n")
            for row in rows:
                txt.insert(END, f"{row[0]:<15} {row[1]:<5} {row[2]:<10.2f} {row[3]:<10.2f} {row[4]:<20}\n")
            txt.config(state="disabled")

        my_sales_btn = tk.Button(root, text="My Sales", command=view_my_sales)
        my_sales_btn.grid(row=5, column=0, columnspan=2, pady=5)

        # Today's Sales button
        def view_todays_sales():
            import sqlite3
            from tkinter import Toplevel, Text, Scrollbar, RIGHT, Y, END
            from datetime import datetime
            win = Toplevel(root)
            win.title("Today's Sales Log")
            txt = Text(win, width=100, height=20)
            txt.pack(side="left", fill="both", expand=True)
            scrollbar = Scrollbar(win, command=txt.yview)
            scrollbar.pack(side=RIGHT, fill=Y)
            txt.config(yscrollcommand=scrollbar.set)
            today = datetime.now().strftime("%Y-%m-%d")
            conn = sqlite3.connect("bar_sales.db")
            cur = conn.cursor()
            cur.execute("SELECT username, item, quantity, price_per_unit, total, timestamp FROM sales WHERE DATE(timestamp)=? ORDER BY timestamp DESC", (today,))
            rows = cur.fetchall()
            conn.close()
            txt.insert(END, f"{'User':<10} {'Item':<15} {'Qty':<5} {'Unit Price':<10} {'Total':<10} {'Time':<20}\n")
            txt.insert(END, "-"*90+"\n")
            for row in rows:
                txt.insert(END, f"{row[0]:<10} {row[1]:<15} {row[2]:<5} {row[3]:<10.2f} {row[4]:<10.2f} {row[5]:<20}\n")
            txt.config(state="disabled")

        todays_sales_btn = tk.Button(root, text="Today's Sales", command=view_todays_sales)
        todays_sales_btn.grid(row=6, column=0, columnspan=2, pady=5)

        # Summary stats
        summary_label = tk.Label(root, text="", fg="blue", justify="left")
        summary_label.grid(row=7, column=0, columnspan=2, sticky="w")

        def update_summary():
            import sqlite3
            from datetime import datetime
            today = datetime.now().strftime("%Y-%m-%d")
            conn = sqlite3.connect("bar_sales.db")
            cur = conn.cursor()
            cur.execute("SELECT SUM(total) FROM sales WHERE username=? AND DATE(timestamp)=?", (current_user['username'], today))
            total_sales = cur.fetchone()[0] or 0
            cur.execute("SELECT item, SUM(quantity) as qty FROM sales WHERE username=? AND DATE(timestamp)=? GROUP BY item ORDER BY qty DESC LIMIT 1", (current_user['username'], today))
            row = cur.fetchone()
            most_sold = row[0] if row else "-"
            conn.close()
            summary_label.config(text=f"Today's Total Sales: ZMW {total_sales:.2f}\nMost Sold Item: {most_sold}")

        update_summary()

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
            cur.execute("SELECT username, item, quantity, price_per_unit, total, timestamp FROM sales ORDER BY timestamp DESC")
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
                cur.execute("SELECT DATE(timestamp), SUM(total) FROM sales GROUP BY DATE(timestamp) ORDER BY DATE(timestamp) DESC LIMIT 7")
                rows = cur.fetchall()[::-1]
                dates = [r[0] for r in rows]
                totals = [r[1] for r in rows]
                # Top items
                cur.execute("SELECT item, SUM(quantity) as qty FROM sales GROUP BY item ORDER BY qty DESC LIMIT 5")
                item_rows = cur.fetchall()
                items = [r[0] for r in item_rows]
                qtys = [r[1] for r in item_rows]
                # Sales by user
                cur.execute("SELECT username, SUM(total) FROM sales GROUP BY username ORDER BY SUM(total) DESC")
                user_rows = cur.fetchall()
                users = [r[0] for r in user_rows]
                user_totals = [r[1] for r in user_rows]
                # Sales by hour
                cur.execute("SELECT strftime('%H', timestamp) as hour, SUM(total) FROM sales GROUP BY hour ORDER BY hour")
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
            from tkinter import Toplevel, Label, Entry, Button, messagebox, Listbox, END, StringVar, OptionMenu
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
            for item, qty in stock_list:
                prices = get_item_prices(item)
                if prices:
                    cost, sell = prices
                    total_cost += (cost or 0) * qty
                    total_sell += (sell or 0) * qty
            profit = total_sell - total_cost
            messagebox.showinfo("Stock Analytics", f"Total Stock Value (Cost): ZMW {total_cost:.2f}\nTotal Stock Value (Sell): ZMW {total_sell:.2f}\nPotential Profit: ZMW {profit:.2f}")

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
            from datetime import datetime
            from sales_utils import get_all_stock
            stock_list = get_all_stock()
            today = datetime.now().strftime('%Y-%m-%d')
            path = f"exports/stock_report_{today}.csv"
            with open(path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Item', 'Quantity', 'Category'])
                for item, qty, cat in stock_list:
                    writer.writerow([item, qty, cat])
            messagebox.showinfo("Export Stock Report", f"Stock report exported to:\n{path}")

        tk.Button(root, text="View Sales", command=view_sales).grid(row=1, column=0, columnspan=2, pady=5)
        tk.Button(root, text="Dashboard", command=dashboard_prompt).grid(row=2, column=0)
        tk.Button(root, text="Export", command=lambda: (log_audit_event(f"Export triggered by {current_user['username']}"), messagebox.showinfo("Export", "Export feature coming soon."))).grid(row=2, column=1)
        tk.Button(root, text="Export All Sales", command=export_all_sales).grid(row=4, column=0, columnspan=2, pady=5)
        tk.Button(root, text="User Management", command=user_management).grid(row=3, column=0, columnspan=2, pady=5)
        tk.Button(root, text="Add/Edit Stock", command=add_stock).grid(row=5, column=0, pady=5)
        tk.Button(root, text="Export Stock Report", command=export_stock_report).grid(row=5, column=1, pady=5)
        tk.Button(root, text="Check Low Stock", command=show_low_stock_alerts).grid(row=6, column=0, pady=5)
        tk.Button(root, text="Stock Analytics", command=show_stock_analytics).grid(row=6, column=1, pady=5)

    root.mainloop()

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
