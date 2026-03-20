import pytest
from unittest.mock import Mock, AsyncMock
from uuid import uuid4

from app.application.integrations import GetRatesUseCase, CarrierResolverService
from app.domain.integrations import RateRequest, RateResponse, RateQuote, CarrierRateProvider, Address, ShipmentItem, ServiceLevel


class TestGetRatesUseCase:
    """Test cases for GetRatesUseCase."""
    
    @pytest.fixture
    def mock_carrier_resolver(self):
        """Mock carrier resolver service."""
        resolver = Mock(spec=CarrierResolverService)
        resolver.resolve_providers = AsyncMock()
        return resolver
    
    @pytest.fixture
    def get_rates_use_case(self, mock_carrier_resolver):
        """Create GetRatesUseCase instance with mocked dependencies."""
        return GetRatesUseCase(mock_carrier_resolver)
    
    @pytest.fixture
    def sample_rate_request(self):
        """Create a sample rate request."""
        origin = Address(zip_code="10001", city="New York", state="NY")
        destination = Address(zip_code="20001", city="Washington", state="DC")
        item = ShipmentItem(weight=100.0, freight_class=None, quantity=1)
        
        return RateRequest(
            origin=origin,
            destination=destination,
            items=[item]
        )
    
    @pytest.fixture
    def mock_provider(self):
        """Create a mock carrier provider."""
        provider = Mock(spec=CarrierRateProvider)
        provider.carrier_name = "Test Carrier"
        provider.carrier_code = "TEST"
        provider.get_rates = AsyncMock()
        return provider
    
    @pytest.mark.asyncio
    async def test_execute_success_single_provider(self, get_rates_use_case, mock_carrier_resolver, sample_rate_request, mock_provider):
        """Test successful execution with a single provider."""
        # Setup
        mock_carrier_resolver.resolve_providers.return_value = [mock_provider]
        
        quote = RateQuote(
            carrier_name="Test Carrier",
            carrier_code="TEST",
            service_level=ServiceLevel.STANDARD,
            total_charge=100.0,
            base_charge=90.0,
            fuel_surcharge=10.0,
            accessorials_charge=0.0
        )
        
        mock_provider.get_rates.return_value = RateResponse(quotes=[quote], errors=[])
        
        # Execute
        result = await get_rates_use_case.execute(sample_rate_request)
        
        # Assert
        assert result.success is True
        assert len(result.quotes) == 1
        assert result.quotes[0].carrier_name == "Test Carrier"
        assert result.quotes[0].total_charge == 100.0
        assert len(result.errors) == 0
        assert result.request_id is not None
        
        # Verify interactions
        mock_carrier_resolver.resolve_providers.assert_called_once_with(None)
        mock_provider.get_rates.assert_called_once_with(sample_rate_request)
    
    @pytest.mark.asyncio
    async def test_execute_success_multiple_providers(self, get_rates_use_case, mock_carrier_resolver, sample_rate_request):
        """Test successful execution with multiple providers."""
        # Setup
        provider1 = Mock(spec=CarrierRateProvider)
        provider1.carrier_name = "Carrier 1"
        provider1.carrier_code = "C1"
        provider1.get_rates = AsyncMock()
        
        provider2 = Mock(spec=CarrierRateProvider)
        provider2.carrier_name = "Carrier 2"
        provider2.carrier_code = "C2"
        provider2.get_rates = AsyncMock()
        
        mock_carrier_resolver.resolve_providers.return_value = [provider1, provider2]
        
        quote1 = RateQuote(
            carrier_name="Carrier 1",
            carrier_code="C1",
            service_level=ServiceLevel.STANDARD,
            total_charge=100.0,
            base_charge=90.0,
            fuel_surcharge=10.0,
            accessorials_charge=0.0
        )
        
        quote2 = RateQuote(
            carrier_name="Carrier 2",
            carrier_code="C2",
            service_level=ServiceLevel.EXPEDITED,
            total_charge=150.0,
            base_charge=135.0,
            fuel_surcharge=15.0,
            accessorials_charge=0.0
        )
        
        provider1.get_rates.return_value = RateResponse(quotes=[quote1], errors=[])
        provider2.get_rates.return_value = RateResponse(quotes=[quote2], errors=[])
        
        # Execute
        result = await get_rates_use_case.execute(sample_rate_request)
        
        # Assert
        assert result.success is True
        assert len(result.quotes) == 2
        assert len(result.errors) == 0
        
        # Verify quotes from both providers are included
        carrier_codes = [quote.carrier_code for quote in result.quotes]
        assert "C1" in carrier_codes
        assert "C2" in carrier_codes
    
    @pytest.mark.asyncio
    async def test_execute_no_providers(self, get_rates_use_case, mock_carrier_resolver, sample_rate_request):
        """Test execution when no providers are found."""
        # Setup
        mock_carrier_resolver.resolve_providers.return_value = []
        
        # Execute
        result = await get_rates_use_case.execute(sample_rate_request)
        
        # Assert
        assert result.success is False  # No quotes means not successful
        assert len(result.quotes) == 0
        assert len(result.errors) == 0
        assert result.request_id is not None
    
    @pytest.mark.asyncio
    async def test_execute_provider_error(self, get_rates_use_case, mock_carrier_resolver, sample_rate_request, mock_provider):
        """Test execution when provider raises an error."""
        # Setup
        mock_carrier_resolver.resolve_providers.return_value = [mock_provider]
        mock_provider.get_rates.side_effect = Exception("Provider error")
        
        # Execute
        result = await get_rates_use_case.execute(sample_rate_request)
        
        # Assert
        assert result.success is False
        assert len(result.quotes) == 0
        assert len(result.errors) == 1
        assert "Failed to get rates from Test Carrier" in result.errors[0].message
    
    @pytest.mark.asyncio
    async def test_execute_with_specific_carrier(self, get_rates_use_case, mock_carrier_resolver, sample_rate_request, mock_provider):
        """Test execution with specific carrier ID."""
        # Setup
        sample_rate_request.carrier_id = "TEST"
        mock_carrier_resolver.resolve_providers.return_value = [mock_provider]
        
        quote = RateQuote(
            carrier_name="Test Carrier",
            carrier_code="TEST",
            service_level=ServiceLevel.STANDARD,
            total_charge=100.0,
            base_charge=90.0,
            fuel_surcharge=10.0,
            accessorials_charge=0.0
        )
        
        mock_provider.get_rates.return_value = RateResponse(quotes=[quote], errors=[])
        
        # Execute
        result = await get_rates_use_case.execute(sample_rate_request)
        
        # Assert
        assert result.success is True
        assert len(result.quotes) == 1
        
        # Verify correct carrier ID was passed
        mock_carrier_resolver.resolve_providers.assert_called_once_with("TEST")
    
    def test_validate_request_success(self, get_rates_use_case, sample_rate_request):
        """Test successful request validation."""
        # Should not raise any exception
        get_rates_use_case._validate_request(sample_rate_request)
    
    def test_validate_request_missing_origin_zip(self, get_rates_use_case, sample_rate_request):
        """Test validation failure with missing origin ZIP."""
        sample_rate_request.origin.zip_code = ""
        
        with pytest.raises(ValueError, match="Origin ZIP code is required"):
            get_rates_use_case._validate_request(sample_rate_request)
    
    def test_validate_request_missing_destination_zip(self, get_rates_use_case, sample_rate_request):
        """Test validation failure with missing destination ZIP."""
        sample_rate_request.destination.zip_code = ""
        
        with pytest.raises(ValueError, match="Destination ZIP code is required"):
            get_rates_use_case._validate_request(sample_rate_request)
    
    def test_validate_request_no_items(self, get_rates_use_case, sample_rate_request):
        """Test validation failure with no items."""
        sample_rate_request.items = []
        
        with pytest.raises(ValueError, match="At least one shipment item is required"):
            get_rates_use_case._validate_request(sample_rate_request)
    
    def test_validate_request_invalid_weight(self, get_rates_use_case, sample_rate_request):
        """Test validation failure with invalid weight."""
        sample_rate_request.items[0].weight = 0
        
        with pytest.raises(ValueError, match="Item weight must be greater than 0"):
            get_rates_use_case._validate_request(sample_rate_request)
