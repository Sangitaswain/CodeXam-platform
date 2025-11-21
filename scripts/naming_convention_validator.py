#!/usr/bin/env python3
"""
CodeXam Naming Convention Validator

This script validates naming conventions across the CodeXam codebase.
It checks Python, JavaScript, and CSS naming patterns according to established standards.

Usage:
    python scripts/naming_convention_validator.py [--check-only] [--verbose] [--output FILE]
"""

import argparse
import ast
import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
from dataclasses import dataclass
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class NamingConventionValidator:
    """Validates naming conventions across the codebase."""
    
    # Class constants for better maintainability
    MAX_FILE_SIZE = 1024 * 1024  # 1MB limit for processing
    EXCLUDED_DIRS = {'venv', '__pycache__', 'node_modules', '.git', '.pytest_cache'}
    EXCLUDED_PATTERNS = {'.min.js', '.min.css', 'test_'}
    
    def __init__(self, project_root: str, verbose: bool = False):
        self.project_root = Path(project_root)
        self.verbose = verbose
        self._setup_logging()
    
    def _setup_logging(self) -> None:
        """Configure logging based on verbosity level."""
        level = logging.DEBUG if self.verbose else logging.INFO
        logging.basicConfig(
            level=level,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%H:%M:%S'
        )
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Determine if a file should be processed based on filtering rules."""
        # Check file size
        try:
            if file_path.stat().st_size > self.MAX_FILE_SIZE:
                if self.verbose:
                    logger.warning(f"Skipping large file: {file_path}")
                return False
        except OSError:
            return False
        
        # Check if file is in excluded directory
        if any(excluded_dir in file_path.parts for excluded_dir in self.EXCLUDED_DIRS):
            return False
        
        # Check excluded patterns
        file_name = file_path.name
        if (file_name.startswith('.') or 
            any(pattern in file_name for pattern in self.EXCLUDED_PATTERNS)):
            return False
        
        return True
    
    def _get_files_by_extension(self, extension: str) -> List[Path]:
        """Get all files with given extension that should be processed."""
        pattern = f"**/*.{extension}"
        all_files = self.project_root.glob(pattern)
        return [f for f in all_files if self._should_process_file(f)]
    
    def validate_python_file(self, file_path: Path) -> List[Dict]:
        """Validate naming conventions in a Python file."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content, filename=str(file_path))
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    if not self._is_snake_case(node.name):
                        violations.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'function',
                            'name': node.name,
                            'message': f"Function '{node.name}' should use snake_case",
                            'suggested': self._to_snake_case(node.name)
                        })
                
                elif isinstance(node, ast.ClassDef):
                    if not self._is_pascal_case(node.name):
                        violations.append({
                            'file': file_path,
                            'line': node.lineno,
                            'type': 'class',
                            'name': node.name,
                            'message': f"Class '{node.name}' should use PascalCase",
                            'suggested': self._to_pascal_case(node.name)
                        })
        
        except Exception as e:
            if self.verbose:
                logger.error(f"Error parsing {file_path}: {e}")
        
        return violations
    
    def validate_javascript_file(self, file_path: Path) -> List[Dict]:
        """Validate naming conventions in a JavaScript file."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Skip namespace objects that correctly use PascalCase
            namespace_objects = [
                'CodeXamApp', 'SystemInfoModal', 'CodeXamUI', 
                'UIEnhancementModule', 'SystemCommandProcessor', 
                'SystemStatsVisualizer'
            ]
            
            # Check for PascalCase variables that should be camelCase
            var_pattern = re.compile(r'(?:const|let|var)\\s+([A-Z][a-zA-Z0-9]*)\\s*=')
            for match in var_pattern.finditer(content):
                name = match.group(1)
                if name not in namespace_objects:
                    line_num = content[:match.start()].count('\\n') + 1
                    violations.append({
                        'file': file_path,
                        'line': line_num,
                        'type': 'variable',
                        'name': name,
                        'message': f"Variable '{name}' should use camelCase",
                        'suggested': self._to_camel_case(name)
                    })
        
        except Exception as e:
            if self.verbose:
                logger.error(f"Error parsing {file_path}: {e}")
        
        return violations
    
    def validate_css_file(self, file_path: Path) -> List[Dict]:
        """Validate naming conventions in a CSS file."""
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for camelCase class names (should be kebab-case)
            class_pattern = re.compile(r'\\.([a-z][a-zA-Z0-9]*[A-Z][a-zA-Z0-9]*)')
            for match in class_pattern.finditer(content):
                name = match.group(1)
                line_num = content[:match.start()].count('\\n') + 1
                violations.append({
                    'file': file_path,
                    'line': line_num,
                    'type': 'css_class',
                    'name': name,
                    'message': f"CSS class '{name}' should use kebab-case",
                    'suggested': self._to_kebab_case(name)
                })
        
        except Exception as e:
            if self.verbose:
                logger.error(f"Error parsing {file_path}: {e}")
        
        return violations
    
    def _is_snake_case(self, name: str) -> bool:
        """Check if name is in snake_case."""
        return re.match(r'^[a-z_][a-z0-9_]*$', name) is not None
    
    def _is_pascal_case(self, name: str) -> bool:
        """Check if name is in PascalCase."""
        return re.match(r'^[A-Z][a-zA-Z0-9]*$', name) is not None
    
    def _to_snake_case(self, name: str) -> str:
        """Convert name to snake_case."""
        s1 = re.sub('([a-z0-9])([A-Z])', r'\\1_\\2', name)
        return s1.lower()
    
    def _to_camel_case(self, name: str) -> str:
        """Convert name to camelCase."""
        parts = re.split(r'[_\\-\\s]+', name.lower())
        if not parts:
            return name
        return parts[0] + ''.join(word.capitalize() for word in parts[1:])
    
    def _to_pascal_case(self, name: str) -> str:
        """Convert name to PascalCase."""
        parts = re.split(r'[_\\-\\s]+', name.lower())
        return ''.join(word.capitalize() for word in parts)
    
    def _to_kebab_case(self, name: str) -> str:
        """Convert name to kebab-case."""
        s1 = re.sub('([a-z0-9])([A-Z])', r'\\1-\\2', name)
        return s1.lower()
    
    def run_validation(self) -> Dict[str, List[Dict]]:
        """Run complete naming convention validation."""
        all_violations = {
            'python': [],
            'javascript': [],
            'css': []
        }
        
        logger.info("Starting naming convention validation...")
        
        # Validate Python files
        logger.info("Validating Python files...")
        for py_file in self.project_root.glob('**/*.py'):
            if (py_file.name.startswith('.') or 
                'venv' in str(py_file) or 
                '__pycache__' in str(py_file) or
                'test_' in py_file.name):
                continue
            violations = self.validate_python_file(py_file)
            all_violations['python'].extend(violations)
        
        # Validate JavaScript files
        logger.info("Validating JavaScript files...")
        for js_file in self.project_root.glob('**/*.js'):
            if (js_file.name.startswith('.') or 
                'node_modules' in str(js_file) or 
                'min.js' in str(js_file)):
                continue
            violations = self.validate_javascript_file(js_file)
            all_violations['javascript'].extend(violations)
        
        # Validate CSS files
        logger.info("Validating CSS files...")
        for css_file in self.project_root.glob('**/*.css'):
            if (css_file.name.startswith('.') or 
                'min.css' in str(css_file)):
                continue
            violations = self.validate_css_file(css_file)
            all_violations['css'].extend(violations)
        
        return all_violations
    
    def generate_report(self, violations: Dict[str, List[Dict]]) -> str:
        """Generate a detailed validation report."""
        report = []
        report.append("# CodeXam Naming Convention Validation Report")
        report.append("")
        
        total_violations = sum(len(v) for v in violations.values())
        report.append(f"**Total Violations Found:** {total_violations}")
        report.append("")
        
        if total_violations == 0:
            report.append("## ✅ No Naming Convention Violations Found!")
            report.append("")
            report.append("The codebase follows all established naming conventions:")
            report.append("- Python: Functions use snake_case, classes use PascalCase")
            report.append("- JavaScript: Variables use camelCase, namespace objects use PascalCase appropriately")
            report.append("- CSS: Classes use kebab-case consistently")
        else:
            for category, category_violations in violations.items():
                if not category_violations:
                    continue
                
                report.append(f"## {category.title()} Violations ({len(category_violations)})")
                report.append("")
                
                for violation in category_violations:
                    report.append(f"- **{violation['file']}:{violation['line']}**")
                    report.append(f"  - Type: {violation['type']}")
                    report.append(f"  - Current: `{violation['name']}`")
                    report.append(f"  - Suggested: `{violation['suggested']}`")
                    report.append(f"  - Message: {violation['message']}")
                    report.append("")
        
        return "\\n".join(report)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Validate naming conventions")
    parser.add_argument("--check-only", action="store_true", help="Only check for violations")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    parser.add_argument("--output", help="Output report to file")
    
    args = parser.parse_args()
    
    project_root = Path(__file__).parent.parent
    validator = NamingConventionValidator(str(project_root), args.verbose)
    
    try:
        violations = validator.run_validation()
        report = validator.generate_report(violations)
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {args.output}")
        else:
            print(report)
        
        total_violations = sum(len(v) for v in violations.values())
        if total_violations > 0:
            logger.warning(f"Found {total_violations} naming convention violations")
            sys.exit(1)
        else:
            logger.info("No naming convention violations found")
            sys.exit(0)
    
    except Exception as e:
        logger.error(f"Validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()