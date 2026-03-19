from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.quote import Quote


class QuoteRepository(ABC):
    @abstractmethod
    async def create(self, quote: Quote) -> Quote:
        pass

    @abstractmethod
    async def get_by_id(self, quote_id: int) -> Optional[Quote]:
        pass

    @abstractmethod
    async def get_by_load_id(self, load_id: int) -> List[Quote]:
        pass

    @abstractmethod
    async def get_by_carrier_id(self, carrier_id: int) -> List[Quote]:
        pass

    @abstractmethod
    async def update(self, quote: Quote) -> Quote:
        pass

    @abstractmethod
    async def delete(self, quote_id: int) -> bool:
        pass
