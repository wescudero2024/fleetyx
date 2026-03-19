from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy import select, func, and_
from app.domain.entities.load import Load, LoadStatus
from app.domain.entities.carrier import Carrier
from app.domain.entities.quote import Quote
from app.domain.interfaces.load_repository import LoadRepository
from app.domain.interfaces.carrier_repository import CarrierRepository
from app.domain.interfaces.quote_repository import QuoteRepository
from app.infrastructure.database.models import LoadModel, CarrierModel, QuoteModel


class SqlAlchemyLoadRepository(LoadRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, load: Load) -> Load:
        db_load = LoadModel(
            origin=load.origin,
            destination=load.destination,
            status=load.status,
            carrier_id=load.carrier_id,
            price=load.price,
            created_at=load.created_at,
            updated_at=load.updated_at,
        )
        self.session.add(db_load)
        await self.session.commit()
        await self.session.refresh(db_load)
        return self._to_entity(db_load)

    async def get_by_id(self, load_id: int) -> Optional[Load]:
        result = await self.session.execute(
            select(LoadModel)
            .options(selectinload(LoadModel.carrier))
            .options(selectinload(LoadModel.quotes))
            .where(LoadModel.id == load_id)
        )
        db_load = result.scalar_one_or_none()
        return self._to_entity(db_load) if db_load else None

    async def get_all(
        self,
        status: Optional[LoadStatus] = None,
        carrier_id: Optional[int] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Load]:
        query = select(LoadModel).options(selectinload(LoadModel.carrier))
        
        conditions = []
        if status:
            conditions.append(LoadModel.status == status)
        if carrier_id:
            conditions.append(LoadModel.carrier_id == carrier_id)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.limit(limit).offset(limit * offset)
        
        result = await self.session.execute(query)
        db_loads = result.scalars().all()
        return [self._to_entity(db_load) for db_load in db_loads]

    async def update(self, load: Load) -> Load:
        result = await self.session.execute(
            select(LoadModel).where(LoadModel.id == load.id)
        )
        db_load = result.scalar_one_or_none()
        if db_load:
            db_load.origin = load.origin
            db_load.destination = load.destination
            db_load.status = load.status
            db_load.carrier_id = load.carrier_id
            db_load.price = load.price
            db_load.updated_at = load.updated_at
            await self.session.commit()
            await self.session.refresh(db_load)
            return self._to_entity(db_load)
        return None

    async def delete(self, load_id: int) -> bool:
        result = await self.session.execute(
            select(LoadModel).where(LoadModel.id == load_id)
        )
        db_load = result.scalar_one_or_none()
        if db_load:
            await self.session.delete(db_load)
            await self.session.commit()
            return True
        return False

    async def count_by_status(self, status: LoadStatus) -> int:
        result = await self.session.execute(
            select(func.count(LoadModel.id)).where(LoadModel.status == status)
        )
        return result.scalar()

    def _to_entity(self, db_load: LoadModel) -> Load:
        return Load(
            id=db_load.id,
            origin=db_load.origin,
            destination=db_load.destination,
            status=db_load.status,
            carrier_id=db_load.carrier_id,
            price=db_load.price,
            created_at=db_load.created_at,
            updated_at=db_load.updated_at,
        )


