# Carrier Integrations Module

This module provides a comprehensive, extensible system for integrating with multiple carrier APIs to fetch shipping rates. It follows Clean Architecture principles and is designed to easily support adding new carriers without modifying core business logic.

## Architecture Overview

The carrier integrations module is organized into four distinct layers:

### Domain Layer (`/app/domain/integrations`)
- **Purpose**: Core business entities and interfaces
- **Components**:
  - `CarrierRateProvider`: Abstract base class for all carrier implementations
  - `RateRequest`: Domain model for rate requests
  - `RateResponse`: Domain model for rate responses
  - Value objects: `Address`, `ShipmentItem`, `FreightClass`, `Accessorial`

### Application Layer (`/app/application/integrations`)
- **Purpose**: Business use cases and orchestration
- **Components**:
  - `GetRatesUseCase`: Orchestrates the rate fetching process
  - `CarrierResolverService`: Resolves which carriers to invoke

### Infrastructure Layer (`/app/infrastructure/integrations`)
- **Purpose**: External API implementations and configurations
- **Components**:
  - `IntegrationRegistry`: Central registry for carrier providers
  - Carrier-specific implementations (e.g., Estes Express)

### Interfaces Layer (`/app/interfaces/api/routes/rates`)
- **Purpose**: HTTP API endpoints and schemas
- **Components**:
  - `POST /rates/get`: Main API endpoint
  - Pydantic schemas for request/response validation

## Supported Carriers

### Estes Express
- **Carrier Code**: `ESTES`
- **Services**: Standard LTL rating with accessorials
- **Features**:
  - Real-time rate quotes
  - Transit time estimates
  - Multiple service levels
  - Comprehensive error handling

## API Usage

### Endpoint
```
POST /rates/get
```

### Request Example
```json
{
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
  "accessorials": ["LIFT_GATE", "RESIDENTIAL"],
  "carrier_id": "estes"
}
```

### Response Example
```json
{
  "success": true,
  "data": {
    "quotes": [
      {
        "carrier_name": "Estes Express",
        "carrier_code": "ESTES",
        "service_level": "STANDARD",
        "total_charge": 150.0,
        "base_charge": 135.0,
        "fuel_surcharge": 15.0,
        "accessorials_charge": 0.0,
        "transit_days": 3,
        "guaranteed": false,
        "quote_id": "QUOTE123"
      }
    ],
    "errors": [],
    "request_id": "uuid-here",
    "success": true,
    "has_quotes": true,
    "has_errors": false
  },
  "error": null
}
```

## Configuration

### Environment Variables
Add the following to your `.env` file:

```bash
# Estes Express API Configuration
ESTES_API_KEY=your-estes-api-key
ESTES_API_SECRET=your-estes-api-secret
ESTES_ACCOUNT_NUMBER=your-estes-account-number
ESTES_BASE_URL=https://api.estes-express.com
ESTES_TIMEOUT=30
ESTES_RETRY_ATTEMPTS=3
ESTES_RETRY_DELAY=1.0
```

## Adding New Carriers

### Step 1: Create Carrier Implementation
Create a new directory under `/app/infrastructure/integrations/carriers/`:

```
/app/infrastructure/integrations/carriers/newcarrier/
├── newcarrier_config.py
├── newcarrier_client.py
├── newcarrier_mapper.py
├── newcarrier_rate_provider.py
└── __init__.py
```

### Step 2: Implement Required Components

**Config (`newcarrier_config.py`)**:
```python
import os
from typing import Optional

class NewCarrierConfig:
    def __init__(self):
        self.api_key = os.getenv("NEWCARRIER_API_KEY")
        self.base_url = os.getenv("NEWCARRIER_BASE_URL")
        # ... other configuration
    
    def is_configured(self) -> bool:
        return all([self.api_key, self.base_url])
```

**Client (`newcarrier_client.py`)**:
```python
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential
from .newcarrier_config import NewCarrierConfig

class NewCarrierClient:
    def __init__(self, config: NewCarrierConfig):
        self.config = config
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=10))
    async def get_rates(self, payload: dict) -> dict:
        # Implement HTTP client logic
        pass
```

**Mapper (`newcarrier_mapper.py`)**:
```python
from app.domain.integrations import RateRequest, RateResponse

class NewCarrierMapper:
    def to_newcarrier_payload(self, request: RateRequest) -> dict:
        # Convert domain request to carrier-specific payload
        pass
    
    def from_newcarrier_response(self, response: dict) -> RateResponse:
        # Convert carrier response to domain response
        pass
```

