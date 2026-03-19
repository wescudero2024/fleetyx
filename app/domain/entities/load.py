from datetime import datetime
from typing import Optional
from enum import Enum


class LoadStatus(str, Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Load:
    def __init__(
        self,
        id: Optional[int] = None,
        origin: str = "",
        destination: str = "",
        status: LoadStatus = LoadStatus.PENDING,
        carrier_id: Optional[int] = None,
        price: float = 0.0,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.origin = origin
        self.destination = destination
        self.status = status
        self.carrier_id = carrier_id
        self.price = price
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def assign_carrier(self, carrier_id: int) -> None:
        self.carrier_id = carrier_id
        self.status = LoadStatus.ASSIGNED
        self.updated_at = datetime.utcnow()

    def update_status(self, status: LoadStatus) -> None:
        if self.status == LoadStatus.DELIVERED:
            raise ValueError("Cannot change status of delivered load")
        if self.status == LoadStatus.CANCELLED:
            raise ValueError("Cannot change status of cancelled load")
        
        self.status = status
        self.updated_at = datetime.utcnow()

    def cancel(self) -> None:
        if self.status == LoadStatus.DELIVERED:
            raise ValueError("Cannot cancel delivered load")
        self.status = LoadStatus.CANCELLED
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"Load(id={self.id}, origin={self.origin}, destination={self.destination}, status={self.status})"
