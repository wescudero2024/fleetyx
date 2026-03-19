from typing import Optional
from app.domain.entities.load import Load, LoadStatus
from app.domain.interfaces.load_repository import LoadRepository


class UpdateLoadStatusUseCase:
    def __init__(self, load_repository: LoadRepository):
        self.load_repository = load_repository

    async def execute(self, load_id: int, new_status: LoadStatus) -> Optional[Load]:
        load = await self.load_repository.get_by_id(load_id)
        if not load:
            raise ValueError(f"Load with id {load_id} not found")

        try:
            load.update_status(new_status)
        except ValueError as e:
            raise ValueError(f"Cannot update load status: {str(e)}")

        return await self.load_repository.update(load)

    async def assign_carrier(self, load_id: int, carrier_id: int) -> Optional[Load]:
        load = await self.load_repository.get_by_id(load_id)
        if not load:
            raise ValueError(f"Load with id {load_id} not found")

        load.assign_carrier(carrier_id)
        return await self.load_repository.update(load)

    async def cancel_load(self, load_id: int) -> Optional[Load]:
        load = await self.load_repository.get_by_id(load_id)
        if not load:
            raise ValueError(f"Load with id {load_id} not found")

        try:
            load.cancel()
        except ValueError as e:
            raise ValueError(f"Cannot cancel load: {str(e)}")

        return await self.load_repository.update(load)
