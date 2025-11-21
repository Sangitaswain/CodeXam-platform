#!/usr/bin/env python3
"""
Asset Build Script for CodeXam

Minifies CSS and JavaScript files for production deployment.
This script processes static assets, creates minified versions,
generates gzipped files, and creates an asset manifest for
optimized loading performance.
"""

import gzip
import json
import os
import re
from pathlib import Path
from typing import Dict, List

def minify_css(css_content: str) -> str:
    """
    Minify CSS content by removing comments, whitespace, and unnecessary characters.
    
    Args:
        css_content: Original CSS content to minify
        
    Returns:
        Minified CSS content with reduced file size
    """
    # Remove comments
    css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
    
    # Remove unnecessary whitespace
    css_content = re.sub(r'\s+', ' ', css_content)
    
    # Remove whitespace around specific characters
    css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
    
    # Remove trailing semicolons before closing braces
    css_content = re.sub(r';\s*}', '}', css_content)
    
    # Remove unnecessary quotes from URLs
    css_content = re.sub(r'url\(["\']([^"\']*)["\']', r'url(\1)', css_content)
    
    return css_content.strip()

def minify_js(js_content: str) -> str:
    """
    Basic JavaScript minification (for simple cases).
    
    Args:
        js_content: Original JavaScript content to minify
        
    Returns:
        Minified JavaScript content with reduced file size
    """
    # Remove single-line comments (but preserve URLs)
    js_content = re.sub(r'(?<!:)//.*$', '', js_content, flags=re.MULTILINE)
    
    # Remove multi-line comments
    js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
    
    # Remove unnecessary whitespace
    js_content = re.sub(r'\s+', ' ', js_content)
    
    # Remove whitespace around operators and punctuation
    js_content = re.sub(r'\s*([{}();,=+\-*/<>!&|])\s*', r'\1', js_content)
    
    return js_content.strip()

def create_critical_css() -> str:
    """
    Extract critical above-the-fold CSS.
    
    Returns:
        Minified critical CSS content for inline inclusion
    """
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
    return minify_css(critical_css)

def build_assets() -> None:
    """
    Build and optimize all assets for production deployment.
    
    This function processes CSS and JavaScript files, creates minified versions,
    generates gzipped files, creates critical CSS, and builds an asset manifest.
    """
    print("🚀 Building CodeXam Assets...")
    
    # Create optimized directory
    optimized_dir = Path("static/optimized")
    optimized_dir.mkdir(exist_ok=True)
    
    # Build CSS
    print("📦 Processing CSS files...")
    css_files = [
        "static/css/style.css",
        "static/css/system-info-modal.css"
    ]
    
    combined_css = ""
    for css_file in css_files:
        if os.path.exists(css_file):
            with open(css_file, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_css += f"/* {css_file} */\n{content}\n\n"
    
    # Minify combined CSS
    minified_css = minify_css(combined_css)
    
    # Write minified CSS
    with open("static/optimized/style.min.css", 'w', encoding='utf-8') as f:
        f.write(minified_css)
    
    # Create gzipped version
    with open("static/optimized/style.min.css.gz", 'wb') as f:
        f.write(gzip.compress(minified_css.encode('utf-8')))
    
    print(f"   ✅ CSS minified: {len(combined_css)} → {len(minified_css)} chars ({len(minified_css)/len(combined_css)*100:.1f}%)")
    
    # Build JavaScript
    print("📦 Processing JavaScript files...")
    js_files = [
        "static/js/main.js",
        "static/js/system-info-modal.js"
    ]
    
    combined_js = ""
    for js_file in js_files:
        if os.path.exists(js_file):
            with open(js_file, 'r', encoding='utf-8') as f:
                content = f.read()
                combined_js += f"/* {js_file} */\n{content}\n\n"
    
    # Basic minification for JavaScript
    minified_js = minify_js(combined_js)
    
    # Write minified JavaScript
    with open("static/optimized/main.min.js", 'w', encoding='utf-8') as f:
        f.write(minified_js)
    
    # Create gzipped version
    with open("static/optimized/main.min.js.gz", 'wb') as f:
        f.write(gzip.compress(minified_js.encode('utf-8')))
    
    print(f"   ✅ JavaScript minified: {len(combined_js)} → {len(minified_js)} chars ({len(minified_js)/len(combined_js)*100:.1f}%)")
    
    # Create critical CSS
    print("📦 Creating critical CSS...")
    critical_css = create_critical_css()
    with open("static/optimized/critical.css", 'w', encoding='utf-8') as f:
        f.write(critical_css)
    
    print(f"   ✅ Critical CSS created: {len(critical_css)} chars")
    
    # Create asset manifest
    manifest = {
        "css": {
            "main": "/static/optimized/style.min.css",
            "critical": "/static/optimized/critical.css"
        },
        "js": {
            "main": "/static/optimized/main.min.js"
        },
        "build_time": str(Path().resolve()),
        "version": "1.0.0"
    }
    
    with open("static/optimized/manifest.json", 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print("   ✅ Asset manifest created")
    
    # Create service worker for caching
    service_worker = """
// CodeXam Service Worker for Asset Caching
const CACHE_NAME = 'codexam-v1';
const STATIC_ASSETS = [
  '/static/optimized/style.min.css',
  '/static/optimized/main.min.js',
  '/static/optimized/critical.css'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(STATIC_ASSETS))
  );
});

self.addEventListener('fetch', event => {
  if (event.request.url.includes('/static/')) {
    event.respondWith(
      caches.match(event.request)
        .then(response => response || fetch(event.request))
    );
  }
});
"""
    
    with open("static/optimized/service-worker.js", 'w') as f:
        f.write(service_worker.strip())
    
    print("   ✅ Service worker created")
    
    print("\n🎉 Asset build complete!")
    print(f"📁 Optimized files saved to: {optimized_dir.absolute()}")
    
    # Show file sizes
    print("\n📊 File sizes:")
    for file_path in optimized_dir.glob("*"):
        if file_path.is_file() and not file_path.name.endswith('.gz'):
            size = file_path.stat().st_size
            print(f"   {file_path.name}: {size:,} bytes")

def main() -> None:
    """Main entry point for the asset build script."""
    build_assets()


if __name__ == "__main__":
    main()