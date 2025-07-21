"""
CodeXam Code Execution Engine
Provides secure code execution for multiple programming languages
"""

import os
import sys
import subprocess
import tempfile
import time
import signal
import threading
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from contextlib import contextmanager
import json
import traceback

# Configure logging
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Optional resource module (not available on Windows)
try:
    import resource
    HAS_RESOURCE = True
except ImportError:
    HAS_RESOURCE = False


class JudgeResult:
    """Constants for judge execution results."""
    PASS = "PASS"
    FAIL = "FAIL"
    ERROR = "ERROR"
    TIMEOUT = "TIMEOUT"


class ExecutionError(Exception):
    """Custom exception for code execution errors."""
    pass


class SecurityError(Exception):
    """Custom exception for security violations."""
    pass


class JudgeConfig:
    """Configuration constants for the SimpleJudge."""
    
    # Supported programming languages
    SUPPORTED_LANGUAGES = ['python', 'javascript', 'java', 'cpp']
    
    # Execution limits
    DEFAULT_TIMEOUT = 5  # seconds
    DEFAULT_MEMORY_LIMIT = 128 * 1024 * 1024  # 128MB in bytes
    MAX_OUTPUT_SIZE = 10 * 1024  # 10KB
    MAX_CODE_LENGTH = 50 * 1024  # 50KB
    
    # Floating point comparison tolerance
    FLOAT_TOLERANCE = 1e-9
    
    # Function detection patterns
    COMMON_FUNCTION_NAMES = ['solution', 'solve', 'twoSum', 'main']
    
    # Security restrictions
    DANGEROUS_IMPORTS = frozenset([
        'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
        'http', 'ftplib', 'smtplib', 'telnetlib', 'webbrowser',
        'tempfile', 'shutil', 'glob', 'pickle', 'marshal',
        '__import__', 'eval', 'exec', 'compile', 'open', 'file',
        'input', 'raw_input'
    ])
    
    DANGEROUS_PATTERNS = frozenset([
        '__import__', 'eval(', 'exec(', 'compile(',
        'open(', 'file(', 'input(', 'raw_input(',
        'globals(', 'locals(', 'vars(', 'dir(',
        'getattr(', 'setattr(', 'delattr(', 'hasattr('
    ])
    
    # JavaScript security restrictions
    DANGEROUS_JS_PATTERNS = frozenset([
        'require(', 'import(', 'eval(',
        'process.', 'global.', '__dirname', '__filename',
        'fs.', 'child_process', 'os.', 'path.', 'util.',
        'http.', 'https.', 'net.', 'dgram.', 'dns.',
        'crypto.', 'buffer.', 'stream.', 'events.',
        'settimeout', 'setinterval', 'setimmediate',
        'vm.', 'worker_threads', 'cluster.',
        'new function', 'new worker'
    ])


