import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
import json

from main import app
from app.domain.integrations import RateRequest, RateResponse, RateQuote, Address, ShipmentItem, ServiceLevel


class TestRatesIntegration:
    """Integration tests for the rates endpoint."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        return TestClient(app)
    
    @pytest.fixture
    def sample_rate_request_data(self):
        """Sample rate request data for API."""
        return {
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
                    "description": "Test Item",
                    "quantity": 1
                }
            ],
            "accessorials": ["LIFT_GATE"],
            "references": ["REF123"],
            "carrier_id": "estes"
        }
    
    @pytest.fixture
    def mock_rate_response(self):
        """Mock rate response from use case."""
        quote = RateQuote(
            carrier_name="Estes Express",
            carrier_code="ESTES",
            service_level=ServiceLevel.STANDARD,
            total_charge=150.0,
            base_charge=135.0,
            fuel_surcharge=15.0,
            accessorials_charge=0.0,
            transit_days=3
        )
        
        return RateResponse(
            quotes=[quote],
            errors=[],
            request_id="test-request-id"
        )
    
    def test_rates_endpoint_success(self, client, sample_rate_request_data, mock_rate_response):
        """Test successful rate request through the API."""
        # Mock the use case
        with patch('app.interfaces.api.routes.rates.get_rates_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_rate_response
            mock_get_use_case.return_value = mock_use_case
            
            response = client.post("/rates/get", json=sample_rate_request_data)
            
            # Debug: print response content
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.content}")
            
            # Verify response
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            assert data["error"] is None
            assert "data" in data
            
            # Verify rate response data
            rate_data = data["data"]
            assert rate_data["success"] is True
            assert rate_data["has_quotes"] is True
            assert rate_data["has_errors"] is False
            assert len(rate_data["quotes"]) == 1
            assert rate_data["request_id"] == "test-request-id"
            
            # Verify quote data
            quote = rate_data["quotes"][0]
            assert quote["carrier_name"] == "Estes Express"
            assert quote["carrier_code"] == "ESTES"
            assert quote["service_level"] == "STANDARD"
            assert quote["total_charge"] == 150.0
            assert quote["transit_days"] == 3
    
    def test_rates_endpoint_validation_error(self, client):
        """Test rate request with validation errors."""
        invalid_request = {
            "origin": {"zip_code": ""},  # Invalid ZIP
            "destination": {"zip_code": "20001"},
            "items": []  # No items
        }
        
        response = client.post("/rates/get", json=invalid_request)
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_rates_endpoint_use_case_validation_error(self, client, sample_rate_request_data):
        """Test rate request with use case validation errors."""
        with patch('app.interfaces.api.routes.rates.get_rates_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = ValueError("Origin ZIP code is required")
            mock_get_use_case.return_value = mock_use_case
            
            response = client.post("/rates/get", json=sample_rate_request_data)
            
            assert response.status_code == 400
            data = response.json()
            assert "Origin ZIP code is required" in data["detail"]
    
    def test_rates_endpoint_unexpected_error(self, client, sample_rate_request_data):
        """Test rate request with unexpected error."""
        with patch('app.interfaces.api.routes.rates.get_rates_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_use_case.execute.side_effect = Exception("Unexpected error")
            mock_get_use_case.return_value = mock_use_case
            
            response = client.post("/rates/get", json=sample_rate_request_data)
            
            assert response.status_code == 500
            data = response.json()
            assert "unexpected error" in data["detail"].lower()
    
    def test_rates_endpoint_with_errors(self, client, sample_rate_request_data):
        """Test rate request that returns errors."""
        from app.domain.integrations import RateError, RateErrorType
        
        error_response = RateResponse(
            quotes=[],
            errors=[RateError(
                error_type=RateErrorType.RATE_UNAVAILABLE,
                message="No rates available for this route",
                carrier_code="ESTES"
            )],
            request_id="test-request-id"
        )
        
        with patch('app.interfaces.api.routes.rates.get_rates_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = error_response
            mock_get_use_case.return_value = mock_use_case
            
            response = client.post("/rates/get", json=sample_rate_request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            assert data["success"] is True
            rate_data = data["data"]
            assert rate_data["success"] is False  # No quotes means not successful
            assert rate_data["has_quotes"] is False
            assert rate_data["has_errors"] is True
            assert len(rate_data["errors"]) == 1
            assert "No rates available" in rate_data["errors"][0]["message"]
    
    def test_rates_endpoint_multiple_quotes(self, client, sample_rate_request_data):
        """Test rate request with multiple quotes."""
        quote1 = RateQuote(
            carrier_name="Estes Express",
            carrier_code="ESTES",
            service_level=ServiceLevel.STANDARD,
            total_charge=150.0,
            base_charge=135.0,
            fuel_surcharge=15.0,
            accessorials_charge=0.0
        )
        
        quote2 = RateQuote(
            carrier_name="Estes Express",
            carrier_code="ESTES",
            service_level=ServiceLevel.EXPEDITED,
            total_charge=200.0,
            base_charge=180.0,
            fuel_surcharge=20.0,
            accessorials_charge=0.0,
            guaranteed=True
        )
        
        response_data = RateResponse(
            quotes=[quote1, quote2],
            errors=[],
            request_id="test-request-id"
        )
        
        with patch('app.interfaces.api.routes.rates.get_rates_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = response_data
            mock_get_use_case.return_value = mock_use_case
            
            response = client.post("/rates/get", json=sample_rate_request_data)
            
            assert response.status_code == 200
            data = response.json()
            
            rate_data = data["data"]
            assert len(rate_data["quotes"]) == 2
            
            # Verify both service levels are present
            service_levels = [quote["service_level"] for quote in rate_data["quotes"]]
            assert "STANDARD" in service_levels
            assert "EXPEDITED" in service_levels
    
    def test_rates_endpoint_minimal_request(self, client):
        """Test rate request with minimal data."""
        minimal_request = {
            "origin": {"zip_code": "10001"},
            "destination": {"zip_code": "20001"},
            "items": [{"weight": 100.0}]
        }
        
        mock_response = RateResponse(
            quotes=[],
            errors=[],
            request_id="test-request-id"
        )
        
        with patch('app.interfaces.api.routes.rates.get_rates_use_case') as mock_get_use_case:
            mock_use_case = AsyncMock()
            mock_use_case.execute.return_value = mock_response
            mock_get_use_case.return_value = mock_use_case
            
            response = client.post("/rates/get", json=minimal_request)
            
            assert response.status_code == 200
    
    def test_rates_endpoint_invalid_json(self, client):
        """Test rate request with invalid JSON."""
        response = client.post(
            "/rates/get",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422
    
    def test_rates_endpoint_missing_required_fields(self, client):
        """Test rate request missing required fields."""
        incomplete_request = {
            "origin": {"zip_code": "10001"}
            # Missing destination and items
        }
        
        response = client.post("/rates/get", json=incomplete_request)
        
        assert response.status_code == 422
    
    def test_rates_endpoint_invalid_item_data(self, client):
        """Test rate request with invalid item data."""
        invalid_request = {
            "origin": {"zip_code": "10001"},
            "destination": {"zip_code": "20001"},
            "items": [
                {
                    "weight": -10.0,  # Invalid weight
                    "quantity": 0      # Invalid quantity
                }
            ]
        }
        
        response = client.post("/rates/get", json=invalid_request)
        
        assert response.status_code == 422
