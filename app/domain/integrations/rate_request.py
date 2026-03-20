from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class FreightClass(Enum):
    """Standard NMFC freight classes."""
    CLASS_50 = "50"
    CLASS_55 = "55"
    CLASS_60 = "60"
    CLASS_65 = "65"
    CLASS_70 = "70"
    CLASS_77_5 = "77.5"
    CLASS_85 = "85"
    CLASS_92_5 = "92.5"
    CLASS_100 = "100"
    CLASS_110 = "110"
    CLASS_125 = "125"
    CLASS_150 = "150"
    CLASS_175 = "175"
    CLASS_200 = "200"
    CLASS_250 = "250"
    CLASS_300 = "300"
    CLASS_400 = "400"
    CLASS_500 = "500"


@dataclass
class Address:
    """Address information for rate requests."""
    zip_code: str
    city: Optional[str] = None
    state: Optional[str] = None
    country: str = "US"
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None


@dataclass
class ShipmentItem:
    """Individual item in the shipment."""
    weight: float  # in pounds
    length: Optional[float] = None  # in inches
    width: Optional[float] = None   # in inches
    height: Optional[float] = None  # in inches
    freight_class: Optional[FreightClass] = None
    description: Optional[str] = None
    nmfc_code: Optional[str] = None
    quantity: int = 1
    stackable: bool = False
    hazardous_material: bool = False


@dataclass
class RateRequest:
    """Rate request domain model."""
    origin: Address
    destination: Address
    items: List[ShipmentItem]
    accessorials: List[str] = None  # Allow any string for accessorials
    references: Optional[List[str]] = None
    carrier_id: Optional[str] = None
    service_type: Optional[str] = None
    shipment_date: Optional[str] = None  # ISO format date string
    declared_value: Optional[float] = None
    insurance_required: bool = False
    
    def __post_init__(self):
        if self.accessorials is None:
            self.accessorials = []
        if self.references is None:
            self.references = []
