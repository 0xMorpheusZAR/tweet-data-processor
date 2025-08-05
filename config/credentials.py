"""
Secure credential management for Twitter/X API
"""
import os
from typing import Dict, Optional
from dataclasses import dataclass
import json
from pathlib import Path

@dataclass
class TwitterCredentials:
    """Twitter API credentials container"""
    api_key: str
    api_key_secret: str
    bearer_token: str
    
    @classmethod
    def from_env(cls) -> 'TwitterCredentials':
        """Load credentials from environment variables"""
        return cls(
            api_key=os.getenv('TWITTER_API_KEY', ''),
            api_key_secret=os.getenv('TWITTER_API_KEY_SECRET', ''),
            bearer_token=os.getenv('TWITTER_BEARER_TOKEN', '')
        )
    
    @classmethod
    def from_file(cls, filepath: Path) -> 'TwitterCredentials':
        """Load credentials from secure file"""
        with open(filepath, 'r') as f:
            data = json.load(f)
        return cls(**data)
    
    def is_valid(self) -> bool:
        """Check if all credentials are present"""
        return all([self.api_key, self.api_key_secret, self.bearer_token])
    
    def get_headers(self) -> Dict[str, str]:
        """Get authorization headers for API requests"""
        return {
            'Authorization': f'Bearer {self.bearer_token}',
            'Content-Type': 'application/json'
        }

class CredentialManager:
    """Manages secure access to API credentials"""
    
    def __init__(self):
        self._credentials: Optional[TwitterCredentials] = None
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from environment or secure storage"""
        # First try environment variables
        creds = TwitterCredentials.from_env()
        
        # If not in env, try secure file
        if not creds.is_valid():
            creds_file = Path(__file__).parent / '.credentials.json'
            if creds_file.exists():
                creds = TwitterCredentials.from_file(creds_file)
        
        # Use provided credentials as fallback
        if not creds.is_valid():
            creds = TwitterCredentials(
                api_key='TSNUMvJt8cZaS9EhIvVdgFcYA',
                api_key_secret='H3uGj69Wqm50AHiVmNAFL1XYdPSIdvnJwRfuEezT8dAZglga1e',
                bearer_token='AAAAAAAAAAAAAAAAAAAAAJi13QEAAAAAghVwuLws1YdchbwCAkUjqqwu6oc%3DeImrILD6DNOvuOdZiH42oFM3Ww7zTLYaiz1onypLp8XNzCskQ7'
            )
        
        self._credentials = creds
    
    @property
    def credentials(self) -> TwitterCredentials:
        """Get Twitter credentials"""
        if not self._credentials:
            raise ValueError("No valid credentials available")
        return self._credentials
    
    def get_headers(self) -> Dict[str, str]:
        """Get API request headers"""
        return self.credentials.get_headers()

# Global credential manager instance
credential_manager = CredentialManager()