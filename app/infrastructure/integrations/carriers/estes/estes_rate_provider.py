import logging

from app.domain.integrations import CarrierRateProvider, RateRequest, RateResponse
from .estes_config import EstesConfig
from .estes_client import EstesClient
from .estes_mapper import EstesMapper


logger = logging.getLogger(__name__)


class EstesRateProvider(CarrierRateProvider):
    """Estes Express rate provider implementation."""
    
    def __init__(self, config: EstesConfig = None):
        self.config = config or EstesConfig()
        self.client = EstesClient(self.config)
        self.mapper = EstesMapper()
        
        # Validate configuration
        self.config.validate()
    
    @property
    def carrier_name(self) -> str:
        return "Estes Express"
    
    @property
    def carrier_code(self) -> str:
        return "ESTES"
    
    async def get_rates(self, request: RateRequest) -> RateResponse:
        """
        Get rates from Estes Express.
        
        Args:
            request: Rate request
            
        Returns:
            Rate response with quotes and/or errors
        """
        logger.info(f"Getting rates from Estes Express", extra={
            "origin_zip": request.origin.zip_code,
            "destination_zip": request.destination.zip_code,
            "items_count": len(request.items)
        })
        
        try:
            # Convert domain request to Estes payload with account number
            estes_payload = self.mapper.to_estes_payload(request, self.config.account_number)
            
            # Call Estes API
            estes_response = await self.client.get_rates(estes_payload)
            
            # Convert Estes response to domain response
            rate_response = self.mapper.from_estes_response(estes_response)
            
            logger.info(f"Successfully received rates from Estes Express", extra={
                "quotes_count": len(rate_response.quotes),
                "errors_count": len(rate_response.errors)
            })
            
            return rate_response
            
        except Exception as e:
            logger.error(f"Error getting rates from Estes Express", extra={
                "error": str(e),
                "origin_zip": request.origin.zip_code,
                "destination_zip": request.destination.zip_code
            }, exc_info=True)
            
            from app.domain.integrations import RateError, RateErrorType
            from ...utils.error_handler import CarrierError
            
            # Extract the proper error message
            error_message = str(e)
            if isinstance(e, CarrierError):
                # Use the user-friendly message from CarrierError
                error_message = e.user_message
                error_type = RateErrorType.NETWORK_ERROR
            else:
                error_message = f"Failed to get rates from Estes Express: {str(e)}"
                error_type = RateErrorType.NETWORK_ERROR
            
            return RateResponse(
                quotes=[],
                errors=[RateError(
                    error_type=error_type,
                    message=error_message,
                    carrier_code=self.carrier_code
                )],
                carrier_code=self.carrier_code
            )
