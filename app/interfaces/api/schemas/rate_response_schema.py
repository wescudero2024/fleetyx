from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime
from enum import Enum


class ServiceLevelSchema(str, Enum):
    """Schema enum for service levels."""
    STANDARD = "STANDARD"
    EXPEDITED = "EXPEDITED"
    GUARANTEED = "GUARANTEED"
    ECONOMY = "ECONOMY"
    TIME_CRITICAL = "TIME_CRITICAL"


class RateErrorTypeSchema(str, Enum):
    """Schema enum for error types."""
    NETWORK_ERROR = "NETWORK_ERROR"
    API_ERROR = "API_ERROR"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_UNAVAILABLE = "RATE_UNAVAILABLE"
    SERVICE_UNAVAILABLE = "SERVICE_UNAVAILABLE"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    MAPPING_ERROR = "MAPPING_ERROR"


class RateQuoteSchema(BaseModel):
    """Schema for individual rate quotes."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )
    
    carrier_name: str = Field(..., description="Carrier name")
    carrier_code: str = Field(..., description="Carrier code")
    service_level: ServiceLevelSchema = Field(..., description="Service level")
    total_charge: float = Field(..., ge=0, description="Total charge")
    base_charge: float = Field(..., ge=0, description="Base charge")
    fuel_surcharge: float = Field(..., ge=0, description="Fuel surcharge")
    accessorials_charge: float = Field(..., ge=0, description="Accessorials charge")
    transit_days: Optional[int] = Field(None, ge=0, description="Transit time in days")
    estimated_delivery_date: Optional[datetime] = Field(None, description="Estimated delivery date")
    guaranteed: bool = Field(default=False, description="Whether service is guaranteed")
    quote_expiration: Optional[datetime] = Field(None, description="Quote expiration date")
    quote_id: Optional[str] = Field(None, description="Quote identifier")
    additional_charges: Optional[Dict[str, float]] = Field(default={}, description="Additional charges")
    service_details: Optional[Dict[str, Any]] = Field(default={}, description="Service details")


class RateErrorSchema(BaseModel):
    """Schema for rate errors."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    error_type: RateErrorTypeSchema = Field(..., description="Type of error")
    message: str = Field(..., description="Error message")
    carrier_code: Optional[str] = Field(None, description="Carrier code if applicable")
    details: Optional[Dict[str, Any]] = Field(default={}, description="Additional error details")
    timestamp: datetime = Field(..., description="Error timestamp")


class RateResponseSchema(BaseModel):
    """Schema for rate responses."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    quotes: List[RateQuoteSchema] = Field(default=[], description="Rate quotes")
    errors: List[RateErrorSchema] = Field(default=[], description="Errors encountered")
    request_id: Optional[str] = Field(None, description="Request identifier")
    timestamp: datetime = Field(..., description="Response timestamp")
    carrier_code: Optional[str] = Field(None, description="Carrier code if specific")
    success: bool = Field(..., description="Whether request was successful")
    has_quotes: bool = Field(..., description="Whether any quotes were returned")
    has_errors: bool = Field(..., description="Whether any errors occurred")


class RateRequestResponseSchema(BaseModel):
    """Schema for the overall API response."""
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )
    
    success: bool = Field(..., description="Whether the API call was successful")
    data: RateResponseSchema = Field(..., description="Rate response data")
    error: Optional[str] = Field(None, description="Error message if API call failed")
