#!/usr/bin/env python3
"""
Bar Sales App Launcher
Comfort_2022 Bar Sales Management System

This script provides a simple way to launch the application with
proper error handling and dependency checking.
"""

import sys
import os
import subprocess

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 7):
        print("❌ Error: Python 3.7 or higher is required.")
        print(f"   Current version: {sys.version}")
        return False
    print(f"✅ Python version: {sys.version.split()[0]}")
    return True

def check_dependencies():
    """Check if all required dependencies are installed"""
    required_packages = ['tkinter', 'sqlite3', 'fpdf', 'bcrypt', 'matplotlib', 'openpyxl']
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'tkinter':
                import tkinter
            elif package == 'sqlite3':
                import sqlite3
            elif package == 'fpdf':
                import fpdf
            elif package == 'bcrypt':
                import bcrypt
            elif package == 'matplotlib':
                import matplotlib
            elif package == 'openpyxl':
                import openpyxl
            print(f"✅ {package} is installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} is missing")
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("   Please install them using: pip install -r requirements.txt")
        return False
    
    return True

def create_directories():
    """Create necessary directories if they don't exist"""
    directories = ['data', 'exports', 'assets']
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"✅ Directory exists: {directory}")

def main():
    """Main launcher function"""
    print("=" * 50)
    print("🍺 Bar Sales Management System - Comfort_2022")
    print("=" * 50)
    print("Checking system requirements...\n")
    
    # Check Python version
    if not check_python_version():
        input("Press Enter to exit...")
        return
    
    print()
    
    # Check dependencies
    if not check_dependencies():
        print("\n💡 To install missing dependencies, run:")
        print("   pip install -r requirements.txt")
        input("Press Enter to exit...")
        return
    
    print()
    
    # Create directories
    create_directories()
    
    print("\n" + "=" * 50)
    print("🚀 Starting Bar Sales Application...")
    print("=" * 50)
    print("\n📋 Default Login Credentials:")
    print("   Admin    - Username: admin,   Password: admin123")
    print("   Cashier  - Username: cashier, Password: cashier123")
    print("\n⚠️  Please change default passwords after first login!")
    print("\n🔒 Session timeout: 10 minutes of inactivity")
    print("💾 Automatic backups: Daily at application close")
    print("\n" + "-" * 50)
    
    try:
        # Import and run the main application
        import main
        print("✅ Application started successfully!")
        
    except ImportError as e:
        print(f"❌ Error importing main module: {e}")
        input("Press Enter to exit...")
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()