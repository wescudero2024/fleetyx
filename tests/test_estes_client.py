import pytest
from unittest.mock import AsyncMock, Mock, patch
import httpx
import tenacity

from app.infrastructure.integrations.carriers.estes import EstesClient, EstesConfig


class TestEstesClient:
    """Test cases for EstesClient."""
    
    @pytest.fixture
    def mock_config(self):
        """Create mock EstesConfig."""
        config = Mock(spec=EstesConfig)
        config.api_key = "test_key"
        config.api_secret = "test_secret"
        config.account_number = "123456"
        config.base_url = "https://api.test-estes.com"
        config.timeout = 30
        config.get_auth_headers.return_value = {
            "X-API-Key": "test_key",
            "X-API-Secret": "test_secret",
            "Content-Type": "application/json"
        }
        return config
    
    @pytest.fixture
    def client(self, mock_config):
        """Create EstesClient instance."""
        return EstesClient(mock_config)
    
    @pytest.fixture
    def sample_payload(self):
        """Sample rate request payload."""
        return {
            "account": "123456",
            "origin": {"zip": "10001"},
            "destination": {"zip": "20001"},
            "items": [{"weight": 100, "class": "50"}]
        }
    
    @pytest.fixture
    def successful_response(self):
        """Successful API response."""
        return {
            "success": True,
            "data": {
                "rates": [
                    {
                        "serviceType": "STANDARD",
                        "totalCharge": 150.0,
                        "baseCharge": 135.0,
                        "fuelSurcharge": 15.0,
                        "accessorialsCharge": 0.0,
                        "transitDays": 3
                    }
                ]
            }
        }
    
    @pytest.mark.asyncio
    async def test_get_rates_success(self, client, mock_config, sample_payload, successful_response):
        """Test successful rate request."""
        # Mock HTTP response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = successful_response
        mock_response.elapsed.total_seconds.return_value = 0.5
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            
            result = await client.get_rates(sample_payload)
            
            # Verify result
            assert result == successful_response
            
            # Verify HTTP call
            mock_client.post.assert_called_once_with(
                "https://api.test-estes.com/v1/rate",
                json=sample_payload,
                headers=mock_config.get_auth_headers.return_value
            )
    
    @pytest.mark.asyncio
    async def test_get_rates_http_error(self, client, mock_config, sample_payload):
        """Test handling of HTTP errors."""
        # Mock HTTP error response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_response.json.return_value = {
            "message": "Invalid ZIP code",
            "errors": ["ZIP code format is invalid"]
        }
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Raise HTTP status error
            http_error = httpx.HTTPStatusError("Bad Request", request=Mock(), response=mock_response)
            mock_client.post.side_effect = http_error
            
            with pytest.raises(ValueError, match="Estes API HTTP error"):
                await client.get_rates(sample_payload)
    
    @pytest.mark.asyncio
    async def test_get_rates_request_error(self, client, sample_payload):
        """Test handling of request errors."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Raise request error
            mock_client.post.side_effect = httpx.RequestError("Connection timeout")
            
            with pytest.raises((httpx.RequestError, tenacity.RetryError)):
                await client.get_rates(sample_payload)
    
    @pytest.mark.asyncio
    async def test_get_rates_api_error_response(self, client, mock_config, sample_payload):
        """Test handling of API-level errors."""
        # Mock API error response
        error_response = {
            "success": False,
            "message": "Authentication failed",
            "errors": ["Invalid API credentials"]
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = error_response
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            
            with pytest.raises(ValueError, match="Estes API error: Authentication failed"):
                await client.get_rates(sample_payload)
    
    @pytest.mark.asyncio
    async def test_get_rates_retry_on_timeout(self, client, mock_config, sample_payload, successful_response):
        """Test retry logic on timeout."""
        # Mock timeout followed by success
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = successful_response
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # First call times out, second succeeds
            mock_client.post.side_effect = [
                httpx.TimeoutException("Request timeout"),
                mock_response
            ]
            
            result = await client.get_rates(sample_payload)
            
            # Verify success after retry
            assert result == successful_response
            
            # Verify retry happened (called twice)
            assert mock_client.post.call_count == 2
    
    @pytest.mark.asyncio
    async def test_get_rates_max_retries_exceeded(self, client, sample_payload):
        """Test max retries exceeded."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            # Always timeout
            mock_client.post.side_effect = httpx.TimeoutException("Request timeout")
            
            with pytest.raises((httpx.TimeoutException, tenacity.RetryError)):
                await client.get_rates(sample_payload)
            
            # Verify max retries attempted (3 times)
            assert mock_client.post.call_count == 3
    
    @pytest.mark.asyncio
    async def test_get_rates_invalid_json(self, client, mock_config, sample_payload):
        """Test handling of invalid JSON response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.side_effect = ValueError("Invalid JSON")
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            
            with pytest.raises(ValueError, match="Unexpected error calling Estes API"):
                await client.get_rates(sample_payload)
    
    @pytest.mark.asyncio
    async def test_test_connection_success(self, client, mock_config):
        """Test successful connection test."""
        # Mock successful rate response
        successful_response = {
            "success": True,
            "data": {"rates": []}
        }
        
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = successful_response
        
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.return_value = mock_response
            
            result = await client.test_connection()
            
            assert result is True
    
    @pytest.mark.asyncio
    async def test_test_connection_failure(self, client):
        """Test failed connection test."""
        with patch('httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            mock_client.post.side_effect = httpx.RequestError("Connection failed")
            
            result = await client.test_connection()
            
            assert result is False
    
    def test_base_url_trailing_slash(self, mock_config):
        """Test base URL normalization."""
        mock_config.base_url = "https://api.test-estes.com/"
        client = EstesClient(mock_config)
        
        assert client.base_url == "https://api.test-estes.com"
    
    def test_base_url_no_trailing_slash(self, mock_config):
        """Test base URL without trailing slash."""
        mock_config.base_url = "https://api.test-estes.com"
        client = EstesClient(mock_config)
        
        assert client.base_url == "https://api.test-estes.com"
