import logging
from typing import List, Optional
from uuid import uuid4

from app.domain.integrations import RateRequest, RateResponse, CarrierRateProvider
from .carrier_resolver_service import CarrierResolverService


logger = logging.getLogger(__name__)


class GetRatesUseCase:
    """Use case for getting rates from carriers."""
    
    def __init__(self, carrier_resolver: CarrierResolverService):
        self.carrier_resolver = carrier_resolver
    
    async def execute(self, request: RateRequest) -> RateResponse:
        """
        Execute the rate request process.
        
        Args:
            request: Rate request containing shipment details
            
        Returns:
            RateResponse containing quotes and/or errors
        """
        request_id = str(uuid4())
        logger.info(f"Processing rate request {request_id}", extra={
            "request_id": request_id,
            "origin_zip": request.origin.zip_code,
            "destination_zip": request.destination.zip_code,
            "carrier_id": request.carrier_id,
            "items_count": len(request.items)
        })
        
        try:
            # Validate request
            self._validate_request(request)
            
            # Resolve carriers
            providers = await self.carrier_resolver.resolve_providers(request.carrier_id)
            
            if not providers:
                logger.warning(f"No carriers found for request {request_id}", extra={
                    "request_id": request_id,
                    "carrier_id": request.carrier_id
                })
                return RateResponse(
                    quotes=[],
                    errors=[],
                    request_id=request_id
                )
            
            # Get rates from all resolved providers
            all_quotes = []
            all_errors = []
            
            for provider in providers:
                try:
                    logger.info(f"Requesting rates from {provider.carrier_name}", extra={
                        "request_id": request_id,
                        "carrier_code": provider.carrier_code
                    })
                    
                    response = await provider.get_rates(request)
                    
                    all_quotes.extend(response.quotes)
                    all_errors.extend(response.errors)
                    
                    logger.info(f"Received response from {provider.carrier_name}", extra={
                        "request_id": request_id,
                        "carrier_code": provider.carrier_code,
                        "quotes_count": len(response.quotes),
                        "errors_count": len(response.errors)
                    })
                    
                except Exception as e:
                    logger.error(f"Error getting rates from {provider.carrier_name}", extra={
                        "request_id": request_id,
                        "carrier_code": provider.carrier_code,
                        "error": str(e)
                    }, exc_info=True)
                    
                    from app.domain.integrations import RateError, RateErrorType
                    error = RateError(
                        error_type=RateErrorType.NETWORK_ERROR,
                        message=f"Failed to get rates from {provider.carrier_name}: {str(e)}",
                        carrier_code=provider.carrier_code
                    )
                    all_errors.append(error)
            
            logger.info(f"Completed rate request {request_id}", extra={
                "request_id": request_id,
                "total_quotes": len(all_quotes),
                "total_errors": len(all_errors)
            })
            
            return RateResponse(
                quotes=all_quotes,
                errors=all_errors,
                request_id=request_id
            )
            
        except Exception as e:
            logger.error(f"Unexpected error in rate request {request_id}", extra={
                "request_id": request_id,
                "error": str(e)
            }, exc_info=True)
            
            from app.domain.integrations import RateError, RateErrorType
            return RateResponse(
                quotes=[],
                errors=[RateError(
                    error_type=RateErrorType.API_ERROR,
                    message=f"Unexpected error: {str(e)}",
                    details={"request_id": request_id}
                )],
                request_id=request_id
            )
    
    def _validate_request(self, request: RateRequest) -> None:
        """Validate the rate request."""
        if not request.origin.zip_code:
            raise ValueError("Origin ZIP code is required")
        
        if not request.destination.zip_code:
            raise ValueError("Destination ZIP code is required")
        
        if not request.items:
            raise ValueError("At least one shipment item is required")
        
        for item in request.items:
            if item.weight <= 0:
                raise ValueError("Item weight must be greater than 0")
            
            if item.quantity <= 0:
                raise ValueError("Item quantity must be greater than 0")
