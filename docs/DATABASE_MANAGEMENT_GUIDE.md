# CodeXam Database Management Guide

## 🗄️ Database Access Methods

### 1. **Built-in Python Scripts** (Recommended)

#### Initialize Database
```bash
python init_db.py
```
- Creates all tables (problems, submissions, users)
- Sets up the database schema
- Safe to run multiple times

#### Add Sample Problems
```bash
python seed_problems.py
```
- Adds sample coding problems
- Includes Easy, Medium, Hard problems
- Good for testing and development

#### Reset Database (DANGER!)
```bash
python reset_db.py
```
- ⚠️ **WARNING**: Deletes ALL data
- Recreates empty database
- Use only for development

#### Add More Sample Problems
```bash
python add_sample_problems.py
```
- Adds additional problems to existing database
- Won't duplicate existing problems

### 2. **Direct SQLite Access**

#### Using SQLite Command Line
```bash
# Open database
sqlite3 database.db

# View all tables
.tables

# View table structure
.schema problems
.schema submissions
.schema users

# Query data
SELECT * FROM problems;
SELECT * FROM submissions LIMIT 10;
SELECT COUNT(*) FROM users;

# Exit
.quit
```

#### Using Python Interactive Shell
```bash
python -c "
import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

# View all problems
cursor.execute('SELECT id, title, difficulty FROM problems')
for row in cursor.fetchall():
    print(row)

# View recent submissions
cursor.execute('SELECT * FROM submissions ORDER BY submitted_at DESC LIMIT 5')
for row in cursor.fetchall():
    print(row)

conn.close()
"
```

### 3. **Web-based Database Viewers**

#### Option A: DB Browser for SQLite (Recommended)
1. Download from: https://sqlitebrowser.org/
2. Install and open
3. Open your `database.db` file
4. Visual interface for:
   - Viewing data
   - Editing records
   - Running queries
   - Exporting data

#### Option B: Online SQLite Viewer
1. Go to: https://sqliteviewer.app/
2. Upload your `database.db` file
3. Browse and query data online

### 4. **Custom Database Admin Panel**

Let me create a simple admin panel for you: