from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.carrier import Carrier


class CarrierRepository(ABC):
    @abstractmethod
    async def create(self, carrier: Carrier) -> Carrier:
        pass

    @abstractmethod
    async def get_by_id(self, carrier_id: int) -> Optional[Carrier]:
        pass

    @abstractmethod
    async def get_by_mc_number(self, mc_number: str) -> Optional[Carrier]:
        pass

    @abstractmethod
    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Carrier]:
        pass

    @abstractmethod
    async def update(self, carrier: Carrier) -> Carrier:
        pass

    @abstractmethod
    async def delete(self, carrier_id: int) -> bool:
        pass

    @abstractmethod
    async def search_by_name(self, name: str) -> List[Carrier]:
        pass
