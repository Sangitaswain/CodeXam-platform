#!/usr/bin/env python3
"""
Performance Monitoring System for CodeXam Platform

This module provides comprehensive performance monitoring with:
- Real-time performance metrics collection
- Database query performance analysis
- System resource monitoring
- Performance alerts and notifications
- Historical performance data storage
- Performance optimization recommendations

Version: 2.0.0
Author: CodeXam Development Team
"""

import time
import threading
import logging
import json
import sqlite3
import psutil
import gc
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
from functools import wraps
from datetime import datetime, timedelta
import weakref
import os
import sys

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetric:
    """Individual performance metric."""
    name: str
    value: float
    unit: str
    timestamp: float
    category: str
    tags: Dict[str, str] = None
    
    def __post_init__(self):
        if self.tags is None:
            self.tags = {}


@dataclass
class QueryPerformance:
    """Database query performance metrics."""
    query_hash: str
    query_text: str
    execution_time: float
    rows_affected: int
    memory_used: int
    cpu_time: float
    timestamp: float
    cache_hit: bool = False
    error: Optional[str] = None


@dataclass
class SystemMetrics:
    """System resource metrics."""
    cpu_percent: float
    memory_percent: float
    memory_used_mb: float
    memory_available_mb: float
    disk_usage_percent: float
    disk_io_read_mb: float
    disk_io_write_mb: float
    network_sent_mb: float
    network_recv_mb: float
    active_connections: int
    timestamp: float


@dataclass
class PerformanceAlert:
    """Performance alert definition."""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    message: str
    severity: str  # 'low', 'medium', 'high', 'critical'
    cooldown_seconds: int = 300
    last_triggered: float = 0


class PerformanceCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self, max_metrics: int = 10000, storage_path: str = None):
        self.max_metrics = max_metrics
        self.storage_path = storage_path or 'performance_metrics.db'
        
        # In-memory storage
        self.metrics = deque(maxlen=max_metrics)
        self.query_metrics = deque(maxlen=max_metrics)
        self.system_metrics = deque(maxlen=1000)  # Keep last 1000 system snapshots
        
        # Aggregated data
        self.metric_aggregates = defaultdict(list)
        self.query_aggregates = defaultdict(list)
        
        # Thread safety
        self.lock = threading.RLock()
        
        # Initialize persistent storage
        self._init_storage()
        
        # Start background collection
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        logger.info(f"Performance collector initialized (storage: {self.storage_path})")
    
    def _init_storage(self) -> None:
        """Initialize persistent storage database."""
        try:
            conn = sqlite3.connect(self.storage_path, check_same_thread=False)
            
            # Performance metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    value REAL NOT NULL,
                    unit TEXT NOT NULL,
                    category TEXT NOT NULL,
                    tags TEXT DEFAULT '{}',
                    timestamp REAL NOT NULL
                )
            ''')
            
            # Query performance table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS query_performance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    query_hash TEXT NOT NULL,
                    query_text TEXT NOT NULL,
                    execution_time REAL NOT NULL,
                    rows_affected INTEGER DEFAULT 0,
                    memory_used INTEGER DEFAULT 0,
                    cpu_time REAL DEFAULT 0,
                    cache_hit BOOLEAN DEFAULT FALSE,
                    error TEXT,
                    timestamp REAL NOT NULL
                )
            ''')
            
            # System metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS system_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    cpu_percent REAL NOT NULL,
                    memory_percent REAL NOT NULL,
                    memory_used_mb REAL NOT NULL,
                    memory_available_mb REAL NOT NULL,
                    disk_usage_percent REAL NOT NULL,
                    disk_io_read_mb REAL DEFAULT 0,
                    disk_io_write_mb REAL DEFAULT 0,
                    network_sent_mb REAL DEFAULT 0,
                    network_recv_mb REAL DEFAULT 0,
                    active_connections INTEGER DEFAULT 0,
                    timestamp REAL NOT NULL
                )
            ''')
            
            # Create indexes
            conn.execute('CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_perf_name ON performance_metrics(name)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_query_timestamp ON query_performance(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_query_hash ON query_performance(query_hash)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_system_timestamp ON system_metrics(timestamp)')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            logger.error(f"Failed to initialize performance storage: {e}")
    
    def record_metric(self, name: str, value: float, unit: str = '', 
                     category: str = 'general', tags: Dict[str, str] = None) -> None:
        """Record a performance metric."""
        metric = PerformanceMetric(
            name=name,
            value=value,
            unit=unit,
            timestamp=time.time(),
            category=category,
            tags=tags or {}
        )
        
        with self.lock:
            self.metrics.append(metric)
            self.metric_aggregates[name].append(value)
            
            # Keep only recent aggregates
            if len(self.metric_aggregates[name]) > 1000:
                self.metric_aggregates[name] = self.metric_aggregates[name][-1000:]
        
        # Store to database (async)
        threading.Thread(target=self._store_metric, args=(metric,), daemon=True).start()
    
    def record_query_performance(self, query_hash: str, query_text: str, 
                                execution_time: float, rows_affected: int = 0,
                                memory_used: int = 0, cpu_time: float = 0,
                                cache_hit: bool = False, error: str = None) -> None:
        """Record database query performance."""
        query_perf = QueryPerformance(
            query_hash=query_hash,
            query_text=query_text,
            execution_time=execution_time,
            rows_affected=rows_affected,
            memory_used=memory_used,
            cpu_time=cpu_time,
            timestamp=time.time(),
            cache_hit=cache_hit,
            error=error
        )
        
        with self.lock:
            self.query_metrics.append(query_perf)
            self.query_aggregates[query_hash].append(execution_time)
            
            # Keep only recent aggregates
            if len(self.query_aggregates[query_hash]) > 100:
                self.query_aggregates[query_hash] = self.query_aggregates[query_hash][-100:]
        
        # Store to database (async)
        threading.Thread(target=self._store_query_performance, args=(query_perf,), daemon=True).start()
    
    def record_system_metrics(self) -> SystemMetrics:
        """Record current system metrics."""
        try:
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            memory_percent = memory.percent
            memory_used_mb = memory.used / 1024 / 1024
            memory_available_mb = memory.available / 1024 / 1024
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            disk_usage_percent = disk.percent
            
            # Disk I/O metrics
            disk_io = psutil.disk_io_counters()
            disk_io_read_mb = disk_io.read_bytes / 1024 / 1024 if disk_io else 0
            disk_io_write_mb = disk_io.write_bytes / 1024 / 1024 if disk_io else 0
            
            # Network metrics
            network = psutil.net_io_counters()
            network_sent_mb = network.bytes_sent / 1024 / 1024 if network else 0
            network_recv_mb = network.bytes_recv / 1024 / 1024 if network else 0
            
            # Connection count (approximate)
            active_connections = len(psutil.net_connections())
            
            system_metric = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory_percent,
                memory_used_mb=memory_used_mb,
                memory_available_mb=memory_available_mb,
                disk_usage_percent=disk_usage_percent,
                disk_io_read_mb=disk_io_read_mb,
                disk_io_write_mb=disk_io_write_mb,
                network_sent_mb=network_sent_mb,
                network_recv_mb=network_recv_mb,
                active_connections=active_connections,
                timestamp=time.time()
            )
            
            with self.lock:
                self.system_metrics.append(system_metric)
            
            # Store to database (async)
            threading.Thread(target=self._store_system_metrics, args=(system_metric,), daemon=True).start()
            
            return system_metric
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
            return None
    
    def _collection_loop(self) -> None:
        """Background collection loop."""
        while True:
            try:
                # Collect system metrics every 30 seconds
                self.record_system_metrics()
                
                # Collect garbage collection metrics
                gc_stats = gc.get_stats()
                if gc_stats:
                    for i, stats in enumerate(gc_stats):
                        self.record_metric(f'gc_generation_{i}_collections', 
                                         stats['collections'], 'count', 'gc')
                        self.record_metric(f'gc_generation_{i}_collected', 
                                         stats['collected'], 'count', 'gc')
                        self.record_metric(f'gc_generation_{i}_uncollectable', 
                                         stats['uncollectable'], 'count', 'gc')
                
                # Collect Python process metrics
                process = psutil.Process()
                self.record_metric('process_memory_rss', process.memory_info().rss / 1024 / 1024, 'MB', 'process')
                self.record_metric('process_memory_vms', process.memory_info().vms / 1024 / 1024, 'MB', 'process')
                self.record_metric('process_cpu_percent', process.cpu_percent(), '%', 'process')
                self.record_metric('process_num_threads', process.num_threads(), 'count', 'process')
                self.record_metric('process_num_fds', process.num_fds(), 'count', 'process')
                
                time.sleep(30)  # Collect every 30 seconds
                
            except Exception as e:
                logger.error(f"Performance collection error: {e}")
                time.sleep(30)
    
    def _store_metric(self, metric: PerformanceMetric) -> None:
        """Store metric to database."""
        try:
            conn = sqlite3.connect(self.storage_path, check_same_thread=False)
            conn.execute('''
                INSERT INTO performance_metrics 
                (name, value, unit, category, tags, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metric.name, metric.value, metric.unit, metric.category,
                json.dumps(metric.tags), metric.timestamp
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store metric: {e}")
    
    def _store_query_performance(self, query_perf: QueryPerformance) -> None:
        """Store query performance to database."""
        try:
            conn = sqlite3.connect(self.storage_path, check_same_thread=False)
            conn.execute('''
                INSERT INTO query_performance 
                (query_hash, query_text, execution_time, rows_affected, 
                 memory_used, cpu_time, cache_hit, error, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                query_perf.query_hash, query_perf.query_text, query_perf.execution_time,
                query_perf.rows_affected, query_perf.memory_used, query_perf.cpu_time,
                query_perf.cache_hit, query_perf.error, query_perf.timestamp
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store query performance: {e}")
    
    def _store_system_metrics(self, system_metric: SystemMetrics) -> None:
        """Store system metrics to database."""
        try:
            conn = sqlite3.connect(self.storage_path, check_same_thread=False)
            conn.execute('''
                INSERT INTO system_metrics 
                (cpu_percent, memory_percent, memory_used_mb, memory_available_mb,
                 disk_usage_percent, disk_io_read_mb, disk_io_write_mb,
                 network_sent_mb, network_recv_mb, active_connections, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                system_metric.cpu_percent, system_metric.memory_percent,
                system_metric.memory_used_mb, system_metric.memory_available_mb,
                system_metric.disk_usage_percent, system_metric.disk_io_read_mb,
                system_metric.disk_io_write_mb, system_metric.network_sent_mb,
                system_metric.network_recv_mb, system_metric.active_connections,
                system_metric.timestamp
            ))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Failed to store system metrics: {e}")
    
    def get_metric_summary(self, name: str, hours: int = 1) -> Dict[str, Any]:
        """Get summary statistics for a metric."""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            recent_values = [
                m.value for m in self.metrics 
                if m.name == name and m.timestamp >= cutoff_time
            ]
        
        if not recent_values:
            return {'name': name, 'count': 0}
        
        return {
            'name': name,
            'count': len(recent_values),
            'min': min(recent_values),
            'max': max(recent_values),
            'avg': sum(recent_values) / len(recent_values),
            'latest': recent_values[-1] if recent_values else None
        }
    
    def get_slow_queries(self, threshold_ms: float = 100, limit: int = 10) -> List[Dict[str, Any]]:
        """Get slowest queries above threshold."""
        threshold_seconds = threshold_ms / 1000
        
        with self.lock:
            slow_queries = [
                {
                    'query_hash': q.query_hash,
                    'query_text': q.query_text[:200] + '...' if len(q.query_text) > 200 else q.query_text,
                    'execution_time_ms': round(q.execution_time * 1000, 2),
                    'rows_affected': q.rows_affected,
                    'timestamp': q.timestamp,
                    'cache_hit': q.cache_hit
                }
                for q in self.query_metrics
                if q.execution_time >= threshold_seconds
            ]
        
        # Sort by execution time (descending) and limit
        slow_queries.sort(key=lambda x: x['execution_time_ms'], reverse=True)
        return slow_queries[:limit]
    
    def get_performance_report(self, hours: int = 1) -> Dict[str, Any]:
        """Generate comprehensive performance report."""
        cutoff_time = time.time() - (hours * 3600)
        
        with self.lock:
            # Recent metrics
            recent_metrics = [m for m in self.metrics if m.timestamp >= cutoff_time]
            recent_queries = [q for q in self.query_metrics if q.timestamp >= cutoff_time]
            recent_system = [s for s in self.system_metrics if s.timestamp >= cutoff_time]
        
        # Query performance analysis
        query_times = [q.execution_time for q in recent_queries]
        cache_hits = sum(1 for q in recent_queries if q.cache_hit)
        cache_hit_rate = (cache_hits / len(recent_queries) * 100) if recent_queries else 0
        
        # System performance analysis
        if recent_system:
            avg_cpu = sum(s.cpu_percent for s in recent_system) / len(recent_system)
            avg_memory = sum(s.memory_percent for s in recent_system) / len(recent_system)
            max_cpu = max(s.cpu_percent for s in recent_system)
            max_memory = max(s.memory_percent for s in recent_system)
        else:
            avg_cpu = avg_memory = max_cpu = max_memory = 0
        
        return {
            'report_period_hours': hours,
            'timestamp': time.time(),
            'metrics': {
                'total_recorded': len(recent_metrics),
                'categories': list(set(m.category for m in recent_metrics))
            },
            'database': {
                'total_queries': len(recent_queries),
                'avg_query_time_ms': round(sum(query_times) / len(query_times) * 1000, 2) if query_times else 0,
                'max_query_time_ms': round(max(query_times) * 1000, 2) if query_times else 0,
                'cache_hit_rate': round(cache_hit_rate, 2),
                'slow_queries_count': len([q for q in query_times if q > 0.1])
            },
            'system': {
                'avg_cpu_percent': round(avg_cpu, 2),
                'max_cpu_percent': round(max_cpu, 2),
                'avg_memory_percent': round(avg_memory, 2),
                'max_memory_percent': round(max_memory, 2),
                'samples_collected': len(recent_system)
            },
            'slow_queries': self.get_slow_queries(100, 5)
        }


class PerformanceMonitor:
    """Main performance monitoring system."""
    
    def __init__(self, collector: PerformanceCollector = None):
        self.collector = collector or PerformanceCollector()
        self.alerts = []
        self.alert_handlers = []
        self.lock = threading.Lock()
        
        # Register default alerts
        self._register_default_alerts()
        
        # Start alert monitoring
        self.alert_thread = threading.Thread(target=self._alert_loop, daemon=True)
        self.alert_thread.start()
        
        logger.info("Performance monitor initialized")
    
    def _register_default_alerts(self) -> None:
        """Register default performance alerts."""
        # High CPU usage alert
        self.add_alert(
            name='high_cpu_usage',
            condition=lambda metrics: metrics.get('system', {}).get('avg_cpu_percent', 0) > 80,
            message='High CPU usage detected: {avg_cpu_percent}%',
            severity='high',
            cooldown_seconds=300
        )
        
        # High memory usage alert
        self.add_alert(
            name='high_memory_usage',
            condition=lambda metrics: metrics.get('system', {}).get('avg_memory_percent', 0) > 85,
            message='High memory usage detected: {avg_memory_percent}%',
            severity='high',
            cooldown_seconds=300
        )
        
        # Slow query alert
        self.add_alert(
            name='slow_queries',
            condition=lambda metrics: metrics.get('database', {}).get('slow_queries_count', 0) > 5,
            message='Multiple slow queries detected: {slow_queries_count} queries > 100ms',
            severity='medium',
            cooldown_seconds=600
        )
        
        # Low cache hit rate alert
        self.add_alert(
            name='low_cache_hit_rate',
            condition=lambda metrics: metrics.get('database', {}).get('cache_hit_rate', 100) < 50,
            message='Low cache hit rate: {cache_hit_rate}%',
            severity='medium',
            cooldown_seconds=900
        )
    
    def add_alert(self, name: str, condition: Callable, message: str, 
                 severity: str = 'medium', cooldown_seconds: int = 300) -> None:
        """Add a performance alert."""
        alert = PerformanceAlert(
            name=name,
            condition=condition,
            message=message,
            severity=severity,
            cooldown_seconds=cooldown_seconds
        )
        
        with self.lock:
            self.alerts.append(alert)
    
    def add_alert_handler(self, handler: Callable[[PerformanceAlert, Dict[str, Any]], None]) -> None:
        """Add an alert handler function."""
        with self.lock:
            self.alert_handlers.append(handler)
    
    def _alert_loop(self) -> None:
        """Background alert monitoring loop."""
        while True:
            try:
                # Get current performance report
                report = self.collector.get_performance_report(hours=0.25)  # Last 15 minutes
                
                current_time = time.time()
                
                with self.lock:
                    for alert in self.alerts:
                        # Check cooldown
                        if current_time - alert.last_triggered < alert.cooldown_seconds:
                            continue
                        
                        # Check condition
                        if alert.condition(report):
                            alert.last_triggered = current_time
                            
                            # Format message
                            try:
                                formatted_message = alert.message.format(**report.get('system', {}), 
                                                                        **report.get('database', {}))
                            except:
                                formatted_message = alert.message
                            
                            # Trigger alert handlers
                            for handler in self.alert_handlers:
                                try:
                                    handler(alert, report)
                                except Exception as e:
                                    logger.error(f"Alert handler error: {e}")
                            
                            # Log alert
                            log_level = {
                                'low': logging.INFO,
                                'medium': logging.WARNING,
                                'high': logging.ERROR,
                                'critical': logging.CRITICAL
                            }.get(alert.severity, logging.WARNING)
                            
                            logger.log(log_level, f"PERFORMANCE ALERT [{alert.severity.upper()}] {alert.name}: {formatted_message}")
                
                time.sleep(60)  # Check alerts every minute
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                time.sleep(60)
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get data for performance dashboard."""
        report = self.collector.get_performance_report(hours=1)
        
        # Add recent system metrics for charts
        with self.collector.lock:
            recent_system = list(self.collector.system_metrics)[-60:]  # Last 60 samples
        
        chart_data = {
            'cpu_usage': [{'timestamp': s.timestamp, 'value': s.cpu_percent} for s in recent_system],
            'memory_usage': [{'timestamp': s.timestamp, 'value': s.memory_percent} for s in recent_system],
            'active_connections': [{'timestamp': s.timestamp, 'value': s.active_connections} for s in recent_system]
        }
        
        return {
            'summary': report,
            'charts': chart_data,
            'alerts': [
                {
                    'name': alert.name,
                    'severity': alert.severity,
                    'last_triggered': alert.last_triggered,
                    'cooldown_remaining': max(0, alert.cooldown_seconds - (time.time() - alert.last_triggered))
                }
                for alert in self.alerts
            ]
        }


def performance_timer(monitor: PerformanceMonitor, category: str = 'general'):
    """Decorator to time function execution."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                monitor.collector.record_metric(
                    name=f'function_{func.__name__}_time',
                    value=execution_time,
                    unit='seconds',
                    category=category
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                monitor.collector.record_metric(
                    name=f'function_{func.__name__}_error_time',
                    value=execution_time,
                    unit='seconds',
                    category=category
                )
                raise
        return wrapper
    return decorator


# Global performance monitor instance
_performance_monitor = None
_monitor_lock = threading.Lock()


def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _performance_monitor
    
    if _performance_monitor is None:
        with _monitor_lock:
            if _performance_monitor is None:
                _performance_monitor = PerformanceMonitor()
    
    return _performance_monitor


def default_alert_handler(alert: PerformanceAlert, report: Dict[str, Any]) -> None:
    """Default alert handler that logs to console."""
    print(f"🚨 PERFORMANCE ALERT: {alert.name} ({alert.severity})")
    print(f"   Message: {alert.message}")
    print(f"   Time: {datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == '__main__':
    # Example usage
    monitor = get_performance_monitor()
    
    # Add default alert handler
    monitor.add_alert_handler(default_alert_handler)
    
    # Test performance monitoring
    @performance_timer(monitor, 'test')
    def test_function():
        time.sleep(0.1)
        return "test result"
    
    # Run test
    result = test_function()
    print(f"Test result: {result}")
    
    # Get dashboard data
    dashboard = monitor.get_dashboard_data()
    print(f"Dashboard data: {json.dumps(dashboard, indent=2, default=str)}")
    
    # Keep running to see alerts
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        print("Performance monitoring stopped")