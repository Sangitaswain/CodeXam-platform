"""Unit tests for CodeXam judge system."""

import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from judge import SimpleJudge


class TestSimpleJudge:
    """Test cases for SimpleJudge class."""
    
    @pytest.mark.unit
    def test_judge_initialization(self):
        """Test judge initialization."""
        judge = SimpleJudge()
        assert judge is not None
        assert hasattr(judge, 'execute_code')
    
    @pytest.mark.unit
    def test_python_code_execution_success(self, sample_code):
        """Test successful Python code execution."""
        judge = SimpleJudge()
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': '[0, 1]'
            }
        ]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'PASS',
                'message': '1/1 test cases passed',
                'test_results': [{'passed': True}],
                'execution_time': 0.001,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert result['result'] == 'PASS'
            assert result['message'] == '1/1 test cases passed'
            assert 'test_results' in result
            assert 'execution_time' in result
            assert 'memory_used' in result
    
    @pytest.mark.unit
    def test_python_code_execution_failure(self, sample_code):
        """Test Python code execution with test failure."""
        judge = SimpleJudge()
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': '[1, 0]'  # Wrong expected output
            }
        ]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'FAIL',
                'message': '0/1 test cases passed',
                'test_results': [{'passed': False}],
                'execution_time': 0.001,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert result['result'] == 'FAIL'
            assert result['message'] == '0/1 test cases passed'
    
    @pytest.mark.unit
    def test_syntax_error_handling(self, sample_code):
        """Test handling of syntax errors in code."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'ERROR',
                'message': 'SyntaxError: invalid syntax',
                'test_results': [],
                'execution_time': 0.0,
                'memory_used': 0
            }
            
            result = judge.execute_code('python', sample_code['invalid_python'], test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'SyntaxError' in result['message']
    
    @pytest.mark.unit
    def test_timeout_handling(self, sample_code):
        """Test handling of code execution timeout."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.side_effect = TimeoutError("Code execution timed out")
            
            result = judge.execute_code('python', sample_code['timeout_python'], test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'timeout' in result['message'].lower()
    
    @pytest.mark.unit
    def test_memory_limit_handling(self, sample_code):
        """Test handling of memory limit exceeded."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.side_effect = MemoryError("Memory limit exceeded")
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'memory' in result['message'].lower()


class TestSecurityFeatures:
    """Test security features of the judge system."""
    
    @pytest.mark.security
    def test_malicious_code_detection(self, sample_code):
        """Test detection of malicious code patterns."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        # Test actual security detection without mocking
        result = judge.execute_code('python', sample_code['malicious_python'], test_cases)
        
        assert result['result'] == 'ERROR'
        assert 'security' in result['message'].lower() or 'violation' in result['message'].lower()
    
    @pytest.mark.security
    def test_dangerous_import_detection(self):
        """Test detection of dangerous imports."""
        judge = SimpleJudge()
        
        dangerous_codes = [
            "import os\ndef solution(): return os.getcwd()",
            "import subprocess\ndef solution(): return 'test'",
            "from sys import exit\ndef solution(): exit()",
            "import socket\ndef solution(): return 'test'"
        ]
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        for code in dangerous_codes:
            result = judge.execute_code('python', code, test_cases)
            assert result['result'] == 'ERROR'
            assert 'security' in result['message'].lower() or 'dangerous' in result['message'].lower()
    
    @pytest.mark.security
    def test_dangerous_function_detection(self):
        """Test detection of dangerous function calls."""
        judge = SimpleJudge()
        
        dangerous_codes = [
            "def solution(): eval('1+1')",
            "def solution(): exec('print(1)')",
            "def solution(): open('file.txt')",
            "def solution(): __import__('os')"
        ]
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        for code in dangerous_codes:
            result = judge.execute_code('python', code, test_cases)
            assert result['result'] == 'ERROR'


class TestRealExecution:
    """Test real code execution without mocking."""
    
    @pytest.mark.integration
    def test_real_python_execution_success(self, sample_code):
        """Test actual Python code execution."""
        judge = SimpleJudge()
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': [0, 1]
            }
        ]
        
        result = judge.execute_code('python', sample_code['valid_python'], test_cases)
        
        assert result['result'] == 'PASS'
        assert len(result['test_results']) == 1
        assert result['test_results'][0]['passed'] is True
        assert result['execution_time'] > 0
    
    @pytest.mark.integration
    def test_real_python_execution_failure(self):
        """Test Python code that fails test cases."""
        judge = SimpleJudge()
        
        # Code that returns wrong answer
        wrong_code = """
def solution(nums, target):
    return [1, 0]  # Wrong order
"""
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': [0, 1]
            }
        ]
        
        result = judge.execute_code('python', wrong_code, test_cases)
        
        assert result['result'] == 'FAIL'
        assert len(result['test_results']) == 1
        assert result['test_results'][0]['passed'] is False
    
    @pytest.mark.integration
    def test_real_syntax_error(self, sample_code):
        """Test actual syntax error handling."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [1, 2], 'expected_output': 3}]
        
        result = judge.execute_code('python', sample_code['invalid_python'], test_cases)
        
        assert result['result'] == 'ERROR'
        assert 'syntax' in result['message'].lower()
        assert 'error_details' in result
        assert result['error_details']['type'] == 'SyntaxError'


class TestInputValidation:
    """Test input validation and edge cases."""
    
    @pytest.mark.unit
    def test_empty_code_validation(self):
        """Test validation of empty code."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [1], 'expected_output': 2}]
        
        result = judge.execute_code('python', '', test_cases)
        
        assert result['result'] == 'ERROR'
        assert 'empty' in result['message'].lower()
    
    @pytest.mark.unit
    def test_invalid_language_validation(self):
        """Test validation of unsupported language."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [1], 'expected_output': 2}]
        
        result = judge.execute_code('cobol', 'def solution(): pass', test_cases)
        
        assert result['result'] == 'ERROR'
        assert 'unsupported' in result['message'].lower()
    
    @pytest.mark.unit
    def test_empty_test_cases_validation(self):
        """Test validation of empty test cases."""
        judge = SimpleJudge()
        
        result = judge.execute_code('python', 'def solution(): pass', [])
        
        assert result['result'] == 'ERROR'
        assert 'test cases' in result['message'].lower()
    
    @pytest.mark.unit
    def test_malformed_test_cases_validation(self):
        """Test validation of malformed test cases."""
        judge = SimpleJudge()
        
        malformed_cases = [
            [{'input': [1]}],  # Missing expected_output
            [{'expected_output': 2}],  # Missing input
            [{'input': [1], 'expected_output': 2, 'extra': 'field'}],  # Extra field is OK
        ]
        
        for test_cases in malformed_cases[:2]:  # Only test the first two (missing fields)
            result = judge.execute_code('python', 'def solution(): pass', test_cases)
            assert result['result'] == 'ERROR'
    
    @pytest.mark.unit
    def test_code_length_validation(self):
        """Test validation of excessively long code."""
        judge = SimpleJudge()
        
        # Create code longer than MAX_CODE_LENGTH
        long_code = 'def solution():\n' + '    # comment\n' * 10000
        
        test_cases = [{'input': [1], 'expected_output': 2}]
        
        result = judge.execute_code('python', long_code, test_cases)
        
        assert result['result'] == 'ERROR'
        assert 'too long' in result['message'].lower()


class TestPerformanceAndLimits:
    """Test performance monitoring and resource limits."""
    
    @pytest.mark.slow
    def test_execution_time_tracking(self, sample_code):
        """Test that execution time is properly tracked."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [[1, 2], 3], 'expected_output': [0, 1]}]
        
        result = judge.execute_code('python', sample_code['valid_python'], test_cases)
        
        assert 'execution_time' in result
        assert isinstance(result['execution_time'], (int, float))
        assert result['execution_time'] >= 0
    
    @pytest.mark.unit
    def test_judge_configuration(self):
        """Test judge configuration and initialization."""
        # Test default initialization
        judge = SimpleJudge()
        assert judge.timeout == 5  # Default timeout
        assert judge.memory_limit == 128 * 1024 * 1024  # Default memory limit
        
        # Test custom initialization
        custom_judge = SimpleJudge(timeout=10, memory_limit=256 * 1024 * 1024)
        assert custom_judge.timeout == 10
        assert custom_judge.memory_limit == 256 * 1024 * 1024
    
    @pytest.mark.unit
    def test_invalid_judge_configuration(self):
        """Test invalid judge configuration."""
        with pytest.raises(ValueError, match="Timeout must be positive"):
            SimpleJudge(timeout=0)
        
        with pytest.raises(ValueError, match="Timeout must be positive"):
            SimpleJudge(timeout=-1)
        
        with pytest.raises(ValueError, match="Memory limit must be positive"):
            SimpleJudge(memory_limit=0)
    
        with pytest.raise"):
            SimpleJudge(memory_limit=-1) be positiveimit musth="Memory latclueError, m(Vas       
 
    @pytest.mark.security
    def test_import_restrictions(self):
        """Test that dangerous imports are restricted."""
        judge = SimpleJudge()
        
        dangerous_imports = [
            'import os',
            'import sys',
            'import subprocess',
            'from os import system',
            '__import__("os")',
        ]
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        for dangerous_import in dangerous_imports:
            code = f'{dangerous_import}\ndef solution(): return "test"'
            
            with patch.object(judge, '_detect_malicious_code') as mock_detect:
                mock_detect.return_value = True
                
                result = judge.execute_code('python', code, test_cases)
                
                assert result['result'] == 'ERROR'
                assert 'security' in result['message'].lower()
    
    @pytest.mark.security
    def test_builtin_function_restrictions(self):
        """Test that dangerous builtin functions are restricted."""
        judge = SimpleJudge()
        
        dangerous_functions = [
            'eval("malicious_code")',
            'exec("malicious_code")',
            'open("/etc/passwd")',
            'compile("code", "file", "exec")',
        ]
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        for dangerous_func in dangerous_functions:
            code = f'def solution():\n    {dangerous_func}\n    return "test"'
            
            with patch.object(judge, '_detect_malicious_code') as mock_detect:
                mock_detect.return_value = True
                
                result = judge.execute_code('python', code, test_cases)
                
                assert result['result'] == 'ERROR'
    
    @pytest.mark.security
    def test_resource_limits_enforcement(self):
        """Test that resource limits are enforced."""
        judge = SimpleJudge()
        
        # Test memory limit
        memory_intensive_code = '''
def solution():
    # Try to allocate large amount of memory
    big_list = [0] * (10**8)  # 100 million integers
    return "test"
'''
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.side_effect = MemoryError("Memory limit exceeded")
            
            result = judge.execute_code('python', memory_intensive_code, test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'memory' in result['message'].lower()
    
    @pytest.mark.security
    def test_execution_time_limits(self):
        """Test that execution time limits are enforced."""
        judge = SimpleJudge()
        
        infinite_loop_code = '''
def solution():
    while True:
        pass
    return "test"
'''
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.side_effect = TimeoutError("Execution timed out")
            
            result = judge.execute_code('python', infinite_loop_code, test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'timeout' in result['message'].lower()


class TestMultiLanguageSupport:
    """Test multi-language support in judge system."""
    
    @pytest.mark.unit
    def test_supported_languages(self):
        """Test that judge supports expected languages."""
        judge = SimpleJudge()
        
        # These should be supported
        supported_languages = ['python', 'javascript', 'java', 'cpp']
        
        for language in supported_languages:
            # Mock the language-specific execution method
            with patch.object(judge, f'_execute_{language}_code') as mock_exec:
                mock_exec.return_value = {
                    'result': 'PASS',
                    'message': 'Test passed',
                    'test_results': [],
                    'execution_time': 0.001,
                    'memory_used': 1024
                }
                
                result = judge.execute_code(language, 'test code', [])
                assert result['result'] == 'PASS'
    
    @pytest.mark.unit
    def test_unsupported_language(self):
        """Test handling of unsupported languages."""
        judge = SimpleJudge()
        
        result = judge.execute_code('unsupported_language', 'test code', [])
        
        assert result['result'] == 'ERROR'
        assert 'unsupported' in result['message'].lower()
    
    @pytest.mark.unit
    def test_javascript_execution(self):
        """Test JavaScript code execution."""
        judge = SimpleJudge()
        
        js_code = '''
function twoSum(nums, target) {
    for (let i = 0; i < nums.length; i++) {
        for (let j = i + 1; j < nums.length; j++) {
            if (nums[i] + nums[j] === target) {
                return [i, j];
            }
        }
    }
    return [];
}
'''
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': '[0, 1]'
            }
        ]
        
        with patch.object(judge, '_execute_javascript_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'PASS',
                'message': '1/1 test cases passed',
                'test_results': [{'passed': True}],
                'execution_time': 0.002,
                'memory_used': 2048
            }
            
            result = judge.execute_code('javascript', js_code, test_cases)
            
            assert result['result'] == 'PASS'
            assert result['message'] == '1/1 test cases passed'


