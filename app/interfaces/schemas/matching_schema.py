from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class InvoiceData(BaseModel):
    invoice_id: str = Field(..., description="Invoice identifier")
    invoice_name: str = Field(..., description="Invoice company name")


class ContractData(BaseModel):
    contract_id: str = Field(..., description="Contract identifier")
    name: str = Field(..., description="Contract company name")


class MatchingRequest(BaseModel):
    invoices: List[InvoiceData] = Field(..., description="List of invoices to match")
    contracts: List[ContractData] = Field(..., description="List of contracts to match against")


class MatchingResult(BaseModel):
    invoice_id: str
    invoice_name: str
    best_match: str
    similarity_score: float
    is_match: bool
    confidence: str


class MatchingResponse(BaseModel):
    matches: List[MatchingResult]
    total_processed: int
    high_confidence_matches: int
    medium_confidence_matches: int
    low_confidence_matches: int


class ApiResponse(BaseModel):
    success: bool = True
    data: Optional[dict] = None
    error: Optional[str] = None
