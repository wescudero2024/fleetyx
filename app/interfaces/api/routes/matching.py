from fastapi import APIRouter, Depends, HTTPException
from app.interfaces.schemas.matching_schema import (
    MatchingRequest, MatchingResponse, ApiResponse
)
from app.application.use_cases.match_invoice_contract import MatchInvoiceContractUseCase

router = APIRouter(prefix="/matching", tags=["matching"])


async def get_matching_use_case() -> MatchInvoiceContractUseCase:
    return MatchInvoiceContractUseCase()


@router.post("/invoice-contract", response_model=ApiResponse)
async def match_invoice_contract(
    matching_request: MatchingRequest,
    use_case: MatchInvoiceContractUseCase = Depends(get_matching_use_case)
):
    try:
        invoice_data = {
            invoice.invoice_id: invoice.invoice_name 
            for invoice in matching_request.invoices
        }
        
        contract_data = [
            {"name": contract.name} 
            for contract in matching_request.contracts
        ]
        
        result = await use_case.execute(invoice_data, contract_data)
        
        return ApiResponse(
            success=True,
            data=result["data"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
