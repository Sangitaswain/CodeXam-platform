#!/usr/bin/env python3
"""
Performance Optimization Script for CodeXam UI Templates

This script optimizes CSS, JavaScript, images, and implements performance
monitoring for production-ready templates. It provides comprehensive
asset optimization with detailed reporting and performance metrics.

Usage: python optimize_performance.py
"""

import gzip
import json
import os
import re
import shutil
from pathlib import Path
from typing import Dict, List, Optional

# Optional dependencies with fallbacks
try:
    import csscompressor
    HAS_CSSCOMPRESSOR = True
except ImportError:
    HAS_CSSCOMPRESSOR = False

try:
    import jsmin
    HAS_JSMIN = True
except ImportError:
    HAS_JSMIN = False

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False


class PerformanceOptimizer:
    """
    Main performance optimization class.
    
    This class provides comprehensive optimization for web assets including
    CSS, JavaScript, images, and HTML templates with detailed reporting
    and performance monitoring capabilities.
    
    Attributes:
        static_dir: Path to static assets directory
        templates_dir: Path to HTML templates directory
        optimized_dir: Path to optimized assets output directory
        optimization_results: Dictionary tracking optimization statistics
    """
    
    def __init__(self) -> None:
        """Initialize the performance optimizer with default paths and settings."""
        self.static_dir = Path("static")
        self.templates_dir = Path("templates")
        self.optimized_dir = Path("static/optimized")
        self.optimized_dir.mkdir(exist_ok=True)
        
        self.optimization_results = {
            'css': {'original_size': 0, 'optimized_size': 0, 'files': []},
            'js': {'original_size': 0, 'optimized_size': 0, 'files': []},
            'images': {'original_size': 0, 'optimized_size': 0, 'files': []},
            'html': {'original_size': 0, 'optimized_size': 0, 'files': []}
        }
        
    def optimize_css(self) -> None:
        """
        Optimize CSS files by minifying and compressing them.
        
        Processes all CSS files in the static directory, creates minified
        versions, and generates gzipped files for better compression.
        """
        print("🎨 Optimizing CSS files...")
        
        css_files = list(self.static_dir.glob("**/*.css"))
        
        for css_file in css_files:
            if 'optimized' in str(css_file) or 'min' in css_file.name:
                continue
                
            print(f"  Optimizing {css_file.name}...")
            
            # Read original CSS
            with open(css_file, 'r', encoding='utf-8') as f:
                original_css = f.read()
                
            original_size = len(original_css.encode('utf-8'))
            
            # Optimize CSS
            if HAS_CSSCOMPRESSOR:
                try:
                    optimized_css = csscompressor.compress(original_css)
                except Exception:
                    optimized_css = self.optimize_css_content(original_css)
            else:
                optimized_css = self.optimize_css_content(original_css)
            
            optimized_size = len(optimized_css.encode('utf-8'))
            
            # Save optimized version
            optimized_file = self.optimized_dir / f"{css_file.stem}.min.css"
            with open(optimized_file, 'w', encoding='utf-8') as f:
                f.write(optimized_css)
                
            # Create gzipped version
            with gzip.open(f"{optimized_file}.gz", 'wt', encoding='utf-8') as f:
                f.write(optimized_css)
                
            self.optimization_results['css']['original_size'] += original_size
            self.optimization_results['css']['optimized_size'] += optimized_size
            self.optimization_results['css']['files'].append({
                'name': css_file.name,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings': original_size - optimized_size
            })
            
    def optimize_css_content(self, css_content: str) -> str:
        """Optimize CSS content."""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        css_content = re.sub(r';\s*}', '}', css_content)
        css_content = re.sub(r'{\s*', '{', css_content)
        css_content = re.sub(r'}\s*', '}', css_content)
        css_content = re.sub(r':\s*', ':', css_content)
        css_content = re.sub(r';\s*', ';', css_content)
        
        # Remove trailing semicolons
        css_content = re.sub(r';(?=\s*})', '', css_content)
        
        # Compress colors
        css_content = re.sub(r'#([0-9a-fA-F])\1([0-9a-fA-F])\2([0-9a-fA-F])\3', r'#\1\2\3', css_content)
        
        return css_content.strip()
        
    def optimize_javascript(self):
        """Optimize JavaScript files."""
        print("⚡ Optimizing JavaScript files...")
        
        js_files = list(self.static_dir.glob("**/*.js"))
        
        for js_file in js_files:
            if 'optimized' in str(js_file) or 'min' in js_file.name:
                continue
                
            print(f"  Optimizing {js_file.name}...")
            
            # Read original JS
            with open(js_file, 'r', encoding='utf-8') as f:
                original_js = f.read()
                
            original_size = len(original_js.encode('utf-8'))
            
            # Optimize JavaScript
            if HAS_JSMIN:
                try:
                    optimized_js = jsmin.jsmin(original_js)
                except Exception:
                    # Fallback to basic optimization
                    optimized_js = self.optimize_js_content(original_js)
            else:
                optimized_js = self.optimize_js_content(original_js)
                
            optimized_size = len(optimized_js.encode('utf-8'))
            
            # Save optimized version
            optimized_file = self.optimized_dir / f"{js_file.stem}.min.js"
            with open(optimized_file, 'w', encoding='utf-8') as f:
                f.write(optimized_js)
                
            # Create gzipped version
            with gzip.open(f"{optimized_file}.gz", 'wt', encoding='utf-8') as f:
                f.write(optimized_js)
                
            self.optimization_results['js']['original_size'] += original_size
            self.optimization_results['js']['optimized_size'] += optimized_size
            self.optimization_results['js']['files'].append({
                'name': js_file.name,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings': original_size - optimized_size
            })
            
    def optimize_js_content(self, js_content: str) -> str:
        """Basic JavaScript optimization."""
        # Remove comments
        js_content = re.sub(r'//.*$', '', js_content, flags=re.MULTILINE)
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        js_content = re.sub(r';\s*', ';', js_content)
        js_content = re.sub(r'{\s*', '{', js_content)
        js_content = re.sub(r'}\s*', '}', js_content)
        
        return js_content.strip()
        
    def optimize_images(self) -> None:
        """
        Optimize image files by compressing them.
        
        Processes image files in the static directory and creates optimized
        versions with reduced file sizes while maintaining quality.
        """
        print("🖼️ Optimizing images...")
        
        if not HAS_PIL:
            print("   ⚠️ PIL not available, skipping image optimization")
            return
        
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
        image_files = []
        
        for ext in image_extensions:
            image_files.extend(self.static_dir.glob(f"**/*{ext}"))
            
        for image_file in image_files:
            if 'optimized' in str(image_file):
                continue
                
            print(f"  Optimizing {image_file.name}...")
            
            original_size = image_file.stat().st_size
            
            try:
                # Optimize image
                optimized_file = self.optimized_dir / image_file.name
                self.optimize_image_file(image_file, optimized_file)
                
                optimized_size = optimized_file.stat().st_size
                
                self.optimization_results['images']['original_size'] += original_size
                self.optimization_results['images']['optimized_size'] += optimized_size
                self.optimization_results['images']['files'].append({
                    'name': image_file.name,
                    'original_size': original_size,
                    'optimized_size': optimized_size,
                    'savings': original_size - optimized_size
                })
                
            except Exception as e:
                print(f"    Error optimizing {image_file.name}: {e}")
                
    def optimize_image_file(self, input_file: Path, output_file: Path) -> None:
        """
        Optimize a single image file.
        
        Args:
            input_file: Path to the original image file
            output_file: Path where optimized image will be saved
            
        Raises:
            Exception: If image processing fails
        """
        if not HAS_PIL:
            # Copy file if PIL is not available
            shutil.copy2(input_file, output_file)
            return
            
        with Image.open(input_file) as img:
            # Convert to RGB if necessary
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
                
            # Optimize based on file type
            if input_file.suffix.lower() in ['.jpg', '.jpeg']:
                img.save(output_file, 'JPEG', quality=85, optimize=True)
            elif input_file.suffix.lower() == '.png':
                img.save(output_file, 'PNG', optimize=True)
            else:
                img.save(output_file, optimize=True)
                
    def create_critical_css(self):
        """Extract and inline critical CSS."""
        print("🚀 Creating critical CSS...")
        
        critical_css = """
/* Critical CSS for above-the-fold content */
:root {
    --bg-primary: #0a0a0a;
    --bg-secondary: #1a1a1a;
    --accent-primary: #00ff88;
    --text-primary: #ffffff;
    --text-secondary: #a0a0a0;
    --font-mono: 'JetBrains Mono', monospace;
    --font-sans: 'Inter', sans-serif;
}

body {
    font-family: var(--font-sans);
    background: var(--bg-primary);
    color: var(--text-primary);
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

.cyber-navbar {
    background: var(--bg-secondary);
    border-bottom: 1px solid #333;
    position: sticky;
    top: 0;
    z-index: 1000;
}

.hero-section {
    min-height: 80vh;
    display: flex;
    align-items: center;
    background: var(--bg-primary);
}

.hero-title {
    font-size: 4rem;
    font-weight: 800;
    color: var(--text-primary);
    margin-bottom: 2rem;
}

.text-accent {
    color: var(--accent-primary);
}

.btn-cyber-primary {
    background: transparent;
    border: 1px solid var(--accent-primary);
    color: var(--accent-primary);
    padding: 0.75rem 1.5rem;
    border-radius: 0.5rem;
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    transition: all 0.3s ease;
}

.btn-cyber-primary:hover {
    background: var(--accent-primary);
    color: var(--bg-primary);
}
"""
        
        # Save critical CSS
        critical_file = self.optimized_dir / "critical.css"
        with open(critical_file, 'w', encoding='utf-8') as f:
            f.write(critical_css)
            
        return critical_css
        
    def add_performance_monitoring(self):
        """Add performance monitoring scripts."""
        print("📊 Adding performance monitoring...")
        
        performance_script = """
// Performance monitoring for CodeXam
(function() {
    'use strict';
    
    // Performance metrics collection
    const metrics = {
        navigationStart: 0,
        domContentLoaded: 0,
        loadComplete: 0,
        firstPaint: 0,
        firstContentfulPaint: 0,
        largestContentfulPaint: 0,
        cumulativeLayoutShift: 0,
        firstInputDelay: 0
    };
    
    // Collect navigation timing
    function collectNavigationTiming() {
        if (performance.timing) {
            const timing = performance.timing;
            metrics.navigationStart = timing.navigationStart;
            metrics.domContentLoaded = timing.domContentLoadedEventEnd - timing.navigationStart;
            metrics.loadComplete = timing.loadEventEnd - timing.navigationStart;
        }
    }
    
    // Collect paint timing
    function collectPaintTiming() {
        if (performance.getEntriesByType) {
            const paintEntries = performance.getEntriesByType('paint');
            paintEntries.forEach(entry => {
                if (entry.name === 'first-paint') {
                    metrics.firstPaint = entry.startTime;
                } else if (entry.name === 'first-contentful-paint') {
                    metrics.firstContentfulPaint = entry.startTime;
                }
            });
        }
    }
    
    // Collect Core Web Vitals
    function collectCoreWebVitals() {
        // Largest Contentful Paint
        if ('PerformanceObserver' in window) {
            try {
                const lcpObserver = new PerformanceObserver((list) => {
                    const entries = list.getEntries();
                    const lastEntry = entries[entries.length - 1];
                    metrics.largestContentfulPaint = lastEntry.startTime;
                });
                lcpObserver.observe({ entryTypes: ['largest-contentful-paint'] });
                
                // Cumulative Layout Shift
                const clsObserver = new PerformanceObserver((list) => {
                    let clsValue = 0;
                    for (const entry of list.getEntries()) {
                        if (!entry.hadRecentInput) {
                            clsValue += entry.value;
                        }
                    }
                    metrics.cumulativeLayoutShift = clsValue;
                });
                clsObserver.observe({ entryTypes: ['layout-shift'] });
                
                // First Input Delay
                const fidObserver = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        metrics.firstInputDelay = entry.processingStart - entry.startTime;
                        break;
                    }
                });
                fidObserver.observe({ entryTypes: ['first-input'] });
                
            } catch (e) {
                console.warn('Performance Observer not fully supported:', e);
            }
        }
    }
    
    // Send metrics to analytics
    function sendMetrics() {
        // Only send in production
        if (location.hostname === 'localhost' || location.hostname === '127.0.0.1') {
            console.log('Performance Metrics:', metrics);
            return;
        }
        
        // Send to analytics service (implement as needed)
        if (typeof gtag !== 'undefined') {
            gtag('event', 'page_performance', {
                'dom_content_loaded': metrics.domContentLoaded,
                'load_complete': metrics.loadComplete,
                'first_contentful_paint': metrics.firstContentfulPaint,
                'largest_contentful_paint': metrics.largestContentfulPaint,
                'cumulative_layout_shift': metrics.cumulativeLayoutShift,
                'first_input_delay': metrics.firstInputDelay
            });
        }
    }
    
    // Initialize performance monitoring
    function init() {
        collectNavigationTiming();
        collectPaintTiming();
        collectCoreWebVitals();
        
        // Send metrics after page load
        window.addEventListener('load', () => {
            setTimeout(sendMetrics, 1000);
        });
    }
    
    // Start monitoring
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    // Expose metrics for debugging
    window.CodeXamPerformance = {
        getMetrics: () => metrics,
        sendMetrics: sendMetrics
    };
    
})();
"""
        
        # Save performance monitoring script
        perf_file = self.optimized_dir / "performance.min.js"
        with open(perf_file, 'w', encoding='utf-8') as f:
            f.write(performance_script)
            
    def implement_lazy_loading(self):
        """Implement lazy loading for images and non-critical content."""
        print("⏳ Implementing lazy loading...")
        
        lazy_loading_script = """
// Lazy loading implementation for CodeXam
(function() {
    'use strict';
    
    // Intersection Observer for lazy loading
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                img.classList.add('loaded');
                observer.unobserve(img);
            }
        });
    });
    
    // Observe all lazy images
    function initLazyImages() {
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => {
            img.classList.add('lazy');
            imageObserver.observe(img);
        });
    }
    
    // Lazy load non-critical CSS
    function loadNonCriticalCSS() {
        const nonCriticalCSS = [
            '/static/optimized/style.min.css',
            '/static/optimized/components.min.css'
        ];
        
        nonCriticalCSS.forEach(href => {
            const link = document.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            link.media = 'print';
            link.onload = function() {
                this.media = 'all';
            };
            document.head.appendChild(link);
        });
    }
    
    // Initialize lazy loading
    function init() {
        initLazyImages();
        
        // Load non-critical CSS after page load
        window.addEventListener('load', () => {
            setTimeout(loadNonCriticalCSS, 100);
        });
    }
    
    // Start lazy loading
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})();
"""
        
        # Save lazy loading script
        lazy_file = self.optimized_dir / "lazy-loading.min.js"
        with open(lazy_file, 'w', encoding='utf-8') as f:
            f.write(lazy_loading_script)
            
    def optimize_html_templates(self):
        """Optimize HTML templates."""
        print("📄 Optimizing HTML templates...")
        
        html_files = list(self.templates_dir.glob("*.html"))
        
        for html_file in html_files:
            print(f"  Optimizing {html_file.name}...")
            
            with open(html_file, 'r', encoding='utf-8') as f:
                original_html = f.read()
                
            original_size = len(original_html.encode('utf-8'))
            
            # Optimize HTML
            optimized_html = self.optimize_html_content(original_html)
            optimized_size = len(optimized_html.encode('utf-8'))
            
            # Save optimized version (backup original first)
            backup_file = html_file.with_suffix('.html.backup')
            if not backup_file.exists():
                shutil.copy2(html_file, backup_file)
                
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(optimized_html)
                
            self.optimization_results['html']['original_size'] += original_size
            self.optimization_results['html']['optimized_size'] += optimized_size
            self.optimization_results['html']['files'].append({
                'name': html_file.name,
                'original_size': original_size,
                'optimized_size': optimized_size,
                'savings': original_size - optimized_size
            })
            
    def optimize_html_content(self, html_content: str) -> str:
        """Optimize HTML content."""
        # Remove HTML comments (but keep conditional comments)
        html_content = re.sub(r'<!--(?!\[if).*?-->', '', html_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace between tags
        html_content = re.sub(r'>\s+<', '><', html_content)
        
        # Remove leading/trailing whitespace from lines
        lines = html_content.split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        html_content = '\n'.join(lines)
        
        # Add performance optimizations
        html_content = self.add_performance_optimizations(html_content)
        
        return html_content
        
    def add_performance_optimizations(self, html_content: str) -> str:
        """Add performance optimizations to HTML."""
        
        # Add preload for critical resources
        preload_links = '''
    <!-- Preload critical resources -->
    <link rel="preload" href="/static/optimized/critical.css" as="style">
    <link rel="preload" href="/static/optimized/performance.min.js" as="script">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
'''
        
        # Insert preload links after <head>
        html_content = html_content.replace('<head>', f'<head>{preload_links}')
        
        # Add critical CSS inline
        critical_css = self.create_critical_css()
        critical_style = f'<style>{critical_css}</style>'
        
        # Insert critical CSS before closing </head>
        html_content = html_content.replace('</head>', f'{critical_style}\n</head>')
        
        # Add performance monitoring script
        perf_script = '''
    <!-- Performance monitoring -->
    <script src="/static/optimized/performance.min.js" defer></script>
    <script src="/static/optimized/lazy-loading.min.js" defer></script>
'''
        
        # Insert performance scripts before closing </body>
        html_content = html_content.replace('</body>', f'{perf_script}\n</body>')
        
        # Convert images to lazy loading
        html_content = re.sub(
            r'<img([^>]*)\s+src="([^"]*)"([^>]*)>',
            r'<img\1 data-src="\2" src="data:image/svg+xml,%3Csvg xmlns=\'http://www.w3.org/2000/svg\' viewBox=\'0 0 1 1\'%3E%3C/svg%3E"\3>',
            html_content
        )
        
        return html_content
        
    def generate_optimization_report(self) -> str:
        """Generate optimization report."""
        report = []
        report.append("🚀 Performance Optimization Report")
        report.append("=" * 50)
        report.append(f"Generated: {os.popen('date').read().strip()}")
        report.append("")
        
        total_original = 0
        total_optimized = 0
        
        for category, data in self.optimization_results.items():
            if data['files']:
                report.append(f"📁 {category.upper()} Optimization:")
                report.append(f"  Files processed: {len(data['files'])}")
                report.append(f"  Original size: {self.format_bytes(data['original_size'])}")
                report.append(f"  Optimized size: {self.format_bytes(data['optimized_size'])}")
                
                if data['original_size'] > 0:
                    savings = data['original_size'] - data['optimized_size']
                    savings_percent = (savings / data['original_size']) * 100
                    report.append(f"  Savings: {self.format_bytes(savings)} ({savings_percent:.1f}%)")
                    
                total_original += data['original_size']
                total_optimized += data['optimized_size']
                report.append("")
                
        # Total savings
        if total_original > 0:
            total_savings = total_original - total_optimized
            total_savings_percent = (total_savings / total_original) * 100
            report.append("📊 Total Optimization Results:")
            report.append(f"  Original size: {self.format_bytes(total_original)}")
            report.append(f"  Optimized size: {self.format_bytes(total_optimized)}")
            report.append(f"  Total savings: {self.format_bytes(total_savings)} ({total_savings_percent:.1f}%)")
            report.append("")
            
        # Recommendations
        report.append("💡 Performance Recommendations:")
        report.append("1. Enable gzip compression on server")
        report.append("2. Set proper cache headers for static assets")
        report.append("3. Use CDN for static file delivery")
        report.append("4. Monitor Core Web Vitals regularly")
        report.append("5. Implement service worker for offline caching")
        report.append("")
        
        return "\n".join(report)
        
    def format_bytes(self, bytes_size: int) -> str:
        """Format bytes to human readable format."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.1f} TB"
        
    def run_optimization(self):
        """Run complete optimization process."""
        print("🚀 Starting Performance Optimization")
        print("=" * 50)
        
        # Create optimized directory
        self.optimized_dir.mkdir(exist_ok=True)
        
        # Run optimizations
        self.optimize_css()
        self.optimize_javascript()
        self.optimize_images()
        self.create_critical_css()
        self.add_performance_monitoring()
        self.implement_lazy_loading()
        self.optimize_html_templates()
        
        # Generate report
        report = self.generate_optimization_report()
        print(report)
        
        # Save report
        with open("performance_optimization_report.txt", "w", encoding="utf-8") as f:
            f.write(report)
            
        print("📄 Optimization report saved to: performance_optimization_report.txt")
        print("✅ Performance optimization completed!")


def main():
    """Main function to run performance optimization."""
    optimizer = PerformanceOptimizer()
    optimizer.run_optimization()


if __name__ == "__main__":
    main()