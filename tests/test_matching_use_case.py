import pytest
from app.application.use_cases.match_invoice_contract import MatchInvoiceContractUseCase


@pytest.fixture
def matching_use_case():
    return MatchInvoiceContractUseCase()


@pytest.mark.asyncio
async def test_perfect_match(matching_use_case):
    invoice_data = {"INV001": "Fast Freight Inc."}
    contract_data = [{"name": "Fast Freight Inc."}]
    
    result = await matching_use_case.execute(invoice_data, contract_data)
    
    assert result["success"] is True
    assert result["data"]["total_processed"] == 1
    assert result["data"]["high_confidence_matches"] == 1
    assert result["data"]["matches"][0]["is_match"] is True
    assert result["data"]["matches"][0]["similarity_score"] >= 0.9


@pytest.mark.asyncio
async def test_partial_match(matching_use_case):
    invoice_data = {"INV001": "Fast Freight Transportation Inc."}
    contract_data = [{"name": "Fast Freight Inc."}]
    
    result = await matching_use_case.execute(invoice_data, contract_data)
    
    assert result["success"] is True
    assert result["data"]["total_processed"] == 1
    assert result["data"]["medium_confidence_matches"] >= 0
    assert result["data"]["matches"][0]["is_match"] is True


@pytest.mark.asyncio
async def test_no_match(matching_use_case):
    invoice_data = {"INV001": "Completely Different Company LLC"}
    contract_data = [{"name": "Fast Freight Inc."}]
    
    result = await matching_use_case.execute(invoice_data, contract_data)
    
    assert result["success"] is True
    assert result["data"]["total_processed"] == 1
    assert result["data"]["matches"][0]["is_match"] is False
    assert result["data"]["matches"][0]["similarity_score"] < 0.8


@pytest.mark.asyncio
async def test_multiple_invoices(matching_use_case):
    invoice_data = {
        "INV001": "Fast Freight Inc.",
        "INV002": "Quick Transport LLC",
        "INV003": "Reliable Shipping Corp"
    }
    contract_data = [
        {"name": "Fast Freight Inc."},
        {"name": "Quick Transport Co."},
        {"name": "Different Company"}
    ]
    
    result = await matching_use_case.execute(invoice_data, contract_data)
    
    assert result["success"] is True
    assert result["data"]["total_processed"] == 3
    assert len(result["data"]["matches"]) == 3


def test_normalize_string(matching_use_case):
    assert matching_use_case.normalize_string("  Fast Freight Inc.  ") == "fast freight inc"
    assert matching_use_case.normalize_string("Quick-Transport_LLC") == "quicktransport llc"
    assert matching_use_case.normalize_string("Company@#$%^&*()") == "company"


def test_calculate_similarity(matching_use_case):
    similarity = matching_use_case.calculate_similarity("Fast Freight Inc.", "Fast Freight Inc.")
    assert similarity == 1.0
    
    similarity = matching_use_case.calculate_similarity("Fast Freight", "Fast Freight Inc.")
    assert similarity > 0.8
    
    similarity = matching_use_case.calculate_similarity("Fast Freight", "Quick Transport")
    assert similarity < 0.5


def test_extract_company_components(matching_use_case):
    components = matching_use_case.extract_company_components("Fast Freight Transportation Inc.")
    assert "fast" in components
    assert "freight" in components
    assert "transportation" in components
    assert "inc" in components
    
    components = matching_use_case.extract_company_components("Quick Transport LLC")
    assert "quick" in components
    assert "transport" in components
    assert "llc" in components
