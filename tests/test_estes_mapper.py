import pytest
from datetime import datetime

from app.infrastructure.integrations.carriers.estes import EstesMapper
from app.domain.integrations import RateRequest, RateResponse, RateQuote, RateError, Address, ShipmentItem, FreightClass, Accessorial, ServiceLevel, RateErrorType


class TestEstesMapper:
    """Test cases for EstesMapper."""
    
    @pytest.fixture
    def mapper(self):
        """Create EstesMapper instance."""
        return EstesMapper()
    
    @pytest.fixture
    def sample_rate_request(self):
        """Create a sample rate request."""
        origin = Address(
            zip_code="10001",
            city="New York",
            state="NY",
            country="US",
            address_line1="123 Main St"
        )
        destination = Address(
            zip_code="20001",
            city="Washington",
            state="DC",
            country="US",
            address_line1="456 Oak Ave"
        )
        item = ShipmentItem(
            weight=100.0,
            length=48.0,
            width=40.0,
            height=36.0,
            freight_class=FreightClass.CLASS_50,
            description="Test Item",
            nmfc_code="123456",
            quantity=2,
            stackable=False,
            hazardous_material=False
        )
        
        return RateRequest(
            origin=origin,
            destination=destination,
            items=[item],
            accessorials=[Accessorial.LIFT_GATE, Accessorial.RESIDENTIAL],
            references=["REF123", "REF456"],
            carrier_id="estes",
            service_type="STANDARD",
            shipment_date="2024-01-15",
            declared_value=1000.0,
            insurance_required=True
        )
    
    def test_to_estes_payload_basic(self, mapper, sample_rate_request):
        """Test basic conversion to Estes payload."""
        payload = mapper.to_estes_payload(sample_rate_request)
        
        # Check structure
        assert "account" in payload
        assert "origin" in payload
        assert "destination" in payload
        assert "items" in payload
        
        # Check origin
        assert payload["origin"]["zip"] == "10001"
        assert payload["origin"]["city"] == "New York"
        assert payload["origin"]["state"] == "NY"
        assert payload["origin"]["country"] == "US"
        assert payload["origin"]["address1"] == "123 Main St"
        
        # Check destination
        assert payload["destination"]["zip"] == "20001"
        assert payload["destination"]["city"] == "Washington"
        assert payload["destination"]["state"] == "DC"
        assert payload["destination"]["address1"] == "456 Oak Ave"
        
        # Check items
        assert len(payload["items"]) == 1
        item = payload["items"][0]
        assert item["weight"] == 100.0
        assert item["quantity"] == 2
        assert item["class"] == "50"
        assert item["description"] == "Test Item"
        assert item["nmfc"] == "123456"
        assert item["dimensions"]["length"] == 48.0
        assert item["dimensions"]["width"] == 40.0
        assert item["dimensions"]["height"] == 36.0
    
    def test_to_estes_payload_accessorials(self, mapper, sample_rate_request):
        """Test accessorials conversion."""
        payload = mapper.to_estes_payload(sample_rate_request)
        
        assert "accessorials" in payload
        assert set(payload["accessorials"]) == {"LG", "RES"}
    
    def test_to_estes_payload_optional_fields(self, mapper, sample_rate_request):
        """Test optional fields conversion."""
        payload = mapper.to_estes_payload(sample_rate_request)
        
        assert payload["shipmentDate"] == "2024-01-15"
        assert payload["declaredValue"] == 1000.0
        assert set(payload["references"]) == {"REF123", "REF456"}
    
    def test_to_estes_payload_minimal(self, mapper):
        """Test conversion with minimal data."""
        origin = Address(zip_code="10001")
        destination = Address(zip_code="20001")
        item = ShipmentItem(weight=100.0)
        
        request = RateRequest(
            origin=origin,
            destination=destination,
            items=[item]
        )
        
        payload = mapper.to_estes_payload(request)
        
        # Check minimal structure
        assert payload["origin"]["zip"] == "10001"
        assert payload["destination"]["zip"] == "20001"
        assert len(payload["items"]) == 1
        assert payload["items"][0]["weight"] == 100.0
        
        # Check optional fields are not present
        assert "accessorials" not in payload
        assert "shipmentDate" not in payload
        assert "declaredValue" not in payload
    
    def test_from_estes_response_success(self, mapper):
        """Test conversion from successful Estes response."""
        estes_response = {
            "success": True,
            "data": {
                "rates": [
                    {
                        "serviceType": "STANDARD",
                        "totalCharge": 150.0,
                        "baseCharge": 135.0,
                        "fuelSurcharge": 15.0,
                        "accessorialsCharge": 0.0,
                        "transitDays": 3,
                        "guaranteed": False,
                        "quoteId": "QUOTE123",
                        "expiration": "2024-01-20T00:00:00Z",
                        "additionalCharges": [
                            {"code": "FUEL", "amount": 15.0}
                        ],
                        "serviceDetails": {
                            "service": "Standard LTL"
                        }
                    }
                ]
            }
        }
        
        result = mapper.from_estes_response(estes_response)
        
        assert isinstance(result, RateResponse)
        assert result.success is True
        assert len(result.quotes) == 1
        assert len(result.errors) == 0
        assert result.carrier_code == "ESTES"
        
        quote = result.quotes[0]
        assert quote.carrier_name == "Estes Express"
        assert quote.carrier_code == "ESTES"
        assert quote.service_level == ServiceLevel.STANDARD
        assert quote.total_charge == 150.0
        assert quote.base_charge == 135.0
        assert quote.fuel_surcharge == 15.0
        assert quote.transit_days == 3
        assert quote.guaranteed is False
        assert quote.quote_id == "QUOTE123"
        assert quote.additional_charges["FUEL"] == 15.0
        assert quote.service_details["service"] == "Standard LTL"
    
    def test_from_estes_response_with_errors(self, mapper):
        """Test conversion from Estes response with errors."""
        estes_response = {
            "success": False,
            "errors": [
                {
                    "message": "Invalid ZIP code",
                    "code": "INVALID_ZIP"
                }
            ]
        }
        
        result = mapper.from_estes_response(estes_response)
        
        assert isinstance(result, RateResponse)
        assert result.success is False
        assert len(result.quotes) == 0
        assert len(result.errors) == 1
        assert result.carrier_code == "ESTES"
        
        error = result.errors[0]
        assert error.error_type == RateErrorType.API_ERROR
        assert "Invalid ZIP code" in error.message
        assert error.carrier_code == "ESTES"
    
    def test_from_estes_response_mixed(self, mapper):
        """Test conversion from Estes response with both quotes and errors."""
        estes_response = {
            "success": True,
            "data": {
                "rates": [
                    {
                        "serviceType": "STANDARD",
                        "totalCharge": 100.0,
                        "baseCharge": 90.0,
                        "fuelSurcharge": 10.0,
                        "accessorialsCharge": 0.0
                    }
                ]
            },
            "errors": [
                {
                    "message": "Warning message",
                    "code": "WARNING"
                }
            ]
        }
        
        result = mapper.from_estes_response(estes_response)
        
        assert len(result.quotes) == 1
        assert len(result.errors) == 1
    
    def test_from_estes_response_empty(self, mapper):
        """Test conversion from empty Estes response."""
        estes_response = {"success": True, "data": {}}
        
        result = mapper.from_estes_response(estes_response)
        
        assert len(result.quotes) == 0
        assert len(result.errors) == 0
    
    def test_convert_rate_to_quote_expedited_service(self, mapper):
        """Test conversion of expedited service rate."""
        rate_data = {
            "serviceType": "EXPEDITED",
            "totalCharge": 200.0,
            "baseCharge": 180.0,
            "fuelSurcharge": 20.0,
            "accessorialsCharge": 0.0,
            "guaranteed": True,
            "transitDays": 1
        }
        
        quote = mapper._convert_rate_to_quote(rate_data)
        
        assert quote.service_level == ServiceLevel.EXPEDITED
        assert quote.guaranteed is True
        assert quote.transit_days == 1
    
    def test_parse_expiration_date_iso(self, mapper):
        """Test parsing ISO format expiration date."""
        date_str = "2024-01-20T00:00:00Z"
        result = mapper._parse_expiration_date(date_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 20
    
    def test_parse_expiration_date_standard(self, mapper):
        """Test parsing standard format expiration date."""
        date_str = "2024-01-20 15:30:00"
        result = mapper._parse_expiration_date(date_str)
        
        assert isinstance(result, datetime)
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 20
        assert result.hour == 15
        assert result.minute == 30
    
    def test_parse_expiration_date_invalid(self, mapper):
        """Test parsing invalid expiration date."""
        date_str = "invalid-date"
        result = mapper._parse_expiration_date(date_str)
        
        assert result is None
    
    def test_parse_expiration_date_none(self, mapper):
        """Test parsing None expiration date."""
        result = mapper._parse_expiration_date(None)
        
        assert result is None
    
    def test_mapping_error_handling(self, mapper):
        """Test handling of mapping errors."""
        # Test with invalid request data
        with pytest.raises(ValueError, match="Mapping error"):
            mapper.to_estes_payload(None)
        
        # Test with invalid response data
        result = mapper.from_estes_response(None)
        assert isinstance(result, RateResponse)
        assert len(result.errors) == 1
        assert result.errors[0].error_type == RateErrorType.MAPPING_ERROR
