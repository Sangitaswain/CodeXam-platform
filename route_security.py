"""
Enhanced Route Security and Validation

This module provides comprehensive security enhancements for Flask routes including
CSRF protection, input validation, rate limiting, and security headers.
"""

import hashlib
import hmac
import time
import re
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, Any, Optional, List
from flask import request, session, jsonify, abort, g
import secrets

logger = logging.getLogger(__name__)

# Security configuration
CSRF_SECRET_KEY = secrets.token_hex(32)
RATE_LIMIT_STORAGE = {}
BLOCKED_IPS = set()
SECURITY_HEADERS = {
    'X-Content-Type-Options': 'nosniff',
    'X-Frame-Options': 'DENY',
    'X-XSS-Protection': '1; mode=block',
    'Strict-Transport-Security': 'max-age=31536000; includeSubDomains',
    'Content-Security-Policy': "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'",
    'Referrer-Policy': 'strict-origin-when-cross-origin'
}

class SecurityError(Exception):
    """Custom exception for security-related errors."""
    def __init__(self, message: str, error_code: str = "SECURITY_ERROR"):
        super().__init__(message)
        self.error_code = error_code

class ValidationError(Exception):
    """Custom exception for validation errors."""
    def __init__(self, message: str, field: str = None):
        super().__init__(message)
        self.field = field

def generate_csrf_token() -> str:
    """Generate a CSRF token for the current session."""
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(32)
    return session['csrf_token']

def validate_csrf_token(token: str) -> bool:
    """Validate CSRF token against session token."""
    session_token = session.get('csrf_token')
    if not session_token or not token:
        return False
    return hmac.compare_digest(session_token, token)

def csrf_protect(f):
    """Decorator to protect routes with CSRF tokens."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'DELETE', 'PATCH']:
            token = request.form.get('csrf_token') or request.headers.get('X-CSRF-Token')
            if not validate_csrf_token(token):
                logger.warning(f"CSRF token validation failed for {request.endpoint}")
                return jsonify({
                    'status': 'error',
                    'message': 'CSRF token validation failed',
                    'error_code': 'CSRF_INVALID'
                }), 403
        return f(*args, **kwargs)
    return decorated_functiondef r
ate_limit(max_requests: int = 60, window: int = 60, per_ip: bool = True):
    """Enhanced rate limiting decorator with IP-based and user-based limits."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Get identifier (IP or user)
            if per_ip:
                identifier = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            else:
                identifier = session.get('user_name', request.remote_addr)
            
            current_time = time.time()
            window_start = current_time - window
            
            # Initialize storage for identifier
            if identifier not in RATE_LIMIT_STORAGE:
                RATE_LIMIT_STORAGE[identifier] = []
            
            # Clean old entries
            RATE_LIMIT_STORAGE[identifier] = [
                timestamp for timestamp in RATE_LIMIT_STORAGE[identifier]
                if timestamp > window_start
            ]
            
            # Check rate limit
            if len(RATE_LIMIT_STORAGE[identifier]) >= max_requests:
                logger.warning(f"Rate limit exceeded for {identifier} on {request.endpoint}")
                return jsonify({
                    'status': 'error',
                    'message': 'Rate limit exceeded. Please try again later.',
                    'error_code': 'RATE_LIMIT_EXCEEDED',
                    'retry_after': window
                }), 429
            
            # Add current request
            RATE_LIMIT_STORAGE[identifier].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def security_headers(f):
    """Decorator to add security headers to responses."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        response = f(*args, **kwargs)
        
        # Add security headers
        if hasattr(response, 'headers'):
            for header, value in SECURITY_HEADERS.items():
                response.headers[header] = value
        
        return response
    return decorated_function

def validate_input(validation_rules: Dict[str, Any]):
    """Decorator for comprehensive input validation."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            errors = []
            
            for field, rules in validation_rules.items():
                value = request.form.get(field) or request.json.get(field) if request.is_json else None
                
                # Required field check
                if rules.get('required', False) and not value:
                    errors.append(f"{field} is required")
                    continue
                
                if value is not None:
                    # Type validation
                    if 'type' in rules:
                        try:
                            if rules['type'] == 'int':
                                value = int(value)
                            elif rules['type'] == 'float':
                                value = float(value)
                            elif rules['type'] == 'email':
                                if not re.match(r'^[^@]+@[^@]+\.[^@]+$', value):
                                    errors.append(f"{field} must be a valid email")
                        except ValueError:
                            errors.append(f"{field} must be of type {rules['type']}")
                    
                    # Length validation
                    if 'min_length' in rules and len(str(value)) < rules['min_length']:
                        errors.append(f"{field} must be at least {rules['min_length']} characters")
                    
                    if 'max_length' in rules and len(str(value)) > rules['max_length']:
                        errors.append(f"{field} must be at most {rules['max_length']} characters")
                    
                    # Pattern validation
                    if 'pattern' in rules and not re.match(rules['pattern'], str(value)):
                        errors.append(f"{field} format is invalid")
                    
                    # Custom validation
                    if 'validator' in rules:
                        try:
                            rules['validator'](value)
                        except ValidationError as e:
                            errors.append(f"{field}: {str(e)}")
            
            if errors:
                return jsonify({
                    'status': 'error',
                    'message': 'Validation failed',
                    'errors': errors,
                    'error_code': 'VALIDATION_ERROR'
                }), 400
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def sanitize_input(input_str: str, allow_html: bool = False) -> str:
    """Sanitize user input to prevent XSS and other attacks."""
    if not input_str:
        return ""
    
    # Remove null bytes
    input_str = input_str.replace('\x00', '')
    
    if not allow_html:
        # Escape HTML characters
        html_escape_table = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&#x27;",
            ">": "&gt;",
            "<": "&lt;",
        }
        input_str = "".join(html_escape_table.get(c, c) for c in input_str)
    
    # Remove potentially dangerous patterns
    dangerous_patterns = [
        r'javascript:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'onclick=',
        r'<script',
        r'</script>',
    ]
    
    for pattern in dangerous_patterns:
        input_str = re.sub(pattern, '', input_str, flags=re.IGNORECASE)
    
    return input_str.strip()

