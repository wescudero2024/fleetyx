from typing import Optional
from app.domain.entities.load import Load
from app.domain.interfaces.load_repository import LoadRepository


class CreateLoadUseCase:
    def __init__(self, load_repository: LoadRepository):
        self.load_repository = load_repository

    async def execute(
        self,
        origin: str,
        destination: str,
        price: float = 0.0,
        carrier_id: Optional[int] = None,
    ) -> Load:
        if not origin or not destination:
            raise ValueError("Origin and destination are required")
        
        if price < 0:
            raise ValueError("Price cannot be negative")

        load = Load(
            origin=origin,
            destination=destination,
            price=price,
            carrier_id=carrier_id,
        )

        return await self.load_repository.create(load)
