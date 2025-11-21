#!/usr/bin/env python3
"""
CodeXam Database Admin Panel

Simple command-line interface for database management.
This module provides a comprehensive CLI tool for managing the CodeXam
database including viewing data, adding problems, and generating reports.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

try:
    from tabulate import tabulate
    HAS_TABULATE = True
except ImportError:
    HAS_TABULATE = False

class DatabaseAdmin:
    """
    Database administration interface for CodeXam.
    
    This class provides a command-line interface for managing the CodeXam
    database with features for viewing data, adding problems, and generating
    statistics and reports.
    
    Attributes:
        db_path: Path to the SQLite database file
        conn: Database connection object
    """
    
    def __init__(self, db_path: str = 'database.db') -> None:
        """
        Initialize the database admin interface.
        
        Args:
            db_path: Path to the SQLite database file
            
        Raises:
            sqlite3.Error: If database connection fails
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
    
    def _print_simple_table(self, headers: List[str], data: List[List[Any]]) -> None:
        """
        Print a simple table when tabulate is not available.
        
        Args:
            headers: List of column headers
            data: List of rows, each row is a list of values
        """
        # Calculate column widths
        col_widths = [len(header) for header in headers]
        for row in data:
            for i, cell in enumerate(row):
                if i < len(col_widths):
                    col_widths[i] = max(col_widths[i], len(str(cell)))
        
        # Print header
        header_row = " | ".join(
            header.ljust(col_widths[i]) for i, header in enumerate(headers)
        )
        print(header_row)
        print("-" * len(header_row))
        
        # Print data rows
        for row in data:
            data_row = " | ".join(
                str(cell).ljust(col_widths[i]) for i, cell in enumerate(row)
            )
            print(data_row)
    
    def show_menu(self) -> None:
        """Display the main menu with available options."""
        print("\n" + "="*50)
        print("🚀 CodeXam Database Admin Panel")
        print("="*50)
        print("1. View Problems")
        print("2. View Submissions")
        print("3. View Users")
        print("4. Add New Problem")
        print("5. Database Statistics")
        print("6. Search Problems")
        print("7. View User Activity")
        print("8. Export Data")
        print("9. Backup Database")
        print("0. Exit")
        print("="*50)
    
    def view_problems(self) -> None:
        """
        Display all problems in the database.
        
        Shows problem ID, title, difficulty, description length, and creation date
        in a formatted table.
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title, difficulty, 
                   LENGTH(description) as desc_length,
                   created_at
            FROM problems 
            ORDER BY difficulty, title
        """)
        
        problems = cursor.fetchall()
        if problems:
            headers = ['ID', 'Title', 'Difficulty', 'Description Length', 'Created']
            data = [[p['id'], p['title'], p['difficulty'], 
                    f"{p['desc_length']} chars", p['created_at']] for p in problems]
            print(f"\n📋 Problems ({len(problems)} total):")
            
            if HAS_TABULATE:
                print(tabulate(data, headers=headers, tablefmt='grid'))
            else:
                self._print_simple_table(headers, data)
        else:
            print("\n❌ No problems found!")
    
    def view_submissions(self, limit=20):
        """Display recent submissions"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT s.id, s.user_name, p.title, s.language, 
                   s.result, s.execution_time, s.submitted_at
            FROM submissions s
            JOIN problems p ON s.problem_id = p.id
            ORDER BY s.submitted_at DESC
            LIMIT ?
        """, (limit,))
        
        submissions = cursor.fetchall()
        if submissions:
            headers = ['ID', 'User', 'Problem', 'Language', 'Result', 'Time (s)', 'Submitted']
            data = [[s['id'], s['user_name'], s['title'][:30], s['language'], 
                    s['result'], f"{s['execution_time']:.3f}" if s['execution_time'] else 'N/A',
                    s['submitted_at']] for s in submissions]
            print(f"\n📊 Recent Submissions ({len(submissions)} shown):")
            print(tabulate(data, headers=headers, tablefmt='grid'))
        else:
            print("\n❌ No submissions found!")
    
    def view_users(self):
        """Display user statistics"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT user_name, 
                   COUNT(*) as total_submissions,
                   SUM(CASE WHEN result = 'PASS' THEN 1 ELSE 0 END) as successful,
                   COUNT(DISTINCT problem_id) as problems_attempted,
                   MIN(submitted_at) as first_submission,
                   MAX(submitted_at) as last_submission
            FROM submissions 
            WHERE user_name != 'Anonymous'
            GROUP BY user_name
            ORDER BY successful DESC, total_submissions DESC
        """)
        
        users = cursor.fetchall()
        if users:
            headers = ['User', 'Total Submissions', 'Successful', 'Problems Tried', 'First', 'Last']
            data = [[u['user_name'], u['total_submissions'], u['successful'],
                    u['problems_attempted'], u['first_submission'], u['last_submission']] 
                   for u in users]
            print(f"\n👥 User Statistics ({len(users)} users):")
            print(tabulate(data, headers=headers, tablefmt='grid'))
        else:
            print("\n❌ No users found!")
    
    def database_stats(self):
        """Show database statistics"""
        cursor = self.conn.cursor()
        
        # Count tables
        stats = {}
        for table in ['problems', 'submissions', 'users']:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            stats[table] = cursor.fetchone()[0]
        
        # Submission stats
        cursor.execute("SELECT result, COUNT(*) FROM submissions GROUP BY result")
        result_stats = dict(cursor.fetchall())
        
        # Language stats
        cursor.execute("SELECT language, COUNT(*) FROM submissions GROUP BY language ORDER BY COUNT(*) DESC")
        language_stats = cursor.fetchall()
        
        # Difficulty stats
        cursor.execute("SELECT difficulty, COUNT(*) FROM problems GROUP BY difficulty")
        difficulty_stats = dict(cursor.fetchall())
        
        print("\n📈 Database Statistics:")
        print(f"Problems: {stats['problems']}")
        print(f"Submissions: {stats['submissions']}")
        print(f"Users: {stats['users']}")
        
        print("\n📊 Submission Results:")
        for result, count in result_stats.items():
            print(f"  {result}: {count}")
        
        print("\n💻 Popular Languages:")
        for lang, count in language_stats[:5]:
            print(f"  {lang}: {count}")
        
        print("\n⚡ Problem Difficulty:")
        for diff, count in difficulty_stats.items():
            print(f"  {diff}: {count}")
    
    def add_problem(self):
        """Add a new problem interactively"""
        print("\n➕ Add New Problem")
        print("-" * 30)
        
        title = input("Problem Title: ").strip()
        if not title:
            print("❌ Title cannot be empty!")
            return
        
        difficulty = input("Difficulty (Easy/Medium/Hard): ").strip()
        if difficulty not in ['Easy', 'Medium', 'Hard']:
            print("❌ Invalid difficulty!")
            return
        
        description = input("Problem Description: ").strip()
        if not description:
            print("❌ Description cannot be empty!")
            return
        
        sample_input = input("Sample Input (optional): ").strip()
        sample_output = input("Sample Output (optional): ").strip()
        
        # Default function signatures
        function_signatures = {
            'python': f'def solution():\n    pass',
            'javascript': f'function solution() {{\n    // Your code here\n}}',
            'java': f'public void solution() {{\n    // Your code here\n}}',
            'cpp': f'void solution() {{\n    // Your code here\n}}'
        }
        
        # Default test cases
        test_cases = [
            {
                'input': sample_input or 'test input',
                'expected_output': sample_output or 'expected output'
            }
        ]
        
        try:
            cursor = self.conn.cursor()
            cursor.execute("""
                INSERT INTO problems (title, difficulty, description, sample_input, 
                                    sample_output, function_signatures, test_cases, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, difficulty, description, sample_input, sample_output,
                  json.dumps(function_signatures), json.dumps(test_cases),
                  datetime.now().isoformat()))
            
            self.conn.commit()
            print(f"✅ Problem '{title}' added successfully!")
            
        except Exception as e:
            print(f"❌ Error adding problem: {e}")
    
    def search_problems(self):
        """Search problems by title or difficulty"""
        query = input("\n🔍 Search problems (title or difficulty): ").strip()
        if not query:
            return
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT id, title, difficulty, LENGTH(description) as desc_length
            FROM problems 
            WHERE title LIKE ? OR difficulty LIKE ?
            ORDER BY title
        """, (f'%{query}%', f'%{query}%'))
        
        results = cursor.fetchall()
        if results:
            headers = ['ID', 'Title', 'Difficulty', 'Description Length']
            data = [[r['id'], r['title'], r['difficulty'], f"{r['desc_length']} chars"] 
                   for r in results]
            print(f"\n🔍 Search Results ({len(results)} found):")
            print(tabulate(data, headers=headers, tablefmt='grid'))
        else:
            print(f"\n❌ No problems found matching '{query}'")
    
    def view_user_activity(self):
        """View activity for a specific user"""
        user = input("\n👤 Enter username: ").strip()
        if not user:
            return
        
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT p.title, s.language, s.result, s.execution_time, s.submitted_at
            FROM submissions s
            JOIN problems p ON s.problem_id = p.id
            WHERE s.user_name = ?
            ORDER BY s.submitted_at DESC
        """, (user,))
        
        activities = cursor.fetchall()
        if activities:
            headers = ['Problem', 'Language', 'Result', 'Time (s)', 'Submitted']
            data = [[a['title'], a['language'], a['result'],
                    f"{a['execution_time']:.3f}" if a['execution_time'] else 'N/A',
                    a['submitted_at']] for a in activities]
            print(f"\n👤 Activity for {user} ({len(activities)} submissions):")
            print(tabulate(data, headers=headers, tablefmt='grid'))
        else:
            print(f"\n❌ No activity found for user '{user}'")
    
    def export_data(self):
        """Export data to CSV files"""
        import csv
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Export problems
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM problems")
        problems = cursor.fetchall()
        
        with open(f'problems_export_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            if problems:
                writer = csv.DictWriter(f, fieldnames=problems[0].keys())
                writer.writeheader()
                for problem in problems:
                    writer.writerow(dict(problem))
        
        # Export submissions
        cursor.execute("SELECT * FROM submissions")
        submissions = cursor.fetchall()
        
        with open(f'submissions_export_{timestamp}.csv', 'w', newline='', encoding='utf-8') as f:
            if submissions:
                writer = csv.DictWriter(f, fieldnames=submissions[0].keys())
                writer.writeheader()
                for submission in submissions:
                    writer.writerow(dict(submission))
        
        print(f"✅ Data exported to:")
        print(f"  - problems_export_{timestamp}.csv")
        print(f"  - submissions_export_{timestamp}.csv")
    
    def backup_database(self):
        """Create database backup"""
        import shutil
        from datetime import datetime
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"database_backup_{timestamp}.db"
        
        try:
            shutil.copy2(self.db_path, backup_name)
            print(f"✅ Database backed up to: {backup_name}")
        except Exception as e:
            print(f"❌ Backup failed: {e}")
    
    def run(self):
        """Main application loop"""
        print("🚀 Welcome to CodeXam Database Admin Panel!")
        
        while True:
            self.show_menu()
            choice = input("\nEnter your choice (0-9): ").strip()
            
            try:
                if choice == '1':
                    self.view_problems()
                elif choice == '2':
                    self.view_submissions()
                elif choice == '3':
                    self.view_users()
                elif choice == '4':
                    self.add_problem()
                elif choice == '5':
                    self.database_stats()
                elif choice == '6':
                    self.search_problems()
                elif choice == '7':
                    self.view_user_activity()
                elif choice == '8':
                    self.export_data()
                elif choice == '9':
                    self.backup_database()
                elif choice == '0':
                    print("\n👋 Goodbye!")
                    break
                else:
                    print("\n❌ Invalid choice! Please try again.")
                
                input("\nPress Enter to continue...")
                
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                input("Press Enter to continue...")
        
        self.conn.close()

def main() -> None:
    """Main entry point for the admin panel."""
    try:
        admin = DatabaseAdmin()
        admin.run()
    except Exception as e:
        print(f"❌ Failed to start admin panel: {e}")
        print("Make sure database.db exists and is accessible.")


if __name__ == "__main__":
    main()