def validate_code_submission(code: str, language: str, max_length: int = 50000) -> Dict[str, Any]:
    """Comprehensive validation for code submissions."""
    errors = []
    warnings = []
    
    # Basic validation
    if not code or not code.strip():
        errors.append("Code cannot be empty")
    
    if not language:
        errors.append("Programming language must be specified")
    
    if language not in ['python', 'javascript', 'java', 'cpp']:
        errors.append(f"Unsupported language: {language}")
    
    if len(code) > max_length:
        errors.append(f"Code exceeds maximum length of {max_length} characters")
    
    # Security validation
    dangerous_patterns = {
        'python': [
            r'import\s+os',
            r'import\s+sys',
            r'import\s+subprocess',
            r'__import__',
            r'eval\s*\(',
            r'exec\s*\(',
            r'open\s*\(',
            r'file\s*\(',
            r'input\s*\(',
            r'raw_input\s*\(',
        ],
        'javascript': [
            r'require\s*\(',
            r'process\.',
            r'global\.',
            r'eval\s*\(',
            r'Function\s*\(',
            r'setTimeout',
            r'setInterval',
        ],
        'java': [
            r'System\.exit',
            r'Runtime\.getRuntime',
            r'ProcessBuilder',
            r'Class\.forName',
            r'java\.io\.File',
            r'java\.lang\.reflect',
        ],
        'cpp': [
            r'#include\s*<fstream>',
            r'#include\s*<cstdlib>',
            r'system\s*\(',
            r'exec\s*\(',
            r'popen\s*\(',
        ]
    }
    
    if language in dangerous_patterns:
        code_lower = code.lower()
        for pattern in dangerous_patterns[language]:
            if re.search(pattern, code_lower):
                errors.append(f"Code contains restricted pattern: {pattern}")
    
    # Performance warnings
    if len(code) > 10000:
        warnings.append("Large code size may impact execution performance")
    
    if code.count('while') + code.count('for') > 10:
        warnings.append("Multiple loops detected - ensure efficient algorithms")
    
    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

def log_security_event(event_type: str, details: Dict[str, Any], request_obj=None):
    """Log security events for monitoring and analysis."""
    event_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'details': details
    }
    
    if request_obj:
        event_data.update({
            'ip_address': request_obj.environ.get('HTTP_X_FORWARDED_FOR', request_obj.remote_addr),
            'user_agent': request_obj.headers.get('User-Agent', ''),
            'endpoint': request_obj.endpoint,
            'method': request_obj.method,
            'user': session.get('user_name', 'Anonymous')
        })
    
    logger.warning(f"Security event: {event_type} - {details}")

def check_ip_reputation(ip_address: str) -> bool:
    """Check if IP address is in blocked list or has bad reputation."""
    # Check blocked IPs
    if ip_address in BLOCKED_IPS:
        return False
    
    # Check for suspicious patterns
    suspicious_patterns = [
        r'^10\.',      # Private networks (should not be external)
        r'^192\.168\.', # Private networks
        r'^172\.(1[6-9]|2[0-9]|3[0-1])\.',  # Private networks
    ]
    
    # Allow private networks in development
    if any(re.match(pattern, ip_address) for pattern in suspicious_patterns):
        return True  # Allow in development
    
    return True  # Default allow

