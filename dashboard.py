 # dashboard.py
import tkinter as tk
from sales_utility import get_total_sales, export_to_csv
from tkinter import messagebox

def show_totals():
    total = get_total_sales()
    messagebox.showinfo("Total Sales", f"Total Sales: ZMW {total:.2f}")

def export():
    export_to_csv()
    messagebox.showinfo("Export", "Sales data exported to 'export/sales.csv'")

root = tk.Tk()
root.title("Bar Dashboard – Comfort_2022")

tk.Button(root, text="View Total Sales", command=show_totals).pack(pady=10)
tk.Button(root, text="Export Sales", command=export).pack(pady=10)

root.mainloop()