**Rate Provider (`newcarrier_rate_provider.py`)**:
```python
from app.domain.integrations import CarrierRateProvider, RateRequest, RateResponse
from .newcarrier_config import NewCarrierConfig
from .newcarrier_client import NewCarrierClient
from .newcarrier_mapper import NewCarrierMapper

class NewCarrierRateProvider(CarrierRateProvider):
    def __init__(self, config: NewCarrierConfig = None):
        self.config = config or NewCarrierConfig()
        self.client = NewCarrierClient(self.config)
        self.mapper = NewCarrierMapper()
    
    @property
    def carrier_name(self) -> str:
        return "New Carrier"
    
    @property
    def carrier_code(self) -> str:
        return "NEWCARRIER"
    
    async def get_rates(self, request: RateRequest) -> RateResponse:
        # Implement rate fetching logic
        pass
```

### Step 3: Register the Carrier
Update `/app/infrastructure/integrations/integration_registry.py`:

```python
def _initialize_providers(self):
    try:
        # Existing providers...
        
        # Initialize new carrier
        newcarrier_provider = NewCarrierRateProvider()
        self.register_provider("newcarrier", newcarrier_provider)
        logger.info("Initialized New Carrier provider")
        
    except Exception as e:
        logger.warning(f"Failed to initialize New Carrier provider: {str(e)}")
```

### Step 4: Update Configuration
Add environment variables to `.env.example`:

```bash
# New Carrier API Configuration
NEWCARRIER_API_KEY=your-newcarrier-api-key
NEWCARRIER_BASE_URL=https://api.newcarrier.com
```

## Testing

### Unit Tests
- `test_get_rates_use_case.py`: Tests the main use case logic
- `test_estes_mapper.py`: Tests data transformation logic
- `test_estes_client.py`: Tests HTTP client behavior

### Integration Tests
- `test_rates_integration.py`: Tests full API endpoint flow

### Running Tests
```bash
pytest tests/test_get_rates_use_case.py
pytest tests/test_estes_mapper.py
pytest tests/test_estes_client.py
pytest tests/test_rates_integration.py
```

## Error Handling

The system provides comprehensive error handling:

### Error Types
- `NETWORK_ERROR`: Connection issues, timeouts
- `API_ERROR`: Carrier API errors
- `VALIDATION_ERROR`: Input validation failures
- `RATE_UNAVAILABLE`: No rates available
- `SERVICE_UNAVAILABLE`: Carrier service down
- `AUTHENTICATION_ERROR`: Credential issues
- `MAPPING_ERROR`: Data transformation errors

### Error Response Format
```json
{
  "success": true,
  "data": {
    "quotes": [],
    "errors": [
      {
        "error_type": "RATE_UNAVAILABLE",
        "message": "No rates available for this route",
        "carrier_code": "ESTES",
        "details": {},
        "timestamp": "2024-01-15T10:30:00Z"
      }
    ],
    "has_quotes": false,
    "has_errors": true
  }
}
```

## Logging

The system uses structured logging with contextual information:

```python
logger.info(f"Processing rate request {request_id}", extra={
    "request_id": request_id,
    "origin_zip": request.origin.zip_code,
    "destination_zip": request.destination.zip_code,
    "carrier_id": request.carrier_id
})
```

## Performance Considerations

### Async Operations
- All external API calls are async using `httpx.AsyncClient`
- Use cases are fully async to prevent blocking

### Retry Logic
- Configurable retry attempts with exponential backoff
- Retries only on transient failures (timeouts, network errors)

### Timeouts
- Configurable timeouts for external API calls
- Prevents hanging requests

## Security

### Credential Management
- All API credentials stored in environment variables
- No hardcoded secrets in the codebase
- Configuration validation on startup

### Input Validation
- Pydantic schemas for request validation
- Domain-level validation in use cases
- Sanitization of all external inputs

## Monitoring

### Key Metrics
- Request success/failure rates
- Response times by carrier
- Error rates by type
- Carrier availability

### Health Checks
- Connection testing for each carrier
- Configuration validation
- Service health endpoints

## Future Enhancements

### Planned Features
- Carrier performance scoring
- Rate caching with TTL
- Batch rate requests
- Historical rate tracking
- Carrier preference rules
- Dynamic carrier selection

### Extensibility
- Plugin architecture for carriers
- Custom accessorials support
- Advanced routing rules
- Multi-modal shipping support