class TestTestCaseExecution:
    """Test test case execution and validation."""
    
    @pytest.mark.unit
    def test_single_test_case_execution(self, sample_code):
        """Test execution of a single test case."""
        judge = SimpleJudge()
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': '[0, 1]'
            }
        ]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'PASS',
                'message': '1/1 test cases passed',
                'test_results': [
                    {
                        'test_case': 1,
                        'input': [2, 7, 11, 15],
                        'expected': '[0, 1]',
                        'actual': '[0, 1]',
                        'passed': True
                    }
                ],
                'execution_time': 0.001,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert result['result'] == 'PASS'
            assert len(result['test_results']) == 1
            assert result['test_results'][0]['passed'] is True
    
    @pytest.mark.unit
    def test_multiple_test_cases_execution(self, sample_code):
        """Test execution of multiple test cases."""
        judge = SimpleJudge()
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': '[0, 1]'
            },
            {
                'input': [[3, 2, 4], 6],
                'expected_output': '[1, 2]'
            },
            {
                'input': [[3, 3], 6],
                'expected_output': '[0, 1]'
            }
        ]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'PASS',
                'message': '3/3 test cases passed',
                'test_results': [
                    {'test_case': 1, 'passed': True},
                    {'test_case': 2, 'passed': True},
                    {'test_case': 3, 'passed': True}
                ],
                'execution_time': 0.003,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert result['result'] == 'PASS'
            assert len(result['test_results']) == 3
            assert all(test['passed'] for test in result['test_results'])
    
    @pytest.mark.unit
    def test_partial_test_case_success(self, sample_code):
        """Test execution with some test cases passing and some failing."""
        judge = SimpleJudge()
        
        test_cases = [
            {
                'input': [[2, 7, 11, 15], 9],
                'expected_output': '[0, 1]'
            },
            {
                'input': [[3, 2, 4], 6],
                'expected_output': '[1, 2]'
            }
        ]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'FAIL',
                'message': '1/2 test cases passed',
                'test_results': [
                    {'test_case': 1, 'passed': True},
                    {'test_case': 2, 'passed': False}
                ],
                'execution_time': 0.002,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert result['result'] == 'FAIL'
            assert result['message'] == '1/2 test cases passed'
            assert len(result['test_results']) == 2
    
    @pytest.mark.unit
    def test_empty_test_cases(self, sample_code):
        """Test execution with empty test cases."""
        judge = SimpleJudge()
        
        test_cases = []
        
        result = judge.execute_code('python', sample_code['valid_python'], test_cases)
        
        assert result['result'] == 'ERROR'
        assert 'no test cases' in result['message'].lower()
    
    @pytest.mark.unit
    def test_malformed_test_cases(self, sample_code):
        """Test execution with malformed test cases."""
        judge = SimpleJudge()
        
        malformed_test_cases = [
            {'input': [1, 2, 3]},  # Missing expected_output
            {'expected_output': '[0, 1]'},  # Missing input
            {}  # Empty test case
        ]
        
        for test_case in malformed_test_cases:
            result = judge.execute_code('python', sample_code['valid_python'], [test_case])
            
            assert result['result'] == 'ERROR'
            assert 'invalid' in result['message'].lower() or 'malformed' in result['message'].lower()


