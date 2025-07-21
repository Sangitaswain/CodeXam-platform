#!/usr/bin/env python3
"""
CodeXam Database Reset Utility
Development utility to reset database state
"""

import os
import sys
from init_db import reset_database

def main():
    """Main function for database reset."""
    print("🔄 CodeXam Database Reset Utility")
    print("⚠️  This will delete all data in the database!")
    
    # Safety check for production
    if os.environ.get('FLASK_ENV') == 'production':
        print("❌ Cannot reset database in production environment!")
        sys.exit(1)
    
    # Confirmation prompt
    confirm = input("Are you sure you want to reset the database? (type 'yes' to confirm): ")
    if confirm.lower() != 'yes':
        print("❌ Database reset cancelled")
        sys.exit(0)
    
    # Reset database
    database_path = os.environ.get('DATABASE_URL', 'database.db')
    if database_path.startswith('sqlite:///'):
        database_path = database_path[10:]
    elif database_path.startswith('sqlite://'):
        database_path = database_path[9:]
    
    success = reset_database(database_path)
    
    if success:
        print("✅ Database reset completed successfully!")
        print("💡 You can now run seed_problems.py to add sample data")
    else:
        print("❌ Database reset failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()