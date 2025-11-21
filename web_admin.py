#!/usr/bin/env python3
"""
CodeXam Web Admin Interface

Simple Flask-based admin panel for database management.
This module provides a web-based interface for managing the CodeXam
database with features for viewing data, adding problems, and monitoring
system activity through a browser interface.
"""

import json
import sqlite3
from datetime import datetime
from typing import Any, Dict, List, Optional

from flask import Flask, jsonify, redirect, render_template_string, request, url_for

app = Flask(__name__)
app.secret_key = 'admin-secret-key-change-in-production'

def get_db() -> sqlite3.Connection:
    """
    Get database connection with row factory.
    
    Returns:
        SQLite database connection configured for dictionary-like row access
    """
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def admin_dashboard() -> str:
    """
    Admin dashboard showing system statistics and recent activity.
    
    Returns:
        Rendered HTML template with dashboard data
    """
    conn = get_db()
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("SELECT COUNT(*) as count FROM problems")
    problems_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(*) as count FROM submissions")
    submissions_count = cursor.fetchone()['count']
    
    cursor.execute("SELECT COUNT(DISTINCT user_name) as count FROM submissions WHERE user_name != 'Anonymous'")
    users_count = cursor.fetchone()['count']
    
    # Get recent activity
    cursor.execute("""
        SELECT s.user_name, p.title, s.result, s.submitted_at
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        ORDER BY s.submitted_at DESC
        LIMIT 10
    """)
    recent_activity = cursor.fetchall()
    
    conn.close()
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>CodeXam Admin Panel</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 20px; }
            .stat-card { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); text-align: center; }
            .stat-number { font-size: 2em; font-weight: bold; color: #3498db; }
            .nav { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; font-weight: bold; }
            .nav a:hover { text-decoration: underline; }
            .activity { background: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; }
            .success { color: #27ae60; }
            .error { color: #e74c3c; }
            .fail { color: #f39c12; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🚀 CodeXam Admin Panel</h1>
                <p>Database Management Interface</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-number">{{ problems_count }}</div>
                    <div>Problems</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ submissions_count }}</div>
                    <div>Submissions</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number">{{ users_count }}</div>
                    <div>Active Users</div>
                </div>
            </div>
            
            <div class="nav">
                <a href="{{ url_for('view_problems') }}">📋 Manage Problems</a>
                <a href="{{ url_for('view_submissions') }}">📊 View Submissions</a>
                <a href="{{ url_for('view_users') }}">👥 User Statistics</a>
                <a href="{{ url_for('add_problem') }}">➕ Add Problem</a>
                <a href="{{ url_for('export_data') }}">💾 Export Data</a>
            </div>
            
            <div class="activity">
                <h3>📈 Recent Activity</h3>
                <table>
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Problem</th>
                            <th>Result</th>
                            <th>Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for activity in recent_activity %}
                        <tr>
                            <td>{{ activity.user_name }}</td>
                            <td>{{ activity.title }}</td>
                            <td class="{{ activity.result.lower() }}">{{ activity.result }}</td>
                            <td>{{ activity.submitted_at }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template, 
                                problems_count=problems_count,
                                submissions_count=submissions_count,
                                users_count=users_count,
                                recent_activity=recent_activity)

@app.route('/problems')
def view_problems():
    """View all problems"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT id, title, difficulty, LENGTH(description) as desc_length, created_at
        FROM problems 
        ORDER BY difficulty, title
    """)
    problems = cursor.fetchall()
    conn.close()
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Problems - CodeXam Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .nav { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; font-weight: bold; }
            .content { background: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; }
            .easy { color: #27ae60; }
            .medium { color: #f39c12; }
            .hard { color: #e74c3c; }
            .btn { padding: 5px 10px; background: #3498db; color: white; text-decoration: none; border-radius: 4px; font-size: 12px; }
            .btn:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📋 Problems Management</h1>
            </div>
            
            <div class="nav">
                <a href="{{ url_for('admin_dashboard') }}">🏠 Dashboard</a>
                <a href="{{ url_for('add_problem') }}">➕ Add Problem</a>
            </div>
            
            <div class="content">
                <h3>All Problems ({{ problems|length }})</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Title</th>
                            <th>Difficulty</th>
                            <th>Description</th>
                            <th>Created</th>
                            <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for problem in problems %}
                        <tr>
                            <td>{{ problem.id }}</td>
                            <td>{{ problem.title }}</td>
                            <td class="{{ problem.difficulty.lower() }}">{{ problem.difficulty }}</td>
                            <td>{{ problem.desc_length }} chars</td>
                            <td>{{ problem.created_at }}</td>
                            <td>
                                <a href="/problem/{{ problem.id }}/edit" class="btn">Edit</a>
                                <a href="/problem/{{ problem.id }}/delete" class="btn" style="background: #e74c3c;" onclick="return confirm('Delete this problem?')">Delete</a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template, problems=problems)

@app.route('/add_problem', methods=['GET', 'POST'])
def add_problem():
    """Add new problem"""
    if request.method == 'POST':
        title = request.form['title']
        difficulty = request.form['difficulty']
        description = request.form['description']
        sample_input = request.form.get('sample_input', '')
        sample_output = request.form.get('sample_output', '')
        
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
        
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO problems (title, difficulty, description, sample_input, 
                                sample_output, function_signatures, test_cases, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (title, difficulty, description, sample_input, sample_output,
              json.dumps(function_signatures), json.dumps(test_cases),
              datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        return redirect(url_for('view_problems'))
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Add Problem - CodeXam Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 800px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .nav { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; font-weight: bold; }
            .content { background: white; padding: 20px; border-radius: 8px; }
            .form-group { margin-bottom: 20px; }
            label { display: block; margin-bottom: 5px; font-weight: bold; }
            input, select, textarea { width: 100%; padding: 10px; border: 1px solid #ddd; border-radius: 4px; }
            textarea { height: 100px; resize: vertical; }
            .btn { padding: 10px 20px; background: #3498db; color: white; border: none; border-radius: 4px; cursor: pointer; }
            .btn:hover { background: #2980b9; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>➕ Add New Problem</h1>
            </div>
            
            <div class="nav">
                <a href="{{ url_for('admin_dashboard') }}">🏠 Dashboard</a>
                <a href="{{ url_for('view_problems') }}">📋 View Problems</a>
            </div>
            
            <div class="content">
                <form method="POST">
                    <div class="form-group">
                        <label for="title">Problem Title:</label>
                        <input type="text" id="title" name="title" required>
                    </div>
                    
                    <div class="form-group">
                        <label for="difficulty">Difficulty:</label>
                        <select id="difficulty" name="difficulty" required>
                            <option value="Easy">Easy</option>
                            <option value="Medium">Medium</option>
                            <option value="Hard">Hard</option>
                        </select>
                    </div>
                    
                    <div class="form-group">
                        <label for="description">Problem Description:</label>
                        <textarea id="description" name="description" required></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="sample_input">Sample Input (optional):</label>
                        <textarea id="sample_input" name="sample_input"></textarea>
                    </div>
                    
                    <div class="form-group">
                        <label for="sample_output">Sample Output (optional):</label>
                        <textarea id="sample_output" name="sample_output"></textarea>
                    </div>
                    
                    <button type="submit" class="btn">Add Problem</button>
                </form>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template)

@app.route('/submissions')
def view_submissions():
    """View submissions"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT s.id, s.user_name, p.title, s.language, s.result, 
               s.execution_time, s.submitted_at
        FROM submissions s
        JOIN problems p ON s.problem_id = p.id
        ORDER BY s.submitted_at DESC
        LIMIT 100
    """)
    submissions = cursor.fetchall()
    conn.close()
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Submissions - CodeXam Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .nav { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; font-weight: bold; }
            .content { background: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; font-size: 14px; }
            th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; }
            .pass { color: #27ae60; font-weight: bold; }
            .fail { color: #f39c12; font-weight: bold; }
            .error { color: #e74c3c; font-weight: bold; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Submissions</h1>
            </div>
            
            <div class="nav">
                <a href="{{ url_for('admin_dashboard') }}">🏠 Dashboard</a>
                <a href="{{ url_for('view_users') }}">👥 Users</a>
            </div>
            
            <div class="content">
                <h3>Recent Submissions ({{ submissions|length }})</h3>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>User</th>
                            <th>Problem</th>
                            <th>Language</th>
                            <th>Result</th>
                            <th>Time (s)</th>
                            <th>Submitted</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for sub in submissions %}
                        <tr>
                            <td>{{ sub.id }}</td>
                            <td>{{ sub.user_name }}</td>
                            <td>{{ sub.title }}</td>
                            <td>{{ sub.language }}</td>
                            <td class="{{ sub.result.lower() }}">{{ sub.result }}</td>
                            <td>{{ "%.3f"|format(sub.execution_time) if sub.execution_time else 'N/A' }}</td>
                            <td>{{ sub.submitted_at }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template, submissions=submissions)

@app.route('/users')
def view_users():
    """View user statistics"""
    conn = get_db()
    cursor = conn.cursor()
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
    conn.close()
    
    template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Users - CodeXam Admin</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
            .container { max-width: 1200px; margin: 0 auto; }
            .header { background: #2c3e50; color: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; }
            .nav { background: white; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
            .nav a { margin-right: 20px; text-decoration: none; color: #3498db; font-weight: bold; }
            .content { background: white; padding: 20px; border-radius: 8px; }
            table { width: 100%; border-collapse: collapse; }
            th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
            th { background: #f8f9fa; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>👥 User Statistics</h1>
            </div>
            
            <div class="nav">
                <a href="{{ url_for('admin_dashboard') }}">🏠 Dashboard</a>
                <a href="{{ url_for('view_submissions') }}">📊 Submissions</a>
            </div>
            
            <div class="content">
                <h3>Active Users ({{ users|length }})</h3>
                <table>
                    <thead>
                        <tr>
                            <th>User</th>
                            <th>Total Submissions</th>
                            <th>Successful</th>
                            <th>Success Rate</th>
                            <th>Problems Tried</th>
                            <th>First Submission</th>
                            <th>Last Activity</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for user in users %}
                        <tr>
                            <td><strong>{{ user.user_name }}</strong></td>
                            <td>{{ user.total_submissions }}</td>
                            <td style="color: #27ae60;">{{ user.successful }}</td>
                            <td>{{ "%.1f"|format((user.successful / user.total_submissions * 100) if user.total_submissions > 0 else 0) }}%</td>
                            <td>{{ user.problems_attempted }}</td>
                            <td>{{ user.first_submission }}</td>
                            <td>{{ user.last_submission }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </body>
    </html>
    """
    
    return render_template_string(template, users=users)

@app.route('/export')
def export_data():
    """Export data"""
    return jsonify({
        "message": "Export functionality - implement CSV/JSON export here",
        "available_exports": ["problems", "submissions", "users"]
    })

def main() -> None:
    """Main entry point for the web admin panel."""
    print("🚀 Starting CodeXam Web Admin Panel...")
    print("📱 Access at: http://localhost:5001")
    print("🔧 Features: View/Add Problems, Monitor Submissions, User Stats")
    app.run(debug=True, port=5001)


if __name__ == "__main__":
    main()