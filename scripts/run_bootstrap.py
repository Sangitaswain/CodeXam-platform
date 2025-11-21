#!/usr/bin/env python3
"""
CodeXam Bootstrap Runner Script

This script demonstrates how to use the Bootstrap MCP system to initialize
the CodeXam platform with sample data and configuration.
"""

import os
import sys
import logging
from bootstrap.bootstrap_runner import BootstrapMCPRunner


def main():
    """Main entry point for bootstrap demonstration."""
    print("CodeXam Bootstrap MCP System")
    print("=" * 40)
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Check if database exists
    db_path = "database.db"
    if not os.path.exists(db_path):
        print(f"Warning: Database file '{db_path}' not found.")
        print("Please run 'python init_db.py' first to create the database.")
        return False
    
    # Initialize bootstrap runner
    runner = BootstrapMCPRunner()
    
    print("\nRunning Bootstrap MCPs...")
    print("This will:")
    print("- Create sample coding problems")
    print("- Set up system configuration")
    print("- Create admin users (if configured)")
    print("- Add comprehensive test cases")
    
    # Run blocking MCPs first
    print("\n1. Running blocking MCPs...")
    success = runner.run_bootstrap(blocking_only=True)
    
    if not success:
        print("❌ Blocking MCPs failed. Stopping execution.")
        return False
    
    print("✅ Blocking MCPs completed successfully")
    
    # Run all MCPs (including non-blocking)
    print("\n2. Running all MCPs...")
    success = runner.run_bootstrap(blocking_only=False)
    
    if success:
        print("✅ All Bootstrap MCPs completed successfully!")
        print("\nYour CodeXam platform is now ready with:")
        print("- Sample problems (Two Sum, Reverse Integer, Palindrome Number)")
        print("- System configuration")
        print("- Comprehensive test cases")
        print("\nYou can now run 'python app.py' to start the server.")
    else:
        print("⚠️  Some optional MCPs failed, but core setup is complete.")
        print("You can still run 'python app.py' to start the server.")
    
    return success


def show_environment_examples():
    """Show examples of environment variable configuration."""
    print("\nEnvironment Variable Examples:")
    print("=" * 40)
    
    print("\n1. Custom Sample Problem:")
    print('export CODEXAM_SAMPLE_PROBLEMS_CONFIG=\'{"title":"Custom Problem","difficulty":"Hard","description":"Your custom problem description"}\'')
    
    print("\n2. Custom Admin User:")
    print('export CODEXAM_ADMIN_CONFIG=\'{"admin_username":"myAdmin","admin_email":"admin@mycompany.com"}\'')
    
    print("\n3. Custom System Config:")
    print('export CODEXAM_SYSTEM_CONFIG=\'{"app_name":"My CodeXam","max_code_length":"20000","execution_timeout":"10"}\'')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--help':
        print(__doc__)
        show_environment_examples()
        sys.exit(0)
    
    success = main()
    sys.exit(0 if success else 1)