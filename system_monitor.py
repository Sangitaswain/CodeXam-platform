#!/usr/bin/env python3
"""
System Monitoring and Performance Tracking for CodeXam Platform

This module provides comprehensive system monitoring including:
- Real-time performance metrics collection
- Resource usage monitoring (CPU, memory, database)
- Performance dashboard for system health
- User activity analytics and usage patterns
- Automated alerts for performance degradation

Version: 2.0.0
Author: CodeXam Development Team
"""

import psutil
import time
import threading
import logging
import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from functools import wraps
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SystemMetrics:
    """System performance metrics snapshot."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    active_connections: int
    process_count: int


@dataclass
class ApplicationMetrics:
    """Application-specific performance metrics."""
    timestamp: float
    active_users: int
    requests_per_minute: int
    avg_response_time: float
    error_rate: float
    submission_count: int
    problem_views: int


class SystemMonitor:
    """Core system monitoring class."""
    
    def __init__(self, collection_interval: int = 30, retention_hours: int = 24):
        self.collection_interval = collection_interval
        self.retention_hours = retention_hours
        
        # Metrics storage
        self.system_metrics = deque(maxlen=int(retention_hours * 3600 / collection_interval))
        self.application_metrics = deque(maxlen=int(retention_hours * 3600 / collection_interval))
        
        # User activity tracking
        self.user_activities = deque(maxlen=10000)
        self.active_sessions = {}
        
        # Performance counters
        self.request_counter = defaultdict(int)
        self.response_times = deque(maxlen=1000)
        self.error_counter = defaultdict(int)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Monitoring thread
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Alert system
        self.alert_handlers = []
        self.alert_thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_usage_percent': 90.0,
            'avg_response_time': 2.0,
            'error_rate': 5.0
        }
        
        # Initialize persistent storage
        self.db_path = 'monitoring.db'
        self._init_database()
        
        logger.info("System monitor initialized")
    
    def _init_database(self):
        """Initialize monitoring database."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # System metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    memory_used_mb REAL NOT NULL,
                    memory_available_mb REAL NOT NULL,
                    disk_usage_percent REAL NOT NULL,
                    active_connections INTEGER DEFAULT 0,
                    process_count INTEGER DEFAULT 0
                )
            ''')
            
            # Application metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS application_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp REAL NOT NULL,
                    active_users INTEGER DEFAULT 0,
                    requests_per_minute INTEGER DEFAULT 0,
                    avg_response_time REAL DEFAULT 0,
                    error_rate REAL DEFAULT 0,
                    submission_count INTEGER DEFAULT 0,
                    problem_views INTEGER DEFAULT 0
                )
            ''')
            
            # User activities table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS user_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    session_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    page TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    duration REAL,
                    metadata TEXT
                )
            ''')
            
            # Performance alerts table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_type TEXT NOT NULL,
                    severity TEXT NOT NULL,
                    message TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_app_timestamp ON application_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_activity_timestamp ON user_activities(timestamp)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize monitoring database: {e}")
    
    def start_monitoring(self):
        """Start the monitoring process."""
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
        self.monitoring_thread.start()
        
        logger.info("System monitoring started")
    
    def stop_monitoring(self):
        """Stop the monitoring process."""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        logger.info("System monitoring stopped")
    
    def _monitoring_loop(self):
        """Main monitoring loop."""
        while self.is_monitoring:
            try:
                # Collect system metrics
                system_metrics = self._collect_system_metrics()
                
                # Collect application metrics
                app_metrics = self._collect_application_metrics()
                
                # Store metrics
                with self.lock:
                    self.system_metrics.append(system_metrics)
                    self.application_metrics.append(app_metrics)
                
                # Store to database
                self._store_metrics(system_metrics, app_metrics)
                
                # Check for alerts
                self._check_alerts(system_metrics, app_metrics)
                
                time.sleep(self.collection_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                time.sleep(self.collection_interval)   
 
    def _collect_system_metrics(self) -> SystemMetrics:
        """Collect current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_available_mb = memory.available / 1024 / 1024
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Process metrics
            active_connections = len(psutil.net_connections())
            process_count = len(psutil.pids())
            
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                active_connections=active_connections,
                process_count=process_count
            )
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return SystemMetrics(
                timestamp=time.time(),
                cpu_percent=0, memory_percent=0, memory_used_mb=0,
                memory_available_mb=0, disk_usage_percent=0,
                active_connections=0, process_count=0
            )
    
    def _collect_application_metrics(self) -> ApplicationMetrics:
        """Collect application-specific metrics."""
        current_time = time.time()
        minute_ago = current_time - 60
        
        with self.lock:
            # Count requests in the last minute
            recent_requests = sum(
                count for timestamp, count in self.request_counter.items()
                if timestamp > minute_ago
            )
            
            # Calculate average response time
            recent_response_times = [
                rt for rt in self.response_times
                if rt['timestamp'] > minute_ago
            ]
            avg_response_time = (
                sum(rt['time'] for rt in recent_response_times) / len(recent_response_times)
                if recent_response_times else 0
            )
            
            # Calculate error rate
            recent_errors = sum(
                count for timestamp, count in self.error_counter.items()
                if timestamp > minute_ago
            )
            error_rate = (recent_errors / recent_requests * 100) if recent_requests > 0 else 0
            
            # Count active users (sessions active in last 30 minutes)
            active_threshold = current_time - 1800  # 30 minutes
            active_users = len([
                session for session, last_activity in self.active_sessions.items()
                if last_activity > active_threshold
            ])
        
        return ApplicationMetrics(
            timestamp=current_time,
            active_users=active_users,
            requests_per_minute=recent_requests,
            avg_response_time=avg_response_time,
            error_rate=error_rate,
            submission_count=0,  # Will be updated by application
            problem_views=0      # Will be updated by application
        )
    
    def _store_metrics(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Store metrics to database."""
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Store system metrics
            conn.execute('''
                INSERT INTO system_metrics 
                (timestamp, cpu_percent, memory_percent, memory_used_mb, memory_available_mb,
                 disk_usage_percent, active_connections, process_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                system_metrics.timestamp, system_metrics.cpu_percent,
                system_metrics.memory_percent, system_metrics.memory_used_mb,
                system_metrics.memory_available_mb, system_metrics.disk_usage_percent,
                system_metrics.active_connections, system_metrics.process_count
            ))
            
            # Store application metrics
            conn.execute('''
                INSERT INTO application_metrics 
                (timestamp, active_users, requests_per_minute, avg_response_time,
                 error_rate, submission_count, problem_views)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                app_metrics.timestamp, app_metrics.active_users,
                app_metrics.requests_per_minute, app_metrics.avg_response_time,
                app_metrics.error_rate, app_metrics.submission_count,
                app_metrics.problem_views
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
    
    def _check_alerts(self, system_metrics: SystemMetrics, app_metrics: ApplicationMetrics):
        """Check for performance alerts."""
        alerts = []
        
        # CPU usage alert
        if system_metrics.cpu_percent > self.alert_thresholds['cpu_percent']:
            alerts.append({
                'type': 'high_cpu',
                'severity': 'warning',
                'message': f'High CPU usage: {system_metrics.cpu_percent:.1f}%',
                'value': system_metrics.cpu_percent
            })
        
        # Memory usage alert
        if system_metrics.memory_percent > self.alert_thresholds['memory_percent']:
            alerts.append({
                'type': 'high_memory',
                'severity': 'warning',
                'message': f'High memory usage: {system_metrics.memory_percent:.1f}%',
                'value': system_metrics.memory_percent
            })
        
        # Disk usage alert
        if system_metrics.disk_usage_percent > self.alert_thresholds['disk_usage_percent']:
            alerts.append({
                'type': 'high_disk',
                'severity': 'critical',
                'message': f'High disk usage: {system_metrics.disk_usage_percent:.1f}%',
                'value': system_metrics.disk_usage_percent
            })
        
        # Response time alert
        if app_metrics.avg_response_time > self.alert_thresholds['avg_response_time']:
            alerts.append({
                'type': 'slow_response',
                'severity': 'warning',
                'message': f'Slow response time: {app_metrics.avg_response_time:.2f}s',
                'value': app_metrics.avg_response_time
            })
        
        # Error rate alert
        if app_metrics.error_rate > self.alert_thresholds['error_rate']:
            alerts.append({
                'type': 'high_errors',
                'severity': 'critical',
                'message': f'High error rate: {app_metrics.error_rate:.1f}%',
                'value': app_metrics.error_rate
            })
        
        # Trigger alert handlers
        for alert in alerts:
            self._trigger_alert(alert)
    
    def _trigger_alert(self, alert: Dict[str, Any]):
        """Trigger alert handlers."""
        try:
            # Store alert in database
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO performance_alerts (alert_type, severity, message, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (alert['type'], alert['severity'], alert['message'], time.time()))
            conn.commit()
            conn.close()
            
            # Call alert handlers
            for handler in self.alert_handlers:
                try:
                    handler(alert)
                except Exception as e:
                    logger.error(f"Alert handler error: {e}")
            
            # Log alert
            severity_level = {
                'info': logging.INFO,
                'warning': logging.WARNING,
                'critical': logging.CRITICAL
            }.get(alert['severity'], logging.WARNING)
            
            logger.log(severity_level, f"PERFORMANCE ALERT: {alert['message']}")
            
        except Exception as e:
            logger.error(f"Failed to trigger alert: {e}")
    
    # Public interface methods
    
    def record_request(self, response_time: float, status_code: int):
        """Record a request for monitoring."""
        current_time = time.time()
        minute_bucket = int(current_time // 60) * 60
        
        with self.lock:
            self.request_counter[minute_bucket] += 1
            self.response_times.append({
                'time': response_time,
                'timestamp': current_time
            })
            
            if status_code >= 400:
                self.error_counter[minute_bucket] += 1
    
    def record_user_activity(self, user_id: str, session_id: str, action: str, 
                           page: str, duration: Optional[float] = None,
                           metadata: Optional[Dict[str, Any]] = None):
        """Record user activity."""
        timestamp = time.time()
        
        with self.lock:
            self.active_sessions[session_id] = timestamp
        
        # Store to database
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute('''
                INSERT INTO user_activities 
                (user_id, session_id, action, page, timestamp, duration, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, session_id, action, page, timestamp, duration,
                json.dumps(metadata) if metadata else None
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store user activity: {e}")
    
    def add_alert_handler(self, handler: Callable[[Dict[str, Any]], None]):
        """Add an alert handler function."""
        self.alert_handlers.append(handler)
    
    def set_alert_threshold(self, metric: str, threshold: float):
        """Set alert threshold for a metric."""
        self.alert_thresholds[metric] = threshold
    
    def get_current_metrics(self) -> Dict[str, Any]:
        """Get current system metrics."""
        with self.lock:
            system_metrics = self.system_metrics[-1] if self.system_metrics else None
            app_metrics = self.application_metrics[-1] if self.application_metrics else None
        
        return {
            'system': asdict(system_metrics) if system_metrics else None,
            'application': asdict(app_metrics) if app_metrics else None,
            'timestamp': time.time()
        }
    
    def get_metrics_history(self, hours: int = 1) -> Dict[str, List[Dict[str, Any]]]:
        """Get metrics history for the specified number of hours."""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            system_history = [
                asdict(metrics) for metrics in self.system_metrics
                if metrics.timestamp > cutoff_time
            ]
            app_history = [
                asdict(metrics) for metrics in self.application_metrics
                if metrics.timestamp > cutoff_time
            ]
        
        return {
            'system': system_history,
            'application': app_history
        }
    
    def get_user_analytics(self, hours: int = 24) -> Dict[str, Any]:
        """Get user activity analytics."""
        cutoff_time = time.time() - (hours * 3600)
        
        try:
            conn = sqlite3.connect(self.db_path)
            
            # Active users
            cursor = conn.execute('''
                SELECT COUNT(DISTINCT user_id) as active_users
                FROM user_activities 
                WHERE timestamp > ?
            ''', (cutoff_time,))
            active_users = cursor.fetchone()[0]
            
            # Page views
            cursor = conn.execute('''
                SELECT page, COUNT(*) as views
                FROM user_activities 
                WHERE timestamp > ? AND action = 'page_view'
                GROUP BY page
                ORDER BY views DESC
                LIMIT 10
            ''', (cutoff_time,))
            page_views = [{'page': row[0], 'views': row[1]} for row in cursor.fetchall()]
            
            # User actions
            cursor = conn.execute('''
                SELECT action, COUNT(*) as count
                FROM user_activities 
                WHERE timestamp > ?
                GROUP BY action
                ORDER BY count DESC
            ''', (cutoff_time,))
            user_actions = [{'action': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'active_users': active_users,
                'page_views': page_views,
                'user_actions': user_actions,
                'period_hours': hours
            }
            
        except Exception as e:
            logger.error(f"Failed to get user analytics: {e}")
            return {}
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        current_metrics = self.get_current_metrics()
        history = self.get_metrics_history(1)  # Last hour
        analytics = self.get_user_analytics(24)  # Last 24 hours
        
        return {
            'current': current_metrics,
            'analytics': analytics,
            'monitoring_status': 'active' if self.is_monitoring else 'inactive'
        }


# Global monitor instance
_system_monitor = None
_monitor_lock = threading.Lock()


def get_system_monitor() -> SystemMonitor:
    """Get the global system monitor instance."""
    global _system_monitor
    
    if _system_monitor is None:
        with _monitor_lock:
            if _system_monitor is None:
                _system_monitor = SystemMonitor()
                _system_monitor.start_monitoring()
    
    return _system_monitor


def monitoring_middleware(app):
    """Flask middleware for request monitoring."""
    monitor = get_system_monitor()
    
    @app.before_request
    def before_request():
        from flask import request, session
        request.start_time = time.time()
        
        # Record user activity
        user_id = session.get('user_id', 'anonymous')
        session_id = session.get('session_id', 'unknown')
        
        monitor.record_user_activity(
            user_id=user_id,
            session_id=session_id,
            action='page_view',
            page=request.endpoint or request.path
        )
    
    @app.after_request
    def after_request(response):
        from flask import request
        if hasattr(request, 'start_time'):
            response_time = time.time() - request.start_time
            monitor.record_request(response_time, response.status_code)
        
        return response
    
    return monitor


if __name__ == '__main__':
    # Example usage and testing
    monitor = SystemMonitor()
    
    # Add a simple alert handler
    def console_alert_handler(alert):
        print(f"🚨 ALERT: {alert['message']} (Severity: {alert['severity']})")
    
    monitor.add_alert_handler(console_alert_handler)
    
    # Start monitoring
    monitor.start_monitoring()
    
    try:
        # Simulate some activity
        for i in range(10):
            monitor.record_request(0.1 + i * 0.01, 200)
            monitor.record_user_activity(f'user_{i}', f'session_{i}', 'test_action', '/test')
            time.sleep(1)
        
        # Get performance summary
        summary = monitor.get_performance_summary()
        print(f"Performance Summary: {json.dumps(summary, indent=2, default=str)}")
        
        # Keep running for a bit to see monitoring in action
        time.sleep(30)
        
    except KeyboardInterrupt:
        print("Stopping monitoring...")
    finally:
        monitor.stop_monitoring()