def validate_user_agent(user_agent: str) -> bool:
    """Validate user agent string for suspicious patterns."""
    if not user_agent:
        return False
    
    # Check for bot patterns
    bot_patterns = [
        r'bot',
        r'crawler',
        r'spider',
        r'scraper',
        r'curl',
        r'wget',
        r'python-requests',
    ]
    
    user_agent_lower = user_agent.lower()
    for pattern in bot_patterns:
        if re.search(pattern, user_agent_lower):
            logger.info(f"Bot detected: {user_agent}")
            return True  # Allow bots but log them
    
    return True

def enhanced_request_validation(f):
    """Comprehensive request validation decorator."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get client IP
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        
        # Check IP reputation
        if not check_ip_reputation(client_ip):
            log_security_event('blocked_ip_access', {'ip': client_ip}, request)
            abort(403)
        
        # Validate user agent
        user_agent = request.headers.get('User-Agent', '')
        if not validate_user_agent(user_agent):
            log_security_event('invalid_user_agent', {'user_agent': user_agent}, request)
            abort(400)
        
        # Check request size
        if request.content_length and request.content_length > 10 * 1024 * 1024:  # 10MB limit
            log_security_event('oversized_request', {'size': request.content_length}, request)
            abort(413)
        
        # Validate content type for POST requests
        if request.method == 'POST' and request.content_type:
            allowed_content_types = [
                'application/x-www-form-urlencoded',
                'application/json',
                'multipart/form-data'
            ]
            if not any(ct in request.content_type for ct in allowed_content_types):
                log_security_event('invalid_content_type', {'content_type': request.content_type}, request)
                abort(400)
        
        return f(*args, **kwargs)
    return decorated_function

# Custom validators for specific fields
def validate_problem_id(value):
    """Validate problem ID."""
    try:
        problem_id = int(value)
        if problem_id <= 0:
            raise ValidationError("Problem ID must be positive")
        return problem_id
    except ValueError:
        raise ValidationError("Problem ID must be a valid integer")

def validate_language(value):
    """Validate programming language."""
    supported_languages = ['python', 'javascript', 'java', 'cpp']
    if value.lower() not in supported_languages:
        raise ValidationError(f"Language must be one of: {', '.join(supported_languages)}")
    return value.lower()

def validate_difficulty(value):
    """Validate problem difficulty."""
    valid_difficulties = ['Easy', 'Medium', 'Hard']
    if value not in valid_difficulties:
        raise ValidationError(f"Difficulty must be one of: {', '.join(valid_difficulties)}")
    return value

def validate_user_name(value):
    """Validate user name."""
    if not value or len(value.strip()) == 0:
        raise ValidationError("User name cannot be empty")
    
    if len(value) > 50:
        raise ValidationError("User name cannot exceed 50 characters")
    
    # Check for invalid characters
    if not re.match(r'^[a-zA-Z0-9_\-\s]+$', value):
        raise ValidationError("User name can only contain letters, numbers, spaces, hyphens, and underscores")
    
    return value.strip()

# Security monitoring functions
def get_security_metrics() -> Dict[str, Any]:
    """Get security metrics for monitoring."""
    current_time = time.time()
    hour_ago = current_time - 3600
    
    # Count recent rate limit violations
    recent_violations = 0
    for identifier, timestamps in RATE_LIMIT_STORAGE.items():
        recent_violations += len([t for t in timestamps if t > hour_ago])
    
    return {
        'blocked_ips': len(BLOCKED_IPS),
        'rate_limit_violations_last_hour': recent_violations,
        'active_rate_limited_clients': len(RATE_LIMIT_STORAGE),
        'timestamp': datetime.now().isoformat()
    }

def cleanup_rate_limit_storage():
    """Clean up old rate limit entries to prevent memory leaks."""
    current_time = time.time()
    cutoff_time = current_time - 3600  # Keep last hour
    
    for identifier in list(RATE_LIMIT_STORAGE.keys()):
        RATE_LIMIT_STORAGE[identifier] = [
            timestamp for timestamp in RATE_LIMIT_STORAGE[identifier]
            if timestamp > cutoff_time
        ]
        
        # Remove empty entries
        if not RATE_LIMIT_STORAGE[identifier]:
            del RATE_LIMIT_STORAGE[identifier]