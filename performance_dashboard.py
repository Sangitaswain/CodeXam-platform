#!/usr/bin/env python3
"""
Performance Dashboard for CodeXam Platform

This module provides a web-based performance dashboard with:
- Real-time system metrics visualization
- User activity analytics
- Performance alerts management
- Historical data analysis
- System health monitoring

Version: 2.0.0
Author: CodeXam Development Team
"""

from flask import Blueprint, render_template, jsonify, request
import json
from datetime import datetime, timedelta
from system_monitor import get_system_monitor
import sqlite3

# Create blueprint for dashboard routes
dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')


@dashboard_bp.route('/')
def index():
    """Main dashboard page."""
    return render_template('dashboard/index.html')


@dashboard_bp.route('/api/metrics/current')
def current_metrics():
    """Get current system metrics."""
    monitor = get_system_monitor()
    metrics = monitor.get_current_metrics()
    return jsonify(metrics)


@dashboard_bp.route('/api/metrics/history')
def metrics_history():
    """Get historical metrics data."""
    hours = request.args.get('hours', 1, type=int)
    monitor = get_system_monitor()
    history = monitor.get_metrics_history(hours)
    return jsonify(history)


@dashboard_bp.route('/api/analytics/users')
def user_analytics():
    """Get user activity analytics."""
    hours = request.args.get('hours', 24, type=int)
    monitor = get_system_monitor()
    analytics = monitor.get_user_analytics(hours)
    return jsonify(analytics)


@dashboard_bp.route('/api/alerts')
def get_alerts():
    """Get recent performance alerts."""
    try:
        conn = sqlite3.connect('monitoring.db')
        cursor = conn.execute('''
            SELECT alert_type, severity, message, timestamp, resolved
            FROM performance_alerts
            ORDER BY timestamp DESC
            LIMIT 50
        ''')
        
        alerts = []
        for row in cursor.fetchall():
            alerts.append({
                'type': row[0],
                'severity': row[1],
                'message': row[2],
                'timestamp': row[3],
                'resolved': bool(row[4]),
                'formatted_time': datetime.fromtimestamp(row[3]).strftime('%Y-%m-%d %H:%M:%S')
            })
        
        conn.close()
        return jsonify(alerts)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/performance/summary')
def performance_summary():
    """Get comprehensive performance summary."""
    monitor = get_system_monitor()
    summary = monitor.get_performance_summary()
    return jsonify(summary)


@dashboard_bp.route('/api/database/stats')
def database_stats():
    """Get database performance statistics."""
    try:
        # Import database optimization modules if available
        try:
            from database_optimized import get_optimized_db
            db = get_optimized_db()
            stats = db.get_performance_stats()
            return jsonify(stats)
        except ImportError:
            # Fallback to basic database stats
            conn = sqlite3.connect('database.db')
            
            # Get table sizes
            cursor = conn.execute('''
                SELECT name, COUNT(*) as row_count
                FROM sqlite_master 
                WHERE type='table' AND name NOT LIKE 'sqlite_%'
            ''')
            
            table_stats = []
            for table_name in cursor.fetchall():
                cursor2 = conn.execute(f'SELECT COUNT(*) FROM {table_name[0]}')
                count = cursor2.fetchone()[0]
                table_stats.append({
                    'table': table_name[0],
                    'rows': count
                })
            
            conn.close()
            
            return jsonify({
                'tables': table_stats,
                'total_tables': len(table_stats)
            })
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@dashboard_bp.route('/api/system/info')
def system_info():
    """Get system information."""
    import platform
    import psutil
    
    try:
        # System information
        system_info = {
            'platform': platform.platform(),
            'processor': platform.processor(),
            'architecture': platform.architecture(),
            'python_version': platform.python_version(),
            'boot_time': psutil.boot_time(),
            'cpu_count': psutil.cpu_count(),
            'memory_total': psutil.virtual_memory().total / 1024 / 1024 / 1024,  # GB
            'disk_total': psutil.disk_usage('/').total / 1024 / 1024 / 1024  # GB
        }
        
        return jsonify(system_info)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


