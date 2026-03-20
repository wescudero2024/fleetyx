from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ServiceLevel(Enum):
    """Common service levels for LTL carriers."""
    STANDARD = "STANDARD"
    EXPEDITED = "EXPEDITED"
    GUARANTEED = "GUARANTEED"
    ECONOMY = "ECONOMY"
    TIME_CRITICAL = "TIME_CRITICAL"


class RateErrorType(Enum):
    """Types of errors that can occur during rate requests."""
    NETWORK_ERROR = "NETWORK_ERROR"
    API_ERROR = "API_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_UNAVAILABLE = "RATE_UNAVAILABLE"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    MAPPING_ERROR = "MAPPING_ERROR"


@dataclass
class RateQuote:
    """Individual rate quote from a carrier."""
    carrier_name: str
    carrier_code: str
    service_level: ServiceLevel
    total_charge: float
    base_charge: float
    fuel_surcharge: float
    accessorials_charge: float
    transit_days: Optional[int] = None
    estimated_delivery_date: Optional[datetime] = None
    guaranteed: bool = False
    quote_expiration: Optional[datetime] = None
    quote_id: Optional[str] = None
    additional_charges: Optional[Dict[str, float]] = None
    service_details: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.additional_charges is None:
            self.additional_charges = {}
        if self.service_details is None:
            self.service_details = {}


@dataclass
class RateError:
    """Error information for rate requests."""
    error_type: RateErrorType
    message: str
    carrier_code: Optional[str] = None
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
        if self.details is None:
            self.details = {}


@dataclass
class RateResponse:
    """Rate response domain model."""
    quotes: List[RateQuote]
    errors: List[RateError] = None
    request_id: Optional[str] = None
    timestamp: datetime = None
    carrier_code: Optional[str] = None
    
    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.timestamp is None:
            self.timestamp = datetime.utcnow()
    
    @property
    def success(self) -> bool:
        """Check if the rate request was successful."""
        return len(self.quotes) > 0 and len(self.errors) == 0
    
    @property
    def has_quotes(self) -> bool:
        """Check if any quotes were returned."""
        return len(self.quotes) > 0
    
    @property
    def has_errors(self) -> bool:
        """Check if any errors occurred."""
        return len(self.errors) > 0