class TestErrorHandling:
    """Test error handling in judge system."""
    
    @pytest.mark.unit
    def test_runtime_error_handling(self, sample_code):
        """Test handling of runtime errors."""
        judge = SimpleJudge()
        
        error_code = '''
def solution():
    x = 1 / 0  # Division by zero
    return x
'''
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'ERROR',
                'message': 'ZeroDivisionError: division by zero',
                'test_results': [],
                'execution_time': 0.001,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', error_code, test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'ZeroDivisionError' in result['message']
    
    @pytest.mark.unit
    def test_name_error_handling(self):
        """Test handling of name errors."""
        judge = SimpleJudge()
        
        error_code = '''
def solution():
    return undefined_variable
'''
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'ERROR',
                'message': 'NameError: name \'undefined_variable\' is not defined',
                'test_results': [],
                'execution_time': 0.001,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', error_code, test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'NameError' in result['message']
    
    @pytest.mark.unit
    def test_type_error_handling(self):
        """Test handling of type errors."""
        judge = SimpleJudge()
        
        error_code = '''
def solution():
    return "string" + 123  # Type error
'''
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'ERROR',
                'message': 'TypeError: can only concatenate str (not "int") to str',
                'test_results': [],
                'execution_time': 0.001,
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', error_code, test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'TypeError' in result['message']
    
    @pytest.mark.unit
    def test_indentation_error_handling(self):
        """Test handling of indentation errors."""
        judge = SimpleJudge()
        
        error_code = '''
def solution():
return "test"  # Indentation error
'''
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'ERROR',
                'message': 'IndentationError: expected an indented block',
                'test_results': [],
                'execution_time': 0.0,
                'memory_used': 0
            }
            
            result = judge.execute_code('python', error_code, test_cases)
            
            assert result['result'] == 'ERROR'
            assert 'IndentationError' in result['message']


