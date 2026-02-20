"""
Modele SubscriptionPlan - Plans d'abonnement configurables par l'administrateur.

Les prix, durees et descriptions sont modifiables depuis le panel admin
sans toucher au code source.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, Integer, Boolean, Text
from app.database import Base


class SubscriptionPlan(Base):
    __tablename__ = "subscription_plans"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    code = Column(String(50), unique=True, nullable=False, index=True)  # mensuel, annuel, trimestriel...
    name = Column(String(255), nullable=False)                          # Nom affiche : "Abonnement Mensuel"
    description = Column(Text, nullable=True)                           # Description du plan
    price = Column(Float, nullable=False)                               # Prix en devise
    currency = Column(String(10), default="USD")                        # Devise
    duration_days = Column(Integer, nullable=False)                     # Duree en jours
    is_active = Column(Boolean, default=True)                           # Plan disponible a la vente
    features = Column(Text, nullable=True)                              # Fonctionnalites incluses (JSON)
    max_sessions_per_day = Column(Integer, nullable=True)               # Limite sessions/jour (null = illimite)
    sort_order = Column(Integer, default=0)                             # Ordre d'affichage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
