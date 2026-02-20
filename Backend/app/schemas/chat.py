from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ── Requetes ──────────────────────────────────────────────

class ChatMessageSend(BaseModel):
    """Message envoye par l'utilisateur au chatbot."""
    message: str = Field(..., min_length=1, max_length=2000, description="Message de l'utilisateur")
    conversation_id: Optional[str] = Field(
        None,
        description="ID de conversation existante. Si absent, une nouvelle conversation est creee.",
    )


# ── Reponses ──────────────────────────────────────────────

class ChatMessageResponse(BaseModel):
    """Un seul message dans la conversation."""
    id: UUID
    conversation_id: str
    role: str  # "user" ou "assistant"
    content: str
    tokens_used: int
    created_at: datetime

    class Config:
        from_attributes = True


class ChatResponse(BaseModel):
    """Reponse du chatbot apres envoi d'un message."""
    conversation_id: str
    user_message: ChatMessageResponse
    assistant_message: ChatMessageResponse
    has_subscription: bool = Field(
        description="Indique si l'utilisateur a un abonnement actif. "
                    "Si False, un message invite a souscrire."
    )


class ConversationSummary(BaseModel):
    """Resume d'une conversation."""
    conversation_id: str
    message_count: int
    last_message_at: datetime
    first_message_preview: str


class ConversationHistoryResponse(BaseModel):
    """Historique complet d'une conversation."""
    conversation_id: str
    messages: List[ChatMessageResponse]
    total_messages: int
