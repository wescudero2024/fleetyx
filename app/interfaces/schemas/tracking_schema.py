from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TrackingEventCreate(BaseModel):
    load_id: int = Field(..., description="Load ID")
    status: str = Field(..., min_length=1, description="Tracking status")
    location: str = Field(..., min_length=1, description="Location")
    notes: Optional[str] = Field(None, description="Additional notes")
    timestamp: Optional[datetime] = Field(None, description="Event timestamp")


class TrackingEventResponse(BaseModel):
    id: int
    load_id: int
    status: str
    location: str
    notes: Optional[str]
    timestamp: datetime

    class Config:
        from_attributes = True


class TrackingTimelineResponse(BaseModel):
    load_id: int
    events: List[TrackingEventResponse]
    total_events: int


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None
