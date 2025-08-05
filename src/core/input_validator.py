"""
Input Validation and Sanitization Module
Protects against injection attacks and malicious inputs
"""

import re
import html
from typing import Dict, Any, Optional, Union
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class InputValidator:
    """Comprehensive input validation and sanitization"""
    
    # Maximum lengths for different input types
    MAX_LENGTHS = {
        'tweet_text': 280,
        'topic': 100,
        'pattern': 50,
        'username': 50,
        'context': 1000,
        'general': 5000
    }
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r'<script[^>]*>.*?</script>',  # Script tags
        r'javascript:',                  # JavaScript protocol
        r'on\w+\s*=',                   # Event handlers
        r'<iframe[^>]*>',               # iframes
        r'<object[^>]*>',               # Objects
        r'<embed[^>]*>',                # Embeds
        r'eval\s*\(',                   # eval function
        r'exec\s*\(',                   # exec function
        r'__import__',                  # Python import
        r'os\.',                        # OS module access
        r'subprocess\.',                # Subprocess access
        r'open\s*\(',                   # File operations
    ]
    
    @classmethod
    def sanitize_text(cls, text: str, max_length: Optional[int] = None, 
                     input_type: str = 'general') -> str:
        """Sanitize text input"""
        if not isinstance(text, str):
            raise ValueError("Input must be a string")
        
        # Determine max length
        if max_length is None:
            max_length = cls.MAX_LENGTHS.get(input_type, cls.MAX_LENGTHS['general'])
        
        # Basic cleaning
        text = text.strip()
        
        # Length check
        if len(text) > max_length:
            logger.warning(f"Input truncated from {len(text)} to {max_length} characters")
            text = text[:max_length]
        
        # HTML escape
        text = html.escape(text)
        
        # Remove dangerous patterns
        for pattern in cls.DANGEROUS_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                logger.warning(f"Dangerous pattern detected and removed: {pattern}")
                text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Normalize whitespace
        text = ' '.join(text.split())
        
        return text
    
    @classmethod
    def validate_pattern_name(cls, pattern: str) -> str:
        """Validate pattern name"""
        if not pattern:
            raise ValueError("Pattern name cannot be empty")
        
        # Sanitize
        pattern = cls.sanitize_text(pattern, input_type='pattern')
        
        # Allow only alphanumeric, underscore, and dash
        if not re.match(r'^[a-zA-Z0-9_-]+$', pattern):
            raise ValueError("Pattern name can only contain letters, numbers, underscore, and dash")
        
        return pattern
    
    @classmethod
    def validate_context(cls, context: Dict[str, Any]) -> Dict[str, Any]:
        """Validate and sanitize context dictionary"""
        if not isinstance(context, dict):
            raise ValueError("Context must be a dictionary")
        
        sanitized = {}
        
        for key, value in context.items():
            # Validate key
            if not isinstance(key, str):
                logger.warning(f"Skipping non-string key: {key}")
                continue
            
            if len(key) > 100:
                logger.warning(f"Key too long, skipping: {key}")
                continue
            
            # Sanitize key
            safe_key = re.sub(r'[^a-zA-Z0-9_]', '_', key)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = cls.sanitize_text(value, input_type='context')
            elif isinstance(value, (int, float)):
                # Validate numeric ranges
                if isinstance(value, int) and -1e9 <= value <= 1e9:
                    sanitized[safe_key] = value
                elif isinstance(value, float) and -1e9 <= value <= 1e9:
                    sanitized[safe_key] = value
                else:
                    logger.warning(f"Numeric value out of range: {key}={value}")
            elif isinstance(value, bool):
                sanitized[safe_key] = value
            elif isinstance(value, list):
                # Sanitize list items (only strings)
                sanitized[safe_key] = [
                    cls.sanitize_text(str(item), max_length=100) 
                    for item in value[:100]  # Limit list size
                ]
            else:
                logger.warning(f"Unsupported value type for {key}: {type(value)}")
        
        return sanitized
    
    @classmethod
    def validate_api_request(cls, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate API request data"""
        validated = {}
        
        # Required fields
        if 'action' not in request_data:
            raise ValueError("Missing required field: action")
        
        # Validate action
        action = str(request_data['action'])
        if action not in ['generate', 'analyze', 'batch', 'status']:
            raise ValueError(f"Invalid action: {action}")
        
        validated['action'] = action
        
        # Validate based on action
        if action == 'generate':
            # Optional context
            if 'context' in request_data:
                validated['context'] = cls.validate_context(request_data['context'])
            
            # Optional pattern
            if 'pattern' in request_data:
                validated['pattern'] = cls.validate_pattern_name(request_data['pattern'])
            
            # Optional quality threshold
            if 'quality_threshold' in request_data:
                threshold = float(request_data['quality_threshold'])
                if 0.0 <= threshold <= 1.0:
                    validated['quality_threshold'] = threshold
                else:
                    raise ValueError("Quality threshold must be between 0.0 and 1.0")
        
        elif action == 'batch':
            if 'requests' not in request_data:
                raise ValueError("Batch action requires 'requests' field")
            
            requests = request_data['requests']
            if not isinstance(requests, list):
                raise ValueError("Requests must be a list")
            
            if len(requests) > 100:
                raise ValueError("Maximum 100 requests per batch")
            
            validated['requests'] = [
                cls.validate_api_request({'action': 'generate', **req})
                for req in requests
            ]
        
        return validated
    
    @classmethod
    def sanitize_filename(cls, filename: str) -> str:
        """Sanitize filename for safe file operations"""
        # Remove path traversal attempts
        filename = filename.replace('..', '')
        filename = filename.replace('/', '')
        filename = filename.replace('\\', '')
        
        # Allow only safe characters
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        
        # Limit length
        if len(filename) > 255:
            filename = filename[:255]
        
        return filename
    
    @classmethod
    def validate_rate_limit_key(cls, key: str) -> str:
        """Validate rate limit key (IP or user ID)"""
        # Remove any potentially dangerous characters
        key = re.sub(r'[^a-zA-Z0-9.:_-]', '', key)
        
        # Limit length
        if len(key) > 100:
            key = key[:100]
        
        return key

class RateLimiter:
    """Simple in-memory rate limiter"""
    
    def __init__(self, per_minute: int = 60, per_hour: int = 1000):
        self.per_minute = per_minute
        self.per_hour = per_hour
        self.requests = {}  # key -> list of timestamps
    
    def check_limit(self, key: str) -> tuple[bool, str]:
        """Check if request is within rate limits"""
        key = InputValidator.validate_rate_limit_key(key)
        now = datetime.utcnow()
        
        if key not in self.requests:
            self.requests[key] = []
        
        # Clean old requests
        minute_ago = (now - timedelta(minutes=1)).timestamp()
        hour_ago = (now - timedelta(hours=1)).timestamp()
        
        self.requests[key] = [
            ts for ts in self.requests[key] 
            if ts > hour_ago
        ]
        
        # Count recent requests
        minute_count = sum(1 for ts in self.requests[key] if ts > minute_ago)
        hour_count = len(self.requests[key])
        
        # Check limits
        if minute_count >= self.per_minute:
            return False, f"Rate limit exceeded: {self.per_minute} requests per minute"
        
        if hour_count >= self.per_hour:
            return False, f"Rate limit exceeded: {self.per_hour} requests per hour"
        
        # Add current request
        self.requests[key].append(now.timestamp())
        
        return True, "OK"

# Example usage
if __name__ == "__main__":
    # Test input validation
    validator = InputValidator()
    
    # Test text sanitization
    dangerous_text = "<script>alert('xss')</script>Hello world!"
    safe_text = validator.sanitize_text(dangerous_text)
    print(f"Sanitized: {safe_text}")
    
    # Test context validation
    context = {
        "topic": "Bitcoin analysis",
        "urgency": "high",
        "malicious": "<script>evil()</script>",
        "number": 42
    }
    safe_context = validator.validate_context(context)
    print(f"Safe context: {safe_context}")
    
    # Test rate limiting
    limiter = RateLimiter(per_minute=5)
    
    for i in range(10):
        allowed, message = limiter.check_limit("user123")
        print(f"Request {i+1}: {allowed} - {message}")