def create_dashboard_template():
    """Create the dashboard HTML template."""
    template_content = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CodeXam Performance Dashboard</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        .metric-card {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 20px;
        }
        
        .metric-value {
            font-size: 2.5rem;
            font-weight: bold;
        }
        
        .metric-label {
            font-size: 0.9rem;
            opacity: 0.8;
        }
        
        .alert-card {
            border-left: 4px solid;
            margin-bottom: 10px;
        }
        
        .alert-warning {
            border-left-color: #ffc107;
            background-color: #fff3cd;
        }
        
        .alert-critical {
            border-left-color: #dc3545;
            background-color: #f8d7da;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            margin-bottom: 30px;
        }
        
        .status-indicator {
            width: 12px;
            height: 12px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 8px;
        }
        
        .status-active {
            background-color: #28a745;
        }
        
        .status-inactive {
            background-color: #dc3545;
        }
    </style>
</head>
<body>
    <div class="container-fluid">
        <div class="row">
            <div class="col-12">
                <nav class="navbar navbar-expand-lg navbar-dark bg-dark">
                    <div class="container-fluid">
                        <a class="navbar-brand" href="#">
                            <span class="status-indicator status-active" id="monitoring-status"></span>
                            CodeXam Performance Dashboard
                        </a>
                        <div class="navbar-nav ms-auto">
                            <span class="navbar-text" id="last-update">
                                Last updated: <span id="update-time">--</span>
                            </span>
                        </div>
                    </div>
                </nav>
            </div>
        </div>
        
        <!-- System Metrics Row -->
        <div class="row mt-4">
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value" id="cpu-usage">--</div>
                    <div class="metric-label">CPU Usage</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value" id="memory-usage">--</div>
                    <div class="metric-label">Memory Usage</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value" id="active-users">--</div>
                    <div class="metric-label">Active Users</div>
                </div>
            </div>
            <div class="col-md-3">
                <div class="metric-card">
                    <div class="metric-value" id="response-time">--</div>
                    <div class="metric-label">Avg Response Time</div>
                </div>
            </div>
        </div>
        
        <!-- Charts Row -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>System Performance</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="system-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Application Metrics</h5>
                    </div>
                    <div class="card-body">
                        <div class="chart-container">
                            <canvas id="app-chart"></canvas>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Alerts and Analytics Row -->
        <div class="row mt-4">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>Recent Alerts</h5>
                    </div>
                    <div class="card-body" id="alerts-container">
                        <p class="text-muted">Loading alerts...</p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-header">
                        <h5>User Activity</h5>
                    </div>
                    <div class="card-body" id="analytics-container">
                        <p class="text-muted">Loading analytics...</p>
                    </div>
                </div>
            </div>
        </div>
    </div>
    
    <script>
        // Dashboard JavaScript
        let systemChart, appChart;
        
        // Initialize charts
        function initCharts() {
            const systemCtx = document.getElementById('system-chart').getContext('2d');
            systemChart = new Chart(systemCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'CPU %',
                        data: [],
                        borderColor: 'rgb(255, 99, 132)',
                        tension: 0.1
                    }, {
                        label: 'Memory %',
                        data: [],
                        borderColor: 'rgb(54, 162, 235)',
                        tension: 0.1
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            beginAtZero: true,
                            max: 100
                        }
                    }
                }
            });
            
            const appCtx = document.getElementById('app-chart').getContext('2d');
            appChart = new Chart(appCtx, {
                type: 'line',
                data: {
                    labels: [],
                    datasets: [{
                        label: 'Requests/min',
                        data: [],
                        borderColor: 'rgb(75, 192, 192)',
                        tension: 0.1
                    }, {
                        label: 'Response Time (ms)',
                        data: [],
                        borderColor: 'rgb(255, 205, 86)',
                        tension: 0.1,
                        yAxisID: 'y1'
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    scales: {
                        y: {
                            type: 'linear',
                            display: true,
                            position: 'left',
                        },
                        y1: {
                            type: 'linear',
                            display: true,
                            position: 'right',
                            grid: {
                                drawOnChartArea: false,
                            },
                        }
                    }
                }
            });
        }
        
        // Update dashboard data
        function updateDashboard() {
            // Update current metrics
            fetch('/dashboard/api/metrics/current')
                .then(response => response.json())
                .then(data => {
                    if (data.system) {
                        document.getElementById('cpu-usage').textContent = 
                            data.system.cpu_percent.toFixed(1) + '%';
                        document.getElementById('memory-usage').textContent = 
                            data.system.memory_percent.toFixed(1) + '%';
                    }
                    
                    if (data.application) {
                        document.getElementById('active-users').textContent = 
                            data.application.active_users;
                        document.getElementById('response-time').textContent = 
                            (data.application.avg_response_time * 1000).toFixed(0) + 'ms';
                    }
                    
                    document.getElementById('update-time').textContent = 
                        new Date().toLocaleTimeString();
                });
            
            // Update charts with historical data
            fetch('/dashboard/api/metrics/history?hours=1')
                .then(response => response.json())
                .then(data => {
                    updateCharts(data);
                });
            
            // Update alerts
            fetch('/dashboard/api/alerts')
                .then(response => response.json())
                .then(data => {
                    updateAlerts(data);
                });
            
            // Update analytics
            fetch('/dashboard/api/analytics/users')
                .then(response => response.json())
                .then(data => {
                    updateAnalytics(data);
                });
        }
        
        function updateCharts(data) {
            if (data.system && data.system.length > 0) {
                const labels = data.system.map(item => 
                    new Date(item.timestamp * 1000).toLocaleTimeString()
                );
                const cpuData = data.system.map(item => item.cpu_percent);
                const memoryData = data.system.map(item => item.memory_percent);
                
                systemChart.data.labels = labels;
                systemChart.data.datasets[0].data = cpuData;
                systemChart.data.datasets[1].data = memoryData;
                systemChart.update();
            }
            
            if (data.application && data.application.length > 0) {
                const labels = data.application.map(item => 
                    new Date(item.timestamp * 1000).toLocaleTimeString()
                );
                const requestData = data.application.map(item => item.requests_per_minute);
                const responseData = data.application.map(item => item.avg_response_time * 1000);
                
                appChart.data.labels = labels;
                appChart.data.datasets[0].data = requestData;
                appChart.data.datasets[1].data = responseData;
                appChart.update();
            }
        }
        
        function updateAlerts(alerts) {
            const container = document.getElementById('alerts-container');
            
            if (alerts.length === 0) {
                container.innerHTML = '<p class="text-success">No recent alerts</p>';
                return;
            }
            
            const alertsHtml = alerts.slice(0, 5).map(alert => `
                <div class="alert-card alert-${alert.severity} p-3">
                    <div class="d-flex justify-content-between">
                        <strong>${alert.message}</strong>
                        <small class="text-muted">${alert.formatted_time}</small>
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = alertsHtml;
        }
        
        function updateAnalytics(analytics) {
            const container = document.getElementById('analytics-container');
            
            if (!analytics.page_views) {
                container.innerHTML = '<p class="text-muted">No analytics data available</p>';
                return;
            }
            
            const analyticsHtml = `
                <div class="row">
                    <div class="col-6">
                        <h6>Active Users (24h)</h6>
                        <p class="h4 text-primary">${analytics.active_users}</p>
                    </div>
                    <div class="col-6">
                        <h6>Total Actions</h6>
                        <p class="h4 text-success">${analytics.user_actions.reduce((sum, action) => sum + action.count, 0)}</p>
                    </div>
                </div>
                <div class="mt-3">
                    <h6>Top Pages</h6>
                    ${analytics.page_views.slice(0, 5).map(page => `
                        <div class="d-flex justify-content-between">
                            <span>${page.page}</span>
                            <span class="badge bg-primary">${page.views}</span>
                        </div>
                    `).join('')}
                </div>
            `;
            
            container.innerHTML = analyticsHtml;
        }
        
        // Initialize dashboard
        document.addEventListener('DOMContentLoaded', function() {
            initCharts();
            updateDashboard();
            
            // Update every 30 seconds
            setInterval(updateDashboard, 30000);
        });
    </script>
</body>
</html>
    '''
    
    return template_content


if __name__ == '__main__':
    # Create template file
    import os
    
    template_dir = 'templates/dashboard'
    os.makedirs(template_dir, exist_ok=True)
    
    with open(f'{template_dir}/index.html', 'w') as f:
        f.write(create_dashboard_template())
    
    print("Dashboard template created successfully!")
    print("To use the dashboard, add the blueprint to your Flask app:")
    print("from performance_dashboard import dashboard_bp")
    print("app.register_blueprint(dashboard_bp)")