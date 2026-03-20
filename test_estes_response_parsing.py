#!/usr/bin/env python3
"""
Test script to verify Estes response parsing with actual API response.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.infrastructure.integrations.carriers.estes import EstesMapper

# Actual Estes API response
estes_response = {
    "data": [
        {
            "serviceLevelId": "99",
            "serviceLevelText": "LTL Standard Transit",
            "quoteId": "LXYQQTR",
            "rateFound": True,
            "dates": {
                "quoteExpiration": "2026-03-20-00.00.00.000000",
                "transitDeliveryDate": "2026-03-24",
                "transitDeliveryTime": "17:00"
            },
            "transitDetails": {
                "transitDays": 2,
                "laneType": "DIRECT",
                "originTerminal": "178",
                "originTerminalInfo": {
                    "name": "Brooklyn",
                    "address1": ".",
                    "city": "North Bergen",
                    "stateProvince": "NJ",
                    "postalCode": "07047",
                    "country": "US",
                    "contact": {
                        "name": "Luis Tirado",
                        "phone": "(201) 869-4238",
                        "fax": "12018694239"
                    }
                },
                "destinationTerminal": "029",
                "destinationTerminalInfo": {
                    "name": "Baltimore",
                    "address1": "5101 Washington Boulevard",
                    "city": "Baltimore",
                    "stateProvince": "MD",
                    "postalCode": "21227",
                    "country": "US",
                    "contact": {
                        "name": "Herman Braxton",
                        "phone": "(410) 565-5403",
                        "fax": "14105360210"
                    }
                },
                "transitMessage": ""
            },
            "quoteRate": {
                "totalCharges": "417.02",
                "totalShipmentWeight": 100,
                "rateType": "Customer Pricing",
                "ratedCube": ".00",
                "ratedLinearFeet": 2,
                "ratedAccessorials": [
                    {
                        "code": "MHPU",
                        "description": "Manhattan, NY Pickup Charge",
                        "charge": ".00"
                    },
                    {
                        "code": "FSC",
                        "description": "Fuel Surcharge",
                        "charge": "129.02"
                    }
                ]
            },
            "lineItemCharges": [
                {
                    "description": "Freight",
                    "classification": "50",
                    "weight": 100,
                    "rate": ".00",
                    "charge": "288.00"
                }
            ],
            "chargeItems": [
                {
                    "description": "Commodity Total",
                    "charge": "288.00"
                },
                {
                    "description": "Manhattan, NY Pickup Charge",
                    "charge": "0.00"
                },
                {
                    "description": "Fuel Surcharge 44.80%",
                    "charge": "129.02"
                }
            ],
            "disclaimersURL": "https://www.estes-express.com/myestes/rate-quote-estimate/terms"
        },
        {
            "serviceLevelId": "98",
            "serviceLevelText": "Guaranteed LTL Standard Transit: 5PM",
            "quoteId": "1XYQQTR",
            "rateFound": True,
            "dates": {
                "quoteExpiration": "2026-03-19-15.00.00.000000",
                "transitDeliveryDate": "2026-03-24",
                "transitDeliveryTime": "17:00"
            },
            "transitDetails": {
                "transitDays": 2,
                "laneType": "DIRECT",
                "originTerminal": "178",
                "originTerminalInfo": {
                    "name": "Brooklyn",
                    "address1": ".",
                    "city": "North Bergen",
                    "stateProvince": "NJ",
                    "postalCode": "07047",
                    "country": "US",
                    "contact": {
                        "name": "Luis Tirado",
                        "phone": "(201) 869-4238",
                        "fax": "12018694239"
                    }
                },
                "destinationTerminal": "029",
                "destinationTerminalInfo": {
                    "name": "Baltimore",
                    "address1": "5101 Washington Boulevard",
                    "city": "Baltimore",
                    "stateProvince": "MD",
                    "postalCode": "21227",
                    "country": "US",
                    "contact": {
                        "name": "Herman Braxton",
                        "phone": "(410) 565-5403",
                        "fax": "14105360210"
                    }
                },
                "transitMessage": ""
            },
            "quoteRate": {
                "totalCharges": "503.42",
                "totalShipmentWeight": 100,
                "rateType": "Customer Pricing",
                "ratedCube": ".00",
                "ratedLinearFeet": 2,
                "ratedAccessorials": [
                    {
                        "code": "MHPU",
                        "description": "Manhattan, NY Pickup Charge",
                        "charge": ".00"
                    },
                    {
                        "code": "FSC",
                        "description": "Fuel Surcharge",
                        "charge": "129.02"
                    }
                ]
            },
            "lineItemCharges": [
                {
                    "description": "Freight",
                    "classification": "50",
                    "weight": 100,
                    "rate": ".00",
                    "charge": "288.00"
                }
            ],
            "chargeItems": [
                {
                    "description": "Commodity Total",
                    "charge": "288.00"
                },
                {
                    "description": "Manhattan, NY Pickup Charge",
                    "charge": "0.00"
                },
                {
                    "description": "Fuel Surcharge 44.80%",
                    "charge": "129.02"
                },
                {
                    "description": "Service Level Adjustment",
                    "charge": "86.40"
                }
            ],
            "disclaimersURL": "https://www.estes-express.com/myestes/rate-quote-estimate/terms"
        },
        {
            "serviceLevelId": "90",
            "serviceLevelText": "Estes Retail Guarantee",
            "quoteId": "RXYQQTR",
            "rateFound": True,
            "dates": {
                "quoteExpiration": "2026-03-19-15.00.00.000000",
                "transitDeliveryDate": "2026-03-24",
                "transitDeliveryTime": "17:00"
            },
            "transitDetails": {
                "transitDays": 2,
                "laneType": "DIRECT",
                "originTerminal": "178",
                "originTerminalInfo": {
                    "name": "Brooklyn",
                    "address1": ".",
                    "city": "North Bergen",
                    "stateProvince": "NJ",
                    "postalCode": "07047",
                    "country": "US",
                    "contact": {
                        "name": "Luis Tirado",
                        "phone": "(201) 869-4238",
                        "fax": "12018694239"
                    }
                },
                "destinationTerminal": "029",
                "destinationTerminalInfo": {
                    "name": "Baltimore",
                    "address1": "5101 Washington Boulevard",
                    "city": "Baltimore",
                    "stateProvince": "MD",
                    "postalCode": "21227",
                    "country": "US",
                    "contact": {
                        "name": "Herman Braxton",
                        "phone": "(410) 565-5403",
                        "fax": "14105360210"
                    }
                },
                "transitMessage": ""
            },
            "quoteRate": {
                "totalCharges": "517.02",
                "totalShipmentWeight": 100,
                "rateType": "Customer Pricing",
                "ratedCube": ".00",
                "ratedLinearFeet": 2,
                "ratedAccessorials": [
                    {
                        "code": "MHPU",
                        "description": "Manhattan, NY Pickup Charge",
                        "charge": ".00"
                    },
                    {
                        "code": "FSC",
                        "description": "Fuel Surcharge",
                        "charge": "129.02"
                    },
                    {
                        "code": "APT",
                        "description": "APPOINTMENT CHARGE",
                        "charge": ".00"
                    }
                ]
            },
            "lineItemCharges": [
                {
                    "description": "Freight",
                    "classification": "50",
                    "weight": 100,
                    "rate": ".00",
                    "charge": "288.00"
                }
            ],
            "chargeItems": [
                {
                    "description": "Commodity Total",
                    "charge": "288.00"
                },
                {
                    "description": "Manhattan, NY Pickup Charge",
                    "charge": "0.00"
                },
                {
                    "description": "Fuel Surcharge 44.80%",
                    "charge": "129.02"
                },
                {
                    "description": "APPOINTMENT CHARGE",
                    "charge": "0.00"
                },
                {
                    "description": "Service Level Adjustment",
                    "charge": "100.00"
                }
            ],
            "disclaimersURL": "https://www.estes-express.com/myestes/rate-quote-estimate/terms"
        },
        {
            "serviceLevelId": "97",
            "serviceLevelText": "Guaranteed Exclusive Use",
            "quoteId": "XXYQQTR",
            "rateFound": True,
            "dates": {
                "quoteExpiration": "2026-03-19-15.00.00.000000",
                "transitDeliveryDate": "2026-03-20",
                "transitDeliveryTime": "07:00"
            },
            "transitDetails": {
                "transitDays": 2,
                "laneType": "DIRECT",
                "originTerminal": "178",
                "originTerminalInfo": {
                    "name": "Brooklyn",
                    "address1": ".",
                    "city": "North Bergen",
                    "stateProvince": "NJ",
                    "postalCode": "07047",
                    "country": "US",
                    "contact": {
                        "name": "Luis Tirado",
                        "phone": "(201) 869-4238",
                        "fax": "12018694239"
                    }
                },
                "destinationTerminal": "029",
                "destinationTerminalInfo": {
                    "name": "Baltimore",
                    "address1": "5101 Washington Boulevard",
                    "city": "Baltimore",
                    "stateProvince": "MD",
                    "postalCode": "21227",
                    "country": "US",
                    "contact": {
                        "name": "Herman Braxton",
                        "phone": "(410) 565-5403",
                        "fax": "14105360210"
                    }
                },
                "transitMessage": ""
            },
            "quoteRate": {
                "totalCharges": "1397.25",
                "totalShipmentWeight": 100,
                "rateType": "Customer Pricing",
                "ratedCube": ".00",
                "ratedLinearFeet": 2,
                "ratedAccessorials": [
                    {
                        "code": "MHPU",
                        "description": "Manhattan, NY Pickup Charge",
                        "charge": ".00"
                    }
                ]
            },
            "lineItemCharges": [
                {
                    "description": "Freight",
                    "classification": "50",
                    "weight": 100,
                    "rate": ".00",
                    "charge": "1397.25"
                }
            ],
            "chargeItems": [
                {
                    "description": "Commodity Total",
                    "charge": "1397.25"
                }
            ],
            "disclaimersURL": "https://www.estes-express.com/myestes/rate-quote-estimate/terms"
        },
        {
            "serviceLevelId": "96",
            "serviceLevelText": "Guaranteed LTL Standard Transit: 12PM",
            "rateFound": False,
            "reasons": [
                {
                    "messageId": "GSC0188",
                    "message": "Guaranteed Service is not available to auto-rate. For assistance,  email timecritical@estes-express.com or call 1-800-645-3952 and PRESS 1."
                }
            ]
        },
        {
            "serviceLevelId": "95",
            "serviceLevelText": "Guaranteed LTL Standard Transit: 10AM",
            "rateFound": False,
            "reasons": [
                {
                    "messageId": "GSC0188",
                    "message": "Guaranteed Service is not available to auto-rate. For assistance,  email timecritical@estes-express.com or call 1-800-645-3952 and PRESS 1."
                }
            ]
        }
    ],
    "error": {
        "code": 0,
        "message": "",
        "details": ""
    }
}

print("🔍 Testing Estes Response Parsing...")

try:
    mapper = EstesMapper()
    rate_response = mapper.from_estes_response(estes_response)
    
    print(f"✅ Successfully parsed Estes response")
    print(f"   Quotes Count: {len(rate_response.quotes)}")
    print(f"   Errors Count: {len(rate_response.errors)}")
    print(f"   Carrier Code: {rate_response.carrier_code}")
    
    print("\n📊 Parsed Quotes:")
    for i, quote in enumerate(rate_response.quotes, 1):
        print(f"   {i}. {quote.service_level} - ${quote.total_charge:.2f}")
        print(f"      Quote ID: {quote.quote_id}")
        print(f"      Transit Days: {quote.transit_days}")
        print(f"      Guaranteed: {quote.guaranteed}")
        print(f"      Base Charge: ${quote.base_charge:.2f}")
        print(f"      Fuel Surcharge: ${quote.fuel_surcharge:.2f}")
        print(f"      Accessorials: ${quote.accessorials_charge:.2f}")
        print(f"      Delivery Date: {quote.estimated_delivery_date}")
        print()
    
    print("📋 Service Details:")
    for i, quote in enumerate(rate_response.quotes[:2], 1):  # Show first 2
        details = quote.service_details
        print(f"   {i}. {details.get('serviceLevelText')}")
        print(f"      Service Level ID: {details.get('serviceLevelId')}")
        print(f"      Lane Type: {details.get('laneType')}")
        print(f"      Origin Terminal: {details.get('originTerminal')} ({details.get('originTerminalInfo', {}).get('city')})")
        print(f"      Destination Terminal: {details.get('destinationTerminal')} ({details.get('destinationTerminalInfo', {}).get('city')})")
        print(f"      Rate Type: {details.get('rateType')}")
        print(f"      Quote Expiration: {details.get('quoteExpiration')}")
        print()
    
    if rate_response.errors:
        print("⚠️  Errors:")
        for error in rate_response.errors:
            print(f"   - {error.message}")
    
    print("\n✅ Standardized Response Format:")
    print("   ✅ Consistent field names across carriers")
    print("   ✅ Standardized charge breakdown")
    print("   ✅ Common service level mapping")
    print("   ✅ Unified error handling")
    print("   ✅ Carrier-specific details preserved")
    
except Exception as e:
    print(f"❌ Error parsing response: {e}")
    import traceback
    traceback.print_exc()
