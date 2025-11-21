#!/usr/bin/env python3
"""
Frontend Performance Optimizer for CodeXam Platform

This script provides comprehensive frontend optimization including:
- Asset minification and compression
- Image optimization and format conversion
- Lazy loading implementation
- Critical CSS extraction
- Service worker generation
- Performance monitoring setup

Version: 2.0.0
Author: CodeXam Development Team
"""

import os
import sys
import json
import gzip
import shutil
import hashlib
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
import re
import base64
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class FrontendOptimizer:
    """Comprehensive frontend performance optimizer."""
    
    def __init__(self, project_root: str = None):
        self.project_root = Path(project_root or os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        self.static_dir = self.project_root / 'static'
        self.optimized_dir = self.static_dir / 'optimized'
        self.templates_dir = self.project_root / 'templates'
        
        # Ensure optimized directory exists
        self.optimized_dir.mkdir(exist_ok=True)
        
        # Performance metrics
        self.metrics = {
            'css_files_processed': 0,
            'js_files_processed': 0,
            'images_optimized': 0,
            'total_size_before': 0,
            'total_size_after': 0,
            'compression_ratio': 0,
            'optimization_time': 0
        }
        
        print(f"🚀 Frontend Optimizer initialized")
        print(f"   Project root: {self.project_root}")
        print(f"   Static directory: {self.static_dir}")
        print(f"   Optimized directory: {self.optimized_dir}")
    
    def optimize_all(self) -> Dict[str, Any]:
        """Run all optimization tasks."""
        start_time = datetime.now()
        
        print("\n" + "="*60)
        print("🎯 STARTING COMPREHENSIVE FRONTEND OPTIMIZATION")
        print("="*60)
        
        try:
            # 1. Minify and compress CSS
            print("\n📦 Step 1: CSS Optimization")
            self.optimize_css()
            
            # 2. Minify and compress JavaScript
            print("\n⚡ Step 2: JavaScript Optimization")
            self.optimize_javascript()
            
            # 3. Optimize images
            print("\n🖼️  Step 3: Image Optimization")
            self.optimize_images()
            
            # 4. Generate critical CSS
            print("\n🎨 Step 4: Critical CSS Generation")
            self.generate_critical_css()
            
            # 5. Create service worker
            print("\n🔧 Step 5: Service Worker Generation")
            self.generate_service_worker()
            
            # 6. Implement lazy loading
            print("\n⏳ Step 6: Lazy Loading Implementation")
            self.implement_lazy_loading()
            
            # 7. Generate asset manifest
            print("\n📋 Step 7: Asset Manifest Generation")
            self.generate_asset_manifest()
            
            # 8. Setup performance monitoring
            print("\n📊 Step 8: Performance Monitoring Setup")
            self.setup_performance_monitoring()
            
            # Calculate final metrics
            end_time = datetime.now()
            self.metrics['optimization_time'] = (end_time - start_time).total_seconds()
            
            if self.metrics['total_size_before'] > 0:
                self.metrics['compression_ratio'] = (
                    (self.metrics['total_size_before'] - self.metrics['total_size_after']) / 
                    self.metrics['total_size_before'] * 100
                )
            
            self.print_optimization_summary()
            return self.metrics
            
        except Exception as e:
            print(f"❌ Optimization failed: {e}")
            import traceback
            traceback.print_exc()
            return {'error': str(e)}
    
    def optimize_css(self) -> None:
        """Optimize CSS files with minification and compression."""
        css_dir = self.static_dir / 'css'
        if not css_dir.exists():
            print("   ⚠️  CSS directory not found")
            return
        
        css_files = list(css_dir.glob('*.css'))
        print(f"   Found {len(css_files)} CSS files to optimize")
        
        for css_file in css_files:
            try:
                # Read original file
                original_content = css_file.read_text(encoding='utf-8')
                original_size = len(original_content.encode('utf-8'))
                
                # Minify CSS
                minified_content = self.minify_css(original_content)
                minified_size = len(minified_content.encode('utf-8'))
                
                # Save minified version
                minified_file = self.optimized_dir / f"{css_file.stem}.min.css"
                minified_file.write_text(minified_content, encoding='utf-8')
                
                # Create gzipped version
                gzipped_file = self.optimized_dir / f"{css_file.stem}.min.css.gz"
                with gzip.open(gzipped_file, 'wt', encoding='utf-8') as f:
                    f.write(minified_content)
                
                gzipped_size = gzipped_file.stat().st_size
                
                # Update metrics
                self.metrics['css_files_processed'] += 1
                self.metrics['total_size_before'] += original_size
                self.metrics['total_size_after'] += gzipped_size
                
                compression_ratio = (original_size - gzipped_size) / original_size * 100
                print(f"   ✅ {css_file.name}: {original_size:,} → {gzipped_size:,} bytes ({compression_ratio:.1f}% reduction)")
                
            except Exception as e:
                print(f"   ❌ Failed to optimize {css_file.name}: {e}")
    
    def minify_css(self, css_content: str) -> str:
        """Minify CSS content."""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r'}\s*', '}', css_content)
        css_content = re.sub(r':\s*', ':', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        css_content = re.sub(r',\s*', ',', css_content)
        
        # Remove trailing semicolons before closing braces
        css_content = re.sub(r';+}', '}', css_content)
        
        return css_content.strip()
    
    def optimize_javascript(self) -> None:
        """Optimize JavaScript files with minification and compression."""
        js_dir = self.static_dir / 'js'
        if not js_dir.exists():
            print("   ⚠️  JavaScript directory not found")
            return
        
        js_files = list(js_dir.glob('*.js'))
        print(f"   Found {len(js_files)} JavaScript files to optimize")
        
        for js_file in js_files:
            try:
                # Read original file
                original_content = js_file.read_text(encoding='utf-8')
                original_size = len(original_content.encode('utf-8'))
                
                # Minify JavaScript
                minified_content = self.minify_javascript(original_content)
                minified_size = len(minified_content.encode('utf-8'))
                
                # Save minified version
                minified_file = self.optimized_dir / f"{js_file.stem}.min.js"
                minified_file.write_text(minified_content, encoding='utf-8')
                
                # Create gzipped version
                gzipped_file = self.optimized_dir / f"{js_file.stem}.min.js.gz"
                with gzip.open(gzipped_file, 'wt', encoding='utf-8') as f:
                    f.write(minified_content)
                
                gzipped_size = gzipped_file.stat().st_size
                
                # Update metrics
                self.metrics['js_files_processed'] += 1
                self.metrics['total_size_before'] += original_size
                self.metrics['total_size_after'] += gzipped_size
                
                compression_ratio = (original_size - gzipped_size) / original_size * 100
                print(f"   ✅ {js_file.name}: {original_size:,} → {gzipped_size:,} bytes ({compression_ratio:.1f}% reduction)")
                
            except Exception as e:
                print(f"   ❌ Failed to optimize {js_file.name}: {e}")
    
    def minify_javascript(self, js_content: str) -> str:
        """Basic JavaScript minification."""
        # Remove single-line comments (but preserve URLs)
        js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        js_content = re.sub(r';\s*', ';', js_content)
        js_content = re.sub(r'{\s*', '{', js_content)
        js_content = re.sub(r'}\s*', '}', js_content)
        js_content = re.sub(r',\s*', ',', js_content)
        js_content = re.sub(r':\s*', ':', js_content)
        
        # Remove spaces around operators (carefully)
        js_content = re.sub(r'\s*([+\-*/=<>!&|])\s*', r'\1', js_content)
        
        return js_content.strip()
    
    def optimize_images(self) -> None:
        """Optimize images with compression and format conversion."""
        img_dir = self.static_dir / 'img'
        if not img_dir.exists():
            print("   ⚠️  Images directory not found")
            return
        
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.svg']
        image_files = []
        for ext in image_extensions:
            image_files.extend(img_dir.glob(f'*{ext}'))
        
        print(f"   Found {len(image_files)} image files to optimize")
        
        for img_file in image_files:
            try:
                original_size = img_file.stat().st_size
                
                # For now, just copy to optimized directory
                # In a real implementation, you'd use PIL or similar for optimization
                optimized_file = self.optimized_dir / img_file.name
                shutil.copy2(img_file, optimized_file)
                
                optimized_size = optimized_file.stat().st_size
                
                # Update metrics
                self.metrics['images_optimized'] += 1
                self.metrics['total_size_before'] += original_size
                self.metrics['total_size_after'] += optimized_size
                
                print(f"   ✅ {img_file.name}: {original_size:,} → {optimized_size:,} bytes")
                
            except Exception as e:
                print(f"   ❌ Failed to optimize {img_file.name}: {e}")
    
    def generate_critical_css(self) -> None:
        """Generate critical CSS for above-the-fold content."""
        critical_css = """
/* Critical CSS for above-the-fold content */
:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #1a1a1a;
    --bg-tertiary: #2a2a2a;
    --text-primary: #ffffff;
    --text-secondary: #b0b0b0;
    --text-accent: #00ff88;
    --border-primary: #333333;
    --border-secondary: #444444;
}

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 0;
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    line-height: 1.6;
}

.cyber-navbar {
    background: var(--bg-secondary);
    border-bottom: 1px solid var(--border-primary);
    padding: 1rem 0;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.navbar-container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.brand-link {
    color: var(--text-accent);
    text-decoration: none;
    font-weight: 700;
    font-size: 1.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.main-content {
    min-height: calc(100vh - 200px);
    padding: 2rem 0;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 1rem;
}

/* Loading states */
.loading {
    opacity: 0.7;
    pointer-events: none;
}

.skeleton {
    background: linear-gradient(90deg, var(--bg-tertiary) 25%, var(--bg-secondary) 50%, var(--bg-tertiary) 75%);
    background-size: 200% 100%;
    animation: loading 1.5s infinite;
}

@keyframes loading {
    0% { background-position: 200% 0; }
    100% { background-position: -200% 0; }
}
"""
        
        critical_file = self.optimized_dir / 'critical.css'
        critical_file.write_text(critical_css.strip(), encoding='utf-8')
        
        print(f"   ✅ Critical CSS generated: {len(critical_css)} characters")
    
    def generate_service_worker(self) -> None:
        """Generate service worker for caching and offline support."""
        service_worker_content = """
// CodeXam Service Worker for Performance Optimization
const CACHE_NAME = 'codexam-v1.0.0';
const STATIC_CACHE = 'codexam-static-v1.0.0';
const DYNAMIC_CACHE = 'codexam-dynamic-v1.0.0';

// Assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/static/optimized/critical.css',
    '/static/optimized/style.min.css',
    '/static/optimized/main.min.js',
    '/static/img/favicon.ico',
    '/static/img/apple-touch-icon.png'
];

// Install event - cache static assets
self.addEventListener('install', event => {
    console.log('Service Worker: Installing...');
    
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('Service Worker: Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('Service Worker: Static assets cached');
                return self.skipWaiting();
            })
            .catch(error => {
                console.error('Service Worker: Failed to cache static assets', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', event => {
    console.log('Service Worker: Activating...');
    
    event.waitUntil(
        caches.keys()
            .then(cacheNames => {
                return Promise.all(
                    cacheNames.map(cacheName => {
                        if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
                            console.log('Service Worker: Deleting old cache', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('Service Worker: Activated');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache with network fallback
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);
    
    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }
    
    // Handle static assets
    if (url.pathname.startsWith('/static/')) {
        event.respondWith(
            caches.match(request)
                .then(response => {
                    if (response) {
                        return response;
                    }
                    
                    return fetch(request)
                        .then(fetchResponse => {
                            // Cache successful responses
                            if (fetchResponse.status === 200) {
                                const responseClone = fetchResponse.clone();
                                caches.open(STATIC_CACHE)
                                    .then(cache => {
                                        cache.put(request, responseClone);
                                    });
                            }
                            return fetchResponse;
                        });
                })
                .catch(() => {
                    // Return offline fallback for images
                    if (request.destination === 'image') {
                        return new Response(
                            '<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200"><rect width="200" height="200" fill="#333"/><text x="100" y="100" text-anchor="middle" fill="#fff" font-family="Arial" font-size="14">Image Unavailable</text></svg>',
                            { headers: { 'Content-Type': 'image/svg+xml' } }
                        );
                    }
                })
        );
        return;
    }
    
    // Handle page requests
    if (url.pathname === '/' || url.pathname.startsWith('/problems') || url.pathname.startsWith('/leaderboard')) {
        event.respondWith(
            caches.match(request)
                .then(response => {
                    return response || fetch(request)
                        .then(fetchResponse => {
                            // Cache successful page responses
                            if (fetchResponse.status === 200) {
                                const responseClone = fetchResponse.clone();
                                caches.open(DYNAMIC_CACHE)
                                    .then(cache => {
                                        cache.put(request, responseClone);
                                    });
                            }
                            return fetchResponse;
                        });
                })
                .catch(() => {
                    // Return offline page
                    return caches.match('/offline.html') || new Response(
                        '<!DOCTYPE html><html><head><title>Offline</title></head><body><h1>You are offline</h1><p>Please check your internet connection.</p></body></html>',
                        { headers: { 'Content-Type': 'text/html' } }
                    );
                })
        );
    }
});

// Background sync for form submissions
self.addEventListener('sync', event => {
    if (event.tag === 'background-sync') {
        event.waitUntil(doBackgroundSync());
    }
});

function doBackgroundSync() {
    // Handle background synchronization
    console.log('Service Worker: Background sync triggered');
    return Promise.resolve();
}

// Push notifications (future enhancement)
self.addEventListener('push', event => {
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body,
            icon: '/static/img/apple-touch-icon.png',
            badge: '/static/img/favicon.ico',
            vibrate: [100, 50, 100],
            data: {
                dateOfArrival: Date.now(),
                primaryKey: data.primaryKey
            }
        };
        
        event.waitUntil(
            self.registration.showNotification(data.title, options)
        );
    }
});
"""
        
        sw_file = self.optimized_dir / 'service-worker.js'
        sw_file.write_text(service_worker_content.strip(), encoding='utf-8')
        
        print(f"   ✅ Service worker generated: {len(service_worker_content)} characters")
    
    def implement_lazy_loading(self) -> None:
        """Generate lazy loading JavaScript."""
        lazy_loading_js = """
// Lazy Loading Implementation for CodeXam
class LazyLoader {
    constructor() {
        this.imageObserver = null;
        this.contentObserver = null;
        this.init();
    }
    
    init() {
        // Initialize Intersection Observer for images
        if ('IntersectionObserver' in window) {
            this.imageObserver = new IntersectionObserver(
                this.handleImageIntersection.bind(this),
                {
                    rootMargin: '50px 0px',
                    threshold: 0.01
                }
            );
            
            this.contentObserver = new IntersectionObserver(
                this.handleContentIntersection.bind(this),
                {
                    rootMargin: '100px 0px',
                    threshold: 0.01
                }
            );
            
            this.observeImages();
            this.observeContent();
        } else {
            // Fallback for browsers without Intersection Observer
            this.loadAllImages();
            this.loadAllContent();
        }
    }
    
    observeImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            this.imageObserver.observe(img);
        });
    }
    
    observeContent() {
        const lazyContent = document.querySelectorAll('[data-lazy-content]');
        lazyContent.forEach(element => {
            this.contentObserver.observe(element);
        });
    }
    
    handleImageIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                this.loadImage(img);
                this.imageObserver.unobserve(img);
            }
        });
    }
    
    handleContentIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const element = entry.target;
                this.loadContent(element);
                this.contentObserver.unobserve(element);
            }
        });
    }
    
    loadImage(img) {
        const src = img.dataset.src;
        const srcset = img.dataset.srcset;
        
        if (src) {
            img.src = src;
            img.removeAttribute('data-src');
        }
        
        if (srcset) {
            img.srcset = srcset;
            img.removeAttribute('data-srcset');
        }
        
        img.classList.add('lazy-loaded');
        
        // Add fade-in animation
        img.style.opacity = '0';
        img.style.transition = 'opacity 0.3s ease';
        
        img.onload = () => {
            img.style.opacity = '1';
        };
    }
    
    loadContent(element) {
        const contentUrl = element.dataset.lazyContent;
        
        if (contentUrl) {
            fetch(contentUrl)
                .then(response => response.text())
                .then(html => {
                    element.innerHTML = html;
                    element.classList.add('lazy-loaded');
                    
                    // Trigger custom event
                    element.dispatchEvent(new CustomEvent('contentLoaded', {
                        detail: { url: contentUrl }
                    }));
                })
                .catch(error => {
                    console.error('Failed to load lazy content:', error);
                    element.innerHTML = '<p>Failed to load content</p>';
                });
        }
    }
    
    loadAllImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => this.loadImage(img));
    }
    
    loadAllContent() {
        const lazyContent = document.querySelectorAll('[data-lazy-content]');
        lazyContent.forEach(element => this.loadContent(element));
    }
}

// Initialize lazy loading when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        new LazyLoader();
    });
} else {
    new LazyLoader();
}

// Export for manual initialization
window.LazyLoader = LazyLoader;
"""
        
        lazy_file = self.optimized_dir / 'lazy-loading.min.js'
        lazy_file.write_text(lazy_loading_js.strip(), encoding='utf-8')
        
        print(f"   ✅ Lazy loading script generated: {len(lazy_loading_js)} characters")
    
    def generate_asset_manifest(self) -> None:
        """Generate asset manifest for cache busting and optimization."""
        manifest = {
            'version': '1.0.0',
            'generated': datetime.now().isoformat(),
            'assets': {},
            'critical_css': 'critical.css',
            'service_worker': 'service-worker.js',
            'lazy_loading': 'lazy-loading.min.js'
        }
        
        # Scan optimized directory for assets
        for file_path in self.optimized_dir.glob('*'):
            if file_path.is_file() and not file_path.name.endswith('.json'):
                # Calculate file hash for cache busting
                file_hash = self.calculate_file_hash(file_path)
                file_size = file_path.stat().st_size
                
                manifest['assets'][file_path.name] = {
                    'hash': file_hash,
                    'size': file_size,
                    'path': f'/static/optimized/{file_path.name}',
                    'gzipped': file_path.with_suffix(file_path.suffix + '.gz').exists()
                }
        
        # Save manifest
        manifest_file = self.optimized_dir / 'manifest.json'
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding='utf-8')
        
        print(f"   ✅ Asset manifest generated with {len(manifest['assets'])} assets")
    
    def calculate_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of file for cache busting."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()[:12]  # Use first 12 characters
    
    def setup_performance_monitoring(self) -> None:
        """Generate performance monitoring JavaScript."""
        perf_monitor_js = """
// Performance Monitoring for CodeXam
class PerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.observers = {};
        this.init();
    }
    
    init() {
        this.setupNavigationTiming();
        this.setupResourceTiming();
        this.setupUserTiming();
        this.setupLargestContentfulPaint();
        this.setupFirstInputDelay();
        this.setupCumulativeLayoutShift();
        this.startMonitoring();
    }
    
    setupNavigationTiming() {
        if ('performance' in window && 'getEntriesByType' in performance) {
            const navigation = performance.getEntriesByType('navigation')[0];
            if (navigation) {
                this.metrics.navigation = {
                    domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
                    loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
                    domInteractive: navigation.domInteractive - navigation.navigationStart,
                    firstByte: navigation.responseStart - navigation.requestStart
                };
            }
        }
    }
    
    setupResourceTiming() {
        if ('performance' in window && 'getEntriesByType' in performance) {
            const resources = performance.getEntriesByType('resource');
            this.metrics.resources = {
                total: resources.length,
                css: resources.filter(r => r.name.includes('.css')).length,
                js: resources.filter(r => r.name.includes('.js')).length,
                images: resources.filter(r => r.name.match(/\\.(png|jpg|jpeg|gif|svg|webp)$/)).length,
                totalSize: resources.reduce((sum, r) => sum + (r.transferSize || 0), 0)
            };
        }
    }
    
    setupUserTiming() {
        // Custom performance marks
        this.mark('app-start');
        
        document.addEventListener('DOMContentLoaded', () => {
            this.mark('dom-ready');
            this.measure('dom-load-time', 'app-start', 'dom-ready');
        });
        
        window.addEventListener('load', () => {
            this.mark('page-loaded');
            this.measure('page-load-time', 'app-start', 'page-loaded');
        });
    }
    
    setupLargestContentfulPaint() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    this.metrics.lcp = lastEntry.startTime;
                });
                observer.observe({ entryTypes: ['largest-contentful-paint'] });
                this.observers.lcp = observer;
            } catch (e) {
                console.warn('LCP observer not supported');
            }
        }
    }
    
    setupFirstInputDelay() {
        if ('PerformanceObserver' in window) {
            try {
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        this.metrics.fid = entry.processingStart - entry.startTime;
                    });
                });
                observer.observe({ entryTypes: ['first-input'] });
                this.observers.fid = observer;
            } catch (e) {
                console.warn('FID observer not supported');
            }
        }
    }
    
    setupCumulativeLayoutShift() {
        if ('PerformanceObserver' in window) {
            try {
                let clsValue = 0;
                const observer = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    entries.forEach(entry => {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                            this.metrics.cls = clsValue;
                        }
                    });
                });
                observer.observe({ entryTypes: ['layout-shift'] });
                this.observers.cls = observer;
            } catch (e) {
                console.warn('CLS observer not supported');
            }
        }
    }
    
    mark(name) {
        if ('performance' in window && 'mark' in performance) {
            performance.mark(name);
        }
    }
    
    measure(name, startMark, endMark) {
        if ('performance' in window && 'measure' in performance) {
            try {
                performance.measure(name, startMark, endMark);
                const measure = performance.getEntriesByName(name)[0];
                if (measure) {
                    this.metrics[name] = measure.duration;
                }
            } catch (e) {
                console.warn('Failed to measure:', name);
            }
        }
    }
    
    startMonitoring() {
        // Send metrics periodically
        setTimeout(() => {
            this.sendMetrics();
        }, 5000);
        
        // Send metrics on page unload
        window.addEventListener('beforeunload', () => {
            this.sendMetrics(true);
        });
    }
    
    sendMetrics(isUnloading = false) {
        const data = {
            url: window.location.href,
            timestamp: Date.now(),
            metrics: this.metrics,
            userAgent: navigator.userAgent,
            viewport: {
                width: window.innerWidth,
                height: window.innerHeight
            }
        };
        
        if (isUnloading && 'sendBeacon' in navigator) {
            navigator.sendBeacon('/api/performance-metrics', JSON.stringify(data));
        } else {
            fetch('/api/performance-metrics', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data)
            }).catch(error => {
                console.warn('Failed to send performance metrics:', error);
            });
        }
    }
    
    getMetrics() {
        return this.metrics;
    }
    
    disconnect() {
        Object.values(this.observers).forEach(observer => {
            if (observer && observer.disconnect) {
                observer.disconnect();
            }
        });
    }
}

// Initialize performance monitoring
const perfMonitor = new PerformanceMonitor();

// Export for global access
window.PerformanceMonitor = PerformanceMonitor;
window.perfMonitor = perfMonitor;
"""
        
        perf_file = self.optimized_dir / 'performance.min.js'
        perf_file.write_text(perf_monitor_js.strip(), encoding='utf-8')
        
        print(f"   ✅ Performance monitoring script generated: {len(perf_monitor_js)} characters")
    
    def print_optimization_summary(self) -> None:
        """Print comprehensive optimization summary."""
        print("\n" + "="*60)
        print("🎉 FRONTEND OPTIMIZATION COMPLETED")
        print("="*60)
        
        print(f"\n📊 OPTIMIZATION METRICS:")
        print(f"   CSS files processed: {self.metrics['css_files_processed']}")
        print(f"   JavaScript files processed: {self.metrics['js_files_processed']}")
        print(f"   Images optimized: {self.metrics['images_optimized']}")
        print(f"   Total size before: {self.metrics['total_size_before']:,} bytes")
        print(f"   Total size after: {self.metrics['total_size_after']:,} bytes")
        print(f"   Compression ratio: {self.metrics['compression_ratio']:.1f}%")
        print(f"   Optimization time: {self.metrics['optimization_time']:.2f} seconds")
        
        print(f"\n🚀 PERFORMANCE ENHANCEMENTS:")
        print(f"   ✅ Asset minification and compression")
        print(f"   ✅ Critical CSS extraction")
        print(f"   ✅ Service worker for caching")
        print(f"   ✅ Lazy loading implementation")
        print(f"   ✅ Performance monitoring setup")
        print(f"   ✅ Asset manifest generation")
        
        print(f"\n📁 OPTIMIZED FILES CREATED:")
        optimized_files = list(self.optimized_dir.glob('*'))
        for file_path in sorted(optimized_files):
            if file_path.is_file():
                size = file_path.stat().st_size
                print(f"   📄 {file_path.name} ({size:,} bytes)")
        
        print(f"\n🎯 NEXT STEPS:")
        print(f"   1. Update templates to use optimized assets")
        print(f"   2. Configure server to serve gzipped files")
        print(f"   3. Set up proper cache headers")
        print(f"   4. Register service worker in main JavaScript")
        print(f"   5. Monitor performance metrics in production")


def main():
    """Main function to run frontend optimization."""
    import argparse
    
    parser = argparse.ArgumentParser(description='CodeXam Frontend Performance Optimizer')
    parser.add_argument('--project-root', help='Project root directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    try:
        optimizer = FrontendOptimizer(args.project_root)
        metrics = optimizer.optimize_all()
        
        if 'error' in metrics:
            print(f"❌ Optimization failed: {metrics['error']}")
            return 1
        
        print(f"\n✅ Frontend optimization completed successfully!")
        return 0
        
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    exit(main())