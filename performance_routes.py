#!/usr/bin/env python3
"""
Performance Routes for CodeXam Platform

This module provides routes for handling performance metrics,
asset optimization, and frontend performance monitoring.

Version: 2.0.0
Author: CodeXam Development Team
"""

from flask import Blueprint, request, jsonify, current_app, send_from_directory, make_response
import json
import os
import gzip
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import sqlite3
from pathlib import Path

# Create blueprint
performance_bp = Blueprint('performance', __name__)

# Performance metrics storage
PERFORMANCE_DB = 'performance_metrics.db'

def init_performance_db():
    """Initialize performance metrics database."""
    conn = sqlite3.connect(PERFORMANCE_DB)
    conn.execute('''
        CREATE TABLE IF NOT EXISTS performance_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            timestamp INTEGER NOT NULL,
            navigation_timing TEXT,
            resource_timing TEXT,
            user_timing TEXT,
            core_web_vitals TEXT,
            user_agent TEXT,
            viewport_width INTEGER,
            viewport_height INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS asset_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            asset_path TEXT NOT NULL,
            request_time REAL NOT NULL,
            file_size INTEGER,
            compression_type TEXT,
            user_agent TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.execute('CREATE INDEX IF NOT EXISTS idx_perf_url ON performance_metrics(url)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_perf_timestamp ON performance_metrics(timestamp)')
    conn.execute('CREATE INDEX IF NOT EXISTS idx_asset_path ON asset_requests(asset_path)')
    
    conn.commit()
    conn.close()

# Initialize database on import
init_performance_db()

@performance_bp.route('/api/performance-metrics', methods=['POST'])
def collect_performance_metrics():
    """Collect performance metrics from frontend."""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Extract metrics
        url = data.get('url', '')
        timestamp = data.get('timestamp', 0)
        metrics = data.get('metrics', {})
        user_agent = data.get('userAgent', '')
        viewport = data.get('viewport', {})
        
        # Store in database
        conn = sqlite3.connect(PERFORMANCE_DB)
        conn.execute('''
            INSERT INTO performance_metrics 
            (url, timestamp, navigation_timing, resource_timing, user_timing, 
             core_web_vitals, user_agent, viewport_width, viewport_height)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            url,
            timestamp,
            json.dumps(metrics.get('navigation', {})),
            json.dumps(metrics.get('resources', {})),
            json.dumps({k: v for k, v in metrics.items() if k.endswith('-time')}),
            json.dumps({
                'lcp': metrics.get('lcp'),
                'fid': metrics.get('fid'),
                'cls': metrics.get('cls')
            }),
            user_agent,
            viewport.get('width'),
            viewport.get('height')
        ))
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to collect performance metrics: {e}")
        return jsonify({'error': 'Failed to store metrics'}), 500

