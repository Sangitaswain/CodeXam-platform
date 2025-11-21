#!/usr/bin/env python3
"""
Asset Helper Functions for CodeXam Platform

This module provides Flask integration for optimized asset serving,
including cache busting, lazy loading, and performance monitoring.

Version: 2.0.0
Author: CodeXam Development Team
"""

import os
import json
import gzip
from pathlib import Path
from typing import Dict, List, Any, Optional
from flask import Flask, request, send_file, make_response, url_for
from functools import wraps
import time
import logging

logger = logging.getLogger(__name__)


class AssetHelper:
    """Helper class for serving optimized assets in Flask."""
    
    def __init__(self, app: Flask = None, static_dir: str = 'static', 
                 optimized_dir: str = 'static/optimized'):
        self.app = app
        self.static_dir = Path(static_dir)
        self.optimized_dir = Path(optimized_dir)
        self.asset_registry = {}
        self.registry_file = self.optimized_dir / 'asset_registry.json'
        
        # Load asset registry
        self._load_registry()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app: Flask):
        """Initialize the asset helper with Flask app."""
        self.app = app
        
        # Register template functions
        app.jinja_env.globals['asset_url'] = self.asset_url
        app.jinja_env.globals['bundle_url'] = self.bundle_url
        app.jinja_env.globals['inline_css'] = self.inline_css
        app.jinja_env.globals['inline_js'] = self.inline_js
        
        # Register routes
        self._register_routes()
        
        # Add response headers for caching
        app.after_request(self._add_cache_headers)
    
    def _load_registry(self):
        """Load the asset registry."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    self.asset_registry = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load asset registry: {e}")
                self.asset_registry = {}
    
    def _register_routes(self):
        """Register asset serving routes."""
        
        @self.app.route('/static/optimized/<path:filename>')
        def serve_optimized_asset(filename):
            """Serve optimized assets with proper headers."""
            file_path = self.optimized_dir / filename
            
            if not file_path.exists():
                # Fallback to original file
                original_path = self.static_dir / filename
                if original_path.exists():
                    return send_file(str(original_path))
                else:
                    return "Asset not found", 404
            
            # Check if gzipped version exists and client accepts it
            gzip_path = Path(str(file_path) + '.gz')
            if (gzip_path.exists() and 
                'gzip' in request.headers.get('Accept-Encoding', '')):
                
                response = make_response(send_file(str(gzip_path)))
                response.headers['Content-Encoding'] = 'gzip'
                response.headers['Vary'] = 'Accept-Encoding'
                return response
            
            return send_file(str(file_path))
        
        @self.app.route('/api/assets/registry')
        def asset_registry_api():
            """API endpoint for asset registry."""
            return self.asset_registry
        
        @self.app.route('/api/assets/performance')
        def asset_performance_api():
            """API endpoint for asset performance metrics."""
            return self._get_performance_metrics()
    
    def _add_cache_headers(self, response):
        """Add appropriate cache headers to responses."""
        if request.endpoint == 'serve_optimized_asset':
            # Long cache for optimized assets (1 year)
            response.headers['Cache-Control'] = 'public, max-age=31536000, immutable'
            response.headers['Expires'] = time.strftime(
                '%a, %d %b %Y %H:%M:%S GMT', 
                time.gmtime(time.time() + 31536000)
            )
        elif request.path.startswith('/static/'):
            # Shorter cache for regular static files (1 hour)
            response.headers['Cache-Control'] = 'public, max-age=3600'
        
        return response
    
    def asset_url(self, asset_path: str, use_optimized: bool = True, 
                  use_hash: bool = True) -> str:
        """Generate URL for an asset with optional optimization and cache busting."""
        if use_optimized and asset_path in self.asset_registry:
            asset_info = self.asset_registry[asset_path]
            optimized_path = asset_info['optimized_path']
            
            if use_hash and 'hash' in asset_info:
                # Add hash for cache busting
                base_path, ext = os.path.splitext(optimized_path)
                versioned_path = f"{base_path}.{asset_info['hash']}{ext}"
                return url_for('static', filename=versioned_path.replace('static/', ''))
            else:
                return url_for('static', filename=optimized_path.replace('static/', ''))
        
        # Fallback to original asset
        return url_for('static', filename=asset_path)
    
    def bundle_url(self, bundle_name: str, use_hash: bool = True) -> str:
        """Generate URL for an asset bundle."""
        if bundle_name in self.asset_registry:
            asset_info = self.asset_registry[bundle_name]
            
            if use_hash and 'hash' in asset_info:
                base_path, ext = os.path.splitext(bundle_name)
                versioned_name = f"{base_path}.{asset_info['hash']}{ext}"
                return url_for('serve_optimized_asset', filename=versioned_name)
            else:
                return url_for('serve_optimized_asset', filename=bundle_name)
        
        return url_for('static', filename=bundle_name)
    
    def inline_css(self, css_path: str, use_optimized: bool = True) -> str:
        """Inline CSS content for critical styles."""
        try:
            if use_optimized and css_path in self.asset_registry:
                asset_info = self.asset_registry[css_path]
                file_path = self.optimized_dir / asset_info['optimized_path'].replace('optimized/', '')
            else:
                file_path = self.static_dir / css_path
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f'<style>{content}</style>'
            
        except Exception as e:
            logger.error(f"Failed to inline CSS {css_path}: {e}")
        
        # Fallback to link tag
        return f'<link rel="stylesheet" href="{self.asset_url(css_path, use_optimized)}">'
    
    def inline_js(self, js_path: str, use_optimized: bool = True) -> str:
        """Inline JavaScript content for critical scripts."""
        try:
            if use_optimized and js_path in self.asset_registry:
                asset_info = self.asset_registry[js_path]
                file_path = self.optimized_dir / asset_info['optimized_path'].replace('optimized/', '')
            else:
                file_path = self.static_dir / js_path
            
            if file_path.exists():
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                return f'<script>{content}</script>'
            
        except Exception as e:
            logger.error(f"Failed to inline JS {js_path}: {e}")
        
        # Fallback to script tag
        return f'<script src="{self.asset_url(js_path, use_optimized)}"></script>'
    
    def _get_performance_metrics(self) -> Dict[str, Any]:
        """Get asset performance metrics."""
        total_original_size = 0
        total_optimized_size = 0
        total_gzip_size = 0
        
        for asset_path, asset_info in self.asset_registry.items():
            if 'size' in asset_info:
                total_optimized_size += asset_info['size']
            if 'gzip_size' in asset_info:
                total_gzip_size += asset_info['gzip_size']
        
        # Calculate estimated original size based on compression ratios
        for asset_path, asset_info in self.asset_registry.items():
            if 'compression_ratio' in asset_info and 'size' in asset_info:
                original_size = asset_info['size'] / (1 - asset_info['compression_ratio'] / 100)
                total_original_size += original_size
        
        return {
            'total_assets': len(self.asset_registry),
            'total_original_size': int(total_original_size),
            'total_optimized_size': total_optimized_size,
            'total_gzip_size': total_gzip_size,
            'optimization_ratio': round((total_original_size - total_optimized_size) / total_original_size * 100, 2) if total_original_size > 0 else 0,
            'gzip_ratio': round((total_optimized_size - total_gzip_size) / total_optimized_size * 100, 2) if total_optimized_size > 0 else 0,
            'assets': self.asset_registry
        }


def lazy_load_decorator(threshold: int = 2):
    """Decorator to implement lazy loading for routes."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Add lazy loading attributes to response
            response = func(*args, **kwargs)
            
            if hasattr(response, 'data'):
                # Inject lazy loading script
                lazy_script = f'''
                <script>
                document.addEventListener('DOMContentLoaded', function() {{
                    const images = document.querySelectorAll('img[data-src]');
                    const imageObserver = new IntersectionObserver((entries, observer) => {{
                        entries.forEach(entry => {{
                            if (entry.isIntersecting) {{
                                const img = entry.target;
                                img.src = img.dataset.src;
                                img.classList.remove('lazy');
                                imageObserver.unobserve(img);
                            }}
                        }});
                    }}, {{
                        rootMargin: '50px 0px',
                        threshold: 0.01
                    }});
                    
                    images.forEach(img => imageObserver.observe(img));
                }});
                </script>
                '''
                
                if isinstance(response.data, bytes):
                    response.data = response.data.decode('utf-8')
                
                if '</body>' in response.data:
                    response.data = response.data.replace('</body>', f'{lazy_script}</body>')
                
                if isinstance(response.data, str):
                    response.data = response.data.encode('utf-8')
            
            return response
        return wrapper
    return decorator


