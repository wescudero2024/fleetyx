import os
from typing import Optional


class EstesConfig:
    """Configuration for Estes Express API integration."""
    
    def __init__(self):
        self.api_key = os.getenv("ESTES_API_KEY")
        self.api_secret = os.getenv("ESTES_API_SECRET")
        self.username = os.getenv("ESTES_USERNAME")
        self.password = os.getenv("ESTES_PASSWORD")
        self.account_number = os.getenv("ESTES_ACCOUNT_NUMBER")
        self.base_url = os.getenv("ESTES_BASE_URL", "https://api.estes-express.com")
        self.timeout = int(os.getenv("ESTES_TIMEOUT", "30"))
        self.retry_attempts = int(os.getenv("ESTES_RETRY_ATTEMPTS", "3"))
        self.retry_delay = float(os.getenv("ESTES_RETRY_DELAY", "1.0"))
    
    @property
    def is_configured(self) -> bool:
        """Check if all required configuration is present."""
        return all([
            self.api_key,
            self.username,
            self.password,
            self.account_number
        ])
    
    def get_auth_headers(self) -> dict:
        """Get authentication headers for Estes API."""
        if not self.is_configured:
            raise ValueError("Estes API configuration is incomplete")
        
        return {
            "X-API-Key": self.api_key,
            "X-API-Secret": self.api_secret,
            "Content-Type": "application/json"
        }
    
    def validate(self) -> None:
        """Validate configuration and raise error if incomplete."""
        if not self.is_configured:
            missing = []
            if not self.api_key:
                missing.append("ESTES_API_KEY")
            if not self.username:
                missing.append("ESTES_USERNAME")
            if not self.password:
                missing.append("ESTES_PASSWORD")
            if not self.account_number:
                missing.append("ESTES_ACCOUNT_NUMBER")
            
            raise ValueError(f"Missing required Estes configuration: {', '.join(missing)}")
