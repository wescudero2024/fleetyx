from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from app.infrastructure.database.models import TrackingEventModel
from app.domain.entities.load import LoadStatus


class TrackingService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_tracking_event(
        self,
        load_id: int,
        status: str,
        location: str,
        notes: Optional[str] = None,
        timestamp: Optional[datetime] = None
    ) -> Dict[str, Any]:
        event = TrackingEventModel(
            load_id=load_id,
            status=status,
            location=location,
            notes=notes,
            timestamp=timestamp or datetime.utcnow()
        )
        
        self.session.add(event)
        await self.session.commit()
        await self.session.refresh(event)
        
        return {
            'id': event.id,
            'load_id': event.load_id,
            'status': event.status,
            'location': event.location,
            'notes': event.notes,
            'timestamp': event.timestamp.isoformat()
        }

    async def get_tracking_timeline(self, load_id: int) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(TrackingEventModel)
            .where(TrackingEventModel.load_id == load_id)
            .order_by(TrackingEventModel.timestamp.desc())
        )
        
        events = result.scalars().all()
        
        return [
            {
                'id': event.id,
                'status': event.status,
                'location': event.location,
                'notes': event.notes,
                'timestamp': event.timestamp.isoformat()
            }
            for event in events
        ]

    async def get_latest_tracking(self, load_id: int) -> Optional[Dict[str, Any]]:
        result = await self.session.execute(
            select(TrackingEventModel)
            .where(TrackingEventModel.load_id == load_id)
            .order_by(TrackingEventModel.timestamp.desc())
            .limit(1)
        )
        
        event = result.scalar_one_or_none()
        if not event:
            return None
            
        return {
            'id': event.id,
            'status': event.status,
            'location': event.location,
            'notes': event.notes,
            'timestamp': event.timestamp.isoformat()
        }

    async def search_by_status(
        self, 
        load_id: int, 
        status: str
    ) -> List[Dict[str, Any]]:
        result = await self.session.execute(
            select(TrackingEventModel)
            .where(
                and_(
                    TrackingEventModel.load_id == load_id,
                    TrackingEventModel.status == status
                )
            )
            .order_by(TrackingEventModel.timestamp.desc())
        )
        
        events = result.scalars().all()
        
        return [
            {
                'id': event.id,
                'status': event.status,
                'location': event.location,
                'notes': event.notes,
                'timestamp': event.timestamp.isoformat()
            }
            for event in events
        ]
