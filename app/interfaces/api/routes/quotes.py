from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.interfaces.schemas.quote_schema import (
    QuoteCreate, QuoteUpdate, QuoteSelection, QuoteResponse, ApiResponse
)
from app.domain.entities.quote import Quote
from app.infrastructure.database.repositories import SqlAlchemyQuoteRepository, SqlAlchemyLoadRepository, SqlAlchemyCarrierRepository
from app.application.use_cases.update_load_status import UpdateLoadStatusUseCase
from app.infrastructure.database.database import get_session
from app.domain.interfaces.quote_repository import QuoteRepository
from app.domain.interfaces.load_repository import LoadRepository
from app.domain.interfaces.carrier_repository import CarrierRepository

router = APIRouter(prefix="/quotes", tags=["quotes"])


async def get_quote_repository(session: AsyncSession = Depends(get_session)) -> QuoteRepository:
    return SqlAlchemyQuoteRepository(session)


async def get_load_repository(session: AsyncSession = Depends(get_session)) -> LoadRepository:
    return SqlAlchemyLoadRepository(session)


async def get_carrier_repository(session: AsyncSession = Depends(get_session)) -> CarrierRepository:
    return SqlAlchemyCarrierRepository(session)


async def get_update_load_status_use_case(
    load_repo: LoadRepository = Depends(get_load_repository)
) -> UpdateLoadStatusUseCase:
    return UpdateLoadStatusUseCase(load_repo)


@router.post("/", response_model=ApiResponse)
async def create_quote(
    quote_data: QuoteCreate,
    quote_repo: QuoteRepository = Depends(get_quote_repository),
    load_repo: LoadRepository = Depends(get_load_repository),
    carrier_repo: CarrierRepository = Depends(get_carrier_repository)
):
    try:
        load = await load_repo.get_by_id(quote_data.load_id)
        if not load:
            raise HTTPException(status_code=404, detail="Load not found")
        
        carrier = await carrier_repo.get_by_id(quote_data.carrier_id)
        if not carrier:
            raise HTTPException(status_code=404, detail="Carrier not found")
        
        quote = Quote(
            load_id=quote_data.load_id,
            carrier_id=quote_data.carrier_id,
            rate=quote_data.rate,
            estimated_delivery_days=quote_data.estimated_delivery_days,
            notes=quote_data.notes,
        )
        
        created_quote = await quote_repo.create(quote)
        
        return ApiResponse(
            success=True,
            data={
                "quote": {
                    "id": created_quote.id,
                    "load_id": created_quote.load_id,
                    "carrier_id": created_quote.carrier_id,
                    "rate": created_quote.rate,
                    "estimated_delivery_days": created_quote.estimated_delivery_days,
                    "notes": created_quote.notes,
                    "created_at": created_quote.created_at.isoformat(),
                    "updated_at": created_quote.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/", response_model=ApiResponse)
async def list_quotes(
    load_id: Optional[int] = Query(None, description="Filter by load ID"),
    carrier_id: Optional[int] = Query(None, description="Filter by carrier ID"),
    quote_repo: QuoteRepository = Depends(get_quote_repository)
):
    try:
        if load_id:
            quotes = await quote_repo.get_by_load_id(load_id)
        elif carrier_id:
            quotes = await quote_repo.get_by_carrier_id(carrier_id)
        else:
            raise HTTPException(status_code=400, detail="Must provide either load_id or carrier_id")
        
        quotes_data = [
            {
                "id": quote.id,
                "load_id": quote.load_id,
                "carrier_id": quote.carrier_id,
                "rate": quote.rate,
                "estimated_delivery_days": quote.estimated_delivery_days,
                "notes": quote.notes,
                "created_at": quote.created_at.isoformat(),
                "updated_at": quote.updated_at.isoformat(),
            }
            for quote in quotes
        ]
        
        return ApiResponse(
            success=True,
            data={
                "quotes": quotes_data,
                "total": len(quotes_data),
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/{quote_id}", response_model=ApiResponse)
async def get_quote(
    quote_id: int,
    quote_repo: QuoteRepository = Depends(get_quote_repository)
):
    try:
        quote = await quote_repo.get_by_id(quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        return ApiResponse(
            success=True,
            data={
                "quote": {
                    "id": quote.id,
                    "load_id": quote.load_id,
                    "carrier_id": quote.carrier_id,
                    "rate": quote.rate,
                    "estimated_delivery_days": quote.estimated_delivery_days,
                    "notes": quote.notes,
                    "created_at": quote.created_at.isoformat(),
                    "updated_at": quote.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.put("/{quote_id}", response_model=ApiResponse)
async def update_quote(
    quote_id: int,
    quote_data: QuoteUpdate,
    quote_repo: QuoteRepository = Depends(get_quote_repository)
):
    try:
        quote = await quote_repo.get_by_id(quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        if quote_data.rate is not None:
            quote.update_rate(quote_data.rate)
        if quote_data.estimated_delivery_days is not None:
            quote.estimated_delivery_days = quote_data.estimated_delivery_days
        if quote_data.notes is not None:
            quote.update_notes(quote_data.notes)
        
        updated_quote = await quote_repo.update(quote)
        
        return ApiResponse(
            success=True,
            data={
                "quote": {
                    "id": updated_quote.id,
                    "load_id": updated_quote.load_id,
                    "carrier_id": updated_quote.carrier_id,
                    "rate": updated_quote.rate,
                    "estimated_delivery_days": updated_quote.estimated_delivery_days,
                    "notes": updated_quote.notes,
                    "created_at": updated_quote.created_at.isoformat(),
                    "updated_at": updated_quote.updated_at.isoformat(),
                }
            }
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.post("/{quote_id}/select", response_model=ApiResponse)
async def select_quote(
    quote_id: int,
    selection_data: QuoteSelection,
    quote_repo: QuoteRepository = Depends(get_quote_repository),
    load_repo: LoadRepository = Depends(get_load_repository),
    update_status_use_case: UpdateLoadStatusUseCase = Depends(get_update_load_status_use_case)
):
    try:
        quote = await quote_repo.get_by_id(quote_id)
        if not quote:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        if quote.id != selection_data.quote_id:
            raise HTTPException(status_code=400, detail="Quote ID mismatch")
        
        load = await update_status_use_case.assign_carrier(quote.load_id, quote.carrier_id)
        
        return ApiResponse(
            success=True,
            data={
                "message": "Quote selected and carrier assigned successfully",
                "load": {
                    "id": load.id,
                    "status": load.status,
                    "carrier_id": load.carrier_id,
                },
                "quote": {
                    "id": quote.id,
                    "rate": quote.rate,
                    "carrier_id": quote.carrier_id,
                }
            }
        )
    except HTTPException:
        raise
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/{quote_id}", response_model=ApiResponse)
async def delete_quote(
    quote_id: int,
    quote_repo: QuoteRepository = Depends(get_quote_repository)
):
    try:
        success = await quote_repo.delete(quote_id)
        if not success:
            raise HTTPException(status_code=404, detail="Quote not found")
        
        return ApiResponse(
            success=True,
            data={"message": "Quote deleted successfully"}
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
