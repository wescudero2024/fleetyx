# ✅ Standardized Carrier Response Format

## 🎯 **Objective**

Create a standardized response format for all carrier integrations to ensure consistency across the system while preserving carrier-specific details.

## 📋 **Standardized Response Structure**

### ✅ **Success Response**
```json
{
  "success": true,
  "data": {
    "quotes": [
      {
        "carrier_name": "ESTES EXPRESS LINES",
        "carrier_code": "ESTES", 
        "service_level": "STANDARD",
        "total_charge": 417.02,
        "base_charge": 288.00,
        "fuel_surcharge": 0.00,
        "accessorials_charge": 129.02,
        "transit_days": 2,
        "estimated_delivery_date": "2026-03-24T17:00:00Z",
        "guaranteed": false,
        "quote_id": "LXYQQTR",
        "additional_charges": {
          "Commodity Total": 288.00,
          "Manhattan, NY Pickup Charge": 0.00,
          "Fuel Surcharge 44.80%": 129.02
        },
        "service_details": {
          "quoteId": "LXYQQTR",
          "serviceLevelText": "LTL Standard Transit",
          "serviceLevelId": "99",
          "laneType": "DIRECT",
          "originTerminal": "178",
          "destinationTerminal": "029",
          "rateType": "Customer Pricing",
          "ratedCube": ".00",
          "ratedLinearFeet": 2,
          "chargeItems": [...],
          "lineItemCharges": [...],
          "ratedAccessorials": [...],
          "transitMessage": "",
          "disclaimersURL": "https://www.estes-express.com/myestes/rate-quote-estimate/terms",
          "quoteExpiration": "2026-03-20-00.00.00.000000",
          "transitDeliveryDate": "2026-03-24",
          "transitDeliveryTime": "17:00",
          "originTerminalInfo": {...},
          "destinationTerminalInfo": {...}
        }
      }
    ],
    "errors": [],
    "request_id": "5ab2394e-600a-4188-bed2-1875db78db47",
    "timestamp": "2026-03-20T02:26:49.040327",
    "carrier_code": "ESTES",
    "success": true,
    "has_quotes": true,
    "has_errors": false
  },
  "error": null
}
```

### ❌ **Error Response**
```json
{
  "success": false,
  "data": {
    "quotes": [],
    "errors": [
      {
        "error_type": "VALIDATION_ERROR",
        "message": "Guaranteed Service is not available to auto-rate. For assistance, email timecritical@estes-express.com or call 1-800-645-3952 and PRESS 1.",
        "carrier_code": "ESTES",
        "details": {
          "service_level": "Guaranteed LTL Standard Transit: 12PM",
          "reason_id": "GSC0188"
        },
        "timestamp": "2026-03-20T02:26:49.040240"
      }
    ],
    "request_id": "5ab2394e-600a-4188-bed2-1875db78db47",
    "timestamp": "2026-03-20T02:26:49.040327",
    "carrier_code": "ESTES",
    "success": false,
    "has_quotes": false,
    "has_errors": true
  },
  "error": null
}
```

## 🔧 **Standardized Fields**

### ✅ **Required Quote Fields**
| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `carrier_name` | string | Full carrier name | "ESTES EXPRESS LINES" |
| `carrier_code` | string | Standard carrier code | "ESTES" |
| `service_level` | enum | Standardized service level | "STANDARD", "GUARANTEED" |
| `total_charge` | float | Total cost to customer | 417.02 |
| `base_charge` | float | Base freight charge | 288.00 |
| `fuel_surcharge` | float | Fuel surcharge amount | 0.00 |
| `accessorials_charge` | float | Total accessorials charge | 129.02 |
| `transit_days` | integer | Transit time in days | 2 |
| `estimated_delivery_date` | datetime | Delivery date/time | "2026-03-24T17:00:00Z" |
| `guaranteed` | boolean | Service guarantee status | false |
| `quote_id` | string | Carrier quote identifier | "LXYQQTR" |

### ✅ **Optional Quote Fields**
| Field | Type | Description |
|-------|------|-------------|
| `additional_charges` | object | Detailed charge breakdown |
| `service_details` | object | Carrier-specific details |

### ✅ **Standard Error Fields**
| Field | Type | Description |
|-------|------|-------------|
| `error_type` | enum | Error classification |
| `message` | string | User-friendly error message |
| `carrier_code` | string | Carrier identifier |
| `details` | object | Additional error context |
| `timestamp` | datetime | Error occurrence time |

## 🚀 **Service Level Mapping**

### ✅ **Standardized Service Levels**
```python
class ServiceLevel(Enum):
    STANDARD = "STANDARD"
    EXPEDITED = "EXPEDITED"
    GUARANTEED = "GUARANTEED"
    ECONOMY = "ECONOMY"
    OVERNIGHT = "OVERNIGHT"
    TIME_CRITICAL = "TIME_CRITICAL"
```

