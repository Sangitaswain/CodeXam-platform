"""
Enhanced Error Handling System for CodeXam Platform
Provides comprehensive error classification, logging, and user-friendly messaging
"""

import logging
import traceback
import time
from datetime import datetime
from typing import Dict, Any, Optional, List, Union
from enum import Enum
from dataclasses import dataclass
import json
import sys


class ErrorType(Enum):
    """Enumeration of error types for classification."""
    # Code execution errors
    SYNTAX_ERROR = "SYNTAX_ERROR"
    RUNTIME_ERROR = "RUNTIME_ERROR"
    TIMEOUT_ERROR = "TIMEOUT_ERROR"
    MEMORY_ERROR = "MEMORY_ERROR"
    SECURITY_ERROR = "SECURITY_ERROR"
    COMPILATION_ERROR = "COMPILATION_ERROR"
    
    # Submission errors
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_LANGUAGE = "INVALID_LANGUAGE"
    CODE_TOO_LONG = "CODE_TOO_LONG"
    EMPTY_CODE = "EMPTY_CODE"
    
    # System errors
    JUDGE_ERROR = "JUDGE_ERROR"
    DATABASE_ERROR = "DATABASE_ERROR"
    FILE_SYSTEM_ERROR = "FILE_SYSTEM_ERROR"
    NETWORK_ERROR = "NETWORK_ERROR"
    
    # Infrastructure errors
    RESOURCE_UNAVAILABLE = "RESOURCE_UNAVAILABLE"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    
    # User errors
    NOT_FOUND = "NOT_FOUND"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    PERMISSION_DENIED = "PERMISSION_DENIED"


