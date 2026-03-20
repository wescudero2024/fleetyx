#!/usr/bin/env python3
"""
Test script to verify complete Estes error flow.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.integrations.utils.error_handler import handle_carrier_api_error, CarrierError
from app.domain.integrations import RateError, RateErrorType

# Test the exact Estes error response
estes_error_response = {
    "data": [],
    "error": {
        "code": 20200,
        "message": "Invalid or missing body parameter",
        "details": "weight value does not conform to datatype Integer"
    }
}

print("🔍 Testing Complete Estes Error Flow...")

try:
    # Step 1: Handle the API error (like EstesClient would)
    carrier_error = handle_carrier_api_error("Estes Express", estes_error_response)
    print(f"✅ Step 1 - CarrierError created: {carrier_error.user_message}")
    
    # Step 2: Convert to RateResponse (like EstesRateProvider would)
    error_message = carrier_error.user_message
    if isinstance(carrier_error, CarrierError):
        error_message = carrier_error.user_message
        error_type = RateErrorType.NETWORK_ERROR
    else:
        error_message = f"Failed to get rates from Estes Express: {str(carrier_error)}"
        error_type = RateErrorType.NETWORK_ERROR
    
    rate_error = RateError(
        error_type=error_type,
        message=error_message,
        carrier_code="ESTES"
    )
    
    print(f"✅ Step 2 - RateError created: {rate_error.message}")
    print(f"✅ Final error message: {rate_error.message}")
    
    # Expected result should be:
    # "Invalid request data for Estes Express. Details: Invalid or missing body parameter"
    
except Exception as e:
    print(f"❌ Error in error flow: {e}")
    import traceback
    traceback.print_exc()
