#!/usr/bin/env python3
"""
CodeXam Asset Optimization Script

This script optimizes static assets for production deployment:
- Minifies CSS and JavaScript files
- Generates compressed versions (gzip, brotli)
- Creates asset manifest for cache busting
- Optimizes images
- Generates critical CSS
- Creates service worker for caching

Usage:
    python scripts/optimize_assets.py [--dev] [--clean]

Options:
    --dev     Development mode (skip compression)
    --clean   Clean output directory before building
"""

import argparse
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import cssmin
    import jsmin
    from PIL import Image
except ImportError as e:
    print(f"❌ Missing required dependencies: {e}")
    print("Install with: pip install cssmin jsmin Pillow")
    sys.exit(1)


class AssetOptimizer:
    """Asset optimization and build management."""
    
    def __init__(self, project_root: str, dev_mode: bool = False):
        """
        Initialize asset optimizer.
        
        Args:
            project_root: Root directory of the project
            dev_mode: Whether to run in development mode
        """
        self.project_root = Path(project_root)
        self.dev_mode = dev_mode
        self.static_dir = self.project_root / "static"
        self.output_dir = self.static_dir / "optimized"
        self.manifest = {}
        
        # Ensure output directory exists
        self.output_dir.mkdir(exist_ok=True)
    
    def clean_output(self) -> None:
        """Clean the output directory."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
            self.output_dir.mkdir()
        print("🧹 Cleaned output directory")
    
    def optimize_css(self) -> None:
        """Optimize CSS files."""
        print("🎨 Optimizing CSS files...")
        
        css_files = [
            ("style.css", "style.min.css"),
            ("clean-nav.css", "clean-nav.min.css"),
            ("system-info-modal.css", "system-info-modal.min.css")
        ]
        
        for source_file, output_file in css_files:
            source_path = self.static_dir / "css" / source_file
            output_path = self.output_dir / output_file
            
            if not source_path.exists():
                print(f"⚠️  CSS file not found: {source_path}")
                continue
            
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    css_content = f.read()
                
                if not self.dev_mode:
                    # Minify CSS
                    css_content = cssmin.cssmin(css_content)
                    
                    # Additional optimizations
                    css_content = self._optimize_css_content(css_content)
                
                # Write optimized CSS
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(css_content)
                
                # Generate compressed versions
                if not self.dev_mode:
                    self._compress_file(output_path)
                
                # Add to manifest
                file_hash = self._get_file_hash(output_path)
                self.manifest[f"css/{source_file}"] = {
                    "path": f"/static/optimized/{output_file}",
                    "hash": file_hash,
                    "size": output_path.stat().st_size
                }
                
                print(f"  ✅ {source_file} → {output_file}")
                
            except Exception as e:
                print(f"  ❌ Failed to optimize {source_file}: {e}")
    
    def optimize_js(self) -> None:
        """Optimize JavaScript files."""
        print("⚡ Optimizing JavaScript files...")
        
        js_files = [
            ("main.js", "main.min.js"),
            ("system-info-modal.js", "system-info-modal.min.js"),
            ("form-validation.js", "form-validation.min.js"),
            ("performance-monitor.js", "performance-monitor.min.js")
        ]
        
        for source_file, output_file in js_files:
            source_path = self.static_dir / "js" / source_file
            output_path = self.output_dir / output_file
            
            if not source_path.exists():
                print(f"⚠️  JS file not found: {source_path}")
                continue
            
            try:
                with open(source_path, 'r', encoding='utf-8') as f:
                    js_content = f.read()
                
                if not self.dev_mode:
                    # Minify JavaScript
                    js_content = jsmin.jsmin(js_content)
                
                # Write optimized JavaScript
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(js_content)
                
                # Generate compressed versions
                if not self.dev_mode:
                    self._compress_file(output_path)
                
                # Add to manifest
                file_hash = self._get_file_hash(output_path)
                self.manifest[f"js/{source_file}"] = {
                    "path": f"/static/optimized/{output_file}",
                    "hash": file_hash,
                    "size": output_path.stat().st_size
                }
                
                print(f"  ✅ {source_file} → {output_file}")
                
            except Exception as e:
                print(f"  ❌ Failed to optimize {source_file}: {e}")
    
    def generate_critical_css(self) -> None:
        """Generate critical CSS for above-the-fold content."""
        print("🚀 Generating critical CSS...")
        
        critical_css = """
        /* Critical CSS - Above the fold styles */
        :root {
          --bg-primary: #0a0a0a;
          --bg-secondary: #1a1a1a;
          --text-primary: #ffffff;
          --text-secondary: #a0a0a0;
          --accent-primary: #00ff88;
          --border-primary: #333333;
          --font-sans: 'Inter', system-ui, sans-serif;
          --font-mono: 'JetBrains Mono', monospace;
          --space-4: 1rem;
          --transition-normal: 0.3s ease;
        }
        
        body {
          margin: 0;
          font-family: var(--font-sans);
          color: var(--text-primary);
          background: var(--bg-primary);
          line-height: 1.5;
        }
        
        .cyber-navbar {
          background: var(--bg-secondary);
          border-bottom: 1px solid var(--border-primary);
          padding: var(--space-4) 0;
          position: sticky;
          top: 0;
          z-index: 1000;
        }
        
        .navbar-container {
          max-width: 1280px;
          margin: 0 auto;
          padding: 0 var(--space-4);
          display: flex;
          align-items: center;
          justify-content: space-between;
        }
        
        .brand-link {
          color: var(--text-primary);
          text-decoration: none;
          font-weight: 600;
          font-size: 1.25rem;
        }
        
        .main-content {
          min-height: calc(100vh - 200px);
        }
        
        .btn-cyber-primary {
          background: transparent;
          border: 1px solid var(--accent-primary);
          color: var(--accent-primary);
          padding: 0.75rem 1.5rem;
          border-radius: 0.5rem;
          font-family: var(--font-mono);
          cursor: pointer;
          transition: var(--transition-normal);
          text-decoration: none;
          display: inline-flex;
          align-items: center;
          gap: 0.5rem;
        }
        
        .btn-cyber-primary:hover {
          background: var(--accent-primary);
          color: var(--bg-primary);
        }
        """
        
        if not self.dev_mode:
            critical_css = cssmin.cssmin(critical_css)
        
        critical_path = self.output_dir / "critical.css"
        with open(critical_path, 'w', encoding='utf-8') as f:
            f.write(critical_css)
        
        self.manifest["critical"] = {
            "path": "/static/optimized/critical.css",
            "hash": self._get_file_hash(critical_path),
            "size": critical_path.stat().st_size
        }
        
        print("  ✅ Critical CSS generated")
    
    def optimize_images(self) -> None:
        """Optimize image files."""
        print("🖼️  Optimizing images...")
        
        img_dir = self.static_dir / "img"
        if not img_dir.exists():
            print("  ⚠️  No images directory found")
            return
        
        image_extensions = {'.png', '.jpg', '.jpeg', '.webp'}
        optimized_count = 0
        
        for img_path in img_dir.iterdir():
            if img_path.suffix.lower() not in image_extensions:
                continue
            
            try:
                with Image.open(img_path) as img:
                    # Optimize image
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Save optimized version
                    output_path = self.output_dir / img_path.name
                    img.save(output_path, optimize=True, quality=85)
                    
                    # Add to manifest
                    file_hash = self._get_file_hash(output_path)
                    self.manifest[f"img/{img_path.name}"] = {
                        "path": f"/static/optimized/{img_path.name}",
                        "hash": file_hash,
                        "size": output_path.stat().st_size
                    }
                    
                    optimized_count += 1
                    
            except Exception as e:
                print(f"  ❌ Failed to optimize {img_path.name}: {e}")
        
        print(f"  ✅ Optimized {optimized_count} images")
    
    def generate_service_worker(self) -> None:
        """Generate service worker for caching."""
        print("🔧 Generating service worker...")
        
        service_worker_content = f'''
        // CodeXam Service Worker
        // Generated on {datetime.now().isoformat()}
        
        const CACHE_NAME = 'codexam-v{self._get_cache_version()}';
        const STATIC_ASSETS = [
          '/',
          '/static/optimized/style.min.css',
          '/static/optimized/main.min.js',
          '/static/optimized/critical.css'
        ];
        
        // Install event
        self.addEventListener('install', event => {{
          event.waitUntil(
            caches.open(CACHE_NAME)
              .then(cache => cache.addAll(STATIC_ASSETS))
              .then(() => self.skipWaiting())
          );
        }});
        
        // Activate event
        self.addEventListener('activate', event => {{
          event.waitUntil(
            caches.keys().then(cacheNames => {{
              return Promise.all(
                cacheNames
                  .filter(cacheName => cacheName !== CACHE_NAME)
                  .map(cacheName => caches.delete(cacheName))
              );
            }}).then(() => self.clients.claim())
          );
        }});
        
        // Fetch event
        self.addEventListener('fetch', event => {{
          if (event.request.destination === 'document') {{
            event.respondWith(
              caches.match(event.request)
                .then(response => response || fetch(event.request))
            );
          }}
        }});
        '''
        
        sw_path = self.output_dir / "service-worker.js"
        with open(sw_path, 'w', encoding='utf-8') as f:
            f.write(service_worker_content.strip())
        
        print("  ✅ Service worker generated")
    
    def generate_manifest(self) -> None:
        """Generate asset manifest file."""
        print("📋 Generating asset manifest...")
        
        manifest_data = {
            "version": self._get_cache_version(),
            "build_time": datetime.now().isoformat(),
            "assets": self.manifest,
            "dev_mode": self.dev_mode
        }
        
        manifest_path = self.output_dir / "manifest.json"
        with open(manifest_path, 'w', encoding='utf-8') as f:
            json.dump(manifest_data, f, indent=2)
        
        print(f"  ✅ Manifest generated with {len(self.manifest)} assets")
    
    def _optimize_css_content(self, css_content: str) -> str:
        """Apply additional CSS optimizations."""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        
        # Remove trailing semicolons before closing braces
        css_content = re.sub(r';\s*}', '}', css_content)
        
        return css_content.strip()
    
    def _compress_file(self, file_path: Path) -> None:
        """Generate compressed versions of a file."""
        # Generate gzip version
        with open(file_path, 'rb') as f_in:
            with gzip.open(f"{file_path}.gz", 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Generate brotli version if available
        try:
            import brotli
            with open(file_path, 'rb') as f_in:
                compressed = brotli.compress(f_in.read())
                with open(f"{file_path}.br", 'wb') as f_out:
                    f_out.write(compressed)
        except ImportError:
            pass  # Brotli not available
    
    def _get_file_hash(self, file_path: Path) -> str:
        """Get SHA-256 hash of a file."""
        hash_sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_sha256.update(chunk)
        return hash_sha256.hexdigest()[:8]
    
    def _get_cache_version(self) -> str:
        """Generate cache version based on current timestamp."""
        return datetime.now().strftime("%Y%m%d%H%M")
    
    def run_optimization(self, clean: bool = False) -> None:
        """Run the complete optimization process."""
        print("🚀 Starting CodeXam asset optimization...")
        print(f"   Mode: {'Development' if self.dev_mode else 'Production'}")
        print(f"   Output: {self.output_dir}")
        print()
        
        if clean:
            self.clean_output()
        
        # Run optimization steps
        self.optimize_css()
        self.optimize_js()
        self.generate_critical_css()
        self.optimize_images()
        
        if not self.dev_mode:
            self.generate_service_worker()
        
        self.generate_manifest()
        
        print()
        print("✅ Asset optimization completed successfully!")
        print(f"   Total assets: {len(self.manifest)}")
        print(f"   Output size: {self._get_total_size():.2f} KB")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Optimize CodeXam static assets")
    parser.add_argument("--dev", action="store_true", help="Development mode")
    parser.add_argument("--clean", action="store_true", help="Clean output directory")
    
    args = parser.parse_args()
    
    # Get project root (assuming script is in scripts/ directory)
    project_root = Path(__file__).parent.parent
    
    # Initialize optimizer
    optimizer = AssetOptimizer(project_root, dev_mode=args.dev)
    
    try:
        optimizer.run_optimization(clean=args.clean)
    except KeyboardInterrupt:
        print("\n❌ Optimization cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Optimization failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()