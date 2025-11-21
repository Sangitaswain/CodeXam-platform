#!/usr/bin/env python3
"""
CodeXam Naming Convention Fixer

This script systematically fixes naming convention inconsistencies across the codebase:
- Standardizes Python function and variable names to snake_case
- Fixes CSS class names to use kebab-case with BEM methodology
- Standardizes JavaScript variable names to camelCase
- Updates database column names to snake_case
- Fixes template variable names

Usage:
    python scripts/fix_naming_conventions.py [--dry-run] [--file-type TYPE]

Options:
    --dry-run     Show what would be changed without making changes
    --file-type   Only process specific file types (python, css, js, html, sql)
"""

import argparse
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Set


class NamingConventionFixer:
    """Fix naming convention inconsistencies across the codebase."""
    
    def __init__(self, project_root: str, dry_run: bool = False):
        """
        Initialize the naming convention fixer.
        
        Args:
            project_root: Root directory of the project
            dry_run: Whether to show changes without applying them
        """
        self.project_root = Path(project_root)
        self.dry_run = dry_run
        self.changes_made = 0
        self.files_processed = 0
        
        # Naming convention patterns
        self.python_patterns = self._get_python_patterns()
        self.css_patterns = self._get_css_patterns()
        self.js_patterns = self._get_js_patterns()
        self.html_patterns = self._get_html_patterns()
    
    def _get_python_patterns(self) -> List[Tuple[str, str, str]]:
        """Get Python naming convention fix patterns."""
        return [
            # Function names: camelCase -> snake_case
            (r'def ([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)\(', 
             lambda m: f'def {self._camel_to_snake(m.group(1))}(',
             'Function name camelCase -> snake_case'),
            
            # Variable assignments: camelCase -> snake_case
            (r'(\s+)([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)\s*=',
             lambda m: f'{m.group(1)}{self._camel_to_snake(m.group(2))} =',
             'Variable name camelCase -> snake_case'),
            
            # Class names: snake_case -> PascalCase (if needed)
            (r'class ([a-z][a-z0-9_]*[a-z0-9])\(',
             lambda m: f'class {self._snake_to_pascal(m.group(1))}(',
             'Class name snake_case -> PascalCase'),
        ]
    
    def _get_css_patterns(self) -> List[Tuple[str, str, str]]:
        """Get CSS naming convention fix patterns."""
        return [
            # CSS classes: camelCase -> kebab-case
            (r'\.([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)\b',
             lambda m: f'.{self._camel_to_kebab(m.group(1))}',
             'CSS class camelCase -> kebab-case'),
            
            # CSS classes: snake_case -> kebab-case
            (r'\.([a-z][a-z0-9_]*[a-z0-9])\b',
             lambda m: f'.{self._snake_to_kebab(m.group(1))}',
             'CSS class snake_case -> kebab-case'),
            
            # CSS IDs: camelCase -> kebab-case
            (r'#([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)\b',
             lambda m: f'#{self._camel_to_kebab(m.group(1))}',
             'CSS ID camelCase -> kebab-case'),
        ]
    
    def _get_js_patterns(self) -> List[Tuple[str, str, str]]:
        """Get JavaScript naming convention fix patterns."""
        return [
            # Variable declarations: snake_case -> camelCase
            (r'(var|let|const)\s+([a-z][a-z0-9_]*[a-z0-9])\s*=',
             lambda m: f'{m.group(1)} {self._snake_to_camel(m.group(2))} =',
             'JS variable snake_case -> camelCase'),
            
            # Function declarations: snake_case -> camelCase
            (r'function\s+([a-z][a-z0-9_]*[a-z0-9])\s*\(',
             lambda m: f'function {self._snake_to_camel(m.group(1))}(',
             'JS function snake_case -> camelCase'),
        ]
    
    def _get_html_patterns(self) -> List[Tuple[str, str, str]]:
        """Get HTML naming convention fix patterns."""
        return [
            # HTML class attributes: camelCase -> kebab-case
            (r'class="([^"]*[a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*[^"]*)"',
             lambda m: f'class="{self._fix_html_classes(m.group(1))}"',
             'HTML class camelCase -> kebab-case'),
            
            # HTML ID attributes: camelCase -> kebab-case
            (r'id="([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)"',
             lambda m: f'id="{self._camel_to_kebab(m.group(1))}"',
             'HTML ID camelCase -> kebab-case'),
        ]
    
    def _camel_to_snake(self, name: str) -> str:
        """Convert camelCase to snake_case."""
        # Insert underscore before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()
    
    def _snake_to_camel(self, name: str) -> str:
        """Convert snake_case to camelCase."""
        components = name.split('_')
        return components[0] + ''.join(word.capitalize() for word in components[1:])
    
    def _snake_to_pascal(self, name: str) -> str:
        """Convert snake_case to PascalCase."""
        return ''.join(word.capitalize() for word in name.split('_'))
    
    def _camel_to_kebab(self, name: str) -> str:
        """Convert camelCase to kebab-case."""
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    
    def _snake_to_kebab(self, name: str) -> str:
        """Convert snake_case to kebab-case."""
        return name.replace('_', '-')
    
    def _fix_html_classes(self, class_string: str) -> str:
        """Fix multiple classes in HTML class attribute."""
        classes = class_string.split()
        fixed_classes = []
        
        for cls in classes:
            # Skip Bootstrap classes and template variables
            if (cls.startswith('btn-') or cls.startswith('d-') or 
                cls.startswith('mt-') or cls.startswith('mb-') or
                cls.startswith('ms-') or cls.startswith('me-') or
                cls.startswith('p-') or cls.startswith('m-') or
                cls.startswith('col-') or cls.startswith('row') or
                cls.startswith('container') or cls.startswith('alert') or
                '{%' in cls or '{{' in cls):
                fixed_classes.append(cls)
            else:
                # Convert camelCase to kebab-case
                if re.match(r'[a-z][a-zA-Z0-9]*[A-Z]', cls):
                    fixed_classes.append(self._camel_to_kebab(cls))
                else:
                    fixed_classes.append(cls)
        
        return ' '.join(fixed_classes)
    
    def fix_python_file(self, file_path: Path) -> int:
        """Fix naming conventions in a Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes = 0
            
            for pattern, replacement, description in self.python_patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    if callable(replacement):
                        content = re.sub(pattern, replacement, content)
                    else:
                        content = re.sub(pattern, replacement, content)
                    
                    new_matches = len(matches)
                    changes += new_matches
                    
                    if not self.dry_run and new_matches > 0:
                        print(f"  ✅ {description}: {new_matches} fixes")
            
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    print(f"  📝 Would fix {changes} naming issues")
            
            return changes
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return 0
    
    def fix_css_file(self, file_path: Path) -> int:
        """Fix naming conventions in a CSS file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes = 0
            
            for pattern, replacement, description in self.css_patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    if callable(replacement):
                        content = re.sub(pattern, replacement, content)
                    else:
                        content = re.sub(pattern, replacement, content)
                    
                    new_matches = len(matches)
                    changes += new_matches
                    
                    if not self.dry_run and new_matches > 0:
                        print(f"  ✅ {description}: {new_matches} fixes")
            
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    print(f"  📝 Would fix {changes} naming issues")
            
            return changes
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return 0
    
    def fix_js_file(self, file_path: Path) -> int:
        """Fix naming conventions in a JavaScript file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes = 0
            
            for pattern, replacement, description in self.js_patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    if callable(replacement):
                        content = re.sub(pattern, replacement, content)
                    else:
                        content = re.sub(pattern, replacement, content)
                    
                    new_matches = len(matches)
                    changes += new_matches
                    
                    if not self.dry_run and new_matches > 0:
                        print(f"  ✅ {description}: {new_matches} fixes")
            
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    print(f"  📝 Would fix {changes} naming issues")
            
            return changes
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return 0
    
    def fix_html_file(self, file_path: Path) -> int:
        """Fix naming conventions in an HTML file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            changes = 0
            
            for pattern, replacement, description in self.html_patterns:
                matches = list(re.finditer(pattern, content))
                if matches:
                    if callable(replacement):
                        content = re.sub(pattern, replacement, content)
                    else:
                        content = re.sub(pattern, replacement, content)
                    
                    new_matches = len(matches)
                    changes += new_matches
                    
                    if not self.dry_run and new_matches > 0:
                        print(f"  ✅ {description}: {new_matches} fixes")
            
            if content != original_content:
                if not self.dry_run:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                else:
                    print(f"  📝 Would fix {changes} naming issues")
            
            return changes
            
        except Exception as e:
            print(f"  ❌ Error processing {file_path}: {e}")
            return 0
    
    def process_directory(self, directory: Path, file_types: Set[str] = None) -> None:
        """Process all files in a directory."""
        if file_types is None:
            file_types = {'python', 'css', 'js', 'html'}
        
        # File type mappings
        type_mappings = {
            'python': ('.py',),
            'css': ('.css',),
            'js': ('.js',),
            'html': ('.html',),
        }
        
        # Get all relevant files
        files_to_process = []
        for file_type in file_types:
            if file_type in type_mappings:
                for ext in type_mappings[file_type]:
                    files_to_process.extend(directory.rglob(f'*{ext}'))
        
        # Process each file
        for file_path in sorted(files_to_process):
            # Skip certain directories
            if any(part in str(file_path) for part in ['.git', '__pycache__', 'node_modules', '.venv']):
                continue
            
            print(f"📁 Processing: {file_path.relative_to(self.project_root)}")
            self.files_processed += 1
            
            changes = 0
            if file_path.suffix == '.py' and 'python' in file_types:
                changes = self.fix_python_file(file_path)
            elif file_path.suffix == '.css' and 'css' in file_types:
                changes = self.fix_css_file(file_path)
            elif file_path.suffix == '.js' and 'js' in file_types:
                changes = self.fix_js_file(file_path)
            elif file_path.suffix == '.html' and 'html' in file_types:
                changes = self.fix_html_file(file_path)
            
            self.changes_made += changes
            
            if changes == 0:
                print(f"  ✅ No naming issues found")
    
    def run_fixes(self, file_types: Set[str] = None) -> None:
        """Run naming convention fixes across the codebase."""
        print("🚀 Starting CodeXam naming convention fixes...")
        print(f"   Mode: {'Dry Run' if self.dry_run else 'Apply Changes'}")
        print(f"   Root: {self.project_root}")
        
        if file_types:
            print(f"   Types: {', '.join(file_types)}")
        
        print()
        
        # Process the project directory
        self.process_directory(self.project_root, file_types)
        
        print()
        print("✅ Naming convention fixes completed!")
        print(f"   Files processed: {self.files_processed}")
        print(f"   Changes made: {self.changes_made}")
        
        if self.dry_run and self.changes_made > 0:
            print()
            print("💡 Run without --dry-run to apply these changes")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Fix CodeXam naming conventions")
    parser.add_argument("--dry-run", action="store_true", help="Show changes without applying them")
    parser.add_argument("--file-type", choices=['python', 'css', 'js', 'html'], 
                       help="Only process specific file types")
    
    args = parser.parse_args()
    
    # Get project root (assuming script is in scripts/ directory)
    project_root = Path(__file__).parent.parent
    
    # Determine file types to process
    file_types = None
    if args.file_type:
        file_types = {args.file_type}
    
    # Initialize fixer
    fixer = NamingConventionFixer(project_root, dry_run=args.dry_run)
    
    try:
        fixer.run_fixes(file_types)
    except KeyboardInterrupt:
        print("\n❌ Naming convention fixes cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Naming convention fixes failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()