class ErrorSeverity(Enum):
    """Error severity levels for logging and alerting."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


@dataclass
class ErrorDetails:
    """Detailed error information for enhanced error handling."""
    error_type: ErrorType
    severity: ErrorSeverity
    message: str
    user_message: str
    technical_details: Optional[str] = None
    suggestion: Optional[str] = None
    error_code: Optional[str] = None
    timestamp: Optional[datetime] = None
    context: Optional[Dict[str, Any]] = None
    stack_trace: Optional[str] = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class EnhancedErrorHandler:
    """Enhanced error handling system with comprehensive error management."""
    
    def __init__(self, logger_name: str = "codexam_errors"):
        """Initialize the enhanced error handler."""
        self.logger = self._setup_logger(logger_name)
        self.error_counts = {}
        self.error_patterns = self._load_error_patterns()
        
    def _setup_logger(self, logger_name: str) -> logging.Logger:
        """Set up comprehensive logging configuration."""
        logger = logging.getLogger(logger_name)
        
        if not logger.handlers:
            # Console handler
            console_handler = logging.StreamHandler(sys.stdout)
            console_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            console_handler.setFormatter(console_formatter)
            console_handler.setLevel(logging.INFO)
            
            # File handler for errors
            try:
                file_handler = logging.FileHandler('codexam_errors.log')
                file_formatter = logging.Formatter(
                    '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
                )
                file_handler.setFormatter(file_formatter)
                file_handler.setLevel(logging.ERROR)
                logger.addHandler(file_handler)
            except Exception:
                # Fallback if file logging fails
                pass
            
            logger.addHandler(console_handler)
            logger.setLevel(logging.DEBUG)
        
        return logger
    
    def _load_error_patterns(self) -> Dict[str, ErrorDetails]:
        """Load predefined error patterns for common issues."""
        return {
            # Python-specific errors
            "SyntaxError": ErrorDetails(
                error_type=ErrorType.SYNTAX_ERROR,
                severity=ErrorSeverity.LOW,
                message="Python syntax error detected",
                user_message="There's a syntax error in your Python code. Please check for missing colons, parentheses, or indentation issues.",
                suggestion="Review your code for proper Python syntax. Common issues include missing colons after if/for/while statements, unmatched parentheses, or incorrect indentation."
            ),
            "IndentationError": ErrorDetails(
                error_type=ErrorType.SYNTAX_ERROR,
                severity=ErrorSeverity.LOW,
                message="Python indentation error detected",
                user_message="Your Python code has incorrect indentation. Python requires consistent use of spaces or tabs.",
                suggestion="Ensure all code at the same level has the same indentation. Use either spaces or tabs consistently (4 spaces is recommended)."
            ),
            "NameError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Python name error detected",
                user_message="You're using a variable or function that hasn't been defined.",
                suggestion="Check that all variables are defined before use and function names are spelled correctly."
            ),
            "TypeError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Python type error detected",
                user_message="You're trying to perform an operation on incompatible data types.",
                suggestion="Check that you're using the correct data types for your operations (e.g., you can't add a string to a number)."
            ),
            "IndexError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Python index error detected",
                user_message="You're trying to access a list or string index that doesn't exist.",
                suggestion="Make sure your list/string indices are within the valid range (0 to length-1)."
            ),
            "KeyError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Python key error detected",
                user_message="You're trying to access a dictionary key that doesn't exist.",
                suggestion="Check that the key exists in the dictionary before accessing it, or use the .get() method with a default value."
            ),
            "ZeroDivisionError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Division by zero detected",
                user_message="You're trying to divide by zero, which is not allowed.",
                suggestion="Check your logic to ensure you're not dividing by zero. Add a condition to handle this case."
            ),
            "RecursionError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.HIGH,
                message="Maximum recursion depth exceeded",
                user_message="Your function is calling itself too many times (infinite recursion).",
                suggestion="Make sure your recursive function has a proper base case to stop the recursion."
            ),
            
            # JavaScript-specific errors
            "ReferenceError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="JavaScript reference error detected",
                user_message="You're using a variable that hasn't been declared.",
                suggestion="Make sure all variables are declared with 'let', 'const', or 'var' before use."
            ),
            "TypeError": ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="JavaScript type error detected",
                user_message="You're trying to perform an operation on the wrong data type.",
                suggestion="Check that you're calling methods on the correct object types and passing the right argument types."
            ),
            "SyntaxError": ErrorDetails(
                error_type=ErrorType.SYNTAX_ERROR,
                severity=ErrorSeverity.LOW,
                message="JavaScript syntax error detected",
                user_message="There's a syntax error in your JavaScript code.",
                suggestion="Check for missing semicolons, brackets, or parentheses. Make sure your function syntax is correct."
            ),
            
            # Security-related errors
            "SecurityError": ErrorDetails(
                error_type=ErrorType.SECURITY_ERROR,
                severity=ErrorSeverity.HIGH,
                message="Security violation detected",
                user_message="Your code contains restricted operations that are not allowed for security reasons.",
                suggestion="Remove any file operations, network calls, or system imports. Focus on solving the algorithmic problem."
            ),
            
            # Timeout errors
            "TimeoutError": ErrorDetails(
                error_type=ErrorType.TIMEOUT_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Code execution timeout",
                user_message="Your code took too long to execute and was stopped.",
                suggestion="Optimize your algorithm to run faster. Look for infinite loops or inefficient operations."
            ),
            
            # Memory errors
            "MemoryError": ErrorDetails(
                error_type=ErrorType.MEMORY_ERROR,
                severity=ErrorSeverity.HIGH,
                message="Memory limit exceeded",
                user_message="Your code used too much memory and was stopped.",
                suggestion="Optimize your memory usage. Avoid creating very large data structures or too many objects."
            ),
            
            # Compilation errors
            "CompilationError": ErrorDetails(
                error_type=ErrorType.COMPILATION_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message="Code compilation failed",
                user_message="Your code couldn't be compiled. There may be syntax errors or missing dependencies.",
                suggestion="Check your code syntax and make sure you're using the correct language features for the selected programming language."
            )
        }
    
    def classify_error(self, error: Exception, language: str = "unknown", 
                      code: str = "", context: Dict[str, Any] = None) -> ErrorDetails:
        """Classify an error and return detailed error information."""
        error_name = type(error).__name__
        error_message = str(error)
        
        # Get base error details from patterns
        if error_name in self.error_patterns:
            error_details = self.error_patterns[error_name]
        else:
            # Default error classification
            error_details = ErrorDetails(
                error_type=ErrorType.RUNTIME_ERROR,
                severity=ErrorSeverity.MEDIUM,
                message=f"Unclassified error: {error_name}",
                user_message="An unexpected error occurred while executing your code.",
                suggestion="Please review your code and try again. If the problem persists, contact support."
            )
        
        # Enhance with specific details
        error_details.technical_details = error_message
        error_details.stack_trace = traceback.format_exc()
        error_details.context = context or {}
        error_details.context.update({
            "language": language,
            "error_type": error_name,
            "code_length": len(code) if code else 0
        })
        
        # Language-specific error handling
        if language.lower() == "python":
            error_details = self._enhance_python_error(error, error_details, code)
        elif language.lower() == "javascript":
            error_details = self._enhance_javascript_error(error, error_details, code)
        
        # Track error statistics
        self._track_error(error_details)
        
        return error_details
    
    def _enhance_python_error(self, error: Exception, details: ErrorDetails, code: str) -> ErrorDetails:
        """Enhance Python-specific error details."""
        error_message = str(error)
        
        if isinstance(error, SyntaxError):
            if "unexpected EOF" in error_message:
                details.user_message = "Your code is incomplete. You might be missing a closing bracket, parenthesis, or quote."
                details.suggestion = "Check for unmatched opening brackets, parentheses, or quotes."
            elif "invalid syntax" in error_message:
                details.user_message = "There's a syntax error in your Python code."
                details.suggestion = "Common issues: missing colons after if/for/while, incorrect indentation, or typos in keywords."
        
        elif isinstance(error, NameError):
            if "not defined" in error_message:
                var_name = error_message.split("'")[1] if "'" in error_message else "variable"
                details.user_message = f"The variable or function '{var_name}' is not defined."
                details.suggestion = f"Make sure you've defined '{var_name}' before using it, or check for typos."
        
        elif isinstance(error, IndexError):
            if "list index out of range" in error_message:
                details.user_message = "You're trying to access a list position that doesn't exist."
                details.suggestion = "Check that your list indices are between 0 and len(list)-1."
        
        return details
    
    def _enhance_javascript_error(self, error: Exception, details: ErrorDetails, code: str) -> ErrorDetails:
        """Enhance JavaScript-specific error details."""
        error_message = str(error)
        
        # Parse common JavaScript error patterns
        if "is not defined" in error_message:
            var_name = error_message.split()[0] if error_message else "variable"
            details.user_message = f"The variable '{var_name}' is not defined."
            details.suggestion = f"Declare '{var_name}' with 'let', 'const', or 'var' before using it."
        
        elif "is not a function" in error_message:
            details.user_message = "You're trying to call something that's not a function."
            details.suggestion = "Check that you're calling a function and not a variable or other data type."
        
        return details
    
    def _track_error(self, error_details: ErrorDetails):
        """Track error statistics for monitoring and analysis."""
        error_key = f"{error_details.error_type.value}_{error_details.severity.value}"
        self.error_counts[error_key] = self.error_counts.get(error_key, 0) + 1
        
        # Log error details
        log_level = {
            ErrorSeverity.LOW: logging.INFO,
            ErrorSeverity.MEDIUM: logging.WARNING,
            ErrorSeverity.HIGH: logging.ERROR,
            ErrorSeverity.CRITICAL: logging.CRITICAL
        }.get(error_details.severity, logging.ERROR)
        
        self.logger.log(log_level, 
            f"Error classified: {error_details.error_type.value} - {error_details.message}")
        
        if error_details.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
            self.logger.error(f"High severity error details: {error_details.technical_details}")
    
    def create_user_response(self, error_details: ErrorDetails, 
                           include_technical: bool = False) -> Dict[str, Any]:
        """Create a user-friendly error response."""
        response = {
            "result": "ERROR",
            "message": error_details.user_message,
            "error_type": error_details.error_type.value,
            "suggestion": error_details.suggestion,
            "timestamp": error_details.timestamp.isoformat() if error_details.timestamp else None
        }
        
        if include_technical and error_details.technical_details:
            response["technical_details"] = error_details.technical_details
        
        return response
    
    def handle_judge_error(self, error: Exception, language: str, code: str, 
                          test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Handle errors from the judge engine with comprehensive error processing."""
        start_time = time.time()
        
        # Classify the error
        error_details = self.classify_error(
            error, 
            language=language, 
            code=code,
            context={
                "test_cases_count": len(test_cases) if test_cases else 0,
                "component": "judge_engine"
            }
        )
        
        # Create judge result format
        execution_time = time.time() - start_time
        
        result = {
            'result': 'ERROR',
            'message': error_details.user_message,
            'test_results': [],
            'execution_time': execution_time,
            'memory_used': 0,
            'error_details': {
                'type': error_details.error_type.value,
                'severity': error_details.severity.value,
                'suggestion': error_details.suggestion
            }
        }
        
        # Add technical details for debugging (server-side only)
        if error_details.technical_details:
            self.logger.error(f"Judge error technical details: {error_details.technical_details}")
        
        return result
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """Get error statistics for monitoring and analysis."""
        total_errors = sum(self.error_counts.values())
        
        return {
            "total_errors": total_errors,
            "error_breakdown": self.error_counts.copy(),
            "most_common_errors": sorted(
                self.error_counts.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5]
        }
    
    def reset_statistics(self):
        """Reset error statistics (useful for testing or periodic resets)."""
        self.error_counts.clear()
        self.logger.info("Error statistics reset")


# Global error handler instance
global_error_handler = EnhancedErrorHandler()


def handle_execution_error(error: Exception, language: str = "unknown", 
                         code: str = "", test_cases: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Global function to handle execution errors with enhanced error processing."""
    return global_error_handler.handle_judge_error(error, language, code, test_cases or [])


def get_user_friendly_error(error: Exception, language: str = "unknown", 
                          code: str = "") -> Dict[str, Any]:
    """Get a user-friendly error response for any exception."""
    error_details = global_error_handler.classify_error(error, language, code)
    return global_error_handler.create_user_response(error_details)


# Error monitoring utilities
def log_system_error(component: str, operation: str, error: Exception, 
                    context: Dict[str, Any] = None):
    """Log system-level errors for monitoring and debugging."""
    error_details = global_error_handler.classify_error(
        error, 
        context={
            "component": component,
            "operation": operation,
            **(context or {})
        }
    )
    
    global_error_handler.logger.error(
        f"System error in {component}.{operation}: {error_details.message}"
    )
    
    if error_details.severity in [ErrorSeverity.HIGH, ErrorSeverity.CRITICAL]:
        global_error_handler.logger.critical(
            f"Critical system error: {error_details.technical_details}"
        )
