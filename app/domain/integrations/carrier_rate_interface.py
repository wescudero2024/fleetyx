from abc import ABC, abstractmethod
from typing import Protocol
from .rate_request import RateRequest
from .rate_response import RateResponse


class CarrierRateProvider(ABC):
    """Abstract base class for carrier rate providers."""
    
    @abstractmethod
    async def get_rates(self, request: RateRequest) -> RateResponse:
        """
        Fetch rates from the carrier API.
        
        Args:
            request: Rate request containing origin, destination, and shipment details
            
        Returns:
            RateResponse containing rates, transit times, and service levels
        """
        pass
    
    @property
    @abstractmethod
    def carrier_name(self) -> str:
        """Return the carrier name."""
        pass
    
    @property
    @abstractmethod
    def carrier_code(self) -> str:
        """Return the carrier code used for identification."""
        pass
