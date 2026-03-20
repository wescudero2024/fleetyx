import logging
from typing import Dict, List, Optional

from app.domain.integrations import CarrierRateProvider
from .carriers.estes import EstesRateProvider


logger = logging.getLogger(__name__)


class IntegrationRegistry:
    """Central registry for carrier integration providers."""
    
    def __init__(self):
        self._providers: Dict[str, CarrierRateProvider] = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """Initialize all available carrier providers."""
        try:
            # Initialize Estes provider
            estes_provider = EstesRateProvider()
            self.register_provider("estes", estes_provider)
            logger.info("Initialized Estes Express provider")
            
        except Exception as e:
            logger.warning(f"Failed to initialize Estes provider: {str(e)}")
    
    def register_provider(self, carrier_code: str, provider: CarrierRateProvider) -> None:
        """
        Register a carrier provider.
        
        Args:
            carrier_code: Unique carrier identifier
            provider: Carrier rate provider instance
        """
        self._providers[carrier_code.lower()] = provider
        logger.info(f"Registered carrier provider: {carrier_code}")
    
    def get_provider(self, carrier_code: str) -> Optional[CarrierRateProvider]:
        """
        Get a specific carrier provider by code.
        
        Args:
            carrier_code: Carrier identifier
            
        Returns:
            Carrier provider or None if not found
        """
        return self._providers.get(carrier_code.lower())
    
    def get_all_providers(self) -> List[CarrierRateProvider]:
        """
        Get all registered carrier providers.
        
        Returns:
            List of all carrier providers
        """
        return list(self._providers.values())
    
    def get_available_carriers(self) -> List[str]:
        """
        Get list of available carrier codes.
        
        Returns:
            List of carrier codes
        """
        return list(self._providers.keys())
    
    def is_carrier_available(self, carrier_code: str) -> bool:
        """
        Check if a carrier is available.
        
        Args:
            carrier_code: Carrier identifier
            
        Returns:
            True if carrier is available, False otherwise
        """
        return carrier_code.lower() in self._providers


# Global instance
_integration_registry: Optional[IntegrationRegistry] = None


def get_integration_registry() -> IntegrationRegistry:
    """Get the global integration registry instance."""
    global _integration_registry
    if _integration_registry is None:
        _integration_registry = IntegrationRegistry()
    return _integration_registry


def reset_integration_registry():
    """Reset the global integration registry (mainly for testing)."""
    global _integration_registry
    _integration_registry = None
