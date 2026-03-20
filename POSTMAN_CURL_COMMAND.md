# 📮 Postman Curl Command for Estes API Testing

## 🚀 **Final Curl Command**

```bash
curl -X POST "http://localhost:8000/rates/get" \
-H "Content-Type: application/json" \
-d '{
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
      "description": "Test freight",
      "stackable": false,
      "hazardous_material": false
    }
  ],
  "carrier_id": "estes",
  "shipment_date": "2024-03-20",
  "accessorials": ["LIFT_GATE", "RESIDENTIAL"]
}'
```

## 📋 **Alternative Formats**

### **Minimal Request**
```bash
curl -X POST "http://localhost:8000/rates/get" \
-H "Content-Type: application/json" \
-d '{
  "origin": {"zip_code": "10001", "country": "US"},
  "destination": {"zip_code": "20001", "country": "US"},
  "items": [{"weight": 100.0, "length": 48.0, "width": 40.0, "height": 36.0, "freight_class": "50"}],
  "carrier_id": "estes"
}'
```

### **With Multiple Items**
```bash
curl -X POST "http://localhost:8000/rates/get" \
-H "Content-Type: application/json" \
-d '{
  "origin": {"zip_code": "10001", "city": "New York", "state": "NY", "country": "US"},
  "destination": {"zip_code": "20001", "city": "Washington", "state": "DC", "country": "US"},
  "items": [
    {
      "weight": 100.0,
      "length": 48.0,
      "width": 40.0,
      "height": 36.0,
      "freight_class": "50",
      "quantity": 2,
      "type": "Pallet",
      "description": "Electronics"
    },
    {
      "weight": 50.0,
      "length": 24.0,
      "width": 24.0,
      "height": 12.0,
      "freight_class": "55",
      "quantity": 1,
      "type": "Box",
      "description": "Documents"
    }
  ],
  "carrier_id": "estes",
  "accessorials": ["LIFT_GATE"]
}'
```

## 🔧 **Postman Setup Instructions**

### 1. **Create New Request**
- Method: `POST`
- URL: `http://localhost:8000/rates/get`

### 2. **Headers**
- `Content-Type`: `application/json`

### 3. **Body**
- Select `raw` and `JSON`
- Copy any of the JSON payloads above

### 4. **Expected Responses**

#### **Success Response (200)**
```json
{
  "success": true,
  "data": {
    "quotes": [
      {
        "carrier_name": "ESTES EXPRESS LINES",
        "carrier_code": "ESTES",
        "service_level": "STANDARD",
        "total_charge": 150.75,
        "base_charge": 120.60,
        "fuel_surcharge": 22.61,
        "accessorials_charge": 7.54,
        "transit_days": 2,
        "estimated_delivery_date": "2024-03-22T10:30:00Z",
        "guaranteed": false,
        "quote_id": "ESTES-123456",
        "additional_charges": {
          "Linehaul": 120.60,
          "Fuel Surcharge": 22.61,
          "Liftgate": 7.54
        }
      }
    ],
    "errors": []
  }
}
```

#### **Error Response (400/422)**
```json
{
  "success": false,
  "error": "Validation Error",
  "message": "Authentication failed with Estes Express. Please check API credentials. Details: Invalid API credentials",
  "details": {
    "error_type": "authentication",
    "carrier": "Estes Express",
    "original_error": "Invalid API credentials"
  }
}
```

#### **Network Error Response (500)**
```json
{
  "success": false,
  "error": "Carrier Error",
  "message": "Estes Express service is temporarily unavailable. Please try again later.",
  "details": {
    "error_type": "service_unavailable",
    "carrier": "Estes Express"
  }
}
```

## 🎯 **Testing Scenarios**

### **1. Successful Rate Request**
- Use valid origin/destination zip codes
- Include proper item dimensions and weight
- Should return quotes with multiple service levels

### **2. Authentication Error**
- Temporarily modify `ESTES_USERNAME` or `ESTES_PASSWORD` in `.env`
- Should return standardized authentication error

### **3. Validation Error**
- Send invalid zip codes or missing required fields
- Should return validation error with specific field issues

### **4. Network Error**
- Stop the FastAPI server and make request
- Should return network error with user-friendly message

## 🔍 **Error Message Examples**

The global error handler provides carrier-specific, user-friendly messages:

- **Authentication**: "Authentication failed with Estes Express. Please check API credentials. Details: Invalid API credentials"
- **Validation**: "Invalid request data for Estes Express. Details: Invalid postal code format"
- **Rate Limit**: "Rate limit exceeded for Estes Express. Please try again later. Details: Too many requests"
- **Service Unavailable**: "Estes Express service is temporarily unavailable. Please try again later."

## 🚀 **Ready for Testing**

The implementation is now ready for comprehensive testing with:
- ✅ Standardized error handling across all carriers
- ✅ User-friendly error messages
- ✅ Complete Postman testing setup
- ✅ Multiple testing scenarios
- ✅ Production-ready error responses
