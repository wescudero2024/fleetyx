import logging
import base64
from datetime import datetime, timedelta
from typing import Dict, Any, Optional
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from .estes_config import EstesConfig
from ...utils.error_handler import handle_carrier_http_error, handle_carrier_api_error, handle_carrier_network_error, CarrierError


logger = logging.getLogger(__name__)


class EstesClient:
    """Async HTTP client for Estes Express API."""
    
    def __init__(self, config: EstesConfig):
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self._token_cache = None
        self._token_expiry = None
    
    async def get_rates(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get rates from Estes API.
        
        Args:
            payload: Rate request payload for Estes API
            
        Returns:
            Response data from Estes API
            
        Raises:
            httpx.HTTPError: For HTTP-related errors
            ValueError: For API response errors
        """
        return await self._get_rates_with_retry(payload)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        retry=retry_if_exception_type((httpx.RequestError, httpx.TimeoutException))
    )
    async def _get_rates_with_retry(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        url = f"{self.base_url}/v1/rate-quotes"
        
        # Generate bearer token for authentication
        token = await self._generate_token()
        headers = {
            "apikey": self.config.api_key,
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        logger.info(f"Making rate request to Estes API", extra={
            "url": url,
            "timeout": self.config.timeout
        })
        
        try:
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(
                    url,
                    json=payload,
                    headers=headers
                )
                
                logger.info(f"Estes API response received", extra={
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() if response.elapsed else None
                })
                
                # Handle HTTP errors
                response.raise_for_status()
                
                # Parse JSON response
                response_data = response.json()
                
                # Check for API-level errors (Estes returns 200 with error object)
                if "error" in response_data:
                    error_obj = response_data["error"]
                    # Only treat as error if there's actually an error (non-zero code or non-empty message)
                    if error_obj.get("code", 0) != 0 or error_obj.get("message", ""):
                        raise handle_carrier_api_error("Estes Express", response_data)
                
                # Check for success flag (if present)
                if response_data.get("success") is False:
                    raise handle_carrier_api_error("Estes Express", response_data)
                
                return response_data
                
        except httpx.HTTPStatusError as e:
            # Try to parse response data for better error message
            response_data = None
            try:
                response_data = e.response.json()
            except:
                pass
            
            raise handle_carrier_http_error(
                carrier_name="Estes Express",
                status_code=e.response.status_code,
                response_text=e.response.text,
                response_data=response_data
            )
            
        except httpx.RequestError as e:
            # Don't convert to CarrierError for retries - let tenacity handle it
            logger.error(f"Request error to Estes API", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise
            
        except Exception as e:
            logger.error(f"Unexpected error calling Estes API", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=True)
            
            # Wrap unexpected errors in CarrierError
            if not isinstance(e, CarrierError):
                raise handle_carrier_network_error("Estes Express", e)
            else:
                raise
    
    async def _generate_token(self) -> str:
        """
        Generate bearer token for Estes API authentication.
        
        Returns:
            Bearer token for API requests
            
        Raises:
            ValueError: If authentication fails
        """
        # Check if we have a cached token that's still valid
        if (self._token_cache and self._token_expiry and 
            datetime.now() < self._token_expiry):
            logger.debug("Using cached Estes API token")
            return self._token_cache
        
        logger.info("Generating new Estes API token")
        
        try:
            # Create Basic Auth credentials using username and password
            credentials_string = f"{self.config.username}:{self.config.password}"
            encoded_credentials = base64.b64encode(credentials_string.encode()).decode()
            
            # Prepare authentication request
            auth_url = "https://cloudapi.estes-express.com/authenticate"
            headers = {
                "apikey": self.config.api_key,
                "Authorization": f"Basic {encoded_credentials}",
                "Content-Type": "application/json"
            }
            
            async with httpx.AsyncClient(timeout=self.config.timeout) as client:
                response = await client.post(auth_url, headers=headers)
                
                logger.info(f"Estes auth response received", extra={
                    "status_code": response.status_code,
                    "response_time": response.elapsed.total_seconds() if response.elapsed else None
                })
                
                if response.status_code != 200:
                    logger.error(f"Estes authentication failed", extra={
                        "status_code": response.status_code,
                        "response_text": response.text
                    })
                    raise ValueError(f"Authentication failed: HTTP {response.status_code}")
                
                # Parse response and extract token
                response_data = response.json()
                token = response_data.get("token")
                
                if not token:
                    logger.error("No token received from Estes API")
                    raise ValueError("No token received from Estes API")
                
                # Cache the token (tokens typically expire after 1 hour)
                self._token_cache = token
                self._token_expiry = datetime.now() + timedelta(hours=1)
                
                logger.info("Estes API token generated successfully")
                return token
                
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error during Estes authentication", extra={
                "status_code": e.response.status_code,
                "response_text": e.response.text
            })
            raise ValueError(f"Estes authentication HTTP error: HTTP {e.response.status_code}")
            
        except httpx.RequestError as e:
            logger.error(f"Request error during Estes authentication", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            })
            raise ValueError(f"Estes authentication request error: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error during Estes authentication", extra={
                "error_type": type(e).__name__,
                "error_message": str(e)
            }, exc_info=True)
            raise ValueError(f"Unexpected error during Estes authentication: {str(e)}")
    
    async def test_connection(self) -> bool:
        """Test connection to Estes API."""
        try:
            # Use a minimal payload for testing
            test_payload = {
                "account": self.config.account_number,
                "origin": {"zip": "10001"},
                "destination": {"zip": "20001"},
                "items": [{"weight": 100, "class": "50"}]
            }
            
            await self.get_rates(test_payload)
            logger.info("Estes API connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"Estes API connection test failed", extra={
                "error": str(e)
            })
            return False
