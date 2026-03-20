import logging
from typing import List, Optional

from app.domain.integrations import CarrierRateProvider
from app.infrastructure.integrations.integration_registry import IntegrationRegistry


logger = logging.getLogger(__name__)


class CarrierResolverService:
    """Service for resolving carrier providers based on carrier ID."""
    
    def __init__(self, integration_registry: IntegrationRegistry):
        self.integration_registry = integration_registry
    
    async def resolve_providers(self, carrier_id: Optional[str] = None) -> List[CarrierRateProvider]:
        """
        Resolve carrier providers based on carrier ID.
        
        Args:
            carrier_id: Optional carrier ID to filter providers
            
        Returns:
            List of carrier rate providers
        """
        logger.info(f"Resolving carriers for carrier_id: {carrier_id}")
        
        if carrier_id:
            # Return specific carrier
            provider = self.integration_registry.get_provider(carrier_id)
            if provider:
                logger.info(f"Resolved specific carrier: {provider.carrier_name}")
                return [provider]
            else:
                logger.warning(f"No provider found for carrier_id: {carrier_id}")
                return []
        else:
            # Return all available carriers
            providers = self.integration_registry.get_all_providers()
            logger.info(f"Resolved {len(providers)} available carriers")
            return providers
