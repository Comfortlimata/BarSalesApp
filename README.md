# 📄 Requirements Analysis Document (RAD)

**Project Title:** Offline Bar Sales Tracking System  
**Client/Stakeholder:** Bar Owners in Zambia  
**Developer:** Comfort Limata  
**Platform:** Desktop App (Python + Tkinter + SQLite)

---

## 1. Introduction

### 1.1 Purpose
This application helps bar owners track beverage sales, monitor stock, and generate receipts and sales reports — all offline using a lightweight desktop system.

### 1.2 Scope
- Record daily sales (items, quantity, price)
- Deduct stock on sale
- Prevent overselling
- Track current inventory levels
- Export daily/weekly/monthly sales reports
- Print receipts via a thermal printer
- Works offline (no internet required)

---

## 2. Overall Description

### 2.1 System Perspective
A standalone Python-based system using SQLite for data storage and Tkinter for GUI.

### 2.2 Product Features
- User login for admin/staff
- Sales processing (add items, calculate totals)
- Inventory update interface
- Low-stock alerts
- Receipt printing
- Daily report export

### 2.3 User Characteristics
| User Role | Description              |
|-----------|--------------------------|
| Admin     | Manages stock and system |
| Staff     | Handles sales and prints receipts |

---

## 3. Functional Requirements

### 3.1 Authentication
- FR1: Users log in with a username and password.
- FR2: Role-based access (admin vs staff).

### 3.2 Product Management
- FR3: Admin can add/edit/remove products.
- FR4: Products must have a name, price, and stock quantity.

### 3.3 Sales Transactions
- FR5: Staff selects products and quantity.
- FR6: System calculates total price.
- FR7: Stock is reduced upon sale.
- FR8: System prevents sales when stock is insufficient.
- FR9: Receipt is printed after a sale.

### 3.4 Inventory Tracking
- FR10: Admin views stock levels.
- FR11: Low-stock warnings (< 10 units).

### 3.5 Reporting
- FR12: View and export sales reports.
- FR13: Support for .CSV and .TXT export.

### 3.6 Printer Support
- FR14: Connects to thermal receipt printers.
- FR15: Uses a simple receipt template.

---

## 4. Non-Functional Requirements

| Category      | Requirement                                                                 |
|---------------|-----------------------------------------------------------------------------|
| Performance   | Sales must be processed in < 2 seconds                                      |
| Usability     | GUI must be simple and intuitive                                            |
| Reliability   | Data must persist after crashes or restarts                                 |
| Maintainability| Code should be modular and well-documented                                 |
| Portability   | Works on Windows 10+ with no internet required                              |

---

## 5. System Requirements

### 5.1 Software
- Python 3.x
- Tkinter
- SQLite3
- Receipt printer driver (manual install)

### 5.2 Hardware
- 4GB RAM minimum
- Windows OS (Windows 10 or later)
- USB Thermal Receipt Printer
- Local Storage (50MB+)

---

## 6. User Interface (UI)

| Page         | Description                              |
|--------------|------------------------------------------|
| Login Page   | Login with role selection                |
| Dashboard    | Summary of sales, stock alerts           |
| Sales Page   | Add items to cart, checkout, print receipt |
| Stock Page   | Add or update product stock              |
| Reports Page | Export daily/weekly/monthly reports      |

---

## 7. Data Design

### 7.1 Database Tables

**users**  
- id (int)  
- username (text)  
- password (text)  
- role (admin/staff)

**products**  
- id (int)  
- name (text)  
- price (float)  
- stock (int)

**sales**  
- id (int)  
- product_id (int)  
- quantity_sold (int)  
- total_price (float)  
- sale_date (datetime)

**settings**  
- key (text)  
- value (text)

---

## 8. Assumptions and Constraints

- Only one user operates the system at a time
- Python must be pre-installed on the computer
- System assumes user will install printer drivers separately
- System language is English

---

## 9. Appendices

- Sample Receipt Format  
- Backup & Restore Guide  
- Deployment & Installation Steps

---

✅ **Status:** In Development  
🛠️ **Next Phase:** Add stock history tracking and customer features  
✉️ **Contact:** Comfort Limata  
📍 **Location:** Zambia  
 
