from typing import List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator
from enum import Enum


class FreightClassSchema(str, Enum):
    """Schema enum for freight classes."""
    CLASS_50 = "50"
    CLASS_55 = "55"
    CLASS_60 = "60"
    CLASS_65 = "65"
    CLASS_70 = "70"
    CLASS_77_5 = "77.5"
    CLASS_85 = "85"
    CLASS_92_5 = "92.5"
    CLASS_100 = "100"
    CLASS_110 = "110"
    CLASS_125 = "125"
    CLASS_150 = "150"
    CLASS_175 = "175"
    CLASS_200 = "200"
    CLASS_250 = "250"
    CLASS_300 = "300"
    CLASS_400 = "400"
    CLASS_500 = "500"


class AddressSchema(BaseModel):
    """Schema for address information."""
    zip_code: str = Field(..., min_length=5, max_length=10, description="ZIP/Postal code")
    city: Optional[str] = Field(None, description="City name")
    state: Optional[str] = Field(None, description="State/province code")
    country: str = Field(default="US", description="Country code")
    address_line1: Optional[str] = Field(None, description="Street address line 1")
    address_line2: Optional[str] = Field(None, description="Street address line 2")
    
    @field_validator('zip_code')
    @classmethod
    def validate_zip_code(cls, v):
        if not v or len(v.strip()) < 3:
            raise ValueError('ZIP code must be at least 3 characters')
        return v.strip()


class ShipmentItemSchema(BaseModel):
    """Schema for shipment items."""
    weight: float = Field(..., gt=0, description="Weight in pounds")
    length: Optional[float] = Field(None, gt=0, description="Length in inches")
    width: Optional[float] = Field(None, gt=0, description="Width in inches")
    height: Optional[float] = Field(None, gt=0, description="Height in inches")
    freight_class: Optional[FreightClassSchema] = Field(None, description="NMFC freight class")
    description: Optional[str] = Field(None, description="Item description")
    nmfc_code: Optional[str] = Field(None, description="NMFC code")
    quantity: int = Field(default=1, gt=0, description="Number of items")
    stackable: bool = Field(default=False, description="Whether items can be stacked")
    hazardous_material: bool = Field(default=False, description="Whether item is hazardous")
    
    @model_validator(mode='after')
    @classmethod
    def validate_dimensions(cls, values):
        # If one dimension is provided, all should be provided
        dimensions = [getattr(values, 'length'), getattr(values, 'width'), getattr(values, 'height')]
        provided_dims = [d for d in dimensions if d is not None]
        
        if provided_dims and len(provided_dims) != 3:
            raise ValueError('If any dimension is provided, all dimensions (length, width, height) must be provided')
        
        return values


class RateRequestSchema(BaseModel):
    """Schema for rate requests."""
    origin: AddressSchema = Field(..., description="Origin address")
    destination: AddressSchema = Field(..., description="Destination address")
    items: List[ShipmentItemSchema] = Field(..., min_length=1, description="Shipment items")
    accessorials: Optional[List[str]] = Field(default=[], description="Requested accessorials - any string value allowed")
    references: Optional[List[str]] = Field(default=[], description="Reference numbers")
    carrier_id: Optional[str] = Field(None, description="Specific carrier to query")
    service_type: Optional[str] = Field(None, description="Preferred service type")
    shipment_date: Optional[str] = Field(None, description="Shipment date (ISO format)")
    declared_value: Optional[float] = Field(None, ge=0, description="Declared value for insurance")
    insurance_required: bool = Field(default=False, description="Whether insurance is required")
    
    @field_validator('items')
    @classmethod
    def validate_items(cls, v):
        if not v:
            raise ValueError('At least one item is required')
        return v
    
    @field_validator('shipment_date')
    @classmethod
    def validate_shipment_date(cls, v):
        if v:
            # Basic ISO format validation
            try:
                from datetime import datetime
                datetime.fromisoformat(v.replace('Z', '+00:00'))
            except ValueError:
                raise ValueError('Shipment date must be in ISO format')
        return v
