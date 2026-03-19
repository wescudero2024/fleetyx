from datetime import datetime
from typing import Optional


class Quote:
    def __init__(
        self,
        id: Optional[int] = None,
        load_id: int = 0,
        carrier_id: int = 0,
        rate: float = 0.0,
        estimated_delivery_days: int = 0,
        notes: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.load_id = load_id
        self.carrier_id = carrier_id
        self.rate = rate
        self.estimated_delivery_days = estimated_delivery_days
        self.notes = notes
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_rate(self, new_rate: float) -> None:
        if new_rate <= 0:
            raise ValueError("Rate must be positive")
        self.rate = new_rate
        self.updated_at = datetime.utcnow()

    def update_notes(self, notes: str) -> None:
        self.notes = notes
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"Quote(id={self.id}, load_id={self.load_id}, carrier_id={self.carrier_id}, rate={self.rate})"
