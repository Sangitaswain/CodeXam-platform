"""
Judge Security Enhancements

This module provides enhanced security features for the CodeXam judge system,
including malicious code detection, resource monitoring, and secure execution.
"""

import ast
import json
import logging
import os
import re
import signal
import subprocess
import sys
import tempfile
import threading
import time
from contextlib import contextmanager
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set, Tuple

# Configure logging
logger = logging.getLogger(__name__)

@dataclass
class SecurityConfig:
    """Configuration for security settings."""
    max_execution_time: int = 5
    max_memory_mb: int = 128
    max_output_size: int = 10240
    max_recursion_depth: int = 1000
    allow_file_operations: bool = False
    allow_network: bool = False
    allow_subprocess: bool = False

class SecurityViolation(Exception):
    """Exception raised when security violations are detected."""
    def __init__(self, message: str, violation_type: str):
        super().__init__(message)
        self.violation_type = violation_type

class MaliciousCodeDetector:
    """Detects potentially malicious code patterns."""
    
    # Python dangerous imports and functions
    PYTHON_DANGEROUS_IMPORTS = {
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'http', 'ftplib', 'smtplib', 'telnetlib', 'webbrowser',
        'tempfile', 'shutil', 'glob', 'pickle', 'marshal',
        'importlib', 'pkgutil', 'zipimport', 'runpy', 'ctypes',
        'multiprocessing', 'threading', 'asyncio', '__builtin__'
    }
    
    PYTHON_DANGEROUS_FUNCTIONS = {
        '__import__', 'eval', 'exec', 'compile', 'open', 'file',
        'input', 'raw_input', 'globals', 'locals', 'vars', 'dir',
        'getattr', 'setattr', 'delattr', 'hasattr', 'callable',
        'exit', 'quit', 'help', 'copyright', 'credits', 'license',
        'reload', 'execfile'
    }
    
    PYTHON_DANGEROUS_ATTRIBUTES = {
        '__class__', '__bases__', '__subclasses__', '__mro__',
        '__dict__', '__globals__', '__code__', '__closure__',
        '__defaults__', '__kwdefaults__', '__annotations__',
        '__builtins__', '__file__', '__name__', '__package__'
    }
    
    # JavaScript dangerous patterns
    JS_DANGEROUS_PATTERNS = {
        'require(', 'import(', 'eval(', 'Function(', 'constructor',
        'process.', 'global.', '__dirname', '__filename',
        'fs.', 'child_process', 'os.', 'path.', 'util.',
        'http.', 'https.', 'net.', 'dgram.', 'dns.',
        'crypto.', 'buffer.', 'stream.', 'events.',
        'setTimeout', 'setInterval', 'setImmediate',
        'vm.', 'worker_threads', 'cluster.',
        'new Function', 'new Worker', 'XMLHttpRequest',
        'fetch(', 'WebSocket', 'EventSource', 'document.',
        'window.', 'location.', 'navigator.'
    }
    
    @classmethod
    def scan_python_code(cls, code: str) -> List[str]:
        """Scan Python code for malicious patterns using AST analysis."""
        violations = []
        
        try:
            # Parse the code into an AST
            tree = ast.parse(code)
            
            # Walk through all nodes in the AST
            for node in ast.walk(tree):
                # Check for dangerous imports
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name in cls.PYTHON_DANGEROUS_IMPORTS:
                            violations.append(f"Dangerous import detected: {alias.name}")
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module in cls.PYTHON_DANGEROUS_IMPORTS:
                        violations.append(f"Dangerous import from: {node.module}")
                
                # Check for dangerous function calls
                elif isinstance(node, ast.Call):
                    if isinstance(node.func, ast.Name):
                        if node.func.id in cls.PYTHON_DANGEROUS_FUNCTIONS:
                            violations.append(f"Dangerous function call: {node.func.id}")
                    elif isinstance(node.func, ast.Attribute):
                        if node.func.attr in cls.PYTHON_DANGEROUS_FUNCTIONS:
                            violations.append(f"Dangerous method call: {node.func.attr}")
                
                # Check for dangerous attribute access
                elif isinstance(node, ast.Attribute):
                    if node.attr in cls.PYTHON_DANGEROUS_ATTRIBUTES:
                        violations.append(f"Dangerous attribute access: {node.attr}")
                
                # Check for exec/eval in string form
                elif isinstance(node, ast.Str):
                    if any(dangerous in node.s.lower() for dangerous in ['exec(', 'eval(', '__import__']):
                        violations.append("Dangerous string content detected")
        
        except SyntaxError as e:
            # If there's a syntax error, we'll let the execution handle it
            logger.debug(f"Syntax error during AST parsing: {e}")
        
        # Additional string-based checks for patterns that might not be caught by AST
        code_lower = code.lower()
        string_patterns = [
            'import os', 'import sys', 'subprocess.', '__import__(',
            'eval(', 'exec(', 'open(', 'file(', 'input(', 'raw_input(',
            'globals(', 'locals(', 'vars(', 'dir('
        ]
        
        for pattern in string_patterns:
            if pattern in code_lower:
                violations.append(f"Dangerous pattern in code: {pattern}")
        
        return violations
    
    @classmethod
    def scan_javascript_code(cls, code: str) -> List[str]:
        """Scan JavaScript code for malicious patterns."""
        violations = []
        code_lower = code.lower()
        
        for pattern in cls.JS_DANGEROUS_PATTERNS:
            if pattern.lower() in code_lower:
                violations.append(f"Dangerous JavaScript pattern: {pattern}")
        
        # Check for dynamic code execution patterns
        dynamic_patterns = [
            'eval(', 'function(', 'new function', 'settimeout(',
            'setinterval(', 'constructor(', '.constructor'
        ]
        
        for pattern in dynamic_patterns:
            if pattern in code_lower:
                violations.append(f"Dynamic code execution pattern: {pattern}")
        
        return violations
    
    @classmethod
    def scan_code(cls, code: str, language: str) -> List[str]:
        """Scan code for malicious patterns based on language."""
        language = language.lower()
        
        if language == 'python':
            return cls.scan_python_code(code)
        elif language == 'javascript':
            return cls.scan_javascript_code(code)
        else:
            # For other languages, perform basic pattern matching
            violations = []
            general_dangerous = [
                'system(', 'exec(', 'shell_exec', 'passthru',
                'popen(', 'proc_open', 'shell(', 'cmd('
            ]
            
            code_lower = code.lower()
            for pattern in general_dangerous:
                if pattern in code_lower:
                    violations.append(f"Potentially dangerous pattern: {pattern}")
            
            return violations

