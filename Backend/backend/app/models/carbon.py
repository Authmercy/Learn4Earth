import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class CarbonFootprint(Base):
    __tablename__ = "carbon_footprints"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    session_id = Column(String(36), ForeignKey("learning_sessions.id"), unique=True, nullable=False)
    duration_minutes = Column(Float, nullable=False)
    energy_kwh = Column(Float, nullable=False)
    carbon_kg = Column(Float, nullable=False)
    server_region = Column(String(100), default="europe-west")
    carbon_factor = Column(Float, nullable=False)  # kg CO2 per kWh for region
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="carbon_footprints")
    session = relationship("LearningSession", back_populates="carbon_footprint")
