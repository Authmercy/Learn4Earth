import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Achievement(Base):
    """Catalogue des badges / accomplissements disponibles."""
    __tablename__ = "achievements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    icon = Column(String(50), default="star")        # nom d'icone (star, fire, tree, book, trophy...)
    category = Column(String(50), nullable=False)     # pedagogie, ecologie, engagement, performance
    xp_reward = Column(Integer, default=0)
    condition_type = Column(String(100), nullable=False)  # sessions_completed, streak_days, paths_completed, score_avg, trees_planted, xp_total, learning_hours
    condition_value = Column(Integer, nullable=False)     # seuil a atteindre
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user_achievements = relationship("UserAchievement", back_populates="achievement", cascade="all, delete-orphan")


class UserAchievement(Base):
    """Association entre un utilisateur et un badge obtenu."""
    __tablename__ = "user_achievements"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    achievement_id = Column(String(36), ForeignKey("achievements.id"), nullable=False)
    unlocked_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="achievements")
    achievement = relationship("Achievement", back_populates="user_achievements")
