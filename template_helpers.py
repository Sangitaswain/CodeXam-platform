#!/usr/bin/env python3
"""
Template Helpers for CodeXam Platform

This module provides template helpers for asset optimization,
performance monitoring, and enhanced frontend functionality.

Version: 2.0.0
Author: CodeXam Development Team
"""

import json
import os
from pathlib import Path
from flask import current_app, url_for, request
from typing import Dict, List, Any, Optional
import hashlib
from datetime import datetime

class AssetManager:
    """Manages optimized assets and provides template helpers."""
    
    def __init__(self, app=None):
        self.app = app
        self.manifest = {}
        self.load_manifest()
        
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize with Flask app."""
        self.app = app
        
        # Register template functions
        app.jinja_env.globals['asset_url'] = self.asset_url
        app.jinja_env.globals['critical_css'] = self.get_critical_css
        app.jinja_env.globals['preload_assets'] = self.get_preload_assets
        app.jinja_env.globals['performance_script'] = self.get_performance_script
        app.jinja_env.globals['service_worker_script'] = self.get_service_worker_script
        app.jinja_env.globals['lazy_loading_script'] = self.get_lazy_loading_script
        app.jinja_env.globals['asset_preconnect'] = self.get_preconnect_links
        
        # Register template filters
        app.jinja_env.filters['optimize_image'] = self.optimize_image_tag
        app.jinja_env.filters['lazy_image'] = self.lazy_image_tag
    
    def load_manifest(self):
        """Load asset manifest for cache busting."""
        try:
            if self.app:
                static_dir = Path(self.app.static_folder)
                manifest_file = static_dir / 'optimized' / 'manifest.json'
                
                if manifest_file.exists():
                    self.manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
                else:
                    self.manifest = {}
        except Exception as e:
            if self.app:
                self.app.logger.warning(f"Failed to load asset manifest: {e}")
            self.manifest = {}
    
    def asset_url(self, filename: str, optimized: bool = True) -> str:
        """Get URL for asset with optimization and cache busting."""
        if not optimized or not self.manifest.get('assets'):
            return url_for('static', filename=filename)
        
        # Check if optimized version exists
        optimized_name = self.get_optimized_filename(filename)
        if optimized_name in self.manifest.get('assets', {}):
            asset_info = self.manifest['assets'][optimized_name]
            # Add hash for cache busting
            return f"/static/optimized/{optimized_name}?v={asset_info.get('hash', '')}"
        
        # Fallback to original
        return url_for('static', filename=filename)
    
    def get_optimized_filename(self, filename: str) -> str:
        """Get optimized filename for given asset."""
        name, ext = os.path.splitext(filename)
        
        if ext in ['.css', '.js']:
            return f"{name}.min{ext}"
        
        return filename
    
    def get_critical_css(self) -> str:
        """Get critical CSS content for inline inclusion."""
        try:
            if self.app:
                static_dir = Path(self.app.static_folder)
                critical_file = static_dir / 'optimized' / 'critical.css'
                
                if critical_file.exists():
                    return critical_file.read_text(encoding='utf-8')
        except Exception as e:
            if self.app:
                self.app.logger.warning(f"Failed to load critical CSS: {e}")
        
        return ""
    
    def get_preload_assets(self, assets: List[str]) -> str:
        """Generate preload links for critical assets."""
        preload_links = []
        
        for asset in assets:
            asset_url = self.asset_url(asset)
            
            if asset.endswith('.css'):
                preload_links.append(
                    f'<link rel="preload" href="{asset_url}" as="style" onload="this.onload=null;this.rel=\'stylesheet\'">'
                )
            elif asset.endswith('.js'):
                preload_links.append(
                    f'<link rel="preload" href="{asset_url}" as="script">'
                )
            elif asset.endswith(('.woff', '.woff2', '.ttf')):
                preload_links.append(
                    f'<link rel="preload" href="{asset_url}" as="font" type="font/{asset.split(".")[-1]}" crossorigin>'
                )
        
        return '\n'.join(preload_links)
    
    def get_performance_script(self) -> str:
        """Get performance monitoring script tag."""
        script_url = self.asset_url('performance.min.js')
        return f'<script src="{script_url}" defer></script>'
    
    def get_service_worker_script(self) -> str:
        """Get service worker registration script."""
        return '''
<script>
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/service-worker.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(err) {
                console.log('ServiceWorker registration failed: ', err);
            });
    });
}
</script>
'''
    
    def get_lazy_loading_script(self) -> str:
        """Get lazy loading script tag."""
        script_url = self.asset_url('lazy-loading.min.js')
        return f'<script src="{script_url}" defer></script>'
    
    def get_preconnect_links(self) -> str:
        """Get preconnect links for external resources."""
        preconnects = [
            '<link rel="preconnect" href="https://fonts.googleapis.com">',
            '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>',
            '<link rel="preconnect" href="https://cdn.jsdelivr.net">',
        ]
        return '\n'.join(preconnects)
    
    def optimize_image_tag(self, src: str, alt: str = "", **kwargs) -> str:
        """Generate optimized image tag with proper attributes."""
        # Extract image attributes
        width = kwargs.get('width', '')
        height = kwargs.get('height', '')
        loading = kwargs.get('loading', 'lazy')
        css_class = kwargs.get('class', '')
        
        # Build attributes
        attrs = []
        if width:
            attrs.append(f'width="{width}"')
        if height:
            attrs.append(f'height="{height}"')
        if loading:
            attrs.append(f'loading="{loading}"')
        if css_class:
            attrs.append(f'class="{css_class}"')
        
        attrs_str = ' '.join(attrs)
        
        # Use optimized image URL
        optimized_src = self.asset_url(src)
        
        return f'<img src="{optimized_src}" alt="{alt}" {attrs_str}>'
    
    def lazy_image_tag(self, src: str, alt: str = "", **kwargs) -> str:
        """Generate lazy-loaded image tag."""
        # Extract image attributes
        width = kwargs.get('width', '')
        height = kwargs.get('height', '')
        css_class = kwargs.get('class', '')
        
        # Build attributes
        attrs = []
        if width:
            attrs.append(f'width="{width}"')
        if height:
            attrs.append(f'height="{height}"')
        if css_class:
            attrs.append(f'class="{css_class} lazy-image"')
        else:
            attrs.append('class="lazy-image"')
        
        attrs_str = ' '.join(attrs)
        
        # Use data-src for lazy loading
        optimized_src = self.asset_url(src)
        placeholder = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1 1'%3E%3C/svg%3E"
        
        return f'<img src="{placeholder}" data-src="{optimized_src}" alt="{alt}" {attrs_str}>'

def create_performance_context():
    """Create performance context for templates."""
    return {
        'page_load_start': datetime.now().timestamp() * 1000,
        'request_path': request.path,
        'user_agent': request.headers.get('User-Agent', ''),
        'viewport_hint': get_viewport_hint(request.headers.get('User-Agent', ''))
    }

def get_viewport_hint(user_agent: str) -> Dict[str, Any]:
    """Get viewport hints based on user agent."""
    mobile_indicators = ['Mobile', 'Android', 'iPhone', 'iPad']
    is_mobile = any(indicator in user_agent for indicator in mobile_indicators)
    
    return {
        'is_mobile': is_mobile,
        'is_tablet': 'iPad' in user_agent or ('Android' in user_agent and 'Mobile' not in user_agent),
        'is_desktop': not is_mobile,
        'supports_webp': 'Chrome' in user_agent or 'Firefox' in user_agent,
        'supports_avif': 'Chrome/8' in user_agent  # Chrome 85+
    }

def generate_csp_header() -> str:
    """Generate Content Security Policy header."""
    csp_directives = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com",
        "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdn.jsdelivr.net",
        "font-src 'self' https://fonts.gstatic.com",
        "img-src 'self' data: https:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ]
    
    return '; '.join(csp_directives)

def inject_performance_headers(response):
    """Inject performance-related headers."""
    # Security headers
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    response.headers['Content-Security-Policy'] = generate_csp_header()
    
    # Performance headers
    response.headers['X-DNS-Prefetch-Control'] = 'on'
    
    # Cache headers for HTML
    if response.content_type and 'text/html' in response.content_type:
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
    
    return response

class PerformanceMiddleware:
    """Middleware for performance monitoring and optimization."""
    
    def __init__(self, app=None):
        self.app = app
        if app:
            self.init_app(app)
    
    def init_app(self, app):
        """Initialize middleware with Flask app."""
        self.app = app
        
        # Register before/after request handlers
        app.before_request(self.before_request)
        app.after_request(self.after_request)
        
        # Register template context processor
        app.context_processor(self.inject_performance_context)
    
    def before_request(self):
        """Handle before request processing."""
        # Store request start time
        request.start_time = datetime.now()
        
        # Add performance context to g
        from flask import g
        g.performance_context = create_performance_context()
    
    def after_request(self, response):
        """Handle after request processing."""
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = (datetime.now() - request.start_time).total_seconds()
            response.headers['X-Response-Time'] = f"{duration:.3f}s"
        
        # Inject performance headers
        response = inject_performance_headers(response)
        
        return response
    
    def inject_performance_context(self):
        """Inject performance context into templates."""
        from flask import g
        return {
            'performance_context': getattr(g, 'performance_context', {}),
            'asset_manager': AssetManager(self.app)
        }

# Template functions for manual registration
def register_template_helpers(app):
    """Register all template helpers with Flask app."""
    asset_manager = AssetManager(app)
    performance_middleware = PerformanceMiddleware(app)
    
    return {
        'asset_manager': asset_manager,
        'performance_middleware': performance_middleware
    }

# Utility functions for templates
def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

def format_duration(milliseconds: float) -> str:
    """Format duration in human readable format."""
    if milliseconds < 1000:
        return f"{milliseconds:.0f}ms"
    else:
        seconds = milliseconds / 1000
        return f"{seconds:.1f}s"

def get_performance_grade(metric_value: float, metric_type: str) -> str:
    """Get performance grade for metric."""
    thresholds = {
        'lcp': {'good': 2500, 'needs_improvement': 4000},
        'fid': {'good': 100, 'needs_improvement': 300},
        'cls': {'good': 0.1, 'needs_improvement': 0.25}
    }
    
    if metric_type not in thresholds:
        return 'unknown'
    
    threshold = thresholds[metric_type]
    
    if metric_value <= threshold['good']:
        return 'good'
    elif metric_value <= threshold['needs_improvement']:
        return 'needs_improvement'
    else:
        return 'poor'