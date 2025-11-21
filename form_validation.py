"""
Enhanced Form Validation and Input Handling for CodeXam Platform
Provides comprehensive client-side and server-side validation with security features
"""

import re
import html
from typing import Dict, Any, List, Optional, Tuple
from flask import request, jsonify
import logging
from datetime import datetime, timedelta
import hashlib
import secrets
from functools import wraps

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class SecurityViolation(Exception):
    """Custom exception for security violations."""
    pass


class RateLimiter:
    """Simple in-memory rate limiter."""
    
    def __init__(self):
        self.requests = {}
        self.blocked_ips = {}
    
    def is_rate_limited(self, ip: str, limit: int = 10, window: int = 60) -> bool:
        """Check if IP is rate limited."""
        now = datetime.now()
        
        # Clean old requests
        self._cleanup_old_requests(now, window)
        
        # Check if IP is temporarily blocked
        if ip in self.blocked_ips:
            if now < self.blocked_ips[ip]:
                return True
            else:
                del self.blocked_ips[ip]
        
        # Count requests in window
        if ip not in self.requests:
            self.requests[ip] = []
        
        self.requests[ip] = [req_time for req_time in self.requests[ip] 
                           if now - req_time < timedelta(seconds=window)]
        
        if len(self.requests[ip]) >= limit:
            # Block IP for extended period
            self.blocked_ips[ip] = now + timedelta(minutes=5)
            logger.warning(f"IP {ip} blocked for rate limiting")
            return True
        
        self.requests[ip].append(now)
        return False
    
    def _cleanup_old_requests(self, now: datetime, window: int):
        """Clean up old request records."""
        cutoff = now - timedelta(seconds=window * 2)
        for ip in list(self.requests.keys()):
            self.requests[ip] = [req_time for req_time in self.requests[ip] 
                               if req_time > cutoff]
            if not self.requests[ip]:
                del self.requests[ip]


class CSRFProtection:
    """CSRF protection for forms."""
    
    def __init__(self):
        self.tokens = {}
    
    def generate_token(self, session_id: str) -> str:
        """Generate CSRF token for session."""
        token = secrets.token_urlsafe(32)
        self.tokens[session_id] = {
            'token': token,
            'created': datetime.now()
        }
        return token
    
    def validate_token(self, session_id: str, token: str) -> bool:
        """Validate CSRF token."""
        if session_id not in self.tokens:
            return False
        
        stored_token = self.tokens[session_id]['token']
        created = self.tokens[session_id]['created']
        
        # Token expires after 1 hour
        if datetime.now() - created > timedelta(hours=1):
            del self.tokens[session_id]
            return False
        
        return stored_token == token
    
    def cleanup_expired_tokens(self):
        """Clean up expired tokens."""
        now = datetime.now()
        expired = [sid for sid, data in self.tokens.items() 
                  if now - data['created'] > timedelta(hours=1)]
        for sid in expired:
            del self.tokens[sid]


# Global instances
rate_limiter = RateLimiter()
csrf_protection = CSRFProtection()


