"""
Global carrier error handling utilities.
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class CarrierErrorType(Enum):
    """Standardized carrier error types."""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization" 
    VALIDATION = "validation"
    NETWORK = "network"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    SERVICE_UNAVAILABLE = "service_unavailable"
    UNKNOWN = "unknown"


class CarrierError(Exception):
    """Standardized carrier error with proper error message handling."""
    
    def __init__(self, carrier_name: str, error_type: CarrierErrorType, 
                 original_message: str, status_code: Optional[int] = None,
                 response_data: Optional[Dict[str, Any]] = None):
        self.carrier_name = carrier_name
        self.error_type = error_type
        self.original_message = original_message
        self.status_code = status_code
        self.response_data = response_data
        
        # Create user-friendly error message
        self.user_message = self._format_user_message()
        
        super().__init__(self.user_message)
    
    def _format_user_message(self) -> str:
        """Format error message for user consumption."""
        base_msg = f"{self.carrier_name}: {self.original_message}"
        
        # Add context based on error type
        if self.error_type == CarrierErrorType.AUTHENTICATION:
            return f"Authentication failed with {self.carrier_name}. Please check API credentials. Details: {self.original_message}"
        elif self.error_type == CarrierErrorType.AUTHORIZATION:
            return f"Access denied by {self.carrier_name}. Please check permissions. Details: {self.original_message}"
        elif self.error_type == CarrierErrorType.VALIDATION:
            return f"Invalid request data for {self.carrier_name}. Details: {self.original_message}"
        elif self.error_type == CarrierErrorType.RATE_LIMIT:
            return f"Rate limit exceeded for {self.carrier_name}. Please try again later. Details: {self.original_message}"
        elif self.error_type == CarrierErrorType.SERVICE_UNAVAILABLE:
            return f"{self.carrier_name} service is temporarily unavailable. Please try again later."
        elif self.error_type == CarrierErrorType.NETWORK:
            return f"Network error connecting to {self.carrier_name}. Please check connection. Details: {self.original_message}"
        elif self.error_type == CarrierErrorType.TIMEOUT:
            return f"Request to {self.carrier_name} timed out. Please try again."
        else:
            return base_msg


def handle_carrier_http_error(carrier_name: str, status_code: int, 
                           response_text: str, response_data: Optional[Dict[str, Any]] = None) -> CarrierError:
    """
    Handle HTTP errors from carrier APIs with standardized error messages.
    
    Args:
        carrier_name: Name of the carrier (e.g., "Estes Express")
        status_code: HTTP status code
        response_text: Raw response text
        response_data: Parsed JSON response data if available
        
    Returns:
        CarrierError with appropriate error type and message
    """
    # Extract error message from response data if available
    error_message = None
    
    if response_data:
        # Check for error object (like Estes format)
        if "error" in response_data:
            error_obj = response_data["error"]
            if isinstance(error_obj, dict):
                error_message = error_obj.get("message") or error_obj.get("description") or str(error_obj)
            else:
                error_message = str(error_obj)
        else:
            # Common error message fields
            for field in ["message", "error", "error_description", "detail"]:
                if field in response_data:
                    error_message = response_data[field]
                    break
    else:
        # Try to parse response text as JSON
        try:
            import json
            parsed_data = json.loads(response_text)
            if "error" in parsed_data:
                error_obj = parsed_data["error"]
                if isinstance(error_obj, dict):
                    error_message = error_obj.get("message") or error_obj.get("description") or str(error_obj)
                else:
                    error_message = str(error_obj)
            else:
                error_message = parsed_data.get("message", response_text)
        except:
            error_message = response_text
    
    # Determine error type based on status code
    if status_code == 401:
        error_type = CarrierErrorType.AUTHENTICATION
    elif status_code == 403:
        error_type = CarrierErrorType.AUTHORIZATION
    elif status_code == 422:
        error_type = CarrierErrorType.VALIDATION
    elif status_code == 429:
        error_type = CarrierErrorType.RATE_LIMIT
    elif status_code >= 500:
        error_type = CarrierErrorType.SERVICE_UNAVAILABLE
    else:
        error_type = CarrierErrorType.UNKNOWN
    
    logger.error(f"HTTP error from {carrier_name}", extra={
        "status_code": status_code,
        "error_type": error_type.value,
        "error_message": error_message,
        "response_data": response_data
    })
    
    return CarrierError(
        carrier_name=carrier_name,
        error_type=error_type,
        original_message=error_message,
        status_code=status_code,
        response_data=response_data
    )


def handle_carrier_api_error(carrier_name: str, response_data: Dict[str, Any]) -> CarrierError:
    """
    Handle API-level errors from carrier responses.
    
    Args:
        carrier_name: Name of the carrier
        response_data: Parsed JSON response data
        
    Returns:
        CarrierError with appropriate error type and message
    """
    # Extract error message from various carrier response formats
    error_message = None
    
    # Check for error object (like Estes format)
    if "error" in response_data:
        error_obj = response_data["error"]
        if isinstance(error_obj, dict):
            error_message = error_obj.get("message") or error_obj.get("description") or str(error_obj)
        else:
            error_message = str(error_obj)
    
    # Common error message fields
    if not error_message:
        for field in ["message", "error", "error_description", "detail"]:
            if field in response_data:
                error_message = response_data[field]
                break
    
    # Check for errors array
    if not error_message and "errors" in response_data:
        errors = response_data["errors"]
        if isinstance(errors, list) and errors:
            error_message = str(errors[0].get("message", errors[0]))
        elif isinstance(errors, dict):
            error_message = str(errors.get("message", errors))
    
    # Default message
    if not error_message:
        error_message = "Unknown API error"
    
    # Try to determine error type from message content
    error_type = CarrierErrorType.UNKNOWN
    error_msg_lower = error_message.lower()
    
    if "authentication" in error_msg_lower or "unauthorized" in error_msg_lower:
        error_type = CarrierErrorType.AUTHENTICATION
    elif "permission" in error_msg_lower or "forbidden" in error_msg_lower:
        error_type = CarrierErrorType.AUTHORIZATION
    elif "validation" in error_msg_lower or "invalid" in error_msg_lower or "missing" in error_msg_lower:
        error_type = CarrierErrorType.VALIDATION
    elif "rate limit" in error_msg_lower or "too many" in error_msg_lower:
        error_type = CarrierErrorType.RATE_LIMIT
    elif "timeout" in error_msg_lower:
        error_type = CarrierErrorType.TIMEOUT
    elif "unavailable" in error_msg_lower or "maintenance" in error_msg_lower:
        error_type = CarrierErrorType.SERVICE_UNAVAILABLE
    
    logger.error(f"API error from {carrier_name}", extra={
        "error_type": error_type.value,
        "error_message": error_message,
        "response_data": response_data
    })
    
    return CarrierError(
        carrier_name=carrier_name,
        error_type=error_type,
        original_message=error_message,
        response_data=response_data
    )


def handle_carrier_network_error(carrier_name: str, original_error: Exception) -> CarrierError:
    """
    Handle network/connectivity errors.
    
    Args:
        carrier_name: Name of the carrier
        original_error: Original network exception
        
    Returns:
        CarrierError with network error type
    """
    error_message = str(original_error)
    
    # Determine error type
    if "timeout" in error_message.lower():
        error_type = CarrierErrorType.TIMEOUT
    else:
        error_type = CarrierErrorType.NETWORK
    
    logger.error(f"Network error for {carrier_name}", extra={
        "error_type": error_type.value,
        "error_message": error_message
    })
    
    return CarrierError(
        carrier_name=carrier_name,
        error_type=error_type,
        original_message=error_message
    )


def extract_carrier_error_details(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract standardized error details from carrier response.
    
    Args:
        response_data: Carrier response data
        
    Returns:
        Dictionary with standardized error details
    """
    details = {}
    
    # Extract common error fields
    for field in ["error_code", "code", "error_id"]:
        if field in response_data:
            details["error_code"] = response_data[field]
            break
    
    # Extract validation errors
    if "validation_errors" in response_data:
        details["validation_errors"] = response_data["validation_errors"]
    elif "field_errors" in response_data:
        details["validation_errors"] = response_data["field_errors"]
    
    # Extract additional context
    for field in ["request_id", "correlation_id", "timestamp"]:
        if field in response_data:
            details[field] = response_data[field]
    
    return details
