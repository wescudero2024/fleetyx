#!/usr/bin/env python3
"""
Test script to verify the token generation implementation.
"""

import asyncio
import os
import sys
from unittest.mock import AsyncMock, patch
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

from app.infrastructure.integrations.carriers.estes import EstesConfig, EstesClient


async def test_token_generation():
    """Test the token generation method with mock response."""
    
    print("🔐 Testing Token Generation Implementation...")
    
    # Check configuration
    config = EstesConfig()
    if not config.is_configured:
        print("❌ Estes API not configured")
        return False
    
    client = EstesClient(config)
    
    # Mock the HTTP request to simulate successful token response
    mock_response = AsyncMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"token": "mock_bearer_token_12345"}
    mock_response.elapsed.total_seconds.return_value = 0.5
    
    with patch('httpx.AsyncClient') as mock_client_class:
        mock_client = AsyncMock()
        mock_client_class.return_value.__aenter__.return_value = mock_client
        mock_client.post.return_value = mock_response
        
        try:
            # Test token generation
            token = await client._generate_token()
            
            print(f"✅ Token generated: {token}")
            print(f"✅ Token cached: {client._token_cache is not None}")
            print(f"✅ Expiry set: {client._token_expiry is not None}")
            
            # Test token caching (second call should use cache)
            token2 = await client._generate_token()
            
            if token == token2:
                print("✅ Token caching working correctly")
            else:
                print("❌ Token caching failed")
                return False
            
            # Verify HTTP request was made correctly
            mock_client.post.assert_called_once()
            call_args = mock_client.post.call_args
            call_kwargs = call_args[1]
            
            # Check URL
            assert call_args[0][0] == "https://cloudapi.estes-express.com/authenticate"
            print("✅ Correct authentication URL used")
            
            # Check headers
            headers = call_kwargs['headers']
            assert 'apikey' in headers
            assert 'Authorization' in headers
            assert headers['Authorization'].startswith('Basic ')
            print("✅ Correct authentication headers")
            
            print("\n🎉 Token generation implementation is working correctly!")
            return True
            
        except Exception as e:
            print(f"❌ Token generation test failed: {e}")
            return False


if __name__ == "__main__":
    asyncio.run(test_token_generation())
