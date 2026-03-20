import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from app.application.integrations import GetRatesUseCase, CarrierResolverService
from app.infrastructure.integrations import get_integration_registry
from app.interfaces.api.schemas import RateRequestSchema, RateRequestResponseSchema
from app.domain.integrations import RateRequest, RateResponse


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rates", tags=["rates"])


def get_rates_use_case() -> GetRatesUseCase:
    """Dependency injection for GetRatesUseCase."""
    integration_registry = get_integration_registry()
    carrier_resolver = CarrierResolverService(integration_registry)
    return GetRatesUseCase(carrier_resolver)


@router.post("/get", response_model=RateRequestResponseSchema)
async def get_rates(
    request: RateRequestSchema,
    use_case: GetRatesUseCase = Depends(get_rates_use_case)
):
    """
    Get shipping rates from carriers.
    
    This endpoint fetches rates from available carriers based on the shipment details.
    You can specify a particular carrier or get rates from all available carriers.
    
    Args:
        request: Rate request containing shipment details
        use_case: Get rates use case (injected)
        
    Returns:
        Rate response with quotes and/or errors
    """
    logger.info(f"Received rate request", extra={
        "origin_zip": request.origin.zip_code,
        "destination_zip": request.destination.zip_code,
        "carrier_id": request.carrier_id,
        "items_count": len(request.items)
    })
    
    try:
        # Convert Pydantic schema to domain model
        domain_request = _convert_schema_to_domain(request)
        
        # Execute use case
        rate_response = await use_case.execute(domain_request)
        
        # Convert domain response to schema
        response_schema = _convert_domain_to_schema(rate_response)
        
        logger.info(f"Successfully processed rate request", extra={
            "request_id": rate_response.request_id,
            "quotes_count": len(rate_response.quotes),
            "errors_count": len(rate_response.errors)
        })
        
        return RateRequestResponseSchema(
            success=True,
            data=response_schema,
            error=None
        )
        
    except ValueError as e:
        logger.warning(f"Validation error in rate request", extra={
            "error": str(e)
        })
        raise HTTPException(status_code=400, detail=str(e))
        
    except Exception as e:
        logger.error(f"Unexpected error in rate request", extra={
            "error": str(e)
        }, exc_info=True)
        
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while processing your rate request"
        )


def _convert_schema_to_domain(schema: RateRequestSchema) -> RateRequest:
    """Convert Pydantic schema to domain model."""
    from app.domain.integrations import Address, ShipmentItem, FreightClass
    
    # Convert addresses
    origin = Address(
        zip_code=schema.origin.zip_code,
        city=schema.origin.city,
        state=schema.origin.state,
        country=schema.origin.country,
        address_line1=schema.origin.address_line1,
        address_line2=schema.origin.address_line2
    )
    
    destination = Address(
        zip_code=schema.destination.zip_code,
        city=schema.destination.city,
        state=schema.destination.state,
        country=schema.destination.country,
        address_line1=schema.destination.address_line1,
        address_line2=schema.destination.address_line2
    )
    
    # Convert items
    items = []
    for item_schema in schema.items:
        freight_class = None
        if item_schema.freight_class:
            freight_class = FreightClass(item_schema.freight_class.value)
        
        item = ShipmentItem(
            weight=item_schema.weight,
            length=item_schema.length,
            width=item_schema.width,
            height=item_schema.height,
            freight_class=freight_class,
            description=item_schema.description,
            nmfc_code=item_schema.nmfc_code,
            quantity=item_schema.quantity,
            stackable=item_schema.stackable,
            hazardous_material=item_schema.hazardous_material
        )
        items.append(item)
    
    # Convert accessorials (now simple strings)
    accessorials = schema.accessorials or []
    
    return RateRequest(
        origin=origin,
        destination=destination,
        items=items,
        accessorials=accessorials,
        references=schema.references,
        carrier_id=schema.carrier_id,
        service_type=schema.service_type,
        shipment_date=schema.shipment_date,
        declared_value=schema.declared_value,
        insurance_required=schema.insurance_required
    )


def _convert_domain_to_schema(domain: RateResponse) -> "RateResponseSchema":
    """Convert domain model to Pydantic schema."""
    from app.interfaces.api.schemas import RateResponseSchema, RateQuoteSchema, RateErrorSchema, ServiceLevelSchema, RateErrorTypeSchema
    
    # Convert quotes
    quotes = []
    for quote in domain.quotes:
        service_level = ServiceLevelSchema(quote.service_level.value)
        
        quote_schema = RateQuoteSchema(
            carrier_name=quote.carrier_name,
            carrier_code=quote.carrier_code,
            service_level=service_level,
            total_charge=quote.total_charge,
            base_charge=quote.base_charge,
            fuel_surcharge=quote.fuel_surcharge,
            accessorials_charge=quote.accessorials_charge,
            transit_days=quote.transit_days,
            estimated_delivery_date=quote.estimated_delivery_date,
            guaranteed=quote.guaranteed,
            quote_expiration=quote.quote_expiration,
            quote_id=quote.quote_id,
            additional_charges=quote.additional_charges,
            service_details=quote.service_details
        )
        quotes.append(quote_schema)
    
    # Convert errors
    errors = []
    for error in domain.errors:
        error_type = RateErrorTypeSchema(error.error_type.value)
        
        error_schema = RateErrorSchema(
            error_type=error_type,
            message=error.message,
            carrier_code=error.carrier_code,
            details=error.details,
            timestamp=error.timestamp
        )
        errors.append(error_schema)
    
    return RateResponseSchema(
        quotes=quotes,
        errors=errors,
        request_id=domain.request_id,
        timestamp=domain.timestamp,
        carrier_code=domain.carrier_code,
        success=domain.success,
        has_quotes=domain.has_quotes,
        has_errors=domain.has_errors
    )
