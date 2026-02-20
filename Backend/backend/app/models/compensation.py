import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class EcoCompensation(Base):
    __tablename__ = "eco_compensations"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    trees_planted = Column(Integer, nullable=False)
    co2_compensated_kg = Column(Float, nullable=False)
    partner_name = Column(String(255), default="EcoTree Partner")
    partner_reference = Column(String(255), nullable=True)
    status = Column(String(30), default="confirmed")  # pending, confirmed, planted
    notes = Column(Text, nullable=True)
    triggered_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="compensations")