class TestPerformanceMetrics:
    """Test performance metrics collection."""
    
    @pytest.mark.unit
    def test_execution_time_measurement(self, sample_code):
        """Test that execution time is properly measured."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'PASS',
                'message': 'Test passed',
                'test_results': [{'passed': True}],
                'execution_time': 0.123,  # Specific execution time
                'memory_used': 1024
            }
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert 'execution_time' in result
            assert result['execution_time'] == 0.123
            assert isinstance(result['execution_time'], float)
    
    @pytest.mark.unit
    def test_memory_usage_measurement(self, sample_code):
        """Test that memory usage is properly measured."""
        judge = SimpleJudge()
        
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'PASS',
                'message': 'Test passed',
                'test_results': [{'passed': True}],
                'execution_time': 0.001,
                'memory_used': 2048  # Specific memory usage
            }
            
            result = judge.execute_code('python', sample_code['valid_python'], test_cases)
            
            assert 'memory_used' in result
            assert result['memory_used'] == 2048
            assert isinstance(result['memory_used'], int)
    
    @pytest.mark.unit
    def test_performance_metrics_on_error(self):
        """Test that performance metrics are included even on errors."""
        judge = SimpleJudge()
        
        error_code = 'invalid python code'
        test_cases = [{'input': [], 'expected_output': 'test'}]
        
        with patch.object(judge, '_execute_python_code') as mock_exec:
            mock_exec.return_value = {
                'result': 'ERROR',
                'message': 'SyntaxError: invalid syntax',
                'test_results': [],
                'execution_time': 0.0,
                'memory_used': 0
            }
            
            result = judge.execute_code('python', error_code, test_cases)
            
            assert 'execution_time' in result
            assert 'memory_used' in result
            assert result['execution_time'] >= 0
            assert result['memory_used'] >= 0