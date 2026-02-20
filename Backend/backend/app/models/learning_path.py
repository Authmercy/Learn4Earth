import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(255), nullable=False)
    difficulty = Column(String(50), default="debutant")
    total_sessions = Column(Integer, default=0)
    completed_sessions = Column(Integer, default=0)
    progress_percent = Column(Float, default=0.0)
    status = Column(String(30), default="en_cours")  # en_cours, termine, abandonne
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="learning_paths")
    sessions = relationship("LearningSession", back_populates="learning_path", cascade="all, delete-orphan")
