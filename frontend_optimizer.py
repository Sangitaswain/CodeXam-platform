#!/usr/bin/env python3
"""
Frontend Performance Optimizer for CodeXam Platform

This module provides frontend performance optimizations including:
- Asset minification and compression
- Lazy loading implementation
- Browser caching optimization
- Performance monitoring

Version: 2.0.0
Author: CodeXam Development Team
"""

import os
import json
import gzip
import hashlib
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
import cssmin
import jsmin

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FrontendOptimizer:
    """Main frontend performance optimization system."""
    
    def __init__(self, static_dir: str = 'static', output_dir: str = 'static/optimized'):
        self.static_dir = Path(static_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Asset manifest for cache busting
        self.manifest = {}
        self.manifest_file = self.output_dir / 'manifest.json'
        
        # Performance metrics
        self.stats = {
            'css_files': 0,
            'js_files': 0,
            'total_size_before': 0,
            'total_size_after': 0,
            'compression_ratio': 0
        }
        
        logger.info(f"Frontend optimizer initialized: {static_dir} -> {output_dir}")
    
    def optimize_css(self, css_file: Path) -> Dict[str, Any]:
        """Optimize CSS file with minification and compression."""
        try:
            with open(css_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Minify CSS
            minified_content = cssmin.cssmin(original_content)
            
            # Create output filename
            base_name = css_file.stem
            output_name = f"{base_name}.min.css"
            output_file = self.output_dir / output_name
            
            # Write minified CSS
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minified_content)
            
            # Create gzipped version
            gzip_file = self.output_dir / f"{output_name}.gz"
            with gzip.open(gzip_file, 'wt', encoding='utf-8') as f:
                f.write(minified_content)
            
            # Update manifest
            self.manifest[str(css_file.relative_to(self.static_dir))] = {
                'minified': output_name,
                'gzipped': f"{output_name}.gz",
                'size_original': len(original_content),
                'size_minified': len(minified_content),
                'size_gzipped': gzip_file.stat().st_size
            }
            
            # Update stats
            self.stats['css_files'] += 1
            self.stats['total_size_before'] += len(original_content)
            self.stats['total_size_after'] += len(minified_content)
            
            logger.info(f"Optimized CSS: {css_file.name} -> {output_name}")
            
            return {
                'original_size': len(original_content),
                'minified_size': len(minified_content),
                'compression_ratio': len(minified_content) / len(original_content),
                'output_file': output_file
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize CSS {css_file}: {e}")
            return None
    
    def optimize_js(self, js_file: Path) -> Dict[str, Any]:
        """Optimize JavaScript file with minification and compression."""
        try:
            with open(js_file, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Minify JavaScript
            minified_content = jsmin.jsmin(original_content)
            
            # Create output filename
            base_name = js_file.stem
            output_name = f"{base_name}.min.js"
            output_file = self.output_dir / output_name
            
            # Write minified JavaScript
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(minified_content)
            
            # Create gzipped version
            gzip_file = self.output_dir / f"{output_name}.gz"
            with gzip.open(gzip_file, 'wt', encoding='utf-8') as f:
                f.write(minified_content)
            
            # Update manifest
            self.manifest[str(js_file.relative_to(self.static_dir))] = {
                'minified': output_name,
                'gzipped': f"{output_name}.gz",
                'size_original': len(original_content),
                'size_minified': len(minified_content),
                'size_gzipped': gzip_file.stat().st_size
            }
            
            # Update stats
            self.stats['js_files'] += 1
            self.stats['total_size_before'] += len(original_content)
            self.stats['total_size_after'] += len(minified_content)
            
            logger.info(f"Optimized JS: {js_file.name} -> {output_name}")
            
            return {
                'original_size': len(original_content),
                'minified_size': len(minified_content),
                'compression_ratio': len(minified_content) / len(original_content),
                'output_file': output_file
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize JS {js_file}: {e}")
            return None
    
    def generate_lazy_loading_script(self) -> str:
        """Generate lazy loading JavaScript."""
        lazy_loading_js = '''
/*!
 * CodeXam Lazy Loading System
 */

class CodeXamLazyLoader {
    constructor(options = {}) {
        this.options = {
            rootMargin: '50px 0px',
            threshold: 0.01,
            loadingClass: 'lazy-loading',
            loadedClass: 'lazy-loaded',
            errorClass: 'lazy-error',
            ...options
        };
        
        this.observer = null;
        this.images = [];
        this.init();
    }
    
    init() {
        if (!('IntersectionObserver' in window)) {
            this.loadAllImages();
            return;
        }
        
        this.observer = new IntersectionObserver(
            this.handleIntersection.bind(this),
            {
                rootMargin: this.options.rootMargin,
                threshold: this.options.threshold
            }
        );
        
        this.findLazyImages();
        this.observeImages();
    }
    
    findLazyImages() {
        this.images = Array.from(document.querySelectorAll('[data-lazy-src]'));
    }
    
    observeImages() {
        this.images.forEach(img => {
            this.observer.observe(img);
        });
    }
    
    handleIntersection(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                this.loadImage(entry.target);
                this.observer.unobserve(entry.target);
            }
        });
    }
    
    loadImage(img) {
        img.classList.add(this.options.loadingClass);
        
        const src = img.dataset.lazySrc;
        const srcset = img.dataset.lazySrcset;
        
        const imageLoader = new Image();
        
        imageLoader.onload = () => {
            if (srcset) {
                img.srcset = srcset;
            }
            img.src = src;
            
            img.classList.remove(this.options.loadingClass);
            img.classList.add(this.options.loadedClass);
            
            delete img.dataset.lazySrc;
            delete img.dataset.lazySrcset;
            
            img.dispatchEvent(new CustomEvent('lazyloaded', {
                detail: { src, srcset }
            }));
        };
        
        imageLoader.onerror = () => {
            img.classList.remove(this.options.loadingClass);
            img.classList.add(this.options.errorClass);
            
            img.dispatchEvent(new CustomEvent('lazyerror', {
                detail: { src, srcset }
            }));
        };
        
        if (srcset) {
            imageLoader.srcset = srcset;
        }
        imageLoader.src = src;
    }
    
    loadAllImages() {
        this.images.forEach(img => {
            this.loadImage(img);
        });
    }
    
    refresh() {
        this.findLazyImages();
        this.observeImages();
    }
    
    destroy() {
        if (this.observer) {
            this.observer.disconnect();
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.CodeXamLazyLoader = new CodeXamLazyLoader();
});
'''
        
        # Minify and save
        minified_js = jsmin.jsmin(lazy_loading_js)
        output_file = self.output_dir / 'lazy-loading.min.js'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(minified_js)
        
        logger.info(f"Generated lazy loading script: {output_file}")
        
        return minified_js
    
    def generate_performance_monitor(self) -> str:
        """Generate performance monitoring script."""
        performance_js = '''
/*!
 * CodeXam Performance Monitor
 */

class CodeXamPerformanceMonitor {
    constructor() {
        this.metrics = {};
        this.config = {
            reportInterval: 30000,
            endpoint: '/api/performance'
        };
        
        this.init();
    }
    
    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.startMonitoring());
        } else {
            this.startMonitoring();
        }
    }
    
    startMonitoring() {
        this.measureNavigationTiming();
        this.measureResourceTiming();
        this.startReporting();
    }
    
    measureNavigationTiming() {
        if (!performance.getEntriesByType) return;
        
        const navigation = performance.getEntriesByType('navigation')[0];
        if (!navigation) return;
        
        this.metrics.navigation = {
            dns: navigation.domainLookupEnd - navigation.domainLookupStart,
            tcp: navigation.connectEnd - navigation.connectStart,
            ttfb: navigation.responseStart - navigation.requestStart,
            download: navigation.responseEnd - navigation.responseStart,
            domParse: navigation.domContentLoadedEventStart - navigation.responseEnd,
            domReady: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
            loadComplete: navigation.loadEventEnd - navigation.loadEventStart,
            total: navigation.loadEventEnd - navigation.navigationStart
        };
    }
    
    measureResourceTiming() {
        if (!performance.getEntriesByType) return;
        
        const resources = performance.getEntriesByType('resource');
        const resourceMetrics = {
            total: resources.length,
            css: 0,
            js: 0,
            images: 0,
            totalSize: 0,
            totalDuration: 0
        };
        
        resources.forEach(resource => {
            const duration = resource.responseEnd - resource.startTime;
            const size = resource.transferSize || 0;
            
            resourceMetrics.totalSize += size;
            resourceMetrics.totalDuration += duration;
            
            if (resource.name.includes('.css')) {
                resourceMetrics.css++;
            } else if (resource.name.includes('.js')) {
                resourceMetrics.js++;
            } else if (/\\.(png|jpg|jpeg|gif|svg|webp)/.test(resource.name)) {
                resourceMetrics.images++;
            }
        });
        
        this.metrics.resources = resourceMetrics;
    }
    
    startReporting() {
        setTimeout(() => this.reportMetrics(), 1000);
        setInterval(() => this.reportMetrics(), this.config.reportInterval);
        window.addEventListener('beforeunload', () => this.reportMetrics(true));
    }
    
    reportMetrics(isUnload = false) {
        const report = {
            timestamp: Date.now(),
            url: window.location.href,
            userAgent: navigator.userAgent,
            metrics: { ...this.metrics },
            isUnload
        };
        
        if (isUnload && navigator.sendBeacon) {
            navigator.sendBeacon(this.config.endpoint, JSON.stringify(report));
        } else {
            fetch(this.config.endpoint, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(report),
                keepalive: isUnload
            }).catch(error => {
                console.warn('Performance reporting failed:', error);
            });
        }
    }
    
    measure(name, fn) {
        const startMark = `${name}-start`;
        const endMark = `${name}-end`;
        
        performance.mark(startMark);
        
        const result = fn();
        
        if (result && typeof result.then === 'function') {
            return result.then(value => {
                performance.mark(endMark);
                performance.measure(name, startMark, endMark);
                return value;
            });
        } else {
            performance.mark(endMark);
            performance.measure(name, startMark, endMark);
            return result;
        }
    }
}

if (typeof window !== 'undefined') {
    window.CodeXamPerformanceMonitor = new CodeXamPerformanceMonitor();
}
'''
        
        # Minify and save
        minified_js = jsmin.jsmin(performance_js)
        output_file = self.output_dir / 'performance.min.js'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(minified_js)
        
        logger.info(f"Generated performance monitor: {output_file}")
        
        return minified_js
    
    def optimize_all(self) -> Dict[str, Any]:
        """Run complete frontend optimization."""
        logger.info("Starting frontend performance optimization...")
        
        start_time = time.time()
        
        try:
            # Optimize CSS files
            css_files = list(self.static_dir.glob('css/*.css'))
            for css_file in css_files:
                self.optimize_css(css_file)
            
            # Optimize JavaScript files
            js_files = list(self.static_dir.glob('js/*.js'))
            for js_file in js_files:
                self.optimize_js(js_file)
            
            # Generate lazy loading
            self.generate_lazy_loading_script()
            
            # Generate performance monitoring
            self.generate_performance_monitor()
            
            # Calculate compression ratio
            if self.stats['total_size_before'] > 0:
                self.stats['compression_ratio'] = (
                    self.stats['total_size_after'] / 
                    self.stats['total_size_before']
                )
            
            # Save manifest
            with open(self.manifest_file, 'w') as f:
                json.dump(self.manifest, f, indent=2)
            
            end_time = time.time()
            total_time = end_time - start_time
            
            logger.info("Frontend optimization completed!")
            
            return {
                'success': True,
                'stats': self.stats,
                'manifest': self.manifest,
                'total_time': total_time,
                'size_reduction': (1 - self.stats['compression_ratio']) * 100 if self.stats['compression_ratio'] > 0 else 0
            }
            
        except Exception as e:
            logger.error(f"Frontend optimization failed: {e}")
            return {
                'success': False,
                'error': str(e),
                'stats': self.stats
            }


if __name__ == '__main__':
    # Run frontend optimization
    optimizer = FrontendOptimizer()
    results = optimizer.optimize_all()
    
    if results['success']:
        print("🚀 Frontend Optimization Completed!")
        print(f"⏱️  Total time: {results['total_time']:.2f} seconds")
        print(f"📦 CSS files optimized: {results['stats']['css_files']}")
        print(f"📦 JS files optimized: {results['stats']['js_files']}")
        print(f"📉 Size reduction: {results['size_reduction']:.1f}%")
    else:
        print(f"❌ Optimization failed: {results['error']}")