class SimpleJudge:
    """
    Simple code execution engine with basic security restrictions.
    """
    
    def __init__(self, timeout: Optional[int] = None, memory_limit: Optional[int] = None):
        """Initialize SimpleJudge with configuration."""
        self.timeout = timeout or JudgeConfig.DEFAULT_TIMEOUT
        self.memory_limit = memory_limit or JudgeConfig.DEFAULT_MEMORY_LIMIT
        
        if self.timeout <= 0:
            raise ValueError(f"Timeout must be positive, got {self.timeout}")
        if self.memory_limit <= 0:
            raise ValueError(f"Memory limit must be positive, got {self.memory_limit}")
            
        self.temp_dir = tempfile.gettempdir()
        logger.info(f"SimpleJudge initialized with timeout={self.timeout}s, memory_limit={self.memory_limit} bytes")
    
    def execute_code(self, language: str, code: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute code with test cases and return results."""
        # Validate inputs
        validation_error = self._validate_inputs(language, code, test_cases)
        if validation_error:
            logger.warning(f"Input validation failed: {validation_error['message']}")
            return validation_error
        
        language = language.lower()
        logger.info(f"Executing {language} code with {len(test_cases)} test cases")
        
        try:
            if language == 'python':
                return self._execute_python(code, test_cases)
            elif language == 'javascript':
                return self._execute_javascript(code, test_cases)
            else:
                return self._create_error_result(f'Language {language} not implemented yet')
                
        except Exception as e:
            return self._create_error_result(f'Execution failed: {str(e)}')
    
    def _validate_inputs(self, language: str, code: str, test_cases: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """Validate inputs for code execution."""
        if not language or not isinstance(language, str):
            return self._create_error_result('Language must be a non-empty string')
        
        language = language.lower()
        if language not in JudgeConfig.SUPPORTED_LANGUAGES:
            return self._create_error_result(
                f'Unsupported language: {language}. Supported: {", ".join(JudgeConfig.SUPPORTED_LANGUAGES)}'
            )
        
        if not code or not isinstance(code, str) or not code.strip():
            return self._create_error_result('Code cannot be empty')
        
        if len(code) > JudgeConfig.MAX_CODE_LENGTH:
            return self._create_error_result(
                f'Code too long: {len(code)} characters (max: {JudgeConfig.MAX_CODE_LENGTH})'
            )
        
        if not test_cases or not isinstance(test_cases, list):
            return self._create_error_result('Test cases must be a non-empty list')
        
        for i, test_case in enumerate(test_cases):
            if not isinstance(test_case, dict):
                return self._create_error_result(f'Test case {i+1} must be a dictionary')
            
            if 'input' not in test_case or 'expected_output' not in test_case:
                return self._create_error_result(
                    f'Test case {i+1} must have "input" and "expected_output" keys'
                )
        
        return None
    
    def _create_error_result(self, message: str, execution_time: float = 0.0) -> Dict[str, Any]:
        """Create a standardized error result dictionary."""
        return {
            'result': JudgeResult.ERROR,
            'message': message,
            'test_results': [],
            'execution_time': execution_time,
            'memory_used': 0
        }
    
    def _execute_python(self, code: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute Python code with security restrictions."""
        start_time = time.time()
        
        try:
            # Security check for dangerous patterns
            self._check_python_security(code)
            
            # Prepare safe execution environment
            safe_globals = self._get_safe_python_globals()
            local_vars = {}
            
            # Execute the code in restricted environment
            try:
                exec(code, safe_globals, local_vars)
            except Exception as e:
                return {
                    'result': JudgeResult.ERROR,
                    'message': f'Code execution error: {str(e)}',
                    'test_results': [],
                    'execution_time': time.time() - start_time,
                    'memory_used': 0
                }
            
            # Find the solution function
            solution_func = None
            for name, obj in local_vars.items():
                if callable(obj) and not name.startswith('_'):
                    solution_func = obj
                    break
            
            if not solution_func:
                return {
                    'result': JudgeResult.ERROR,
                    'message': 'No solution function found in code',
                    'test_results': [],
                    'execution_time': time.time() - start_time,
                    'memory_used': 0
                }
            
            # Run test cases
            test_results, all_passed = self._run_test_cases(solution_func, test_cases)
            
            execution_time = time.time() - start_time
            result_status = JudgeResult.PASS if all_passed else JudgeResult.FAIL
            result_message = 'All test cases passed' if all_passed else f'{sum(1 for t in test_results if not t["passed"])} of {len(test_results)} test cases failed'
            
            return {
                'result': result_status,
                'message': result_message,
                'test_results': test_results,
                'execution_time': execution_time,
                'memory_used': 0
            }
            
        except SecurityError as e:
            return {
                'result': JudgeResult.ERROR,
                'message': f'Security violation: {str(e)}',
                'test_results': [],
                'execution_time': time.time() - start_time,
                'memory_used': 0
            }
        except Exception as e:
            return {
                'result': JudgeResult.ERROR,
                'message': f'Execution error: {str(e)}',
                'test_results': [],
                'execution_time': time.time() - start_time,
                'memory_used': 0
            }
    
    def _check_python_security(self, code: str) -> None:
        """Check Python code for security violations."""
        code_lower = code.lower()
        
        for dangerous in JudgeConfig.DANGEROUS_IMPORTS:
            if dangerous in code_lower:
                if f'import {dangerous}' in code_lower or f'from {dangerous}' in code_lower:
                    logger.warning(f"Security violation: dangerous import '{dangerous}' detected")
                    raise SecurityError(f'Dangerous import detected: {dangerous}')
                if f'{dangerous}(' in code_lower:
                    logger.warning(f"Security violation: dangerous function call '{dangerous}' detected")
                    raise SecurityError(f'Dangerous function call detected: {dangerous}')
        
        for pattern in JudgeConfig.DANGEROUS_PATTERNS:
            if pattern in code_lower:
                logger.warning(f"Security violation: dangerous pattern '{pattern}' detected")
                raise SecurityError(f'Dangerous pattern detected: {pattern}')
    
    def _get_safe_python_globals(self) -> Dict[str, Any]:
        """Get safe globals dictionary for Python execution."""
        safe_builtins = {
            'int': int, 'float': float, 'str': str, 'bool': bool,
            'list': list, 'dict': dict, 'tuple': tuple, 'set': set,
            'len': len, 'range': range, 'enumerate': enumerate,
            'zip': zip, 'map': map, 'filter': filter,
            'sorted': sorted, 'reversed': reversed,
            'sum': sum, 'min': min, 'max': max, 'abs': abs,
            'round': round, 'pow': pow, 'ord': ord, 'chr': chr,
            'divmod': divmod, 'isinstance': isinstance, 'type': type,
            'Exception': Exception, 'ValueError': ValueError,
            'TypeError': TypeError, 'IndexError': IndexError,
            'KeyError': KeyError,
        }
        
        return {
            '__builtins__': safe_builtins,
            '__name__': '__main__'
        }
    
    def _run_test_cases(self, solution_func, test_cases: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], bool]:
        """Run test cases against a solution function."""
        test_results = []
        all_passed = True
        
        for i, test_case in enumerate(test_cases):
            test_input = test_case.get('input')
            expected_output = test_case.get('expected_output')
            
            try:
                actual_output = self._run_with_timeout(solution_func, test_input, self.timeout)
                passed = self._compare_outputs(actual_output, expected_output)
                
                test_results.append({
                    'test_case': i + 1,
                    'passed': passed,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': actual_output if passed else None,
                    'error': None
                })
                
                if not passed:
                    all_passed = False
                    
            except TimeoutError:
                test_results.append({
                    'test_case': i + 1,
                    'passed': False,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': None,
                    'error': 'Timeout'
                })
                all_passed = False
                
            except Exception as e:
                test_results.append({
                    'test_case': i + 1,
                    'passed': False,
                    'input': test_input,
                    'expected': expected_output,
                    'actual': None,
                    'error': str(e)
                })
                all_passed = False
        
        return test_results, all_passed
    
    def _run_with_timeout(self, func, args, timeout: int):
        """Run function with timeout using threading."""
        result = [None]
        exception = [None]
        
        def target():
            try:
                if isinstance(args, (list, tuple)) and len(args) > 1:
                    result[0] = func(*args)
                elif isinstance(args, (list, tuple)) and len(args) == 1:
                    result[0] = func(args[0])
                else:
                    result[0] = func(args)
            except Exception as e:
                exception[0] = e
        
        thread = threading.Thread(target=target)
        thread.daemon = True
        thread.start()
        thread.join(timeout)
        
        if thread.is_alive():
            raise TimeoutError(f'Code execution timed out after {timeout} seconds')
        
        if exception[0]:
            raise exception[0]
        
        return result[0]
    
    def _compare_outputs(self, actual, expected) -> bool:
        """Compare actual and expected outputs with proper type handling."""
        try:
            return self._deep_compare(actual, expected)
        except Exception as e:
            logger.debug(f"Output comparison failed: {e}")
            return False
    
    def _deep_compare(self, actual, expected) -> bool:
        """Recursively compare two values with proper type and tolerance handling."""
        if actual is None or expected is None:
            return actual is expected
        
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            if isinstance(actual, float) or isinstance(expected, float):
                return abs(float(actual) - float(expected)) < JudgeConfig.FLOAT_TOLERANCE
            return actual == expected
        
        if isinstance(actual, str) and isinstance(expected, str):
            return actual.strip() == expected.strip()
        
        if isinstance(actual, (list, tuple)) and isinstance(expected, (list, tuple)):
            if len(actual) != len(expected):
                return False
            return all(self._deep_compare(a, e) for a, e in zip(actual, expected))
        
        if isinstance(actual, dict) and isinstance(expected, dict):
            if set(actual.keys()) != set(expected.keys()):
                return False
            return all(self._deep_compare(actual[k], expected[k]) for k in actual.keys())
        
        if isinstance(actual, set) and isinstance(expected, set):
            return actual == expected
        
        if isinstance(actual, bool) and isinstance(expected, bool):
            return actual == expected
        
        if type(actual) != type(expected):
            return False
        
        return actual == expected
    
    def _execute_javascript(self, code: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Execute JavaScript code using Node.js subprocess."""
        try:
            subprocess.run(['node', '--version'], capture_output=True, check=True)
        except (subprocess.CalledProcessError, FileNotFoundError):
            return self._create_error_result('Node.js not found. Please install Node.js to run JavaScript code.')
        
        start_time = time.time()
        
        try:
            self._check_javascript_security(code)
            js_code = self._wrap_javascript_code(code, test_cases)
            
            with self._temporary_file('.js', js_code) as temp_file:
                result = subprocess.run(
                    ['node', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout,
                    cwd=self.temp_dir
                )
                
                if result.returncode != 0:
                    error_msg = result.stderr.strip() if result.stderr else 'Unknown JavaScript error'
                    return self._create_error_result(f'JavaScript execution error: {error_msg}')
                
                try:
                    output_lines = result.stdout.strip().split('\n')
                    results_json = output_lines[-1]
                    results = json.loads(results_json)
                    
                    return {
                        'result': results['result'],
                        'message': results['message'],
                        'test_results': results['test_results'],
                        'execution_time': time.time() - start_time,
                        'memory_used': 0
                    }
                    
                except (json.JSONDecodeError, ValueError, KeyError) as e:
                    return self._create_error_result(f'Failed to parse JavaScript execution results: {str(e)}')
                    
        except SecurityError as e:
            return self._create_error_result(f'Security violation: {str(e)}')
        except subprocess.TimeoutExpired:
            return {
                'result': JudgeResult.TIMEOUT,
                'message': f'JavaScript execution timed out after {self.timeout} seconds',
                'test_results': [],
                'execution_time': self.timeout,
                'memory_used': 0
            }
        except Exception as e:
            return self._create_error_result(f'JavaScript execution failed: {str(e)}')
    
    def _check_javascript_security(self, code: str) -> None:
        """Check JavaScript code for security violations."""
        code_lower = code.lower()
        
        for pattern in JudgeConfig.DANGEROUS_JS_PATTERNS:
            if pattern in code_lower:
                logger.warning(f"Security violation: dangerous JavaScript pattern '{pattern}' detected")
                raise SecurityError(f'Dangerous JavaScript pattern detected: {pattern}')
    
    @contextmanager
    def _temporary_file(self, suffix: str = '', content: str = ''):
        """Context manager for temporary file creation and cleanup."""
        temp_file = None
        try:
            with tempfile.NamedTemporaryFile(
                mode='w', 
                suffix=suffix, 
                delete=False, 
                dir=self.temp_dir
            ) as f:
                if content:
                    f.write(content)
                temp_file = f.name
            
            yield temp_file
            
        finally:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.unlink(temp_file)
                except OSError:
                    pass
    
    def _wrap_javascript_code(self, code: str, test_cases: List[Dict[str, Any]]) -> str:
        """Wrap JavaScript code with test execution logic."""
        test_cases_json = json.dumps(test_cases)
        common_names_json = json.dumps(JudgeConfig.COMMON_FUNCTION_NAMES)
        
        return f'''
{code}

// Test execution wrapper
const testCases = {test_cases_json};
const results = [];
let allPassed = true;

// Function detection utility
function findSolutionFunction() {{
    const commonNames = {common_names_json};
    
    for (const name of commonNames) {{
        try {{
            if (typeof eval(name) === 'function') {{
                return eval(name);
            }}
        }} catch (e) {{
            // Function not found, continue
        }}
    }}
    
    return null;
}}

// Get solution function
const solutionFunc = findSolutionFunction();

if (!solutionFunc) {{
    console.log(JSON.stringify({{
        result: 'ERROR',
        message: 'No solution function found',
        test_results: []
    }}));
}} else {{
    // Run test cases
    for (let i = 0; i < testCases.length; i++) {{
        const testCase = testCases[i];
        try {{
            const actual = solutionFunc(...testCase.input);
            const expected = testCase.expected_output;
            const passed = JSON.stringify(actual) === JSON.stringify(expected);
            
            results.push({{
                test_case: i + 1,
                passed: passed,
                input: testCase.input,
                expected: expected,
                actual: passed ? actual : null,
                error: null
            }});
            
            if (!passed) allPassed = false;
        }} catch (error) {{
            results.push({{
                test_case: i + 1,
                passed: false,
                input: testCase.input,
                expected: testCase.expected_output,
                actual: null,
                error: error.message
            }});
            allPassed = false;
        }}
    }}
    
    console.log(JSON.stringify({{
        result: allPassed ? 'PASS' : 'FAIL',
        message: allPassed ? 'All test cases passed' : `${{results.filter(r => !r.passed).length}} of ${{results.length}} test cases failed`,
        test_results: results
    }}));
}}
'''


# Testing function
if __name__ == "__main__":
    print("🧪 Testing SimpleJudge...")
    
    judge = SimpleJudge()
    
    # Test cases for Two Sum problem
    test_cases = [
        {"input": [[2, 7, 11, 15], 9], "expected_output": [0, 1]},
        {"input": [[3, 2, 4], 6], "expected_output": [1, 2]},
        {"input": [[3, 3], 6], "expected_output": [0, 1]}
    ]
    
    # Test Python execution
    python_code = """
def solution(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return [i, j]
    return []
"""
    
    print("\n🐍 Testing Python execution...")
    result = judge.execute_code('python', python_code, test_cases)
    print(f"Result: {result['result']}")
    print(f"Message: {result['message']}")
    print(f"Execution time: {result['execution_time']:.3f}s")
    
    print("\n✅ SimpleJudge testing completed!")