import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from app.domain.integrations import RateRequest, RateResponse, RateQuote, ServiceLevel, RateError, RateErrorType
from app.domain.integrations.rate_request import Address, ShipmentItem, FreightClass


logger = logging.getLogger(__name__)


class EstesMapper:
    """Mapper for converting between domain models and Estes API payloads."""
    
    # Mapping of Estes service types to domain service levels
    ESTES_SERVICE_MAPPING = {
        "STANDARD": ServiceLevel.STANDARD,
        "EXPEDITED": ServiceLevel.EXPEDITED,
        "GUARANTEED": ServiceLevel.GUARANTEED,
        "ECONOMY": ServiceLevel.ECONOMY,
        "TIME_CRITICAL": ServiceLevel.TIME_CRITICAL
    }
    
    def to_estes_payload(self, request: RateRequest, account_number: str) -> Dict[str, Any]:
        """
        Convert RateRequest to Estes API payload based on the JavaScript example.
        
        Args:
            request: Domain rate request
            account_number: Estes account number
            
        Returns:
            Estes API payload
        """
        try:
            # Format ship date as YYYY-MM-DD (required by Estes schema)
            ship_date = request.shipment_date.strftime("%Y-%m-%d") if request.shipment_date else datetime.now().strftime("%Y-%m-%d")
            
            # Convert country codes (USA -> US, etc.)
            origin_country = "US" if request.origin.country == "USA" else request.origin.country
            destination_country = "US" if request.destination.country == "USA" else request.destination.country
            
            # Map handling unit types (using exact Estes schema values)
            def map_handling_unit_type(item_type: Optional[str]) -> str:
                if not item_type:
                    return "PL"  # Default to Pallet (PT in Estes schema, but PL is more common)
                
                type_mapping = {
                    "Skids": "SK",
                    "Pieces": "PC", 
                    "Pallet": "PT",  # Estes schema uses PT for Pallet
                    "Cartons": "CT",
                    "Box": "BX",
                    "Crate": "CR",
                    "Drums": "DR",
                    "Barrels": "BR",
                    "Rolls": "RL",
                    "Bundle": "BD",
                    "Bag": "BG",
                    "Bucket": "BK",
                    "Bale": "BL",
                    "Can": "CN",
                    "Case": "CS",
                    "Cylinders": "CY",
                    "Jerrican": "JC",
                    "Kit": "KT",
                    "Package": "PK",
                    "Pail": "PL",
                    "Reel": "RE",
                    "Truckload": "TL",
                    "Tote": "TO"
                }
                return type_mapping.get(item_type, "PT")
            
            # Build handling units from items
            handling_units = []
            for item in request.items:
                handling_unit = {
                    "count": item.quantity,
                    "type": map_handling_unit_type(getattr(item, 'type', None)),
                    "weight": int(item.weight),  # Convert to integer as required by Estes API
                    "weightUnit": "Pounds",
                    "lineItems": [
                        {
                            "description": item.description or "Freight",
                            "weight": int(item.weight),  # Convert to integer as required by Estes API
                            "pieces": item.quantity,
                            "packagingType": map_handling_unit_type(getattr(item, 'type', None)),
                            "classification": str(item.freight_class.value) if item.freight_class else "50",
                            "isHazardous": item.hazardous_material if hasattr(item, 'hazardous_material') else False
                        }
                    ]
                }
                
                # Add dimensions only if available (conditionally required for certain service levels)
                if item.length and item.width and item.height:
                    handling_unit.update({
                        "length": int(item.length),
                        "width": int(item.width),
                        "height": int(item.height),
                        "dimensionsUnit": "Inches"
                    })
                
                # Add stackable flag if available
                if hasattr(item, 'stackable'):
                    handling_unit["isStackable"] = item.stackable
                
                handling_units.append(handling_unit)
            
            # Map accessorials to Estes codes
            estes_accessorials = []
            for accessorial in request.accessorials:
                # Map common accessorial names to Estes codes
                accessorial_mapping = {
                    "LIFT_GATE": "LGATE",
                    "LIFTGATE_DELIVERY": "LGATE", 
                    "RESIDENTIAL": "HD",
                    "RESIDENTIAL_DELIVERY": "HD",
                    "INSIDE_DELIVERY": "INS",
                    "INSIDE_PICKUP": "INP",
                    "APPOINTMENT": "APT",
                    "APPOINTMENT_DELIVERY": "APT",
                    "NOTIFICATION": "NCM",
                    "LIMITED_ACCESS": "LADPU",
                    "HAZARDOUS": "HAZ",
                    "REFRIGERATED": "HET",
                    "OVERWEIGHT": "LONG12"  # Default overweight handling
                }
                
                # Try to find matching Estes code
                estes_code = accessorial_mapping.get(accessorial.upper(), accessorial.upper())
                estes_accessorials.append(estes_code)
            
            # Build base payload
            payload = {
                "quoteRequest": {
                    "shipDate": ship_date,
                    "serviceLevels": ["LTL", "LTLTC", "ERG", "EU"]  # Service levels from JS example
                },
                "payment": {
                    "account": account_number,
                    "payor": "Third Party",
                    "terms": "Prepaid"
                },
                "requestor": {
                    "name": "Rate Request",
                    "phone": "",
                    "email": ""
                },
                "origin": {
                    "address": {
                        "city": request.origin.city or "",
                        "stateProvince": request.origin.state or "",
                        "postalCode": request.origin.zip_code,
                        "country": origin_country
                    }
                },
                "destination": {
                    "address": {
                        "city": request.destination.city or "",
                        "stateProvince": request.destination.state or "",
                        "postalCode": request.destination.zip_code,
                        "country": destination_country
                    }
                },
                "commodity": {
                    "handlingUnits": handling_units
                },
                "accessorials": {
                    "codes": estes_accessorials
                }
            }
            
            # Add address lines if available
            if request.origin.address_line1:
                payload["origin"]["address"]["addressLine1"] = request.origin.address_line1
            if request.origin.address_line2:
                payload["origin"]["address"]["addressLine2"] = request.origin.address_line2
            if request.destination.address_line1:
                payload["destination"]["address"]["addressLine1"] = request.destination.address_line1
            if request.destination.address_line2:
                payload["destination"]["address"]["addressLine2"] = request.destination.address_line2
            
            # Add accessorials if present
            if request.accessorials:
                # Accessorials are already mapped above in estes_accessorials
                if estes_accessorials:
                    payload["accessorials"] = {
                        "codes": estes_accessorials
                    }
            
            logger.info(f"Converted RateRequest to Estes payload", extra={
                "service_levels": payload["quoteRequest"]["serviceLevels"],
                "handling_units_count": len(handling_units),
                "accessorials_count": len(estes_accessorials) if request.accessorials else 0
            })
            
            return payload
            
        except Exception as e:
            logger.error(f"Error converting RateRequest to Estes payload", extra={
                "error": str(e)
            }, exc_info=True)
            raise ValueError(f"Mapping error: {str(e)}")
    
    def from_estes_response(self, estes_response: Dict[str, Any]) -> RateResponse:
        """
        Convert Estes API response to standardized RateResponse.
        
        Args:
            estes_response: Response from Estes API
            
        Returns:
            Standardized domain rate response
        """
        try:
            quotes = []
            errors = []
            
            # Extract quotes data from the Estes response structure
            quotes_data = estes_response.get("data", [])
            
            for rate_quote in quotes_data:
                try:
                    # Only include quotes where rateFound is true and no reasons
                    if (rate_quote.get("rateFound", False) and 
                        not rate_quote.get("reasons")):
                        
                        quote = self._convert_rate_to_quote(rate_quote)
                        quotes.append(quote)
                    elif rate_quote.get("reasons"):
                        # Add reasons as errors
                        for reason in rate_quote.get("reasons", []):
                            errors.append(RateError(
                                error_type=RateErrorType.VALIDATION_ERROR,
                                message=reason.get("message", "Unknown service restriction"),
                                carrier_code="ESTES",
                                details={"service_level": rate_quote.get("serviceLevelText"), "reason_id": reason.get("messageId")}
                            ))
                        
                except Exception as e:
                    logger.error(f"Error converting individual rate to quote", extra={
                        "error": str(e),
                        "rate_data": rate_quote
                    })
                    errors.append(RateError(
                        error_type=RateErrorType.MAPPING_ERROR,
                        message=f"Error converting rate to quote: {str(e)}",
                        carrier_code="ESTES",
                        details={"rate_data": rate_quote}
                    ))
            
            # Check for API-level errors (non-zero error code or non-empty message)
            if "error" in estes_response:
                error_obj = estes_response["error"]
                if error_obj.get("code", 0) != 0 or error_obj.get("message", ""):
                    errors.append(RateError(
                        error_type=RateErrorType.API_ERROR,
                        message=error_obj.get("message", "Unknown API error"),
                        carrier_code="ESTES",
                        details=error_obj
                    ))
            
            # Create standardized response
            response = RateResponse(
                quotes=quotes,
                errors=errors,
                carrier_code="ESTES",
                timestamp=datetime.utcnow()
            )
            
            logger.info(f"Converted Estes response to RateResponse", extra={
                "quotes_count": len(quotes),
                "errors_count": len(errors),
                "has_quotes": len(quotes) > 0
            })
            
            return response
            
        except Exception as e:
            logger.error(f"Error converting Estes response to RateResponse", extra={
                "error": str(e)
            }, exc_info=True)
            raise ValueError(f"Response mapping error: {str(e)}")
    
    def _convert_rate_to_quote(self, rate_quote: Dict[str, Any]) -> RateQuote:
        """
        Convert individual rate quote data from Estes API to standardized RateQuote.
        
        Args:
            rate_quote: Individual rate quote from Estes API
            
        Returns:
            Standardized domain RateQuote
        """
        try:
            # Extract service level information
            service_level_text = rate_quote.get("serviceLevelText", "STANDARD")
            service_level = self.ESTES_SERVICE_MAPPING.get(
                service_level_text, 
                ServiceLevel.STANDARD
            )
            
            # Extract quote rate information
            quote_rate = rate_quote.get("quoteRate", {})
            total_charges = float(quote_rate.get("totalCharges", 0))
            
            # Extract transit details
            transit_details = rate_quote.get("transitDetails", {})
            transit_days = transit_details.get("transitDays")
            
            # Calculate estimated delivery date
            estimated_delivery = None
            dates = rate_quote.get("dates", {})
            if dates.get("transitDeliveryDate"):
                try:
                    delivery_date_str = dates["transitDeliveryDate"]
                    delivery_time_str = dates.get("transitDeliveryTime", "00:00")
                    delivery_datetime = f"{delivery_date_str} {delivery_time_str}"
                    estimated_delivery = datetime.strptime(delivery_datetime, "%Y-%m-%d %H:%M")
                except ValueError:
                    # Fallback to transit days calculation
                    if transit_days:
                        estimated_delivery = datetime.utcnow() + timedelta(days=transit_days)
            
            # Parse charge items for detailed breakdown
            charge_items = quote_rate.get("chargeItems", [])
            line_item_charges = quote_rate.get("lineItemCharges", [])
            rated_accessorials = quote_rate.get("ratedAccessorials", [])
            
            # Calculate charge breakdown
            base_charge = total_charges  # Default to total if no breakdown
            fuel_surcharge = 0
            accessorials_charge = 0
            
            # Extract fuel surcharge from charge items
            for charge_item in charge_items:
                charge_amount = float(charge_item.get("charge", 0))
                description = charge_item.get("description", "").lower()
                
                if "fuel" in description:
                    fuel_surcharge += charge_amount
                elif "accessorial" in description or "charge" in description:
                    accessorials_charge += charge_amount
            
            # Extract from rated accessorials as well
            for accessorial in rated_accessorials:
                charge_amount = float(accessorial.get("charge", 0))
                if charge_amount > 0:
                    accessorials_charge += charge_amount
            
            # Calculate base charge
            base_charge = total_charges - fuel_surcharge - accessorials_charge
            
            # Create additional charges dict
            additional_charges = {}
            for charge_item in charge_items:
                description = charge_item.get("description", "Unknown Charge")
                charge_amount = float(charge_item.get("charge", 0))
                additional_charges[description] = charge_amount
            
            # Determine if service is guaranteed
            is_guaranteed = any(term in service_level_text.lower() for term in ["guaranteed", "erg", "exclusive use"])
            
            # Create service details
            service_details = {
                "quoteId": rate_quote.get("quoteId"),
                "serviceLevelText": service_level_text,
                "serviceLevelId": rate_quote.get("serviceLevelId"),
                "laneType": transit_details.get("laneType"),
                "originTerminal": transit_details.get("originTerminal"),
                "destinationTerminal": transit_details.get("destinationTerminal"),
                "rateType": quote_rate.get("rateType"),
                "ratedCube": quote_rate.get("ratedCube"),
                "ratedLinearFeet": quote_rate.get("ratedLinearFeet"),
                "chargeItems": charge_items,
                "lineItemCharges": line_item_charges,
                "ratedAccessorials": rated_accessorials,
                "transitMessage": transit_details.get("transitMessage"),
                "disclaimersURL": rate_quote.get("disclaimersURL"),
                "quoteExpiration": dates.get("quoteExpiration"),
                "transitDeliveryDate": dates.get("transitDeliveryDate"),
                "transitDeliveryTime": dates.get("transitDeliveryTime")
            }
            
            # Add terminal information if available
            if transit_details.get("originTerminalInfo"):
                service_details["originTerminalInfo"] = transit_details["originTerminalInfo"]
            if transit_details.get("destinationTerminalInfo"):
                service_details["destinationTerminalInfo"] = transit_details["destinationTerminalInfo"]
            
            quote = RateQuote(
                carrier_name="ESTES EXPRESS LINES",
                carrier_code="ESTES",
                service_level=service_level,
                total_charge=total_charges,
                base_charge=base_charge,
                fuel_surcharge=fuel_surcharge,
                accessorials_charge=accessorials_charge,
                transit_days=transit_days,
                estimated_delivery_date=estimated_delivery,
                guaranteed=is_guaranteed,
                quote_id=rate_quote.get("quoteId"),
                additional_charges=additional_charges,
                service_details=service_details
            )
            
            logger.debug(f"Converted Estes rate quote to RateQuote", extra={
                "quote_id": rate_quote.get("quoteId"),
                "service_level": service_level_text,
                "total_charge": total_charges,
                "transit_days": transit_days,
                "guaranteed": is_guaranteed
            })
            
            return quote
            
        except Exception as e:
            logger.error(f"Error converting Estes rate quote to RateQuote", extra={
                "error": str(e),
                "rate_quote": rate_quote
            }, exc_info=True)
            raise ValueError(f"Quote conversion error: {str(e)}")
    
    def _parse_expiration_date(self, expiration_str: Optional[str]) -> Optional[datetime]:
        """Parse expiration date string to datetime."""
        if not expiration_str:
            return None
        
        try:
            # Try ISO format first
            return datetime.fromisoformat(expiration_str.replace('Z', '+00:00'))
        except:
            try:
                # Try common formats
                return datetime.strptime(expiration_str, "%Y-%m-%d %H:%M:%S")
            except:
                logger.warning(f"Could not parse expiration date: {expiration_str}")
                return None
