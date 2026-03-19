from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.schemas.carrier_schema import (
    CarrierCreate, CarrierUpdate, CarrierResponse, ApiResponse
)
from app.domain.entities.carrier import Carrier
from app.infrastructure.database.repositories import SqlAlchemyCarrierRepository
from app.infrastructure.database.database import get_session
from app.domain.interfaces.carrier_repository import CarrierRepository

router = APIRouter(prefix="/carriers", tags=["carriers"])


async def get_carrier_repository(session: AsyncSession = Depends(get_session)) -> CarrierRepository:
    return SqlAlchemyCarrierRepository(session)


@router.post("/", response_model=ApiResponse)
async def create_carrier(
    carrier_data: CarrierCreate,
    carrier_repo: CarrierRepository = Depends(get_carrier_repository)
):
    try:
        existing_carrier = await carrier_repo.get_by_mc_number(carrier_data.mc_number)
        if existing_carrier:
            raise HTTPException(status_code=400, detail="Carrier with this MC number already exists")
        
        carrier = Carrier(
            name=carrier_data.name,
            mc_number=carrier_data.mc_number,
            phone=carrier_data.phone,
            email=carrier_data.email,
        )
        
        created_carrier = await carrier_repo.create(carrier)
        
        return ApiResponse(
            success=True,
            data={
                "carrier": {
                    "id": created_carrier.id,
                    "name": created_carrier.name,
                    "mc_number": created_carrier.mc_number,
                    "phone": created_carrier.phone,
                    "email": created_carrier.email,
                    "created_at": created_carrier.created_at.isoformat(),
                    "updated_at": created_carrier.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=ApiResponse)
async def list_carriers(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(100, ge=1, le=1000, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by carrier name"),
    carrier_repo: CarrierRepository = Depends(get_carrier_repository)
):
    try:
        if search:
            carriers = await carrier_repo.search_by_name(search)
        else:
            offset = (page - 1) * limit
            carriers = await carrier_repo.get_all(limit=limit, offset=offset)
        
        carriers_data = [
            {
                "id": carrier.id,
                "name": carrier.name,
                "mc_number": carrier.mc_number,
                "phone": carrier.phone,
                "email": carrier.email,
                "created_at": carrier.created_at.isoformat(),
                "updated_at": carrier.updated_at.isoformat(),
            }
            for carrier in carriers
        ]
        
        return ApiResponse(
            success=True,
            data={
                "carriers": carriers_data,
                "total": len(carriers_data),
                "page": page,
                "limit": limit,
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{carrier_id}", response_model=ApiResponse)
async def get_carrier(
    carrier_id: int,
    carrier_repo: CarrierRepository = Depends(get_carrier_repository)
):
    try:
        carrier = await carrier_repo.get_by_id(carrier_id)
        if not carrier:
            raise HTTPException(status_code=404, detail="Carrier not found")
        
        return ApiResponse(
            success=True,
            data={
                "carrier": {
                    "id": carrier.id,
                    "name": carrier.name,
                    "mc_number": carrier.mc_number,
                    "phone": carrier.phone,
                    "email": carrier.email,
                    "created_at": carrier.created_at.isoformat(),
                    "updated_at": carrier.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{carrier_id}", response_model=ApiResponse)
async def update_carrier(
    carrier_id: int,
    carrier_data: CarrierUpdate,
    carrier_repo: CarrierRepository = Depends(get_carrier_repository)
):
    try:
        carrier = await carrier_repo.get_by_id(carrier_id)
        if not carrier:
            raise HTTPException(status_code=404, detail="Carrier not found")
        
        if carrier_data.name is not None:
            carrier.name = carrier_data.name
        if carrier_data.mc_number is not None:
            existing_carrier = await carrier_repo.get_by_mc_number(carrier_data.mc_number)
            if existing_carrier and existing_carrier.id != carrier_id:
                raise HTTPException(status_code=400, detail="MC number already exists")
            carrier.mc_number = carrier_data.mc_number
        if carrier_data.phone is not None:
            carrier.phone = carrier_data.phone
        if carrier_data.email is not None:
            carrier.email = carrier_data.email
        
        updated_carrier = await carrier_repo.update(carrier)
        
        return ApiResponse(
            success=True,
            data={
                "carrier": {
                    "id": updated_carrier.id,
                    "name": updated_carrier.name,
                    "mc_number": updated_carrier.mc_number,
                    "phone": updated_carrier.phone,
                    "email": updated_carrier.email,
                    "created_at": updated_carrier.created_at.isoformat(),
                    "updated_at": updated_carrier.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{carrier_id}", response_model=ApiResponse)
async def delete_carrier(
    carrier_id: int,
    carrier_repo: CarrierRepository = Depends(get_carrier_repository)
):
    try:
        success = await carrier_repo.delete(carrier_id)
        if not success:
            raise HTTPException(status_code=404, detail="Carrier not found")
        
        return ApiResponse(
            success=True,
            data={"message": "Carrier deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
