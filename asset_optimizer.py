#!/usr/bin/env python3
"""
Asset Optimization System for CodeXam Platform

This module provides comprehensive asset optimization including:
- CSS and JavaScript minification
- Image optimization and compression
- Asset bundling and code splitting
- Browser caching optimization
- Performance monitoring and analysis

Version: 2.0.0
Author: CodeXam Development Team
"""

import os
import re
import json
import gzip
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import time
from dataclasses import dataclass
import shutil
import subprocess

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class AssetInfo:
    """Information about an optimized asset."""
    original_path: str
    optimized_path: str
    original_size: int
    optimized_size: int
    compression_ratio: float
    hash: str
    last_modified: float


class CSSMinifier:
    """CSS minification and optimization."""
    
    def __init__(self):
        self.stats = {'files_processed': 0, 'bytes_saved': 0}
    
    def minify_css(self, css_content: str) -> str:
        """Minify CSS content."""
        # Remove comments
        css_content = re.sub(r'/\*.*?\*/', '', css_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        css_content = re.sub(r'\s+', ' ', css_content)
        
        # Remove whitespace around specific characters
        css_content = re.sub(r'\s*([{}:;,>+~])\s*', r'\1', css_content)
        
        # Remove trailing semicolons before closing braces
        css_content = re.sub(r';\s*}', '}', css_content)
        
        # Remove unnecessary quotes from URLs
        css_content = re.sub(r'url\(["\']([^"\']*)["\']?\)', r'url(\1)', css_content)
        
        # Convert hex colors to shorter format where possible
        css_content = re.sub(r'#([0-9a-fA-F])\1([0-9a-fA-F])\2([0-9a-fA-F])\3', r'#\1\2\3', css_content)
        
        # Remove leading zeros from numbers
        css_content = re.sub(r'(\W)0+(\d+)', r'\1\2', css_content)
        
        # Remove unnecessary units for zero values
        css_content = re.sub(r'(\W)0(px|em|rem|%|pt|pc|in|cm|mm|ex)', r'\g<1>0', css_content)
        
        return css_content.strip()
    
    def process_file(self, input_path: str, output_path: str) -> AssetInfo:
        """Process a single CSS file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        minified_content = self.minify_css(original_content)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_content)
        
        original_size = len(original_content.encode('utf-8'))
        optimized_size = len(minified_content.encode('utf-8'))
        compression_ratio = (original_size - optimized_size) / original_size * 100
        
        # Generate hash for cache busting
        file_hash = hashlib.md5(minified_content.encode('utf-8')).hexdigest()[:8]
        
        self.stats['files_processed'] += 1
        self.stats['bytes_saved'] += (original_size - optimized_size)
        
        return AssetInfo(
            original_path=input_path,
            optimized_path=output_path,
            original_size=original_size,
            optimized_size=optimized_size,
            compression_ratio=compression_ratio,
            hash=file_hash,
            last_modified=time.time()
        )


class JSMinifier:
    """JavaScript minification and optimization."""
    
    def __init__(self):
        self.stats = {'files_processed': 0, 'bytes_saved': 0}
    
    def minify_js(self, js_content: str) -> str:
        """Basic JavaScript minification."""
        # Remove single-line comments (but preserve URLs)
        js_content = re.sub(r'(?<!:)//.*?(?=\n|$)', '', js_content)
        
        # Remove multi-line comments
        js_content = re.sub(r'/\*.*?\*/', '', js_content, flags=re.DOTALL)
        
        # Remove unnecessary whitespace
        js_content = re.sub(r'\s+', ' ', js_content)
        
        # Remove whitespace around operators and punctuation
        js_content = re.sub(r'\s*([{}();,=+\-*/<>!&|])\s*', r'\1', js_content)
        
        # Remove whitespace after keywords
        keywords = ['var', 'let', 'const', 'function', 'return', 'if', 'else', 'for', 'while', 'do', 'switch', 'case', 'break', 'continue']
        for keyword in keywords:
            js_content = re.sub(rf'\b{keyword}\s+', f'{keyword} ', js_content)
        
        return js_content.strip()
    
    def process_file(self, input_path: str, output_path: str) -> AssetInfo:
        """Process a single JavaScript file."""
        with open(input_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        minified_content = self.minify_js(original_content)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(minified_content)
        
        original_size = len(original_content.encode('utf-8'))
        optimized_size = len(minified_content.encode('utf-8'))
        compression_ratio = (original_size - optimized_size) / original_size * 100
        
        # Generate hash for cache busting
        file_hash = hashlib.md5(minified_content.encode('utf-8')).hexdigest()[:8]
        
        self.stats['files_processed'] += 1
        self.stats['bytes_saved'] += (original_size - optimized_size)
        
        return AssetInfo(
            original_path=input_path,
            optimized_path=output_path,
            original_size=original_size,
            optimized_size=optimized_size,
            compression_ratio=compression_ratio,
            hash=file_hash,
            last_modified=time.time()
        )


class AssetBundler:
    """Asset bundling and code splitting."""
    
    def __init__(self):
        self.bundles = {}
        self.stats = {'bundles_created': 0, 'total_size_reduction': 0}
    
    def create_css_bundle(self, files: List[str], output_path: str, 
                         minify: bool = True) -> AssetInfo:
        """Create a CSS bundle from multiple files."""
        combined_content = []
        total_original_size = 0
        
        for file_path in files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append(f"/* {os.path.basename(file_path)} */")
                    combined_content.append(content)
                    total_original_size += len(content.encode('utf-8'))
        
        bundle_content = '\n'.join(combined_content)
        
        if minify:
            minifier = CSSMinifier()
            bundle_content = minifier.minify_css(bundle_content)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bundle_content)
        
        optimized_size = len(bundle_content.encode('utf-8'))
        compression_ratio = (total_original_size - optimized_size) / total_original_size * 100
        
        # Generate hash for cache busting
        file_hash = hashlib.md5(bundle_content.encode('utf-8')).hexdigest()[:8]
        
        self.stats['bundles_created'] += 1
        self.stats['total_size_reduction'] += (total_original_size - optimized_size)
        
        return AssetInfo(
            original_path=','.join(files),
            optimized_path=output_path,
            original_size=total_original_size,
            optimized_size=optimized_size,
            compression_ratio=compression_ratio,
            hash=file_hash,
            last_modified=time.time()
        )
    
    def create_js_bundle(self, files: List[str], output_path: str, 
                        minify: bool = True) -> AssetInfo:
        """Create a JavaScript bundle from multiple files."""
        combined_content = []
        total_original_size = 0
        
        for file_path in files:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    combined_content.append(f"/* {os.path.basename(file_path)} */")
                    combined_content.append(content)
                    combined_content.append('')  # Add separator
                    total_original_size += len(content.encode('utf-8'))
        
        bundle_content = '\n'.join(combined_content)
        
        if minify:
            minifier = JSMinifier()
            bundle_content = minifier.minify_js(bundle_content)
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(bundle_content)
        
        optimized_size = len(bundle_content.encode('utf-8'))
        compression_ratio = (total_original_size - optimized_size) / total_original_size * 100
        
        # Generate hash for cache busting
        file_hash = hashlib.md5(bundle_content.encode('utf-8')).hexdigest()[:8]
        
        self.stats['bundles_created'] += 1
        self.stats['total_size_reduction'] += (total_original_size - optimized_size)
        
        return AssetInfo(
            original_path=','.join(files),
            optimized_path=output_path,
            original_size=total_original_size,
            optimized_size=optimized_size,
            compression_ratio=compression_ratio,
            hash=file_hash,
            last_modified=time.time()
        )


class GzipCompressor:
    """Gzip compression for assets."""
    
    def __init__(self):
        self.stats = {'files_compressed': 0, 'compression_ratio': 0}
    
    def compress_file(self, input_path: str, output_path: str = None) -> AssetInfo:
        """Compress a file with gzip."""
        if output_path is None:
            output_path = input_path + '.gz'
        
        with open(input_path, 'rb') as f_in:
            original_content = f_in.read()
        
        with gzip.open(output_path, 'wb') as f_out:
            f_out.write(original_content)
        
        original_size = len(original_content)
        compressed_size = os.path.getsize(output_path)
        compression_ratio = (original_size - compressed_size) / original_size * 100
        
        # Generate hash
        file_hash = hashlib.md5(original_content).hexdigest()[:8]
        
        self.stats['files_compressed'] += 1
        self.stats['compression_ratio'] += compression_ratio
        
        return AssetInfo(
            original_path=input_path,
            optimized_path=output_path,
            original_size=original_size,
            optimized_size=compressed_size,
            compression_ratio=compression_ratio,
            hash=file_hash,
            last_modified=time.time()
        )


class AssetOptimizer:
    """Main asset optimization coordinator."""
    
    def __init__(self, static_dir: str = 'static', output_dir: str = 'static/optimized'):
        self.static_dir = Path(static_dir)
        self.output_dir = Path(output_dir)
        self.css_minifier = CSSMinifier()
        self.js_minifier = JSMinifier()
        self.bundler = AssetBundler()
        self.compressor = GzipCompressor()
        
        # Asset registry for cache busting
        self.asset_registry = {}
        self.registry_file = self.output_dir / 'asset_registry.json'
        
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing registry
        self._load_registry()
    
    def _load_registry(self):
        """Load existing asset registry."""
        if self.registry_file.exists():
            try:
                with open(self.registry_file, 'r') as f:
                    self.asset_registry = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load asset registry: {e}")
                self.asset_registry = {}
    
    def _save_registry(self):
        """Save asset registry to file."""
        try:
            with open(self.registry_file, 'w') as f:
                json.dump(self.asset_registry, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save asset registry: {e}")
    
    def optimize_css_files(self) -> List[AssetInfo]:
        """Optimize all CSS files."""
        css_files = list(self.static_dir.glob('css/*.css'))
        optimized_assets = []
        
        logger.info(f"Optimizing {len(css_files)} CSS files...")
        
        for css_file in css_files:
            output_file = self.output_dir / 'css' / css_file.name
            
            try:
                asset_info = self.css_minifier.process_file(str(css_file), str(output_file))
                optimized_assets.append(asset_info)
                
                # Update registry
                self.asset_registry[f'css/{css_file.name}'] = {
                    'optimized_path': f'optimized/css/{css_file.name}',
                    'hash': asset_info.hash,
                    'size': asset_info.optimized_size,
                    'compression_ratio': asset_info.compression_ratio
                }
                
                logger.info(f"Optimized {css_file.name}: {asset_info.compression_ratio:.1f}% reduction")
                
            except Exception as e:
                logger.error(f"Failed to optimize {css_file}: {e}")
        
        return optimized_assets
    
    def optimize_js_files(self) -> List[AssetInfo]:
        """Optimize all JavaScript files."""
        js_files = list(self.static_dir.glob('js/*.js'))
        optimized_assets = []
        
        logger.info(f"Optimizing {len(js_files)} JavaScript files...")
        
        for js_file in js_files:
            output_file = self.output_dir / 'js' / js_file.name
            
            try:
                asset_info = self.js_minifier.process_file(str(js_file), str(output_file))
                optimized_assets.append(asset_info)
                
                # Update registry
                self.asset_registry[f'js/{js_file.name}'] = {
                    'optimized_path': f'optimized/js/{js_file.name}',
                    'hash': asset_info.hash,
                    'size': asset_info.optimized_size,
                    'compression_ratio': asset_info.compression_ratio
                }
                
                logger.info(f"Optimized {js_file.name}: {asset_info.compression_ratio:.1f}% reduction")
                
            except Exception as e:
                logger.error(f"Failed to optimize {js_file}: {e}")
        
        return optimized_assets
    
    def create_bundles(self) -> List[AssetInfo]:
        """Create optimized asset bundles."""
        bundles = []
        
        # Define bundle configurations
        bundle_configs = [
            {
                'name': 'core.css',
                'type': 'css',
                'files': [
                    'static/css/style.css',
                    'static/css/components.css',
                    'static/css/enhanced-ui.css'
                ]
            },
            {
                'name': 'core.js',
                'type': 'js',
                'files': [
                    'static/js/main.js',
                    'static/js/codexam-modules.js',
                    'static/js/ajax-handler.js'
                ]
            },
            {
                'name': 'editor.js',
                'type': 'js',
                'files': [
                    'static/js/enhanced-editor.js',
                    'static/js/submission-handler.js'
                ]
            }
        ]
        
        logger.info("Creating asset bundles...")
        
        for config in bundle_configs:
            output_path = str(self.output_dir / config['name'])
            
            try:
                if config['type'] == 'css':
                    asset_info = self.bundler.create_css_bundle(
                        config['files'], output_path, minify=True
                    )
                elif config['type'] == 'js':
                    asset_info = self.bundler.create_js_bundle(
                        config['files'], output_path, minify=True
                    )
                
                bundles.append(asset_info)
                
                # Update registry
                self.asset_registry[config['name']] = {
                    'optimized_path': f"optimized/{config['name']}",
                    'hash': asset_info.hash,
                    'size': asset_info.optimized_size,
                    'compression_ratio': asset_info.compression_ratio,
                    'bundle': True,
                    'source_files': config['files']
                }
                
                logger.info(f"Created bundle {config['name']}: {asset_info.compression_ratio:.1f}% reduction")
                
            except Exception as e:
                logger.error(f"Failed to create bundle {config['name']}: {e}")
        
        return bundles
    
    def compress_assets(self) -> List[AssetInfo]:
        """Compress optimized assets with gzip."""
        compressed_assets = []
        
        # Compress CSS and JS files
        for file_type in ['css', 'js']:
            type_dir = self.output_dir / file_type
            if type_dir.exists():
                for asset_file in type_dir.glob(f'*.{file_type}'):
                    try:
                        asset_info = self.compressor.compress_file(str(asset_file))
                        compressed_assets.append(asset_info)
                        
                        # Update registry with gzip info
                        registry_key = f"{file_type}/{asset_file.name}"
                        if registry_key in self.asset_registry:
                            self.asset_registry[registry_key]['gzip_path'] = f"optimized/{file_type}/{asset_file.name}.gz"
                            self.asset_registry[registry_key]['gzip_size'] = asset_info.optimized_size
                            self.asset_registry[registry_key]['gzip_ratio'] = asset_info.compression_ratio
                        
                        logger.info(f"Compressed {asset_file.name}: {asset_info.compression_ratio:.1f}% reduction")
                        
                    except Exception as e:
                        logger.error(f"Failed to compress {asset_file}: {e}")
        
        # Compress bundles
        for bundle_file in self.output_dir.glob('*.css'):
            try:
                asset_info = self.compressor.compress_file(str(bundle_file))
                compressed_assets.append(asset_info)
                
                # Update registry
                if bundle_file.name in self.asset_registry:
                    self.asset_registry[bundle_file.name]['gzip_path'] = f"optimized/{bundle_file.name}.gz"
                    self.asset_registry[bundle_file.name]['gzip_size'] = asset_info.optimized_size
                    self.asset_registry[bundle_file.name]['gzip_ratio'] = asset_info.compression_ratio
                
            except Exception as e:
                logger.error(f"Failed to compress bundle {bundle_file}: {e}")
        
        for bundle_file in self.output_dir.glob('*.js'):
            try:
                asset_info = self.compressor.compress_file(str(bundle_file))
                compressed_assets.append(asset_info)
                
                # Update registry
                if bundle_file.name in self.asset_registry:
                    self.asset_registry[bundle_file.name]['gzip_path'] = f"optimized/{bundle_file.name}.gz"
                    self.asset_registry[bundle_file.name]['gzip_size'] = asset_info.optimized_size
                    self.asset_registry[bundle_file.name]['gzip_ratio'] = asset_info.compression_ratio
                
            except Exception as e:
                logger.error(f"Failed to compress bundle {bundle_file}: {e}")
        
        return compressed_assets
    
    def optimize_all(self) -> Dict[str, Any]:
        """Run complete asset optimization."""
        start_time = time.time()
        
        logger.info("Starting complete asset optimization...")
        
        # Optimize individual files
        css_assets = self.optimize_css_files()
        js_assets = self.optimize_js_files()
        
        # Create bundles
        bundles = self.create_bundles()
        
        # Compress assets
        compressed_assets = self.compress_assets()
        
        # Save registry
        self._save_registry()
        
        # Calculate statistics
        total_time = time.time() - start_time
        total_original_size = sum(asset.original_size for asset in css_assets + js_assets + bundles)
        total_optimized_size = sum(asset.optimized_size for asset in css_assets + js_assets + bundles)
        total_compression_ratio = (total_original_size - total_optimized_size) / total_original_size * 100 if total_original_size > 0 else 0
        
        stats = {
            'optimization_time': round(total_time, 2),
            'css_files_optimized': len(css_assets),
            'js_files_optimized': len(js_assets),
            'bundles_created': len(bundles),
            'files_compressed': len(compressed_assets),
            'total_original_size': total_original_size,
            'total_optimized_size': total_optimized_size,
            'total_compression_ratio': round(total_compression_ratio, 2),
            'bytes_saved': total_original_size - total_optimized_size,
            'css_stats': self.css_minifier.stats,
            'js_stats': self.js_minifier.stats,
            'bundle_stats': self.bundler.stats,
            'compression_stats': self.compressor.stats
        }
        
        logger.info(f"Asset optimization completed in {total_time:.2f}s")
        logger.info(f"Total size reduction: {total_compression_ratio:.1f}% ({stats['bytes_saved']} bytes saved)")
        
        return stats
    
    def get_asset_url(self, asset_path: str, use_hash: bool = True) -> str:
        """Get optimized asset URL with optional cache busting."""
        if asset_path in self.asset_registry:
            asset_info = self.asset_registry[asset_path]
            optimized_path = asset_info['optimized_path']
            
            if use_hash:
                # Add hash for cache busting
                base_path, ext = os.path.splitext(optimized_path)
                return f"{base_path}.{asset_info['hash']}{ext}"
            else:
                return optimized_path
        
        # Fallback to original path
        return asset_path
    
    def get_registry(self) -> Dict[str, Any]:
        """Get the complete asset registry."""
        return self.asset_registry.copy()


def create_cache_headers_config() -> str:
    """Create Apache/Nginx cache headers configuration."""
    apache_config = r"""
# Apache Cache Headers Configuration for CodeXam Assets

<IfModule mod_expires.c>
    ExpiresActive On
    
    # CSS and JavaScript - 1 year (with versioning)
    ExpiresByType text/css "access plus 1 year"
    ExpiresByType application/javascript "access plus 1 year"
    ExpiresByType text/javascript "access plus 1 year"
    
    # Images - 1 month
    ExpiresByType image/png "access plus 1 month"
    ExpiresByType image/jpg "access plus 1 month"
    ExpiresByType image/jpeg "access plus 1 month"
    ExpiresByType image/gif "access plus 1 month"
    ExpiresByType image/svg+xml "access plus 1 month"
    ExpiresByType image/webp "access plus 1 month"
    
    # Fonts - 1 year
    ExpiresByType font/woff "access plus 1 year"
    ExpiresByType font/woff2 "access plus 1 year"
    ExpiresByType application/font-woff "access plus 1 year"
    ExpiresByType application/font-woff2 "access plus 1 year"
    
    # HTML - 1 hour
    ExpiresByType text/html "access plus 1 hour"
</IfModule>

<IfModule mod_headers.c>
    # Add cache control headers
    <FilesMatch "\.(css|js|png|jpg|jpeg|gif|svg|woff|woff2)$">
        Header set Cache-Control "public, max-age=31536000"
    </FilesMatch>
    
    <FilesMatch "\.(html)$">
        Header set Cache-Control "public, max-age=3600"
    </FilesMatch>
    
    # Enable gzip compression
    <FilesMatch "\.(css|js|html|xml|txt)$">
        Header set Vary "Accept-Encoding"
    </FilesMatch>
</IfModule>

# Gzip Compression
<IfModule mod_deflate.c>
    AddOutputFilterByType DEFLATE text/plain
    AddOutputFilterByType DEFLATE text/html
    AddOutputFilterByType DEFLATE text/xml
    AddOutputFilterByType DEFLATE text/css
    AddOutputFilterByType DEFLATE application/xml
    AddOutputFilterByType DEFLATE application/xhtml+xml
    AddOutputFilterByType DEFLATE application/rss+xml
    AddOutputFilterByType DEFLATE application/javascript
    AddOutputFilterByType DEFLATE application/x-javascript
    AddOutputFilterByType DEFLATE application/json
</IfModule>
"""
    
    nginx_config = r"""
# Nginx Cache Headers Configuration for CodeXam Assets

location ~* \.(css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    add_header Vary "Accept-Encoding";
    
    # Serve gzipped version if available
    gzip_static on;
}

location ~* \.(png|jpg|jpeg|gif|svg|webp)$ {
    expires 1M;
    add_header Cache-Control "public";
}

location ~* \.(woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public";
}

location ~* \.html$ {
    expires 1h;
    add_header Cache-Control "public";
}

# Gzip compression
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types
    text/plain
    text/css
    text/xml
    text/javascript
    application/javascript
    application/xml+rss
    application/json;
"""
    
    return f"# Cache Headers Configuration\n\n## Apache Configuration\n{apache_config}\n\n## Nginx Configuration\n{nginx_config}"


if __name__ == '__main__':
    # Run asset optimization
    optimizer = AssetOptimizer()
    
    try:
        stats = optimizer.optimize_all()
        
        print("\n" + "="*50)
        print("ASSET OPTIMIZATION RESULTS")
        print("="*50)
        
        print(f"Optimization completed in: {stats['optimization_time']}s")
        print(f"CSS files optimized: {stats['css_files_optimized']}")
        print(f"JavaScript files optimized: {stats['js_files_optimized']}")
        print(f"Bundles created: {stats['bundles_created']}")
        print(f"Files compressed: {stats['files_compressed']}")
        print(f"Total size reduction: {stats['total_compression_ratio']}%")
        print(f"Bytes saved: {stats['bytes_saved']:,} bytes")
        
        # Create cache headers configuration
        cache_config = create_cache_headers_config()
        with open('cache_headers_config.txt', 'w') as f:
            f.write(cache_config)
        
        print(f"\nCache headers configuration saved to: cache_headers_config.txt")
        print(f"Asset registry saved to: {optimizer.registry_file}")
        
    except Exception as e:
        print(f"Asset optimization failed: {e}")
        import traceback
        traceback.print_exc()