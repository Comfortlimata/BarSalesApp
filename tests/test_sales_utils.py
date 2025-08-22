import unittest
import os
import sqlite3
from sales_utils import (
    init_db, record_sale, export_to_csv, generate_pdf_receipt,
    create_user, get_user, hash_password, check_password, DB_NAME
)

class TestSalesUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use a test database
        cls.test_db = 'test_bar_sales.db'
        global DB_NAME
        DB_NAME = cls.test_db
        init_db()

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)
        if os.path.exists('exports/sales.csv'):
            os.remove('exports/sales.csv')
        # Remove any test receipts
        for f in os.listdir('exports'):
            if f.startswith('receipt_') and f.endswith('.pdf'):
                os.remove(os.path.join('exports', f))

    def test_user_creation_and_password(self):
        username = 'testuser'
        password = 'testpass123'
        role = 'cashier'
        self.assertTrue(create_user(username, password, role))
        user = get_user(username)
        self.assertIsNotNone(user)
        if user is not None:
            self.assertEqual(user['role'], role)
            self.assertTrue(check_password(password, user['password_hash']))
            self.assertFalse(check_password('wrongpass', user['password_hash']))

    def test_record_sale_and_export(self):
        username = 'testuser'
        item = 'Beer'
        qty = 2
        price = 10.0
        total = record_sale(username, item, qty, price)
        self.assertEqual(total, qty * price)
        # Export to CSV
        export_to_csv()
        self.assertTrue(os.path.exists('exports/sales.csv'))
        with open('exports/sales.csv', 'r') as f:
            content = f.read()
            self.assertIn('Beer', content)

    def test_generate_pdf_receipt(self):
        import uuid
        from datetime import datetime
        receipt_id = str(uuid.uuid4())[:8]
        username = 'testuser'
        item = 'Soda'
        qty = 1
        price = 5.0
        total = qty * price
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        pdf_path = generate_pdf_receipt(receipt_id, username, item, qty, price, total, timestamp)
        self.assertTrue(os.path.exists(pdf_path))
        self.assertTrue(pdf_path.endswith('.pdf'))

if __name__ == '__main__':
    unittest.main() 