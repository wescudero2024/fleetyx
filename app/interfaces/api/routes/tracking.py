from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.schemas.tracking_schema import (
    TrackingEventCreate, TrackingEventResponse, ApiResponse
)
from app.application.services.tracking_service import TrackingService
from app.infrastructure.database.database import get_session

router = APIRouter(prefix="/tracking", tags=["tracking"])


async def get_tracking_service(session: AsyncSession = Depends(get_session)) -> TrackingService:
    return TrackingService(session)


@router.post("/update", response_model=ApiResponse)
async def update_tracking(
    tracking_data: TrackingEventCreate,
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    try:
        event = await tracking_service.add_tracking_event(
            load_id=tracking_data.load_id,
            status=tracking_data.status,
            location=tracking_data.location,
            notes=tracking_data.notes,
            timestamp=tracking_data.timestamp
        )
        
        return ApiResponse(
            success=True,
            data={
                "tracking_event": event,
                "message": "Tracking event added successfully"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{load_id}", response_model=ApiResponse)
async def get_tracking_timeline(
    load_id: int,
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    try:
        events = await tracking_service.get_tracking_timeline(load_id)
        
        return ApiResponse(
            success=True,
            data={
                "load_id": load_id,
                "events": events,
                "total_events": len(events)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{load_id}/latest", response_model=ApiResponse)
async def get_latest_tracking(
    load_id: int,
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    try:
        event = await tracking_service.get_latest_tracking(load_id)
        
        if not event:
            return ApiResponse(
                success=True,
                data={
                    "message": "No tracking events found for this load",
                    "load_id": load_id
                }
            )
        
        return ApiResponse(
            success=True,
            data={
                "latest_tracking": event,
                "load_id": load_id
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{load_id}/status/{status}", response_model=ApiResponse)
async def get_tracking_by_status(
    load_id: int,
    status: str,
    tracking_service: TrackingService = Depends(get_tracking_service)
):
    try:
        events = await tracking_service.search_by_status(load_id, status)
        
        return ApiResponse(
            success=True,
            data={
                "load_id": load_id,
                "status": status,
                "events": events,
                "total_events": len(events)
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