class ResourceMonitor:
    """Monitors resource usage during code execution."""
    
    def __init__(self, config: SecurityConfig):
        self.config = config
        self.start_time = None
        self.peak_memory = 0
        self.monitoring = False
        
    @contextmanager
    def monitor_execution(self):
        """Context manager for monitoring code execution."""
        self.start_time = time.time()
        self.peak_memory = 0
        self.monitoring = True
        
        try:
            yield self
        finally:
            self.monitoring = False
    
    def check_limits(self) -> Optional[str]:
        """Check if any resource limits have been exceeded."""
        if not self.monitoring or not self.start_time:
            return None
        
        # Check execution time
        elapsed = time.time() - self.start_time
        if elapsed > self.config.max_execution_time:
            return f"Execution timeout: {elapsed:.2f}s > {self.config.max_execution_time}s"
        
        # Memory checking would require platform-specific implementation
        # For now, we rely on the subprocess timeout and system limits
        
        return None
    
    def get_stats(self) -> Dict[str, Any]:
        """Get current resource usage statistics."""
        elapsed = time.time() - self.start_time if self.start_time else 0
        return {
            'execution_time': elapsed,
            'peak_memory_bytes': self.peak_memory,
            'peak_memory_mb': self.peak_memory / (1024 * 1024) if self.peak_memory else 0
        }

