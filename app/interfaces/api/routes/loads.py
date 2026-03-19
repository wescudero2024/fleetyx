from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.schemas.load_schema import (
    LoadCreate, LoadUpdate, LoadStatusUpdate, LoadCarrierAssignment,
    LoadResponse, LoadListResponse, LoadKPIs, ApiResponse
)
from app.application.use_cases.create_load import CreateLoadUseCase
from app.application.use_cases.update_load_status import UpdateLoadStatusUseCase
from app.domain.entities.load import LoadStatus
from app.infrastructure.database.repositories import SqlAlchemyLoadRepository
from app.infrastructure.database.database import get_session
from app.domain.interfaces.load_repository import LoadRepository

router = APIRouter(prefix="/loads", tags=["loads"])


async def get_load_repository(session: AsyncSession = Depends(get_session)) -> LoadRepository:
    return SqlAlchemyLoadRepository(session)


async def get_create_load_use_case(repo: LoadRepository = Depends(get_load_repository)) -> CreateLoadUseCase:
    return CreateLoadUseCase(repo)


async def get_update_load_status_use_case(repo: LoadRepository = Depends(get_load_repository)) -> UpdateLoadStatusUseCase:
    return UpdateLoadStatusUseCase(repo)


@router.post("/", response_model=ApiResponse)
async def create_load(
    load_data: LoadCreate,
    use_case: CreateLoadUseCase = Depends(get_create_load_use_case)
):
    try:
        load = await use_case.execute(
            origin=load_data.origin,
            destination=load_data.destination,
            price=load_data.price,
            carrier_id=load_data.carrier_id,
        )
        
        return ApiResponse(
            success=True,
            data={
                "load": {
                    "id": load.id,
                    "origin": load.origin,
                    "destination": load.destination,
                    "status": load.status,
                    "carrier_id": load.carrier_id,
                    "price": load.price,
                    "created_at": load.created_at.isoformat(),
                    "updated_at": load.updated_at.isoformat(),
                }
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=ApiResponse)
async def list_loads(
    status: Optional[LoadStatus] = Query(None, description="Filter by load status"),
    carrier_id: Optional[int] = Query(None, description="Filter by carrier ID"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
    repo: LoadRepository = Depends(get_load_repository)
):
    try:
        offset = (page - 1) * limit
        loads = await repo.get_all(
            status=status,
            carrier_id=carrier_id,
            limit=limit,
            offset=offset
        )
        
        loads_data = [
            {
                "id": load.id,
                "origin": load.origin,
                "destination": load.destination,
                "status": load.status,
                "carrier_id": load.carrier_id,
                "price": load.price,
                "created_at": load.created_at.isoformat(),
                "updated_at": load.updated_at.isoformat(),
            }
            for load in loads
        ]
        
        return ApiResponse(
            success=True,
            data={
                "loads": loads_data,
                "total": len(loads_data),
                "page": page,
                "limit": limit,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{load_id}", response_model=ApiResponse)
async def get_load(
    load_id: int,
    repo: LoadRepository = Depends(get_load_repository)
):
    try:
        load = await repo.get_by_id(load_id)
        if not load:
            raise HTTPException(status_code=404, detail="Load not found")
        
        return ApiResponse(
            success=True,
            data={
                "load": {
                    "id": load.id,
                    "origin": load.origin,
                    "destination": load.destination,
                    "status": load.status,
                    "carrier_id": load.carrier_id,
                    "price": load.price,
                    "created_at": load.created_at.isoformat(),
                    "updated_at": load.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{load_id}", response_model=ApiResponse)
async def update_load(
    load_id: int,
    load_data: LoadUpdate,
    repo: LoadRepository = Depends(get_load_repository)
):
    try:
        load = await repo.get_by_id(load_id)
        if not load:
            raise HTTPException(status_code=404, detail="Load not found")
        
        if load_data.origin is not None:
            load.origin = load_data.origin
        if load_data.destination is not None:
            load.destination = load_data.destination
        if load_data.price is not None:
            load.price = load_data.price
        
        updated_load = await repo.update(load)
        
        return ApiResponse(
            success=True,
            data={
                "load": {
                    "id": updated_load.id,
                    "origin": updated_load.origin,
                    "destination": updated_load.destination,
                    "status": updated_load.status,
                    "carrier_id": updated_load.carrier_id,
                    "price": updated_load.price,
                    "created_at": updated_load.created_at.isoformat(),
                    "updated_at": updated_load.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.patch("/{load_id}/status", response_model=ApiResponse)
async def update_load_status(
    load_id: int,
    status_data: LoadStatusUpdate,
    use_case: UpdateLoadStatusUseCase = Depends(get_update_load_status_use_case)
):
    try:
        load = await use_case.execute(load_id, status_data.status)
        
        return ApiResponse(
            success=True,
            data={
                "load": {
                    "id": load.id,
                    "origin": load.origin,
                    "destination": load.destination,
                    "status": load.status,
                    "carrier_id": load.carrier_id,
                    "price": load.price,
                    "created_at": load.created_at.isoformat(),
                    "updated_at": load.updated_at.isoformat(),
                }
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{load_id}/assign", response_model=ApiResponse)
async def assign_carrier(
    load_id: int,
    assignment_data: LoadCarrierAssignment,
    use_case: UpdateLoadStatusUseCase = Depends(get_update_load_status_use_case)
):
    try:
        load = await use_case.assign_carrier(load_id, assignment_data.carrier_id)
        
        return ApiResponse(
            success=True,
            data={
                "load": {
                    "id": load.id,
                    "origin": load.origin,
                    "destination": load.destination,
                    "status": load.status,
                    "carrier_id": load.carrier_id,
                    "price": load.price,
                    "created_at": load.created_at.isoformat(),
                    "updated_at": load.updated_at.isoformat(),
                }
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{load_id}/cancel", response_model=ApiResponse)
async def cancel_load(
    load_id: int,
    use_case: UpdateLoadStatusUseCase = Depends(get_update_load_status_use_case)
):
    try:
        load = await use_case.cancel_load(load_id)
        
        return ApiResponse(
            success=True,
            data={
                "load": {
                    "id": load.id,
                    "origin": load.origin,
                    "destination": load.destination,
                    "status": load.status,
                    "carrier_id": load.carrier_id,
                    "price": load.price,
                    "created_at": load.created_at.isoformat(),
                    "updated_at": load.updated_at.isoformat(),
                }
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/kpis/dashboard", response_model=ApiResponse)
async def get_load_kpis(
    repo: LoadRepository = Depends(get_load_repository)
):
    try:
        total_loads = len(await repo.get_all(limit=10000))
        pending_loads = await repo.count_by_status(LoadStatus.PENDING)
        assigned_loads = await repo.count_by_status(LoadStatus.ASSIGNED)
        in_transit_loads = await repo.count_by_status(LoadStatus.IN_TRANSIT)
        delivered_loads = await repo.count_by_status(LoadStatus.DELIVERED)
        cancelled_loads = await repo.count_by_status(LoadStatus.CANCELLED)
        
        return ApiResponse(
            success=True,
            data={
                "total_loads": total_loads,
                "pending_loads": pending_loads,
                "assigned_loads": assigned_loads,
                "in_transit_loads": in_transit_loads,
                "delivered_loads": delivered_loads,
                "cancelled_loads": cancelled_loads,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
