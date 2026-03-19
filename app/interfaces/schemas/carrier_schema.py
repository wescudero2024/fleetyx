from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CarrierCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Carrier name")
    mc_number: str = Field(..., min_length=1, description="MC number")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")


class CarrierUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, description="Carrier name")
    mc_number: Optional[str] = Field(None, min_length=1, description="MC number")
    phone: Optional[str] = Field(None, description="Phone number")
    email: Optional[str] = Field(None, description="Email address")


class CarrierResponse(BaseModel):
    id: int
    name: str
    mc_number: str
    phone: Optional[str]
    email: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CarrierListResponse(BaseModel):
    carriers: list[CarrierResponse]
    total: int
    page: int
    limit: int


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None
