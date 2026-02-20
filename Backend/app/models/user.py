import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Text, Integer, Float, Date
from sqlalchemy.orm import relationship
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone_number = Column(String(20), nullable=True, index=True)
    hashed_password = Column(String(255), nullable=False)

    # Identite (full_name stocke en clair car non sensible au sens strict)
    full_name = Column(String(255), nullable=False)

    # Donnees sensibles RGPD - CHIFFREES (Fernet AES-128-CBC)
    # Stockees sous forme de texte chiffre base64, dechiffrees a la lecture
    encrypted_date_of_birth = Column(Text, nullable=True)      # date de naissance
    encrypted_address_line = Column(Text, nullable=True)       # adresse (rue, numero)
    encrypted_address_city = Column(Text, nullable=True)       # ville
    encrypted_address_postal_code = Column(Text, nullable=True)  # code postal
    encrypted_address_country = Column(Text, nullable=True)    # pays

    # Verification SMS + Email (meme code OTP envoye sur les deux canaux)
    verification_code = Column(String(10), nullable=True)
    verification_code_expires_at = Column(DateTime, nullable=True)
    is_email_verified = Column(Boolean, default=False)  # email verifie

    # Consentement RGPD
    gdpr_consent = Column(Boolean, default=False, nullable=False)      # consentement traitement donnees
    gdpr_consent_at = Column(DateTime, nullable=True)                  # date du consentement
    gdpr_marketing_consent = Column(Boolean, default=False)            # consentement communications marketing
    gdpr_data_retention_consent = Column(Boolean, default=False)       # consentement conservation des donnees

    # Profil enrichi
    avatar_url = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)
    language = Column(String(10), default="fr")
    timezone = Column(String(50), default="Europe/Paris")

    # Apprentissage
    level = Column(String(50), default="debutant")  # debutant, intermediaire, avance, expert
    objectives = Column(Text, nullable=True)
    preferences = Column(Text, nullable=True)

    # Cours gratuits (avant abonnement)
    free_courses_remaining = Column(Integer, default=5)  # 5 cours gratuits a l'inscription

    # Progression & Gamification
    total_xp = Column(Integer, default=0)
    current_streak = Column(Integer, default=0)          # jours consecutifs d'activite
    longest_streak = Column(Integer, default=0)           # meilleure serie
    last_activity_date = Column(Date, nullable=True)      # date de la derniere session
    total_learning_minutes = Column(Float, default=0.0)   # cumul temps d'apprentissage

    # Role & Statut
    role = Column(String(20), default="user")  # user, admin, super_admin
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    deactivated_at = Column(DateTime, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    subscriptions = relationship("Subscription", back_populates="user", cascade="all, delete-orphan")
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    learning_paths = relationship("LearningPath", back_populates="user", cascade="all, delete-orphan")
    sessions = relationship("LearningSession", back_populates="user", cascade="all, delete-orphan")
    carbon_footprints = relationship("CarbonFootprint", back_populates="user", cascade="all, delete-orphan")
    compensations = relationship("EcoCompensation", back_populates="user", cascade="all, delete-orphan")
    achievements = relationship("UserAchievement", back_populates="user", cascade="all, delete-orphan")
    chat_messages = relationship("ChatMessage", back_populates="user", cascade="all, delete-orphan")
