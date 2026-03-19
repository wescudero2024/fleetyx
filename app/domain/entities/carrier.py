from datetime import datetime
from typing import Optional


class Carrier:
    def __init__(
        self,
        id: Optional[int] = None,
        name: str = "",
        mc_number: str = "",
        phone: Optional[str] = None,
        email: Optional[str] = None,
        created_at: Optional[datetime] = None,
        updated_at: Optional[datetime] = None,
    ):
        self.id = id
        self.name = name
        self.mc_number = mc_number
        self.phone = phone
        self.email = email
        self.created_at = created_at or datetime.utcnow()
        self.updated_at = updated_at or datetime.utcnow()

    def update_contact_info(self, phone: Optional[str] = None, email: Optional[str] = None) -> None:
        if phone is not None:
            self.phone = phone
        if email is not None:
            self.email = email
        self.updated_at = datetime.utcnow()

    def __repr__(self) -> str:
        return f"Carrier(id={self.id}, name={self.name}, mc_number={self.mc_number})"
