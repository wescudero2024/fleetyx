#!/usr/bin/env python3
"""
Test script to verify Estes payload structure matches the official schema.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.integrations.carriers.estes import EstesConfig, EstesMapper, EstesRateProvider
from app.domain.integrations.rate_request import RateRequest, Address, ShipmentItem, FreightClass
from datetime import datetime

print("🔍 Testing Estes Payload Schema Compliance...")

# Create test data
origin = Address(
    zip_code="10001",
    city="New York", 
    state="NY",
    country="US"
)

destination = Address(
    zip_code="20001",
    city="Washington",
    state="DC", 
    country="US"
)

items = [
    ShipmentItem(
        weight=100.0,  # This will be converted to integer
        length=48.0,  # This will be converted to integer
        width=40.0,   # This will be converted to integer
        height=36.0,  # This will be converted to integer
        freight_class=FreightClass.CLASS_50,
        quantity=1,
        description="Test freight",
        stackable=False
    )
]

request = RateRequest(
    origin=origin,
    destination=destination,
    items=items,
    shipment_date=datetime.now()
)

# Test the mapper
mapper = EstesMapper()
account_number = "B156880"

try:
    payload = mapper.to_estes_payload(request, account_number)
    
    print("✅ Generated Payload Structure:")
    print(f"   Ship Date: {payload['quoteRequest']['shipDate']} (type: {type(payload['quoteRequest']['shipDate'])})")
    print(f"   Service Levels: {payload['quoteRequest']['serviceLevels']}")
    print(f"   Account: {payload['payment']['account']}")
    print(f"   Payor: {payload['payment']['payor']}")
    print(f"   Terms: {payload['payment']['terms']}")
    
    # Check handling units
    handling_unit = payload['commodity']['handlingUnits'][0]
    print(f"   Handling Unit Count: {handling_unit['count']} (type: {type(handling_unit['count'])})")
    print(f"   Handling Unit Type: {handling_unit['type']}")
    print(f"   Handling Unit Weight: {handling_unit['weight']} (type: {type(handling_unit['weight'])})")
    print(f"   Handling Unit Weight Unit: {handling_unit['weightUnit']}")
    
    if 'length' in handling_unit:
        print(f"   Dimensions: {handling_unit['length']}x{handling_unit['width']}x{handling_unit['height']} (type: {type(handling_unit['length'])})")
    
    # Check line items
    line_item = handling_unit['lineItems'][0]
    print(f"   Line Item Weight: {line_item['weight']} (type: {type(line_item['weight'])})")
    print(f"   Line Item Pieces: {line_item['pieces']} (type: {type(line_item['pieces'])})")
    print(f"   Line Item Classification: {line_item['classification']}")
    
    # Validate schema requirements
    print("\n🔍 Schema Validation:")
    
    # Check required fields
    required_fields = [
        ('quoteRequest.shipDate', payload['quoteRequest']['shipDate']),
        ('quoteRequest.serviceLevels', payload['quoteRequest']['serviceLevels']),
        ('payment.account', payload['payment']['account']),
        ('payment.payor', payload['payment']['payor']),
        ('payment.terms', payload['payment']['terms']),
        ('origin.address.city', payload['origin']['address']['city']),
        ('origin.address.stateProvince', payload['origin']['address']['stateProvince']),
        ('origin.address.postalCode', payload['origin']['address']['postalCode']),
        ('origin.address.country', payload['origin']['address']['country']),
        ('destination.address.city', payload['destination']['address']['city']),
        ('destination.address.stateProvince', payload['destination']['address']['stateProvince']),
        ('destination.address.postalCode', payload['destination']['address']['postalCode']),
        ('destination.address.country', payload['destination']['address']['country']),
    ]
    
    for field_path, value in required_fields:
        if value is None or (isinstance(value, str) and not value.strip()):
            print(f"   ❌ Missing required field: {field_path}")
        else:
            print(f"   ✅ {field_path}: {value}")
    
    # Check data types
    type_checks = [
        ('handlingUnits[0].count', handling_unit['count'], int),
        ('handlingUnits[0].weight', handling_unit['weight'], int),
        ('lineItems[0].weight', line_item['weight'], int),
        ('lineItems[0].pieces', line_item['pieces'], int),
    ]
    
    for field_path, value, expected_type in type_checks:
        if not isinstance(value, expected_type):
            print(f"   ❌ {field_path}: Expected {expected_type.__name__}, got {type(value).__name__}")
        else:
            print(f"   ✅ {field_path}: {expected_type.__name__} = {value}")
    
    print("\n✅ Payload schema validation complete!")
    
except Exception as e:
    print(f"❌ Error generating payload: {e}")
    import traceback
    traceback.print_exc()
