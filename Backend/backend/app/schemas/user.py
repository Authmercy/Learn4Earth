"""
Schemas Pydantic pour les utilisateurs.

Conformite RGPD :
- Les champs sensibles sont chiffres avant stockage (via encrypt_data)
- Les reponses API ne retournent que des donnees dechiffrees aux utilisateurs autorises
- Les validations strictes protegent l'integrite des donnees personnelles
- Le consentement RGPD est obligatoire a l'inscription
"""

import re
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from datetime import datetime, date
from uuid import UUID


# ── Creation & Auth ────────────────────────────────────────

class UserCreate(BaseModel):
    """
    Schema d'inscription enrichi avec donnees personnelles.
    Les champs marques [CHIFFRE] seront chiffres avant stockage en DB.
    """
    # Identite obligatoire
    email: EmailStr
    password: str
    full_name: str
    phone_number: str                       # [CHIFFRE en base] Format E.164 : +243898900119

    # Donnees personnelles [CHIFFREES en base]
    date_of_birth: str                      # Format YYYY-MM-DD

    # Adresse [CHIFFREE en base]
    address_line: Optional[str] = None      # Rue et numero
    address_city: Optional[str] = None      # Ville
    address_postal_code: Optional[str] = None  # Code postal
    address_country: Optional[str] = None   # Pays

    # Apprentissage
    level: Optional[str] = "debutant"
    objectives: Optional[str] = None
    preferences: Optional[str] = None

    # Consentement RGPD (OBLIGATOIRE)
    gdpr_consent: bool                      # Doit etre True pour s'inscrire
    gdpr_marketing_consent: Optional[bool] = False   # Communications marketing (facultatif)
    gdpr_data_retention_consent: Optional[bool] = False  # Conservation des donnees (facultatif)

    # ── Validations ─────────────────────────────────────

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        """
        Mot de passe robuste :
        - Minimum 8 caracteres
        - Au moins 1 majuscule, 1 minuscule, 1 chiffre, 1 caractere special
        """
        if len(v) < 8:
            raise ValueError("Le mot de passe doit contenir au moins 8 caracteres.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une lettre majuscule.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une lettre minuscule.")
        if not re.search(r"\d", v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:'\",.<>?/\\`~]", v):
            raise ValueError("Le mot de passe doit contenir au moins un caractere special (!@#$%^&*...).")
        return v

    @field_validator("phone_number")
    @classmethod
    def validate_phone_number(cls, v):
        v = v.strip()
        if not v.startswith("+"):
            raise ValueError("Le numero de telephone doit commencer par '+' (format E.164, ex: +243898900119).")
        if len(v) < 8 or len(v) > 20:
            raise ValueError("Le numero de telephone doit contenir entre 8 et 20 caracteres.")
        if not v[1:].isdigit():
            raise ValueError("Le numero de telephone ne doit contenir que des chiffres apres le '+'.")
        return v

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v):
        """Valider que la date de naissance est au format YYYY-MM-DD et coherente."""
        try:
            dob = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("La date de naissance doit etre au format YYYY-MM-DD (ex: 1990-05-15).")
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 13:
            raise ValueError("L'utilisateur doit avoir au moins 13 ans pour s'inscrire (conformite RGPD).")
        if age > 120:
            raise ValueError("Date de naissance invalide.")
        return v

    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        allowed = ("debutant", "intermediaire", "avance", "expert")
        if v and v not in allowed:
            raise ValueError(f"Niveau invalide. Valeurs possibles : {', '.join(allowed)}")
        return v

    @field_validator("gdpr_consent")
    @classmethod
    def validate_gdpr_consent(cls, v):
        """Le consentement RGPD est obligatoire pour l'inscription."""
        if not v:
            raise ValueError(
                "Le consentement au traitement des donnees personnelles est obligatoire "
                "pour s'inscrire (conformite RGPD, Article 6)."
            )
        return v


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"


# ── Profil ──────────────────────────────────────────────────

class UserUpdate(BaseModel):
    """
    Mise a jour du profil. Les champs sensibles sont re-chiffres automatiquement.
    """
    full_name: Optional[str] = None
    date_of_birth: Optional[str] = None
    address_line: Optional[str] = None
    address_city: Optional[str] = None
    address_postal_code: Optional[str] = None
    address_country: Optional[str] = None
    avatar_url: Optional[str] = None
    bio: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None
    level: Optional[str] = None
    objectives: Optional[str] = None
    preferences: Optional[str] = None

    @field_validator("date_of_birth")
    @classmethod
    def validate_date_of_birth(cls, v):
        if v is None:
            return v
        try:
            dob = datetime.strptime(v, "%Y-%m-%d").date()
        except ValueError:
            raise ValueError("La date de naissance doit etre au format YYYY-MM-DD.")
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 13:
            raise ValueError("L'utilisateur doit avoir au moins 13 ans.")
        return v

    @field_validator("level")
    @classmethod
    def validate_level(cls, v):
        allowed = ("debutant", "intermediaire", "avance", "expert")
        if v and v not in allowed:
            raise ValueError(f"Niveau invalide. Valeurs possibles : {', '.join(allowed)}")
        return v