class InputValidator:
    """Comprehensive input validation system."""
    
    # Security patterns to detect
    MALICIOUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                # JavaScript protocol
        r'on\w+\s*=',                 # Event handlers
        r'eval\s*\(',                 # eval() calls
        r'expression\s*\(',           # CSS expressions
        r'vbscript:',                 # VBScript protocol
        r'<iframe[^>]*>',             # iframe tags
        r'<object[^>]*>',             # object tags
        r'<embed[^>]*>',              # embed tags
        r'<link[^>]*>',               # link tags
        r'<meta[^>]*>',               # meta tags
        r'<form[^>]*>',               # form tags
    ]
    
    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r'(union|select|insert|update|delete|drop|create|alter)\s+',
        r'(or|and)\s+\d+\s*=\s*\d+',
        r'[\'\"]\s*(or|and)\s+[\'\"]\d+[\'\"]\s*=\s*[\'\"]\d+[\'\"]*',
        r';\s*(drop|delete|update|insert)',
        r'exec\s*\(',
        r'sp_\w+',
    ]
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 1000) -> str:
        """Sanitize string input."""
        if not isinstance(value, str):
            raise ValidationError("Input must be a string")
        
        # Length check
        if len(value) > max_length:
            raise ValidationError(f"Input exceeds maximum length of {max_length} characters")
        
        # HTML escape
        sanitized = html.escape(value.strip())
        
        # Check for malicious patterns
        for pattern in InputValidator.MALICIOUS_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise SecurityViolation(f"Potentially malicious input detected")
        
        # Check for SQL injection
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, sanitized, re.IGNORECASE):
                raise SecurityViolation("Potential SQL injection detected")
        
        return sanitized
    
    @staticmethod
    def validate_problem_id(problem_id: Any) -> int:
        """Validate problem ID."""
        try:
            pid = int(problem_id)
            if pid <= 0:
                raise ValidationError("Problem ID must be a positive integer")
            if pid > 1000000:  # Reasonable upper limit
                raise ValidationError("Problem ID is too large")
            return pid
        except (ValueError, TypeError):
            raise ValidationError("Problem ID must be a valid integer")
    
    @staticmethod
    def validate_language(language: str, supported_languages: List[str]) -> str:
        """Validate programming language."""
        if not language or not isinstance(language, str):
            raise ValidationError("Programming language is required")
        
        language = language.lower().strip()
        
        if language not in supported_languages:
            raise ValidationError(
                f"Unsupported language: {language}. "
                f"Supported languages: {', '.join(supported_languages)}"
            )
        
        return language
    
    @staticmethod
    def validate_code(code: str, language: str, max_length: int = 50000) -> str:
        """Validate code input."""
        if not code or not isinstance(code, str):
            raise ValidationError("Code cannot be empty")
        
        code = code.strip()
        
        if not code:
            raise ValidationError("Code cannot be empty")
        
        if len(code) > max_length:
            raise ValidationError(
                f"Code exceeds maximum length of {max_length} characters. "
                f"Current length: {len(code)}"
            )
        
        # Language-specific validation
        if language == 'python':
            InputValidator._validate_python_code(code)
        elif language == 'javascript':
            InputValidator._validate_javascript_code(code)
        
        return code
    
    @staticmethod
    def _validate_python_code(code: str):
        """Python-specific code validation."""
        # Check for dangerous imports
        dangerous_imports = [
            'os', 'sys', 'subprocess', 'socket', 'urllib', 'requests',
            'http', 'ftplib', 'smtplib', 'webbrowser', 'tempfile',
            'shutil', 'glob', 'pickle', 'marshal'
        ]
        
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip().lower()
            
            # Check for dangerous imports
            for dangerous in dangerous_imports:
                if f'import {dangerous}' in line or f'from {dangerous}' in line:
                    raise SecurityViolation(
                        f"Restricted import '{dangerous}' found on line {line_num}. "
                        "File operations and network access are not allowed."
                    )
            
            # Check for dangerous functions
            dangerous_functions = ['open(', 'file(', 'input(', 'eval(', 'exec(']
            for func in dangerous_functions:
                if func in line:
                    raise SecurityViolation(
                        f"Restricted function '{func.rstrip('(')}' found on line {line_num}. "
                        "This function is not allowed for security reasons."
                    )
    
    @staticmethod
    def _validate_javascript_code(code: str):
        """JavaScript-specific code validation."""
        dangerous_patterns = [
            'require(', 'import(', 'eval(', 'process.', 'global.',
            '__dirname', '__filename', 'fs.', 'child_process',
            'http.', 'https.', 'net.', 'crypto.'
        ]
        
        lines = code.split('\n')
        for line_num, line in enumerate(lines, 1):
            line = line.strip().lower()
            
            for pattern in dangerous_patterns:
                if pattern in line:
                    raise SecurityViolation(
                        f"Restricted operation '{pattern.rstrip('.')}' found on line {line_num}. "
                        "File operations and network access are not allowed."
                    )
    
    @staticmethod
    def validate_user_name(name: str) -> str:
        """Validate user name input."""
        if not name or not isinstance(name, str):
            raise ValidationError("Name is required")
        
        name = name.strip()
        
        if not name:
            raise ValidationError("Name cannot be empty")
        
        if len(name) > 50:
            raise ValidationError("Name cannot exceed 50 characters")
        
        if len(name) < 2:
            raise ValidationError("Name must be at least 2 characters long")
        
        # Allow only alphanumeric, spaces, and common punctuation
        if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', name):
            raise ValidationError(
                "Name can only contain letters, numbers, spaces, hyphens, underscores, and periods"
            )
        
        return InputValidator.sanitize_string(name, 50)
    
    @staticmethod
    def validate_admin_input(data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate admin form inputs."""
        validated = {}
        
        # Problem title
        if 'title' in data:
            title = InputValidator.sanitize_string(data['title'], 200)
            if len(title) < 3:
                raise ValidationError("Problem title must be at least 3 characters long")
            validated['title'] = title
        
        # Problem description
        if 'description' in data:
            description = InputValidator.sanitize_string(data['description'], 5000)
            if len(description) < 10:
                raise ValidationError("Problem description must be at least 10 characters long")
            validated['description'] = description
        
        # Difficulty
        if 'difficulty' in data:
            difficulty = data['difficulty'].strip().title()
            if difficulty not in ['Easy', 'Medium', 'Hard']:
                raise ValidationError("Difficulty must be Easy, Medium, or Hard")
            validated['difficulty'] = difficulty
        
        return validated


def rate_limit(limit: int = 10, window: int = 60):
    """Decorator for rate limiting."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            
            if rate_limiter.is_rate_limited(client_ip, limit, window):
                return jsonify({
                    "status": "ERROR",
                    "error": {
                        "type": "RATE_LIMIT_EXCEEDED",
                        "message": "Too many requests. Please try again later.",
                        "retry_after": 300  # 5 minutes
                    }
                }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def csrf_protect(f):
    """Decorator for CSRF protection."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method == 'POST':
            session_id = request.environ.get('HTTP_X_SESSION_ID', 'default')
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            
            if not token or not csrf_protection.validate_token(session_id, token):
                return jsonify({
                    "status": "ERROR",
                    "error": {
                        "type": "CSRF_VIOLATION",
                        "message": "Invalid or missing CSRF token",
                    }
                }), 403
        
        return f(*args, **kwargs)
    return decorated_function


def validate_submission_request(request_data: Dict[str, Any]) -> Tuple[int, str, str]:
    """Validate code submission request with enhanced security."""
    try:
        # Extract and validate problem ID
        problem_id = InputValidator.validate_problem_id(request_data.get('problem_id'))
        
        # Extract and validate language
        supported_languages = ['python', 'javascript', 'java', 'cpp']
        language = InputValidator.validate_language(
            request_data.get('language', ''), 
            supported_languages
        )
        
        # Extract and validate code
        code = InputValidator.validate_code(
            request_data.get('code', ''), 
            language
        )
        
        return problem_id, code, language
        
    except (ValidationError, SecurityViolation) as e:
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Unexpected validation error: {e}")
        raise ValidationError("Invalid submission data")


def validate_user_name_request(name: str) -> str:
    """Validate user name setting request."""
    try:
        return InputValidator.validate_user_name(name)
    except (ValidationError, SecurityViolation) as e:
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Unexpected name validation error: {e}")
        raise ValidationError("Invalid name")


def validate_admin_request(request_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate admin form request."""
    try:
        return InputValidator.validate_admin_input(request_data)
    except (ValidationError, SecurityViolation) as e:
        raise ValidationError(str(e))
    except Exception as e:
        logger.error(f"Unexpected admin validation error: {e}")
        raise ValidationError("Invalid admin input")


def get_client_info(request) -> Dict[str, str]:
    """Get client information for logging and security."""
    return {
        'ip': request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr),
        'user_agent': request.headers.get('User-Agent', 'Unknown'),
        'referer': request.headers.get('Referer', 'Unknown'),
        'timestamp': datetime.now().isoformat()
    }


def log_security_event(event_type: str, details: Dict[str, Any], request=None):
    """Log security events for monitoring."""
    log_data = {
        'event_type': event_type,
        'details': details,
        'timestamp': datetime.now().isoformat()
    }
    
    if request:
        log_data['client_info'] = get_client_info(request)
    
    logger.warning(f"Security event: {event_type} - {details}")


# Periodic cleanup function
def cleanup_security_data():
    """Clean up expired security data."""
    csrf_protection.cleanup_expired_tokens()
    # Rate limiter cleanup is handled automatically
