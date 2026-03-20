#!/usr/bin/env python3
"""
Test script to verify flexible accessorials validation.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import json
from app.interfaces.api.schemas import RateRequestSchema

print("🔍 Testing Flexible Accessorials Validation...")

# Test cases with various accessorial formats
test_cases = [
    {
        "name": "Standard accessorials",
        "accessorials": ["LIFT_GATE", "RESIDENTIAL", "APPOINTMENT"],
        "should_pass": True
    },
    {
        "name": "Custom accessorials (original issue)",
        "accessorials": ["LIFTGATE_DELIVERY", "RESIDENTIAL_DELIVERY", "APPOINTMENT_DELIVERY"],
        "should_pass": True
    },
    {
        "name": "Mixed format accessorials",
        "accessorials": ["LIFT_GATE", "RESIDENTIAL_DELIVERY", "CUSTOM_ACCESSORIAL", "SPECIAL_SERVICE"],
        "should_pass": True
    },
    {
        "name": "Empty accessorials",
        "accessorials": [],
        "should_pass": True
    },
    {
        "name": "Single custom accessorial",
        "accessorials": ["SOME_RANDOM_ACCESSORIAL_NAME"],
        "should_pass": True
    },
    {
        "name": "Numeric accessorials",
        "accessorials": ["123", "456_SERVICE"],
        "should_pass": True
    }
]

# Base request data
base_request = {
    "origin": {
        "zip_code": "10001",
        "city": "New York",
        "state": "NY",
        "country": "US"
    },
    "destination": {
        "zip_code": "20001",
        "city": "Washington",
        "state": "DC",
        "country": "US"
    },
    "items": [
        {
            "weight": 100.0,
            "length": 48.0,
            "width": 40.0,
            "height": 36.0,
            "freight_class": "50",
            "quantity": 1,
            "description": "Test freight"
        }
    ]
}

passed_tests = 0
failed_tests = 0

for i, test_case in enumerate(test_cases, 1):
    print(f"\n📋 Test {i}: {test_case['name']}")
    print(f"   Accessorials: {test_case['accessorials']}")
    
    # Create request with test accessorials
    request_data = base_request.copy()
    request_data["accessorials"] = test_case["accessorials"]
    
    try:
        # Validate with Pydantic schema
        schema = RateRequestSchema(**request_data)
        
        if test_case["should_pass"]:
            print(f"   ✅ PASSED - Validation succeeded as expected")
            print(f"   📊 Parsed accessorials: {schema.accessorials}")
            passed_tests += 1
        else:
            print(f"   ❌ FAILED - Expected validation to fail but it passed")
            failed_tests += 1
            
    except Exception as e:
        if test_case["should_pass"]:
            print(f"   ❌ FAILED - Expected validation to pass but got error: {e}")
            failed_tests += 1
        else:
            print(f"   ✅ PASSED - Validation failed as expected: {e}")
            passed_tests += 1

print(f"\n📊 Test Results:")
print(f"   ✅ Passed: {passed_tests}")
print(f"   ❌ Failed: {failed_tests}")
print(f"   📈 Success Rate: {passed_tests/(passed_tests+failed_tests)*100:.1f}%")

if failed_tests == 0:
    print("\n🎉 All tests passed! Flexible accessorials validation is working correctly.")
    print("\n💡 The system now accepts ANY string value for accessorials:")
    print("   - Standard names: LIFT_GATE, RESIDENTIAL, APPOINTMENT")
    print("   - Custom names: LIFTGATE_DELIVERY, RESIDENTIAL_DELIVERY")
    print("   - Any format: CUSTOM_ACCESSORIAL, 123_SERVICE, etc.")
else:
    print(f"\n⚠️  {failed_tests} test(s) failed. Please check the implementation.")
