"""
Modeles pour la gestion des cours video.
Supporte : YouTube, Vimeo, URLs externes, fichiers uploades.
"""

import uuid
from datetime import datetime
from sqlalchemy import (
    Column, String, DateTime, Text, Integer, Float,
    ForeignKey, Boolean,
)
from sqlalchemy.orm import relationship
from app.database import Base


class VideoCourse(Base):
    """
    Cours video de la plateforme EcoLearn AI.
    Gere par les administrateurs, accessible aux utilisateurs selon leur abonnement.
    """
    __tablename__ = "video_courses"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    # Informations generales
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    subject = Column(String(255), nullable=False, index=True)       # ex: Python, Ecologie, IA
    category = Column(String(100), nullable=True, index=True)       # ex: Programmation, Sciences
    difficulty = Column(String(50), default="debutant")             # debutant, intermediaire, avance
    language = Column(String(10), default="fr")                     # fr, en, etc.
    tags = Column(Text, nullable=True)                              # Tags separes par virgule

    # Video source
    video_url = Column(String(500), nullable=False)                 # URL YouTube/Vimeo ou chemin fichier
    video_type = Column(String(20), nullable=False, default="youtube")  # youtube, vimeo, upload, external
    thumbnail_url = Column(String(500), nullable=True)              # Vignette de la video
    duration_seconds = Column(Integer, default=0)                   # Duree en secondes

    # Organisation dans un parcours (optionnel)
    learning_path_id = Column(String(36), ForeignKey("learning_paths.id"), nullable=True)
    order_index = Column(Integer, default=0)                        # Ordre dans le parcours

    # Acces et publication
    is_free = Column(Boolean, default=False)                        # True = accessible sans abonnement
    is_published = Column(Boolean, default=False)                   # True = visible par les utilisateurs
    requires_subscription = Column(Boolean, default=True)           # True = abonnement requis

    # Statistiques
    views_count = Column(Integer, default=0)
    likes_count = Column(Integer, default=0)

    # Administration
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)  # Admin createur

    # Horodatage
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relations
    creator = relationship("User", foreign_keys=[created_by])
    learning_path = relationship("LearningPath", backref="videos")
    progress_records = relationship("VideoProgress", back_populates="video", cascade="all, delete-orphan")

    @property
    def duration_formatted(self):
        """Retourne la duree au format HH:MM:SS."""
        hours = self.duration_seconds // 3600
        minutes = (self.duration_seconds % 3600) // 60
        seconds = self.duration_seconds % 60
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        return f"{minutes:02d}:{seconds:02d}"

    @property
    def embed_url(self):
        """Genere l'URL d'embed pour YouTube/Vimeo."""
        if self.video_type == "youtube":
            # Extraire l'ID YouTube
            video_id = self.video_url
            if "watch?v=" in self.video_url:
                video_id = self.video_url.split("watch?v=")[-1].split("&")[0]
            elif "youtu.be/" in self.video_url:
                video_id = self.video_url.split("youtu.be/")[-1].split("?")[0]
            elif "embed/" in self.video_url:
                return self.video_url
            return f"https://www.youtube.com/embed/{video_id}"
        elif self.video_type == "vimeo":
            video_id = self.video_url.split("/")[-1]
            return f"https://player.vimeo.com/video/{video_id}"
        return self.video_url


class VideoProgress(Base):
    """
    Suivi de progression d'un utilisateur sur une video.
    Permet la reprise de lecture et le calcul de progression.
    """
    __tablename__ = "video_progress"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    video_id = Column(String(36), ForeignKey("video_courses.id"), nullable=False)

    # Progression
    watched_seconds = Column(Integer, default=0)           # Position de lecture actuelle
    progress_percent = Column(Float, default=0.0)          # % de progression (0-100)
    is_completed = Column(Boolean, default=False)           # True si >= 90% regarde
    watch_count = Column(Integer, default=1)                # Nombre de fois regardee

    # XP attribue
    xp_earned = Column(Integer, default=0)

    # Horodatage
    last_watched_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relations
    user = relationship("User", backref="video_progress")
    video = relationship("VideoCourse", back_populates="progress_records")
