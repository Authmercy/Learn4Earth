import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class LearningSession(Base):
    __tablename__ = "learning_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    learning_path_id = Column(String(36), ForeignKey("learning_paths.id"), nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=True)  # Contenu genere par GPT
    ai_prompt_used = Column(Text, nullable=True)
    duration_minutes = Column(Float, default=0.0)
    score = Column(Float, nullable=True)  # Score de performance 0-100
    session_number = Column(Integer, nullable=False)
    status = Column(String(30), default="en_cours")  # en_cours, terminee, abandonnee
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="sessions")
    learning_path = relationship("LearningPath", back_populates="sessions")
    carbon_footprint = relationship("CarbonFootprint", back_populates="session", uselist=False)
