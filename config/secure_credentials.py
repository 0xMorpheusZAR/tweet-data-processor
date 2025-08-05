"""
Secure Credentials Management System
Replaces hardcoded credentials with environment variables
"""

import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

@dataclass
class TwitterCredentials:
    """Secure Twitter API credentials from environment"""
    api_key: str
    api_key_secret: str
    bearer_token: str
    access_token: Optional[str] = None
    access_token_secret: Optional[str] = None
    
    @classmethod
    def from_env(cls) -> 'TwitterCredentials':
        """Load credentials from environment variables"""
        api_key = os.getenv('TWITTER_API_KEY')
        api_key_secret = os.getenv('TWITTER_API_SECRET')
        bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')
        
        if not all([api_key, api_key_secret, bearer_token]):
            raise ValueError(
                "Missing required Twitter credentials. "
                "Please set TWITTER_API_KEY, TWITTER_API_SECRET, and TWITTER_BEARER_TOKEN "
                "in your environment or .env file"
            )
        
        return cls(
            api_key=api_key,
            api_key_secret=api_key_secret,
            bearer_token=bearer_token,
            access_token=access_token,
            access_token_secret=access_token_secret
        )
    
    def validate(self) -> bool:
        """Validate credentials are properly set"""
        required = [self.api_key, self.api_key_secret, self.bearer_token]
        return all(cred and cred != 'your_api_key_here' for cred in required)

@dataclass
class ServerConfig:
    """Server configuration from environment"""
    host: str
    port: int
    debug: bool
    secret_key: str
    
    @classmethod
    def from_env(cls) -> 'ServerConfig':
        """Load server config from environment"""
        return cls(
            host=os.getenv('SERVER_HOST', '0.0.0.0'),
            port=int(os.getenv('SERVER_PORT', 8080)),
            debug=os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            secret_key=os.getenv('SECRET_KEY', 'default-secret-key-change-me')
        )

@dataclass
class SecurityConfig:
    """Security configuration"""
    rate_limit_per_minute: int
    rate_limit_per_hour: int
    allowed_origins: list
    jwt_secret: str
    
    @classmethod
    def from_env(cls) -> 'SecurityConfig':
        """Load security config from environment"""
        origins = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8080').split(',')
        return cls(
            rate_limit_per_minute=int(os.getenv('RATE_LIMIT_PER_MINUTE', 60)),
            rate_limit_per_hour=int(os.getenv('RATE_LIMIT_PER_HOUR', 1000)),
            allowed_origins=[origin.strip() for origin in origins],
            jwt_secret=os.getenv('JWT_SECRET_KEY', 'default-jwt-secret-change-me')
        )

# Singleton instances
_twitter_creds = None
_server_config = None
_security_config = None

def get_twitter_credentials() -> TwitterCredentials:
    """Get Twitter credentials singleton"""
    global _twitter_creds
    if _twitter_creds is None:
        _twitter_creds = TwitterCredentials.from_env()
        if not _twitter_creds.validate():
            logger.warning("Twitter credentials not properly configured")
    return _twitter_creds

def get_server_config() -> ServerConfig:
    """Get server configuration singleton"""
    global _server_config
    if _server_config is None:
        _server_config = ServerConfig.from_env()
    return _server_config

def get_security_config() -> SecurityConfig:
    """Get security configuration singleton"""
    global _security_config
    if _security_config is None:
        _security_config = SecurityConfig.from_env()
    return _security_config

# Utility function to check if running with default/example credentials
def check_credential_security() -> dict:
    """Check if credentials are securely configured"""
    issues = []
    
    # Check Twitter credentials
    try:
        twitter = get_twitter_credentials()
        if 'your_api_key_here' in str(twitter.api_key):
            issues.append("Twitter API key not configured")
    except ValueError as e:
        issues.append(f"Twitter credentials error: {e}")
    
    # Check server secret
    server = get_server_config()
    if server.secret_key == 'default-secret-key-change-me':
        issues.append("Server secret key is using default value")
    
    # Check JWT secret
    security = get_security_config()
    if security.jwt_secret == 'default-jwt-secret-change-me':
        issues.append("JWT secret key is using default value")
    
    return {
        'secure': len(issues) == 0,
        'issues': issues
    }

if __name__ == "__main__":
    # Test credential loading
    print("Testing secure credential management...")
    
    security_check = check_credential_security()
    if security_check['secure']:
        print("✓ All credentials properly configured")
    else:
        print("⚠️ Security issues found:")
        for issue in security_check['issues']:
            print(f"  - {issue}")