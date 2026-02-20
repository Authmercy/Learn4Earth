import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Text, ForeignKey, Integer
from sqlalchemy.orm import relationship
from app.database import Base


class ChatMessage(Base):
    """
    Historique des messages du chatbot IA.
    Accessible a tous les utilisateurs (avec ou sans abonnement).
    """
    __tablename__ = "chat_messages"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    conversation_id = Column(String(36), nullable=False, index=True)  # Regroupe les messages d'une conversation

    role = Column(String(20), nullable=False)  # "user" ou "assistant"
    content = Column(Text, nullable=False)

    # Metriques
    tokens_used = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", back_populates="chat_messages")
