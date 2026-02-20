"""
Router du Chatbot IA - Accessible a TOUS les utilisateurs (avec ou sans abonnement).
Le chatbot repond aux questions generales, donne des conseils d'apprentissage,
et invite les utilisateurs sans abonnement a souscrire pour generer des cours complets.
"""

import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
import httpx

from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.subscription import Subscription
from app.models.chat_message import ChatMessage
from app.schemas.chat import (
    ChatMessageSend,
    ChatMessageResponse,
    ChatResponse,
    ConversationSummary,
    ConversationHistoryResponse,
)
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot IA"])


def _user_has_active_subscription(db: Session, user_id: str) -> bool:
    """Verifie si l'utilisateur a un abonnement actif."""
    return (
        db.query(Subscription)
        .filter(
            Subscription.user_id == user_id,
            Subscription.is_active == True,
            Subscription.end_date > datetime.utcnow(),
        )
        .first()
    ) is not None


@router.post("/send", response_model=ChatResponse)
async def send_message(
    payload: ChatMessageSend,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Envoyer un message au chatbot IA.
    Accessible a tous les utilisateurs authentifies (avec ou sans abonnement).
    Le chatbot repond aux questions generales et oriente les non-abonnes vers les offres.
    """
    # Determiner ou creer l'identifiant de conversation
    conversation_id = payload.conversation_id or str(uuid.uuid4())

    # Verifier si l'utilisateur a un abonnement actif
    has_subscription = _user_has_active_subscription(db, current_user.id)

    # Recuperer l'historique de la conversation (les 10 derniers messages)
    history_records = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.conversation_id == conversation_id,
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )
    conversation_history = [
        {"role": msg.role, "content": msg.content}
        for msg in history_records[-10:]
    ]

    # Sauvegarder le message de l'utilisateur
    user_msg = ChatMessage(
        user_id=current_user.id,
        conversation_id=conversation_id,
        role="user",
        content=payload.message,
        tokens_used=0,
    )
    db.add(user_msg)
    db.flush()

    # Appeler le service IA Flask
    ai_response_text = ""
    tokens_used = 0
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/chat",
                json={
                    "message": payload.message,
                    "conversation_history": conversation_history,
                    "user_name": current_user.full_name,
                    "has_subscription": has_subscription,
                },
            )
            if response.status_code == 200:
                ai_result = response.json()
                ai_response_text = ai_result.get("response", "")
                tokens_used = ai_result.get("tokens_used", 0)
    except Exception:
        pass

    # Fallback si pas de reponse
    if not ai_response_text:
        ai_response_text = (
            f"Bonjour {current_user.full_name} ! Je suis EcoBot. "
            "Je rencontre un petit souci technique, reessayez dans quelques instants."
        )
        if not has_subscription:
            ai_response_text += (
                "\n\nEn attendant, decouvrez nos offres d'abonnement pour acceder "
                "aux cours generes par IA ! Consultez GET /api/subscriptions/plans."
            )

    # Sauvegarder la reponse du chatbot
    assistant_msg = ChatMessage(
        user_id=current_user.id,
        conversation_id=conversation_id,
        role="assistant",
        content=ai_response_text,
        tokens_used=tokens_used,
    )
    db.add(assistant_msg)
    db.commit()

    db.refresh(user_msg)
    db.refresh(assistant_msg)

    return ChatResponse(
        conversation_id=conversation_id,
        user_message=ChatMessageResponse.model_validate(user_msg),
        assistant_message=ChatMessageResponse.model_validate(assistant_msg),
        has_subscription=has_subscription,
    )


@router.get("/conversations", response_model=List[ConversationSummary])
def list_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lister toutes les conversations de l'utilisateur.
    Accessible a tous les utilisateurs authentifies.
    """
    # Sous-requete : compter les messages et date du dernier message par conversation
    conversations = (
        db.query(
            ChatMessage.conversation_id,
            func.count(ChatMessage.id).label("message_count"),
            func.max(ChatMessage.created_at).label("last_message_at"),
        )
        .filter(ChatMessage.user_id == current_user.id)
        .group_by(ChatMessage.conversation_id)
        .order_by(func.max(ChatMessage.created_at).desc())
        .all()
    )

    result = []
    for conv_id, count, last_at in conversations:
        # Recuperer le premier message pour un apercu
        first_msg = (
            db.query(ChatMessage)
            .filter(
                ChatMessage.user_id == current_user.id,
                ChatMessage.conversation_id == conv_id,
                ChatMessage.role == "user",
            )
            .order_by(ChatMessage.created_at.asc())
            .first()
        )
        preview = (first_msg.content[:80] + "...") if first_msg and len(first_msg.content) > 80 else (first_msg.content if first_msg else "")

        result.append(ConversationSummary(
            conversation_id=conv_id,
            message_count=count,
            last_message_at=last_at,
            first_message_preview=preview,
        ))

    return result


@router.get("/conversations/{conversation_id}", response_model=ConversationHistoryResponse)
def get_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Recuperer l'historique complet d'une conversation.
    Accessible a tous les utilisateurs authentifies.
    """
    messages = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.conversation_id == conversation_id,
        )
        .order_by(ChatMessage.created_at.asc())
        .all()
    )

    if not messages:
        raise HTTPException(status_code=404, detail="Conversation introuvable.")

    return ConversationHistoryResponse(
        conversation_id=conversation_id,
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
        total_messages=len(messages),
    )


@router.delete("/conversations/{conversation_id}")
def delete_conversation(
    conversation_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Supprimer une conversation et tous ses messages.
    Accessible a tous les utilisateurs authentifies (droit RGPD a l'effacement).
    """
    deleted = (
        db.query(ChatMessage)
        .filter(
            ChatMessage.user_id == current_user.id,
            ChatMessage.conversation_id == conversation_id,
        )
        .delete()
    )

    if deleted == 0:
        raise HTTPException(status_code=404, detail="Conversation introuvable.")

    db.commit()
    return {
        "message": f"Conversation supprimee ({deleted} messages effaces).",
        "conversation_id": conversation_id,
    }