### ✅ **Carrier-Specific Mapping**
```python
# Estes Mapping
ESTES_SERVICE_MAPPING = {
    "LTL Standard Transit": ServiceLevel.STANDARD,
    "Guaranteed LTL Standard Transit: 5PM": ServiceLevel.GUARANTEED,
    "Estes Retail Guarantee": ServiceLevel.GUARANTEED,
    "Guaranteed Exclusive Use": ServiceLevel.GUARANTEED,
}

# Future Carrier Mapping
FUTURE_CARRIER_MAPPING = {
    "Standard": ServiceLevel.STANDARD,
    "Expedited": ServiceLevel.EXPEDITED,
    "Guaranteed": ServiceLevel.GUARANTEED,
}
```

## 📊 **Charge Breakdown Standardization**

### ✅ **Required Charge Categories**
| Category | Description | Source |
|----------|-------------|--------|
| `base_charge` | Core freight charge | Calculated from total - other charges |
| `fuel_surcharge` | Fuel-related charges | Identified by "fuel" in description |
| `accessorials_charge` | Additional services | All other non-fuel charges |

### ✅ **Charge Detection Logic**
```python
# Fuel surcharge detection
if "fuel" in description.lower():
    fuel_surcharge += charge_amount

# Accessorial detection  
elif any(term in description.lower() for term in ["accessorial", "charge", "pickup", "delivery"]):
    accessorials_charge += charge_amount

# Base charge calculation
base_charge = total_charge - fuel_surcharge - accessorials_charge
```

## 🎯 **Carrier Integration Template**

### ✅ **Response Parser Template**
```python
def from_carrier_response(self, carrier_response: Dict[str, Any]) -> RateResponse:
    """
    Convert carrier response to standardized format.
    
    Args:
        carrier_response: Raw carrier API response
        
    Returns:
        Standardized RateResponse
    """
    quotes = []
    errors = []
    
    # Parse quotes data
    quotes_data = carrier_response.get("data", [])
    for carrier_quote in quotes_data:
        if self._is_valid_quote(carrier_quote):
            quote = self._convert_to_standard_quote(carrier_quote)
            quotes.append(quote)
        elif carrier_quote.get("reasons"):
            # Convert reasons to errors
            errors.extend(self._convert_reasons_to_errors(carrier_quote))
    
    # Check for API-level errors
    if "error" in carrier_response:
        errors.extend(self._convert_api_errors(carrier_response["error"]))
    
    return RateResponse(
        quotes=quotes,
        errors=errors,
        carrier_code=self.carrier_code,
        timestamp=datetime.utcnow()
    )
```

### ✅ **Quote Converter Template**
```python
def _convert_to_standard_quote(self, carrier_quote: Dict[str, Any]) -> RateQuote:
    """Convert carrier-specific quote to standard format."""
    
    # Extract standardized fields
    total_charge = float(carrier_quote["total_charges"])
    service_level = self._map_service_level(carrier_quote["service_type"])
    
    # Calculate charge breakdown
    charge_breakdown = self._calculate_charge_breakdown(carrier_quote)
    
    # Parse delivery information
    delivery_date = self._parse_delivery_date(carrier_quote["delivery_info"])
    
    return RateQuote(
        carrier_name=self.carrier_name,
        carrier_code=self.carrier_code,
        service_level=service_level,
        total_charge=total_charge,
        base_charge=charge_breakdown["base"],
        fuel_surcharge=charge_breakdown["fuel"],
        accessorials_charge=charge_breakdown["accessorials"],
        transit_days=carrier_quote.get("transit_days"),
        estimated_delivery_date=delivery_date,
        guaranteed=self._is_guaranteed_service(carrier_quote["service_type"]),
        quote_id=carrier_quote.get("quote_id"),
        additional_charges=charge_breakdown["details"],
        service_details=self._preserve_carrier_details(carrier_quote)
    )
```

## 🧪 **Testing Requirements**

### ✅ **Response Validation Tests**
1. **Schema Compliance**: All required fields present
2. **Data Types**: Correct field types (float for charges, int for days)
3. **Service Level Mapping**: Proper service level conversion
4. **Charge Breakdown**: Accurate charge categorization
5. **Error Handling**: Proper error message extraction

### ✅ **Integration Tests**
1. **End-to-End Flow**: Request → Carrier → Standardized Response
2. **Error Scenarios**: Invalid data, network errors, API errors
3. **Multiple Quotes**: Proper handling of multiple service levels
4. **Edge Cases**: Missing fields, zero charges, invalid dates

## 🎉 **Benefits of Standardization**

✅ **Consistent UX**: Same response format across all carriers  
✅ **Easy Integration**: Frontend can use single data structure  
✅ **Carrier Agnostic**: Business logic doesn't need carrier-specific code  
✅ **Extensible**: Easy to add new carriers  
✅ **Maintainable**: Centralized response handling  
✅ **Testable**: Standardized test patterns  
✅ **Analytics**: Consistent data for reporting  

The standardized response format ensures **consistency across all carriers** while preserving **carrier-specific details** for advanced use cases! 🚀
