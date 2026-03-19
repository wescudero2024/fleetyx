import pytest
from unittest.mock import AsyncMock, MagicMock
from app.application.use_cases.create_load import CreateLoadUseCase
from app.application.use_cases.update_load_status import UpdateLoadStatusUseCase
from app.domain.entities.load import Load, LoadStatus
from app.domain.interfaces.load_repository import LoadRepository


@pytest.fixture
def mock_load_repository():
    repo = AsyncMock(spec=LoadRepository)
    return repo


@pytest.fixture
def create_load_use_case(mock_load_repository):
    return CreateLoadUseCase(mock_load_repository)


@pytest.fixture
def update_load_status_use_case(mock_load_repository):
    return UpdateLoadStatusUseCase(mock_load_repository)


@pytest.fixture
def sample_load():
    return Load(
        id=1,
        origin="New York, NY",
        destination="Los Angeles, CA",
        status=LoadStatus.PENDING,
        price=2500.0
    )


@pytest.mark.asyncio
async def test_create_load_success(create_load_use_case, mock_load_repository, sample_load):
    mock_load_repository.create.return_value = sample_load
    
    result = await create_load_use_case.execute(
        origin="New York, NY",
        destination="Los Angeles, CA",
        price=2500.0
    )
    
    assert result.origin == "New York, NY"
    assert result.destination == "Los Angeles, CA"
    assert result.price == 2500.0
    assert result.status == LoadStatus.PENDING
    mock_load_repository.create.assert_called_once()


@pytest.mark.asyncio
async def test_create_load_invalid_origin(create_load_use_case):
    with pytest.raises(ValueError, match="Origin and destination are required"):
        await create_load_use_case.execute(
            origin="",
            destination="Los Angeles, CA",
            price=2500.0
        )


@pytest.mark.asyncio
async def test_create_load_negative_price(create_load_use_case):
    with pytest.raises(ValueError, match="Price cannot be negative"):
        await create_load_use_case.execute(
            origin="New York, NY",
            destination="Los Angeles, CA",
            price=-100.0
        )


@pytest.mark.asyncio
async def test_update_load_status_success(update_load_status_use_case, mock_load_repository, sample_load):
    mock_load_repository.get_by_id.return_value = sample_load
    mock_load_repository.update.return_value = sample_load
    
    result = await update_load_status_use_case.execute(1, LoadStatus.ASSIGNED)
    
    assert result.status == LoadStatus.ASSIGNED
    mock_load_repository.get_by_id.assert_called_once_with(1)
    mock_load_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_load_status_not_found(update_load_status_use_case, mock_load_repository):
    mock_load_repository.get_by_id.return_value = None
    
    with pytest.raises(ValueError, match="Load with id 1 not found"):
        await update_load_status_use_case.execute(1, LoadStatus.ASSIGNED)


@pytest.mark.asyncio
async def test_assign_carrier_success(update_load_status_use_case, mock_load_repository, sample_load):
    mock_load_repository.get_by_id.return_value = sample_load
    mock_load_repository.update.return_value = sample_load
    
    result = await update_load_status_use_case.assign_carrier(1, 5)
    
    assert result.carrier_id == 5
    assert result.status == LoadStatus.ASSIGNED
    mock_load_repository.get_by_id.assert_called_once_with(1)
    mock_load_repository.update.assert_called_once()


@pytest.mark.asyncio
async def test_cancel_load_success(update_load_status_use_case, mock_load_repository, sample_load):
    mock_load_repository.get_by_id.return_value = sample_load
    mock_load_repository.update.return_value = sample_load
    
    result = await update_load_status_use_case.cancel_load(1)
    
    assert result.status == LoadStatus.CANCELLED
    mock_load_repository.get_by_id.assert_called_once_with(1)
    mock_load_repository.update.assert_called_once()