class SqlAlchemyCarrierRepository(CarrierRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, carrier: Carrier) -> Carrier:
        db_carrier = CarrierModel(
            name=carrier.name,
            mc_number=carrier.mc_number,
            phone=carrier.phone,
            email=carrier.email,
            created_at=carrier.created_at,
            updated_at=carrier.updated_at,
        )
        self.session.add(db_carrier)
        await self.session.commit()
        await self.session.refresh(db_carrier)
        return self._to_entity(db_carrier)

    async def get_by_id(self, carrier_id: int) -> Optional[Carrier]:
        result = await self.session.execute(
            select(CarrierModel).where(CarrierModel.id == carrier_id)
        )
        db_carrier = result.scalar_one_or_none()
        return self._to_entity(db_carrier) if db_carrier else None

    async def get_by_mc_number(self, mc_number: str) -> Optional[Carrier]:
        result = await self.session.execute(
            select(CarrierModel).where(CarrierModel.mc_number == mc_number)
        )
        db_carrier = result.scalar_one_or_none()
        return self._to_entity(db_carrier) if db_carrier else None

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Carrier]:
        result = await self.session.execute(
            select(CarrierModel).limit(limit).offset(limit * offset)
        )
        db_carriers = result.scalars().all()
        return [self._to_entity(db_carrier) for db_carrier in db_carriers]

    async def update(self, carrier: Carrier) -> Carrier:
        result = await self.session.execute(
            select(CarrierModel).where(CarrierModel.id == carrier.id)
        )
        db_carrier = result.scalar_one_or_none()
        if db_carrier:
            db_carrier.name = carrier.name
            db_carrier.mc_number = carrier.mc_number
            db_carrier.phone = carrier.phone
            db_carrier.email = carrier.email
            db_carrier.updated_at = carrier.updated_at
            await self.session.commit()
            await self.session.refresh(db_carrier)
            return self._to_entity(db_carrier)
        return None

    async def delete(self, carrier_id: int) -> bool:
        result = await self.session.execute(
            select(CarrierModel).where(CarrierModel.id == carrier_id)
        )
        db_carrier = result.scalar_one_or_none()
        if db_carrier:
            await self.session.delete(db_carrier)
            await self.session.commit()
            return True
        return False

    async def search_by_name(self, name: str) -> List[Carrier]:
        result = await self.session.execute(
            select(CarrierModel).where(CarrierModel.name.ilike(f"%{name}%"))
        )
        db_carriers = result.scalars().all()
        return [self._to_entity(db_carrier) for db_carrier in db_carriers]

    def _to_entity(self, db_carrier: CarrierModel) -> Carrier:
        return Carrier(
            id=db_carrier.id,
            name=db_carrier.name,
            mc_number=db_carrier.mc_number,
            phone=db_carrier.phone,
            email=db_carrier.email,
            created_at=db_carrier.created_at,
            updated_at=db_carrier.updated_at,
        )


class SqlAlchemyQuoteRepository(QuoteRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, quote: Quote) -> Quote:
        db_quote = QuoteModel(
            load_id=quote.load_id,
            carrier_id=quote.carrier_id,
            rate=quote.rate,
            estimated_delivery_days=quote.estimated_delivery_days,
            notes=quote.notes,
            created_at=quote.created_at,
            updated_at=quote.updated_at,
        )
        self.session.add(db_quote)
        await self.session.commit()
        await self.session.refresh(db_quote)
        return self._to_entity(db_quote)

    async def get_by_id(self, quote_id: int) -> Optional[Quote]:
        result = await self.session.execute(
            select(QuoteModel)
            .options(selectinload(QuoteModel.load))
            .options(selectinload(QuoteModel.carrier))
            .where(QuoteModel.id == quote_id)
        )
        db_quote = result.scalar_one_or_none()
        return self._to_entity(db_quote) if db_quote else None

    async def get_by_load_id(self, load_id: int) -> List[Quote]:
        result = await self.session.execute(
            select(QuoteModel)
            .options(selectinload(QuoteModel.carrier))
            .where(QuoteModel.load_id == load_id)
        )
        db_quotes = result.scalars().all()
        return [self._to_entity(db_quote) for db_quote in db_quotes]

    async def get_by_carrier_id(self, carrier_id: int) -> List[Quote]:
        result = await self.session.execute(
            select(QuoteModel)
            .options(selectinload(QuoteModel.load))
            .where(QuoteModel.carrier_id == carrier_id)
        )
        db_quotes = result.scalars().all()
        return [self._to_entity(db_quote) for db_quote in db_quotes]

    async def update(self, quote: Quote) -> Quote:
        result = await self.session.execute(
            select(QuoteModel).where(QuoteModel.id == quote.id)
        )
        db_quote = result.scalar_one_or_none()
        if db_quote:
            db_quote.rate = quote.rate
            db_quote.estimated_delivery_days = quote.estimated_delivery_days
            db_quote.notes = quote.notes
            db_quote.updated_at = quote.updated_at
            await self.session.commit()
            await self.session.refresh(db_quote)
            return self._to_entity(db_quote)
        return None

    async def delete(self, quote_id: int) -> bool:
        result = await self.session.execute(
            select(QuoteModel).where(QuoteModel.id == quote_id)
        )
        db_quote = result.scalar_one_or_none()
        if db_quote:
            await self.session.delete(db_quote)
            await self.session.commit()
            return True
        return False

    def _to_entity(self, db_quote: QuoteModel) -> Quote:
        return Quote(
            id=db_quote.id,
            load_id=db_quote.load_id,
            carrier_id=db_quote.carrier_id,
            rate=db_quote.rate,
            estimated_delivery_days=db_quote.estimated_delivery_days,
            notes=db_quote.notes,
            created_at=db_quote.created_at,
            updated_at=db_quote.updated_at,
        )
