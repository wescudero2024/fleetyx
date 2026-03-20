#!/usr/bin/env python3
"""
Test script to verify Estes error handling.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.integrations.utils.error_handler import handle_carrier_api_error, CarrierError

# Test the exact Estes error response
estes_error_response = {
    "data": [],
    "error": {
        "code": 20200,
        "message": "Invalid or missing body parameter",
        "details": "weight value does not conform to datatype Integer"
    }
}

print("🔍 Testing Estes Error Response Handling...")
print(f"Input: {estes_error_response}")

try:
    carrier_error = handle_carrier_api_error("Estes Express", estes_error_response)
    
    print(f"✅ Error Type: {carrier_error.error_type.value}")
    print(f"✅ Carrier Name: {carrier_error.carrier_name}")
    print(f"✅ Original Message: {carrier_error.original_message}")
    print(f"✅ User Message: {carrier_error.user_message}")
    print(f"✅ Status Code: {carrier_error.status_code}")
    
except Exception as e:
    print(f"❌ Error in error handler: {e}")
    import traceback
    traceback.print_exc()
