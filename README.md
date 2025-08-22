# Bar Sales Management System - Comfort_2022

A professional point-of-sale (POS) and inventory management system built with Python and Tkinter, designed specifically for bar and restaurant operations.

## Features

### 🔐 User Authentication & Role Management
- **Admin Role**: Full system access including analytics, user management, and inventory control
- **Cashier Role**: Sales recording, receipt generation, and personal sales tracking
- Secure password hashing with bcrypt
- Session timeout for security (10 minutes of inactivity)

### 💰 Sales Management
- **Quick Sale Recording**: Item, quantity, and price entry
- **Automatic Receipt Generation**: PDF receipts with digital signatures
- **Real-time Stock Validation**: Prevents overselling
- **Sales History**: Personal and system-wide sales tracking
- **Today's Sales Summary**: Real-time performance metrics

### 📊 Analytics & Reporting
- **Professional Dashboard**: Interactive charts and graphs using matplotlib
- **Sales Analytics**: 7-day trends, top-selling items, sales by user/hour
- **Low Sales Alerts**: Automatic notifications for below-average performance
- **Export Capabilities**: CSV and Excel export with date filtering
- **Stock Analytics**: Inventory valuation and profit calculations

### 📦 Inventory Management
- **Stock Tracking**: Real-time inventory levels with categories
- **Price Management**: Cost and selling price tracking
- **Low Stock Alerts**: Configurable threshold warnings (default: 5 units)
- **Stock History**: Item-specific sales history
- **Bulk Operations**: Add, edit, and delete inventory items

### 🔧 System Features
- **Automatic Backups**: Daily JSON backups of sales data
- **Audit Logging**: Comprehensive activity tracking
- **Error Handling**: Robust error management and user feedback
- **Professional UI**: Modern, responsive interface with color-coded elements
- **Cross-platform**: Runs on Windows, macOS, and Linux

## Installation

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Required Dependencies
Install the required packages using pip:

```bash
pip install -r requirements.txt
```

The requirements include:
- `fpdf` - PDF receipt generation
- `bcrypt` - Secure password hashing
- `matplotlib` - Analytics charts and graphs
- `tkcalendar` - Date picker widgets
- `openpyxl` - Excel export functionality

### Setup
1. Clone or download the repository
2. Navigate to the project directory
3. Install dependencies: `pip install -r requirements.txt`
4. Run the application: `python main.py`

## Usage

### Default Login Credentials
- **Admin**: Username: `admin`, Password: `admin123`
- **Cashier**: Username: `cashier`, Password: `cashier123`

⚠️ **Important**: Change these default passwords immediately after first login through the User Management interface.

### For Cashiers
1. **Recording Sales**:
   - Enter item name, quantity, and price per unit
   - Click "Record Sale" to process
   - PDF receipt is automatically generated in the `exports/` folder

2. **Viewing Sales**:
   - "My Sales": View your personal sales history
   - "Today's Sales": View all sales for the current day
   - Summary panel shows your daily performance

### For Administrators
1. **Analytics Dashboard**:
   - Access comprehensive sales analytics
   - View charts for daily trends, top items, and user performance
   - Monitor current stock levels

2. **User Management**:
   - Add new users (admin or cashier roles)
   - Edit existing user passwords and roles
   - Delete users (with safety checks)

3. **Inventory Management**:
   - Add new items or restock existing ones
   - Set cost and selling prices
   - Categorize items for better organization
   - View sales history for specific items

4. **Export & Reporting**:
   - Export sales data with date filtering
   - Choose between CSV and Excel formats
   - Generate stock reports
   - Access audit logs

## File Structure

```
BarSalesApp-master/
├── main.py              # Main application entry point
├── dashboard.py         # Professional admin dashboard (standalone)
├── sales_utils.py       # Core business logic and database operations
├── requirements.txt     # Python dependencies
├── README.md           # This documentation
├── LICENSE             # MIT License
├── assets/
│   └── logo.png        # Company logo for receipts
├── data/               # Backup files and audit logs
│   ├── backup_YYYY-MM-DD.json
│   └── audit.log
├── exports/            # Generated receipts and export files
│   ├── receipt_*.pdf
│   ├── sales_*.csv
│   └── stock_report_*.csv
├── tests/
│   └── test_sales_utils.py  # Unit tests
└── bar_sales.db        # SQLite database (auto-created)
```

## Database Schema

The application uses SQLite with three main tables:

### Sales Table
- `id`: Primary key
- `username`: User who made the sale
- `item`: Product name
- `quantity`: Number of units sold
- `price_per_unit`: Price per individual unit
- `total`: Total sale amount
- `timestamp`: Sale date and time

### Users Table
- `id`: Primary key
- `username`: Unique username
- `password_hash`: Bcrypt-hashed password
- `role`: User role (admin/cashier)

### Inventory Table
- `item`: Product name (primary key)
- `quantity`: Current stock level
- `cost_price`: Purchase/cost price
- `selling_price`: Retail selling price
- `category`: Product category

## Security Features

- **Password Hashing**: All passwords are hashed using bcrypt
- **Session Management**: Automatic logout after 10 minutes of inactivity
- **Role-based Access**: Different interfaces for admin and cashier roles
- **Audit Trail**: All significant actions are logged with timestamps
- **Data Validation**: Input validation prevents SQL injection and data corruption
- **Backup System**: Automatic daily backups prevent data loss

## Customization

### Business Information
Edit the business details in `sales_utils.py`:
```python
business_name = "Your Business Name"
business_address = "Your Business Address"
```

### Stock Alert Threshold
Modify the low stock threshold in the relevant functions:
```python
if qty <= 5:  # Change this value as needed
```

### Session Timeout
Adjust the session timeout in `main.py`:
```python
SESSION_TIMEOUT_MS = 10 * 60 * 1000  # 10 minutes in milliseconds
```

## Troubleshooting

### Common Issues

1. **Database Errors**: 
   - Delete `bar_sales.db` to reset the database
   - The application will recreate it automatically

2. **Missing Dependencies**:
   - Run `pip install -r requirements.txt` again
   - Ensure you're using Python 3.7+

3. **PDF Generation Issues**:
   - Ensure the `exports/` directory exists
   - Check file permissions

4. **Chart Display Problems**:
   - Install tkinter development packages on Linux
   - Update matplotlib to the latest version

### Performance Tips

- Regular database maintenance (the app handles this automatically)
- Keep the `exports/` folder clean by archiving old files
- Monitor the `data/audit.log` file size

## Development

### Running Tests
```bash
python -m pytest tests/
```

### Adding New Features
The modular design makes it easy to extend:
- Business logic: `sales_utils.py`
- UI components: `main.py`
- Database operations: Centralized in `sales_utils.py`

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support, feature requests, or bug reports, please create an issue in the project repository.

## Version History

- **v2.0**: Professional UI redesign, enhanced dashboard, improved error handling
- **v1.0**: Initial release with basic POS functionality

---

**Comfort_2022 Bar Sales Management System** - Professional, Secure, Reliable