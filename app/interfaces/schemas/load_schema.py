from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.domain.entities.load import LoadStatus


class LoadCreate(BaseModel):
    origin: str = Field(..., min_length=1, description="Origin address")
    destination: str = Field(..., min_length=1, description="Destination address")
    price: float = Field(0.0, ge=0, description="Load price")
    carrier_id: Optional[int] = Field(None, description="Assigned carrier ID")


class LoadUpdate(BaseModel):
    origin: Optional[str] = Field(None, min_length=1, description="Origin address")
    destination: Optional[str] = Field(None, min_length=1, description="Destination address")
    price: Optional[float] = Field(None, ge=0, description="Load price")


class LoadStatusUpdate(BaseModel):
    status: LoadStatus = Field(..., description="New load status")


class LoadCarrierAssignment(BaseModel):
    carrier_id: int = Field(..., description="Carrier ID to assign")


class LoadResponse(BaseModel):
    id: int
    origin: str
    destination: str
    status: LoadStatus
    carrier_id: Optional[int]
    price: float
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class LoadListResponse(BaseModel):
    loads: list[LoadResponse]
    total: int
    page: int
    limit: int


class LoadKPIs(BaseModel):
    total_loads: int
    pending_loads: int
    assigned_loads: int
    in_transit_loads: int
    delivered_loads: int
    cancelled_loads: int


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None