class PerformanceMonitor:
    """Monitor frontend performance metrics."""
    
    def __init__(self):
        self.metrics = []
        self.page_load_times = {}
    
    def record_page_load(self, page: str, load_time: float):
        """Record page load time."""
        if page not in self.page_load_times:
            self.page_load_times[page] = []
        
        self.page_load_times[page].append({
            'load_time': load_time,
            'timestamp': time.time()
        })
        
        # Keep only last 100 measurements per page
        if len(self.page_load_times[page]) > 100:
            self.page_load_times[page] = self.page_load_times[page][-100:]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary."""
        summary = {}
        
        for page, measurements in self.page_load_times.items():
            if measurements:
                load_times = [m['load_time'] for m in measurements]
                summary[page] = {
                    'avg_load_time': sum(load_times) / len(load_times),
                    'min_load_time': min(load_times),
                    'max_load_time': max(load_times),
                    'measurements_count': len(measurements),
                    'last_measurement': measurements[-1]['timestamp']
                }
        
        return summary


def create_performance_middleware(app: Flask):
    """Create performance monitoring middleware."""
    monitor = PerformanceMonitor()
    
    @app.before_request
    def before_request():
        request.start_time = time.time()
    
    @app.after_request
    def after_request(response):
        if hasattr(request, 'start_time'):
            load_time = time.time() - request.start_time
            monitor.record_page_load(request.endpoint or 'unknown', load_time)
            
            # Add performance headers
            response.headers['X-Response-Time'] = f"{load_time:.3f}s"
        
        return response
    
    @app.route('/api/performance/summary')
    def performance_summary():
        return monitor.get_performance_summary()
    
    return monitor


def optimize_images_lazy_loading():
    """Generate lazy loading HTML for images."""
    return '''
    <script>
    // Lazy loading implementation
    document.addEventListener('DOMContentLoaded', function() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const image = entry.target;
                        image.src = image.dataset.src;
                        image.classList.remove('lazy');
                        image.classList.add('loaded');
                        imageObserver.unobserve(image);
                    }
                });
            }, {
                rootMargin: '50px 0px',
                threshold: 0.01
            });
            
            lazyImages.forEach(image => {
                imageObserver.observe(image);
            });
        } else {
            // Fallback for older browsers
            lazyImages.forEach(image => {
                image.src = image.dataset.src;
                image.classList.remove('lazy');
                image.classList.add('loaded');
            });
        }
    });
    </script>
    
    <style>
    img.lazy {
        opacity: 0;
        transition: opacity 0.3s;
    }
    
    img.loaded {
        opacity: 1;
    }
    
    img.lazy::before {
        content: '';
        display: block;
        width: 100%;
        height: 200px;
        background: #f0f0f0;
        background-image: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
        background-size: 200% 100%;
        animation: loading 1.5s infinite;
    }
    
    @keyframes loading {
        0% { background-position: 200% 0; }
        100% { background-position: -200% 0; }
    }
    </style>
    '''


if __name__ == '__main__':
    # Example usage
    from flask import Flask, render_template_string
    
    app = Flask(__name__)
    asset_helper = AssetHelper(app)
    performance_monitor = create_performance_middleware(app)
    
    @app.route('/')
    def index():
        return render_template_string('''
        <!DOCTYPE html>
        <html>
        <head>
            <title>Asset Optimization Demo</title>
            {{ inline_css('css/style.css') }}
        </head>
        <body>
            <h1>Asset Optimization Demo</h1>
            <p>This page demonstrates optimized asset loading.</p>
            
            <!-- Lazy loaded image -->
            <img class="lazy" data-src="{{ asset_url('img/demo.jpg') }}" alt="Demo Image">
            
            <!-- Optimized JavaScript bundle -->
            <script src="{{ bundle_url('core.js') }}"></script>
            
            {{ optimize_images_lazy_loading() | safe }}
        </body>
        </html>
        ''')
    
    if __name__ == '__main__':
        app.run(debug=True)