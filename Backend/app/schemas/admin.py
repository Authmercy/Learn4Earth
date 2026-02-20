"""
Schemas Pydantic pour le module Administration.

- CRUD des plans d'abonnement
- Gestion des utilisateurs (liste, stats, roles)
- Dashboard administrateur (revenus, KPIs)
"""

from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


# ══════════════════════════════════════════════════════════
#  PLANS D'ABONNEMENT
# ══════════════════════════════════════════════════════════

class PlanCreate(BaseModel):
    """Creer un nouveau plan d'abonnement."""
    code: str                                    # ex: mensuel, annuel, trimestriel
    name: str                                    # ex: "Abonnement Mensuel"
    description: Optional[str] = None
    price: float                                 # Prix
    currency: str = "USD"
    duration_days: int                           # Duree en jours
    is_active: bool = True
    features: Optional[str] = None               # Fonctionnalites (JSON)
    max_sessions_per_day: Optional[int] = None
    sort_order: int = 0

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v < 0:
            raise ValueError("Le prix ne peut pas etre negatif.")
        return round(v, 2)

    @field_validator("duration_days")
    @classmethod
    def validate_duration(cls, v):
        if v < 1:
            raise ValueError("La duree doit etre d'au moins 1 jour.")
        return v


class PlanUpdate(BaseModel):
    """Modifier un plan d'abonnement existant."""
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    duration_days: Optional[int] = None
    is_active: Optional[bool] = None
    features: Optional[str] = None
    max_sessions_per_day: Optional[int] = None
    sort_order: Optional[int] = None

    @field_validator("price")
    @classmethod
    def validate_price(cls, v):
        if v is not None and v < 0:
            raise ValueError("Le prix ne peut pas etre negatif.")
        return round(v, 2) if v is not None else v


class PlanResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: Optional[str]
    price: float
    currency: str
    duration_days: int
    is_active: bool
    features: Optional[str]
    max_sessions_per_day: Optional[int]
    sort_order: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


# ══════════════════════════════════════════════════════════
#  GESTION UTILISATEURS (vue admin)
# ══════════════════════════════════════════════════════════

class AdminUserResponse(BaseModel):
    """Vue admin d'un utilisateur (plus de details que UserResponse)."""
    id: UUID
    email: str
    phone_number: Optional[str]
    full_name: str
    gender: Optional[str]
    role: str
    level: str
    total_xp: int
    current_streak: int
    total_learning_minutes: float
    is_active: bool
    is_verified: bool
    gdpr_consent: bool
    gdpr_consent_at: Optional[datetime]
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class AdminUserRoleUpdate(BaseModel):
    """Changer le role d'un utilisateur."""
    role: str  # user, admin, super_admin

    @field_validator("role")
    @classmethod
    def validate_role(cls, v):
        allowed = ("user", "admin", "super_admin")
        if v not in allowed:
            raise ValueError(f"Role invalide. Valeurs possibles : {', '.join(allowed)}")
        return v


class AdminUsersList(BaseModel):
    """Liste paginee des utilisateurs."""
    total: int
    page: int
    per_page: int
    users: List[AdminUserResponse]


# ══════════════════════════════════════════════════════════
#  DASHBOARD ADMIN (statistiques)
# ══════════════════════════════════════════════════════════

class AdminStats(BaseModel):
    """Statistiques globales pour le dashboard admin."""
    # Utilisateurs
    total_users: int
    active_users: int
    verified_users: int
    new_users_today: int
    new_users_this_month: int

    # Abonnements
    total_subscriptions: int
    active_subscriptions: int
    subscriptions_by_plan: List[dict]  # [{"plan": "mensuel", "count": 12, "revenue": 119.88}]

    # Revenus
    total_revenue: float
    revenue_this_month: float
    revenue_currency: str
    total_payments: int
    completed_payments: int
    failed_payments: int
    pending_payments: int

    # Apprentissage
    total_learning_paths: int
    total_sessions: int
    completed_sessions: int
    total_learning_hours: float

    # Ecologie
    total_carbon_kg: float
    total_trees_planted: int
    total_co2_compensated_kg: float
