from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class QuoteCreate(BaseModel):
    load_id: int = Field(..., description="Load ID")
    carrier_id: int = Field(..., description="Carrier ID")
    rate: float = Field(..., gt=0, description="Quote rate")
    estimated_delivery_days: int = Field(0, ge=0, description="Estimated delivery days")
    notes: Optional[str] = Field(None, description="Additional notes")


class QuoteUpdate(BaseModel):
    rate: Optional[float] = Field(None, gt=0, description="Quote rate")
    estimated_delivery_days: Optional[int] = Field(None, ge=0, description="Estimated delivery days")
    notes: Optional[str] = Field(None, description="Additional notes")


class QuoteResponse(BaseModel):
    id: int
    load_id: int
    carrier_id: int
    rate: float
    estimated_delivery_days: int
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QuoteWithCarrierResponse(QuoteResponse):
    carrier_name: Optional[str] = None
    carrier_mc_number: Optional[str] = None


class QuoteSelection(BaseModel):
    quote_id: int = Field(..., description="Quote ID to select")


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None
