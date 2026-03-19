from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from app.domain.entities.load import LoadStatus

Base = declarative_base()


class LoadModel(Base):
    __tablename__ = "loads"

    id = Column(Integer, primary_key=True, index=True)
    origin = Column(String, nullable=False)
    destination = Column(String, nullable=False)
    status = Column(Enum(LoadStatus), default=LoadStatus.PENDING, nullable=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id"), nullable=True)
    price = Column(Float, default=0.0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    carrier = relationship("CarrierModel", back_populates="loads")
    quotes = relationship("QuoteModel", back_populates="load")
    tracking_events = relationship("TrackingEventModel", back_populates="load")


class CarrierModel(Base):
    __tablename__ = "carriers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    mc_number = Column(String, unique=True, nullable=False)
    phone = Column(String, nullable=True)
    email = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    loads = relationship("LoadModel", back_populates="carrier")
    quotes = relationship("QuoteModel", back_populates="carrier")


class QuoteModel(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    load_id = Column(Integer, ForeignKey("loads.id"), nullable=False)
    carrier_id = Column(Integer, ForeignKey("carriers.id"), nullable=False)
    rate = Column(Float, nullable=False)
    estimated_delivery_days = Column(Integer, default=0, nullable=False)
    notes = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    load = relationship("LoadModel", back_populates="quotes")
    carrier = relationship("CarrierModel", back_populates="quotes")


class TrackingEventModel(Base):
    __tablename__ = "tracking_events"

    id = Column(Integer, primary_key=True, index=True)
    load_id = Column(Integer, ForeignKey("loads.id"), nullable=False)
    status = Column(String, nullable=False)
    location = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String, nullable=True)

    load = relationship("LoadModel", back_populates="tracking_events")