@performance_bp.route('/api/performance-dashboard')
def performance_dashboard():
    """Get performance dashboard data."""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        conn.row_factory = sqlite3.Row
        
        # Get recent metrics (last 24 hours)
        cutoff_time = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        
        cursor = conn.execute('''
            SELECT * FROM performance_metrics 
            WHERE timestamp > ? 
            ORDER BY timestamp DESC 
            LIMIT 100
        ''', (cutoff_time,))
        
        metrics = []
        for row in cursor.fetchall():
            metrics.append({
                'url': row['url'],
                'timestamp': row['timestamp'],
                'navigation': json.loads(row['navigation_timing'] or '{}'),
                'resources': json.loads(row['resource_timing'] or '{}'),
                'user_timing': json.loads(row['user_timing'] or '{}'),
                'core_web_vitals': json.loads(row['core_web_vitals'] or '{}'),
                'viewport': {
                    'width': row['viewport_width'],
                    'height': row['viewport_height']
                }
            })
        
        # Calculate aggregated metrics
        if metrics:
            avg_lcp = sum(m['core_web_vitals'].get('lcp', 0) for m in metrics if m['core_web_vitals'].get('lcp')) / len(metrics)
            avg_fid = sum(m['core_web_vitals'].get('fid', 0) for m in metrics if m['core_web_vitals'].get('fid')) / len(metrics)
            avg_cls = sum(m['core_web_vitals'].get('cls', 0) for m in metrics if m['core_web_vitals'].get('cls')) / len(metrics)
            
            avg_dom_load = sum(m['navigation'].get('domContentLoaded', 0) for m in metrics if m['navigation'].get('domContentLoaded')) / len(metrics)
            avg_page_load = sum(m['navigation'].get('loadComplete', 0) for m in metrics if m['navigation'].get('loadComplete')) / len(metrics)
        else:
            avg_lcp = avg_fid = avg_cls = avg_dom_load = avg_page_load = 0
        
        # Get asset performance
        cursor = conn.execute('''
            SELECT asset_path, AVG(request_time) as avg_time, COUNT(*) as requests,
                   AVG(file_size) as avg_size, compression_type
            FROM asset_requests 
            WHERE created_at > datetime('now', '-24 hours')
            GROUP BY asset_path, compression_type
            ORDER BY requests DESC
            LIMIT 20
        ''')
        
        asset_performance = []
        for row in cursor.fetchall():
            asset_performance.append({
                'path': row['asset_path'],
                'avg_time': round(row['avg_time'], 2),
                'requests': row['requests'],
                'avg_size': int(row['avg_size'] or 0),
                'compression': row['compression_type']
            })
        
        conn.close()
        
        return jsonify({
            'summary': {
                'total_metrics': len(metrics),
                'avg_lcp': round(avg_lcp, 2),
                'avg_fid': round(avg_fid, 2),
                'avg_cls': round(avg_cls, 4),
                'avg_dom_load': round(avg_dom_load, 2),
                'avg_page_load': round(avg_page_load, 2)
            },
            'recent_metrics': metrics[-10:],  # Last 10 metrics
            'asset_performance': asset_performance
        }), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get performance dashboard: {e}")
        return jsonify({'error': 'Failed to get dashboard data'}), 500

@performance_bp.route('/static/optimized/<path:filename>')
def serve_optimized_asset(filename):
    """Serve optimized static assets with proper headers."""
    try:
        static_dir = Path(current_app.static_folder)
        optimized_dir = static_dir / 'optimized'
        
        # Check if gzipped version exists and client accepts gzip
        accepts_gzip = 'gzip' in request.headers.get('Accept-Encoding', '')
        gzipped_file = optimized_dir / f"{filename}.gz"
        regular_file = optimized_dir / filename
        
        start_time = datetime.now()
        
        if accepts_gzip and gzipped_file.exists():
            # Serve gzipped version
            response = make_response(send_from_directory(optimized_dir, f"{filename}.gz"))
            response.headers['Content-Encoding'] = 'gzip'
            response.headers['Content-Type'] = get_content_type(filename)
            file_size = gzipped_file.stat().st_size
            compression_type = 'gzip'
        elif regular_file.exists():
            # Serve regular version
            response = make_response(send_from_directory(optimized_dir, filename))
            response.headers['Content-Type'] = get_content_type(filename)
            file_size = regular_file.stat().st_size
            compression_type = 'none'
        else:
            return "File not found", 404
        
        # Set cache headers for static assets
        if filename.endswith(('.css', '.js', '.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico')):
            # Cache for 1 year for versioned assets
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            response.headers['Expires'] = (datetime.now() + timedelta(days=365)).strftime('%a, %d %b %Y %H:%M:%S GMT')
        else:
            # Cache for 1 hour for other assets
            response.headers['Cache-Control'] = 'public, max-age=3600'
        
        # Add performance headers
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        
        # Log asset request for performance monitoring
        request_time = (datetime.now() - start_time).total_seconds()
        log_asset_request(filename, request_time, file_size, compression_type)
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Failed to serve optimized asset {filename}: {e}")
        return "Internal server error", 500

def get_content_type(filename: str) -> str:
    """Get content type based on file extension."""
    ext = filename.lower().split('.')[-1]
    content_types = {
        'css': 'text/css',
        'js': 'application/javascript',
        'png': 'image/png',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'gif': 'image/gif',
        'svg': 'image/svg+xml',
        'ico': 'image/x-icon',
        'woff': 'font/woff',
        'woff2': 'font/woff2',
        'ttf': 'font/ttf',
        'eot': 'application/vnd.ms-fontobject'
    }
    return content_types.get(ext, 'application/octet-stream')