class PasswordChange(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, v):
        if len(v) < 8:
            raise ValueError("Le nouveau mot de passe doit contenir au moins 8 caracteres.")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une lettre majuscule.")
        if not re.search(r"[a-z]", v):
            raise ValueError("Le mot de passe doit contenir au moins une lettre minuscule.")
        if not re.search(r"\d", v):
            raise ValueError("Le mot de passe doit contenir au moins un chiffre.")
        if not re.search(r"[!@#$%^&*()_+\-=\[\]{}|;:'\",.<>?/\\`~]", v):
            raise ValueError("Le mot de passe doit contenir au moins un caractere special.")
        return v


class VerifySMS(BaseModel):
    """Schema pour la verification par code SMS."""
    email: EmailStr
    code: str


class ResendOTP(BaseModel):
    """Schema pour renvoyer un code OTP."""
    email: EmailStr


# ── Reponse utilisateur ─────────────────────────────────────

class UserResponse(BaseModel):
    """
    Reponse API utilisateur avec donnees dechiffrees.
    Les champs sensibles sont automatiquement dechiffres avant envoi.
    """
    id: UUID
    email: str
    phone_number: Optional[str]
    full_name: str

    # Donnees personnelles (dechiffrees)
    date_of_birth: Optional[str] = None

    # Adresse (dechiffree)
    address_city: Optional[str] = None
    address_country: Optional[str] = None
    # address_line et postal_code sont partiellement masques par securite
    address_line_masked: Optional[str] = None
    address_postal_code_masked: Optional[str] = None

    # Consentements RGPD
    gdpr_consent: bool
    gdpr_consent_at: Optional[datetime] = None
    gdpr_marketing_consent: bool = False
    gdpr_data_retention_consent: bool = False

    # Profil
    avatar_url: Optional[str]
    bio: Optional[str]
    language: str
    timezone: str
    level: str
    objectives: Optional[str]
    preferences: Optional[str]
    free_courses_remaining: int = 5
    total_xp: int
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date]
    total_learning_minutes: float
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class UserFullDataExport(BaseModel):
    """
    Export complet des donnees personnelles (droit a la portabilite RGPD, Article 20).
    Inclut TOUTES les donnees en clair, y compris celles masquees dans UserResponse.
    """
    id: UUID
    email: str
    phone_number: Optional[str]
    full_name: str
    date_of_birth: Optional[str]
    address_line: Optional[str]
    address_city: Optional[str]
    address_postal_code: Optional[str]
    address_country: Optional[str]
    gdpr_consent: bool
    gdpr_consent_at: Optional[datetime]
    gdpr_marketing_consent: bool
    gdpr_data_retention_consent: bool
    avatar_url: Optional[str]
    bio: Optional[str]
    language: str
    timezone: str
    level: str
    objectives: Optional[str]
    preferences: Optional[str]
    total_xp: int
    current_streak: int
    longest_streak: int
    last_activity_date: Optional[date]
    total_learning_minutes: float
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]


class GDPRConsentUpdate(BaseModel):
    """Schema pour mettre a jour les consentements RGPD."""
    gdpr_marketing_consent: Optional[bool] = None
    gdpr_data_retention_consent: Optional[bool] = None


# ── Progression ──────────────────────────────────────────────

class LearningPathProgressItem(BaseModel):
    path_id: UUID
    title: str
    subject: str
    difficulty: str
    total_sessions: int
    completed_sessions: int
    progress_percent: float
    status: str
    average_score: Optional[float]
    total_duration_minutes: float
    created_at: datetime


class UserProgressionSummary(BaseModel):
    """Resume complet de la progression de l'utilisateur."""
    # Identite
    user_id: UUID
    full_name: str
    level: str

    # XP & Gamification
    total_xp: int
    xp_to_next_level: int
    current_streak: int
    longest_streak: int

    # Stats pedagogiques globales
    total_paths: int
    active_paths: int
    completed_paths: int
    abandoned_paths: int
    total_sessions: int
    completed_sessions: int
    average_score: Optional[float]
    best_score: Optional[float]
    total_learning_minutes: float
    total_learning_hours: float

    # Detail parcours
    paths: List[LearningPathProgressItem]

    # Badges
    total_achievements_unlocked: int
    total_achievements_available: int
    achievements: List["AchievementResponse"]


# ── Achievements ──────────────────────────────────────────────

class AchievementResponse(BaseModel):
    id: UUID
    code: str
    name: str
    description: str
    icon: str
    category: str
    xp_reward: int
    unlocked_at: Optional[datetime] = None  # None si pas encore debloque

    class Config:
        from_attributes = True


class UserAchievementResponse(BaseModel):
    id: UUID
    achievement: AchievementResponse
    unlocked_at: datetime

    class Config:
        from_attributes = True


# Resoudre les references forward
Token.model_rebuild()
UserProgressionSummary.model_rebuild()