class SecureCodeExecutor:
    """Secure code executor with enhanced security features."""
    
    def __init__(self, config: SecurityConfig = None):
        self.config = config or SecurityConfig()
        self.temp_dir = tempfile.mkdtemp(prefix='codexam_secure_')
        
    def __del__(self):
        """Cleanup temporary directory."""
        try:
            import shutil
            shutil.rmtree(self.temp_dir, ignore_errors=True)
        except Exception:
            pass
    
    def execute_code_securely(self, language: str, code: str, test_cases: List[Dict]) -> Dict[str, Any]:
        """Execute code with comprehensive security checks."""
        start_time = time.time()
        
        # Step 1: Scan for malicious code
        violations = MaliciousCodeDetector.scan_code(code, language)
        if violations:
            logger.warning(f"Security violations detected: {violations}")
            return {
                'result': 'ERROR',
                'message': 'Security violation detected in code',
                'test_results': [],
                'execution_time': 0,
                'memory_used': 0,
                'security_violations': violations,
                'error_details': {
                    'type': 'SECURITY_VIOLATION',
                    'violations': violations
                }
            }
        
        # Step 2: Execute with monitoring
        monitor = ResourceMonitor(self.config)
        
        try:
            with monitor.monitor_execution():
                if language.lower() == 'python':
                    return self._execute_python_secure(code, test_cases, monitor)
                elif language.lower() == 'javascript':
                    return self._execute_javascript_secure(code, test_cases, monitor)
                else:
                    return {
                        'result': 'ERROR',
                        'message': f'Language {language} not supported in secure mode',
                        'test_results': [],
                        'execution_time': time.time() - start_time,
                        'memory_used': 0,
                        'security_violations': []
                    }
        
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Secure execution failed: {e}")
            return {
                'result': 'ERROR',
                'message': f'Execution failed: {str(e)}',
                'test_results': [],
                'execution_time': execution_time,
                'memory_used': 0,
                'security_violations': [],
                'error_details': {
                    'type': type(e).__name__,
                    'message': str(e)
                }
            }
    
    def _execute_python_secure(self, code: str, test_cases: List[Dict], monitor: ResourceMonitor) -> Dict[str, Any]:
        """Execute Python code with security restrictions."""
        # Create secure wrapper
        secure_wrapper = self._create_python_security_wrapper(code, test_cases)
        
        # Write to temporary file
        script_path = os.path.join(self.temp_dir, 'secure_solution.py')
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(secure_wrapper)
        
        # Execute with subprocess
        try:
            process = subprocess.Popen(
                [sys.executable, script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                cwd=self.temp_dir
            )
            
            try:
                stdout, stderr = process.communicate(timeout=self.config.max_execution_time + 1)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                raise subprocess.TimeoutExpired(process.args, self.config.max_execution_time)
            
            # Check for resource limit violations
            limit_violation = monitor.check_limits()
            if limit_violation:
                return {
                    'result': 'TIMEOUT',
                    'message': limit_violation,
                    'test_results': [],
                    'execution_time': self.config.max_execution_time,
                    'memory_used': 0,
                    'security_violations': []
                }
            
            # Process results
            stats = monitor.get_stats()
            
            if process.returncode != 0:
                error_message = self._get_user_friendly_error(stderr, 'python')
                return {
                    'result': 'ERROR',
                    'message': error_message,
                    'test_results': [],
                    'execution_time': stats['execution_time'],
                    'memory_used': stats['peak_memory_bytes'],
                    'security_violations': [],
                    'error_details': {
                        'stderr': stderr,
                        'returncode': process.returncode
                    }
                }
            
            # Parse test results
            try:
                results = json.loads(stdout)
                passed_count = sum(1 for r in results if r.get('passed', False))
                total_count = len(results)
                
                overall_result = 'PASS' if passed_count == total_count else 'FAIL'
                message = f'{passed_count}/{total_count} test cases passed'
                
                return {
                    'result': overall_result,
                    'message': message,
                    'test_results': results,
                    'execution_time': stats['execution_time'],
                    'memory_used': stats['peak_memory_bytes'],
                    'security_violations': []
                }
                
            except json.JSONDecodeError:
                return {
                    'result': 'ERROR',
                    'message': 'Failed to parse execution results',
                    'test_results': [],
                    'execution_time': stats['execution_time'],
                    'memory_used': stats['peak_memory_bytes'],
                    'security_violations': [],
                    'error_details': {
                        'stdout': stdout[:1000],  # Limit output
                        'stderr': stderr[:1000]
                    }
                }
        
        except subprocess.TimeoutExpired:
            return {
                'result': 'TIMEOUT',
                'message': f'Code execution timed out after {self.config.max_execution_time} seconds',
                'test_results': [],
                'execution_time': self.config.max_execution_time,
                'memory_used': 0,
                'security_violations': []
            }
    
    def _create_python_security_wrapper(self, user_code: str, test_cases: List[Dict]) -> str:
        """Create a secure Python wrapper that restricts dangerous operations."""
        return f'''
import sys
import json
import signal
from io import StringIO

# Security: Disable dangerous built-ins
dangerous_builtins = [
    '__import__', 'eval', 'exec', 'compile', 'open', 'file',
    'input', 'raw_input', 'globals', 'locals', 'vars', 'dir',
    'getattr', 'setattr', 'delattr', 'hasattr', 'exit', 'quit',
    'help', 'copyright', 'credits', 'license', 'reload'
]

# Store original builtins
original_builtins = {{}}
for name in dangerous_builtins:
    if hasattr(__builtins__, name):
        if isinstance(__builtins__, dict):
            original_builtins[name] = __builtins__.get(name)
            __builtins__[name] = lambda *args, **kwargs: None
        else:
            original_builtins[name] = getattr(__builtins__, name, None)
            setattr(__builtins__, name, lambda *args, **kwargs: None)

# Set recursion limit
sys.setrecursionlimit({self.config.max_recursion_depth})

# Timeout handler
def timeout_handler(signum, frame):
    raise TimeoutError("Execution timed out")

try:
    signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm({self.config.max_execution_time})
except:
    pass  # Signal handling not available on all platforms

# User code execution
try:
    # Execute user code in restricted environment
    exec("""
{user_code}
""")
    
    # Test execution
    test_cases = {json.dumps(test_cases)}
    results = []
    
    for i, test_case in enumerate(test_cases):
        try:
            # Capture output
            old_stdout = sys.stdout
            sys.stdout = captured_output = StringIO()
            
            # Get test inputs and expected output
            inputs = test_case.get('input', [])
            expected = test_case.get('expected_output', '')
            
            # Find solution function
            solution_func = None
            for func_name in ['solution', 'solve', 'twoSum', 'main']:
                if func_name in locals():
                    solution_func = locals()[func_name]
                    break
            
            if solution_func and callable(solution_func):
                # Execute the solution
                if isinstance(inputs, list) and len(inputs) > 1:
                    result = solution_func(*inputs)
                elif isinstance(inputs, list) and len(inputs) == 1:
                    result = solution_func(inputs[0])
                else:
                    result = solution_func(inputs)
            else:
                result = "No solution function found"
            
            # Restore stdout
            sys.stdout = old_stdout
            output = captured_output.getvalue()
            
            # Compare results
            passed = str(result).strip() == str(expected).strip()
            
            results.append({{
                'test_case': i + 1,
                'input': inputs,
                'expected': expected,
                'actual': result,
                'passed': passed,
                'output': output[:500]  # Limit output size
            }})
            
        except Exception as e:
            sys.stdout = old_stdout
            results.append({{
                'test_case': i + 1,
                'input': inputs if 'inputs' in locals() else [],
                'expected': expected if 'expected' in locals() else '',
                'actual': None,
                'passed': False,
                'error': str(e)[:200]  # Limit error message size
            }})
    
    # Output results as JSON
    print(json.dumps(results))
    
except Exception as e:
    # Handle execution errors
    error_result = [{{
        'test_case': 0,
        'input': [],
        'expected': '',
        'actual': None,
        'passed': False,
        'error': f"Execution error: {{str(e)[:200]}}"
    }}]
    print(json.dumps(error_result))

finally:
    try:
        signal.alarm(0)  # Cancel alarm
    except:
        pass
'''
    
    def _execute_javascript_secure(self, code: str, test_cases: List[Dict], monitor: ResourceMonitor) -> Dict[str, Any]:
        """Execute JavaScript code with security restrictions."""
        # For now, return not implemented
        return {
            'result': 'ERROR',
            'message': 'Secure JavaScript execution not yet implemented',
            'test_results': [],
            'execution_time': 0,
            'memory_used': 0,
            'security_violations': []
        }
    
    def _get_user_friendly_error(self, stderr: str, language: str) -> str:
        """Convert technical error messages to user-friendly ones."""
        if not stderr:
            return "Unknown execution error"
        
        stderr_lower = stderr.lower()
        
        if language == 'python':
            if 'syntaxerror' in stderr_lower:
                return "There's a syntax error in your Python code. Please check for missing colons, parentheses, or indentation issues."
            elif 'nameerror' in stderr_lower:
                return "You're using a variable or function that hasn't been defined. Check for typos in variable names."
            elif 'typeerror' in stderr_lower:
                return "You're trying to perform an operation on incompatible data types."
            elif 'indexerror' in stderr_lower:
                return "You're trying to access a list or string index that doesn't exist."
            elif 'keyerror' in stderr_lower:
                return "You're trying to access a dictionary key that doesn't exist."
            elif 'zerodivisionerror' in stderr_lower:
                return "You're trying to divide by zero, which is not allowed."
            elif 'recursionerror' in stderr_lower:
                return "Your function is calling itself too many times (infinite recursion)."
            elif 'timeouterror' in stderr_lower or 'timeout' in stderr_lower:
                return "Your code took too long to execute. Please optimize your algorithm."
        
        # Return first line of error for brevity
        first_line = stderr.split('\n')[0] if stderr else "Unknown error"
        return f"Execution error: {first_line[:100]}"

# Integration function for existing judge system
def enhance_judge_security(judge_instance, config: SecurityConfig = None):
    """Enhance an existing judge instance with security features."""
    if not hasattr(judge_instance, '_secure_executor'):
        judge_instance._secure_executor = SecureCodeExecutor(config)
        judge_instance._original_execute_code = judge_instance.execute_code
        
        def secure_execute_code(language: str, code: str, test_cases: List[Dict]) -> Dict[str, Any]:
            """Enhanced execute_code method with security features."""
            return judge_instance._secure_executor.execute_code_securely(language, code, test_cases)
        
        judge_instance.execute_code = secure_execute_code
        logger.info("Judge security enhancements applied")
    
    return judge_instance

if __name__ == "__main__":
    # Test the security enhancements
    print("🧪 Testing Judge Security Enhancements...")
    
    # Test malicious code detection
    malicious_python = "import os; os.system('rm -rf /')"
    violations = MaliciousCodeDetector.scan_python_code(malicious_python)
    assert len(violations) > 0, "Should detect malicious code"
    print("✅ Malicious code detection test passed")
    
    # Test secure execution
    config = SecurityConfig(max_execution_time=2, max_memory_mb=64)
    executor = SecureCodeExecutor(config)
    
    safe_code = '''
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
'''
    
    test_cases = [
        {'input': [[2, 7, 11, 15], 9], 'expected_output': '[0, 1]'}
    ]
    
    result = executor.execute_code_securely('python', safe_code, test_cases)
    assert result['result'] in ['PASS', 'FAIL'], f"Unexpected result: {result}"
    print("✅ Secure execution test passed")
    
    print("🎉 All security enhancement tests passed!")