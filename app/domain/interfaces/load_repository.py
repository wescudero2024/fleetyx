from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.load import Load, LoadStatus


class LoadRepository(ABC):
    @abstractmethod
    async def create(self, load: Load) -> Load:
        pass

    @abstractmethod
    async def get_by_id(self, load_id: int) -> Optional[Load]:
        pass

    @abstractmethod
    async def get_all(
        self, 
        status: Optional[LoadStatus] = None,
        carrier_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Load]:
        pass

    @abstractmethod
    async def update(self, load: Load) -> Load:
        pass

    @abstractmethod
    async def delete(self, load_id: int) -> bool:
        pass

    @abstractmethod
    async def count_by_status(self, status: LoadStatus) -> int:
        pass
