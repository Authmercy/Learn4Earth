"""
Schemas Pydantic pour la gestion des cours video.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID


# ══════════════════════════════════════════════════
#  REQUETES (Input)
# ══════════════════════════════════════════════════

class VideoCourseCreate(BaseModel):
    """Creation d'un cours video (par un admin)."""
    title: str = Field(..., min_length=3, max_length=255, description="Titre de la video")
    description: Optional[str] = Field(None, max_length=5000, description="Description detaillee")
    subject: str = Field(..., min_length=2, max_length=255, description="Sujet (ex: Python, Ecologie)")
    category: Optional[str] = Field(None, max_length=100, description="Categorie (ex: Programmation)")
    difficulty: Optional[str] = Field("debutant", description="debutant, intermediaire, avance")
    language: Optional[str] = Field("fr", max_length=10)
    tags: Optional[str] = Field(None, description="Tags separes par virgule")

    video_url: str = Field(..., max_length=500, description="URL YouTube/Vimeo ou chemin fichier")
    video_type: str = Field("youtube", description="youtube, vimeo, upload, external")
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    duration_seconds: Optional[int] = Field(0, ge=0, description="Duree en secondes")

    learning_path_id: Optional[str] = Field(None, description="ID du parcours associe")
    order_index: Optional[int] = Field(0, ge=0, description="Ordre dans le parcours")

    is_free: Optional[bool] = Field(False, description="Accessible sans abonnement")
    is_published: Optional[bool] = Field(False, description="Visible par les utilisateurs")
    requires_subscription: Optional[bool] = Field(True, description="Abonnement requis")


class VideoCourseUpdate(BaseModel):
    """Mise a jour d'un cours video (par un admin)."""
    title: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    subject: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[str] = Field(None, max_length=100)
    difficulty: Optional[str] = None
    language: Optional[str] = None
    tags: Optional[str] = None

    video_url: Optional[str] = Field(None, max_length=500)
    video_type: Optional[str] = None
    thumbnail_url: Optional[str] = None
    duration_seconds: Optional[int] = Field(None, ge=0)

    learning_path_id: Optional[str] = None
    order_index: Optional[int] = None

    is_free: Optional[bool] = None
    is_published: Optional[bool] = None
    requires_subscription: Optional[bool] = None


class VideoProgressUpdate(BaseModel):
    """Mise a jour de la progression de lecture."""
    watched_seconds: int = Field(..., ge=0, description="Position actuelle en secondes")


# ══════════════════════════════════════════════════
#  REPONSES (Output)
# ══════════════════════════════════════════════════

class VideoCourseResponse(BaseModel):
    """Reponse complete d'un cours video."""
    id: UUID
    title: str
    description: Optional[str]
    subject: str
    category: Optional[str]
    difficulty: str
    language: str
    tags: Optional[str]

    video_url: str
    video_type: str
    thumbnail_url: Optional[str]
    duration_seconds: int

    learning_path_id: Optional[str]
    order_index: int

    is_free: bool
    is_published: bool
    requires_subscription: bool

    views_count: int
    likes_count: int

    created_by: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class VideoCourseListResponse(BaseModel):
    """Version resumee pour les listes."""
    id: UUID
    title: str
    subject: str
    category: Optional[str]
    difficulty: str
    video_type: str
    thumbnail_url: Optional[str]
    duration_seconds: int
    is_free: bool
    views_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class VideoProgressResponse(BaseModel):
    """Reponse de la progression sur une video."""
    id: UUID
    user_id: UUID
    video_id: UUID
    watched_seconds: int
    progress_percent: float
    is_completed: bool
    watch_count: int
    xp_earned: int
    last_watched_at: datetime
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class VideoWithProgressResponse(BaseModel):
    """Video avec la progression de l'utilisateur courant."""
    video: VideoCourseResponse
    progress: Optional[VideoProgressResponse] = None


class VideoCatalogResponse(BaseModel):
    """Catalogue de videos avec pagination."""
    videos: List[VideoCourseListResponse]
    total: int
    page: int
    per_page: int
    total_pages: int


class VideoStatsResponse(BaseModel):
    """Statistiques globales des videos (admin)."""
    total_videos: int
    published_videos: int
    free_videos: int
    total_views: int
    total_watch_time_hours: float
    completions: int
    subjects: List[dict]