def log_asset_request(asset_path: str, request_time: float, file_size: int, compression_type: str):
    """Log asset request for performance monitoring."""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        conn.execute('''
            INSERT INTO asset_requests 
            (asset_path, request_time, file_size, compression_type, user_agent)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            asset_path,
            request_time,
            file_size,
            compression_type,
            request.headers.get('User-Agent', '')
        ))
        conn.commit()
        conn.close()
    except Exception as e:
        current_app.logger.error(f"Failed to log asset request: {e}")

@performance_bp.route('/service-worker.js')
def serve_service_worker():
    """Serve service worker with proper headers."""
    try:
        static_dir = Path(current_app.static_folder)
        sw_file = static_dir / 'optimized' / 'service-worker.js'
        
        if not sw_file.exists():
            return "Service worker not found", 404
        
        response = make_response(send_from_directory(static_dir / 'optimized', 'service-worker.js'))
        response.headers['Content-Type'] = 'application/javascript'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Service-Worker-Allowed'] = '/'
        
        return response
        
    except Exception as e:
        current_app.logger.error(f"Failed to serve service worker: {e}")
        return "Internal server error", 500

@performance_bp.route('/api/asset-manifest')
def get_asset_manifest():
    """Get asset manifest for cache busting."""
    try:
        static_dir = Path(current_app.static_folder)
        manifest_file = static_dir / 'optimized' / 'manifest.json'
        
        if not manifest_file.exists():
            return jsonify({'error': 'Manifest not found'}), 404
        
        manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
        return jsonify(manifest), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to get asset manifest: {e}")
        return jsonify({'error': 'Failed to get manifest'}), 500

@performance_bp.route('/api/performance-report')
def get_performance_report():
    """Get comprehensive performance report."""
    try:
        conn = sqlite3.connect(PERFORMANCE_DB)
        conn.row_factory = sqlite3.Row
        
        # Get metrics from last 7 days
        cutoff_time = int((datetime.now() - timedelta(days=7)).timestamp() * 1000)
        
        # Core Web Vitals analysis
        cursor = conn.execute('''
            SELECT core_web_vitals, url FROM performance_metrics 
            WHERE timestamp > ? AND core_web_vitals != '{}'
        ''', (cutoff_time,))
        
        lcp_values = []
        fid_values = []
        cls_values = []
        url_performance = {}
        
        for row in cursor.fetchall():
            vitals = json.loads(row['core_web_vitals'])
            url = row['url']
            
            if vitals.get('lcp'):
                lcp_values.append(vitals['lcp'])
            if vitals.get('fid'):
                fid_values.append(vitals['fid'])
            if vitals.get('cls'):
                cls_values.append(vitals['cls'])
            
            if url not in url_performance:
                url_performance[url] = {'lcp': [], 'fid': [], 'cls': []}
            
            if vitals.get('lcp'):
                url_performance[url]['lcp'].append(vitals['lcp'])
            if vitals.get('fid'):
                url_performance[url]['fid'].append(vitals['fid'])
            if vitals.get('cls'):
                url_performance[url]['cls'].append(vitals['cls'])
        
        # Calculate percentiles
        def percentile(data, p):
            if not data:
                return 0
            sorted_data = sorted(data)
            index = int(len(sorted_data) * p / 100)
            return sorted_data[min(index, len(sorted_data) - 1)]
        
        # Asset performance analysis
        cursor = conn.execute('''
            SELECT asset_path, AVG(request_time) as avg_time, 
                   COUNT(*) as requests, AVG(file_size) as avg_size
            FROM asset_requests 
            WHERE created_at > datetime('now', '-7 days')
            GROUP BY asset_path
            ORDER BY avg_time DESC
        ''')
        
        slow_assets = []
        for row in cursor.fetchall():
            if row['avg_time'] > 0.1:  # Assets taking more than 100ms
                slow_assets.append({
                    'path': row['asset_path'],
                    'avg_time': round(row['avg_time'], 3),
                    'requests': row['requests'],
                    'avg_size': int(row['avg_size'] or 0)
                })
        
        conn.close()
        
        report = {
            'core_web_vitals': {
                'lcp': {
                    'p50': percentile(lcp_values, 50),
                    'p75': percentile(lcp_values, 75),
                    'p95': percentile(lcp_values, 95),
                    'samples': len(lcp_values)
                },
                'fid': {
                    'p50': percentile(fid_values, 50),
                    'p75': percentile(fid_values, 75),
                    'p95': percentile(fid_values, 95),
                    'samples': len(fid_values)
                },
                'cls': {
                    'p50': percentile(cls_values, 50),
                    'p75': percentile(cls_values, 75),
                    'p95': percentile(cls_values, 95),
                    'samples': len(cls_values)
                }
            },
            'url_performance': {
                url: {
                    'lcp_avg': sum(data['lcp']) / len(data['lcp']) if data['lcp'] else 0,
                    'fid_avg': sum(data['fid']) / len(data['fid']) if data['fid'] else 0,
                    'cls_avg': sum(data['cls']) / len(data['cls']) if data['cls'] else 0,
                    'samples': max(len(data['lcp']), len(data['fid']), len(data['cls']))
                }
                for url, data in url_performance.items()
            },
            'slow_assets': slow_assets[:10],  # Top 10 slowest assets
            'recommendations': generate_performance_recommendations(lcp_values, fid_values, cls_values, slow_assets)
        }
        
        return jsonify(report), 200
        
    except Exception as e:
        current_app.logger.error(f"Failed to generate performance report: {e}")
        return jsonify({'error': 'Failed to generate report'}), 500

def generate_performance_recommendations(lcp_values, fid_values, cls_values, slow_assets):
    """Generate performance optimization recommendations."""
    recommendations = []
    
    # LCP recommendations
    if lcp_values:
        avg_lcp = sum(lcp_values) / len(lcp_values)
        if avg_lcp > 2500:  # Poor LCP
            recommendations.append({
                'type': 'lcp',
                'severity': 'high',
                'message': f'Largest Contentful Paint is slow ({avg_lcp:.0f}ms). Consider optimizing images and critical resources.',
                'suggestions': [
                    'Optimize and compress images',
                    'Use next-gen image formats (WebP, AVIF)',
                    'Implement lazy loading for below-the-fold images',
                    'Optimize critical CSS delivery'
                ]
            })
        elif avg_lcp > 1500:  # Needs improvement
            recommendations.append({
                'type': 'lcp',
                'severity': 'medium',
                'message': f'Largest Contentful Paint could be improved ({avg_lcp:.0f}ms).',
                'suggestions': [
                    'Further optimize critical resources',
                    'Consider using a CDN',
                    'Optimize server response times'
                ]
            })
    
    # FID recommendations
    if fid_values:
        avg_fid = sum(fid_values) / len(fid_values)
        if avg_fid > 100:  # Poor FID
            recommendations.append({
                'type': 'fid',
                'severity': 'high',
                'message': f'First Input Delay is high ({avg_fid:.0f}ms). Consider reducing JavaScript execution time.',
                'suggestions': [
                    'Split large JavaScript bundles',
                    'Remove unused JavaScript',
                    'Use web workers for heavy computations',
                    'Optimize third-party scripts'
                ]
            })
    
    # CLS recommendations
    if cls_values:
        avg_cls = sum(cls_values) / len(cls_values)
        if avg_cls > 0.1:  # Poor CLS
            recommendations.append({
                'type': 'cls',
                'severity': 'high',
                'message': f'Cumulative Layout Shift is high ({avg_cls:.3f}). Consider stabilizing layout.',
                'suggestions': [
                    'Set explicit dimensions for images and videos',
                    'Reserve space for dynamic content',
                    'Avoid inserting content above existing content',
                    'Use CSS transforms for animations'
                ]
            })
    
    # Asset recommendations
    if slow_assets:
        recommendations.append({
            'type': 'assets',
            'severity': 'medium',
            'message': f'Found {len(slow_assets)} slow-loading assets.',
            'suggestions': [
                'Enable gzip compression for all text assets',
                'Implement proper caching headers',
                'Consider using a CDN',
                'Optimize asset delivery order'
            ]
        })
    
    return recommendations

# Register error handlers
@performance_bp.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

@performance_bp.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500