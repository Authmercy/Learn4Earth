"""
Router pour la gestion des cours video.

Endpoints publics (utilisateurs authentifies) :
- Catalogue de videos (filtrage, pagination, recherche)
- Detail d'une video
- Suivi de progression (resume la lecture)
- Marquer une video comme terminee

Endpoints admin :
- CRUD complet des videos
- Upload de fichier video
- Statistiques globales
"""

import os
import uuid
import math
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.video import VideoCourse, VideoProgress
from app.schemas.video import (
    VideoCourseCreate,
    VideoCourseUpdate,
    VideoCourseResponse,
    VideoCourseListResponse,
    VideoProgressUpdate,
    VideoProgressResponse,
    VideoWithProgressResponse,
    VideoCatalogResponse,
    VideoStatsResponse,
)
from app.utils.security import get_current_user, get_current_admin

router = APIRouter(prefix="/api/videos", tags=["Cours Video"])

# ── Repertoire de stockage des videos uploadees ──
UPLOAD_DIR = "/app/uploads/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ── Tailles et formats autorises ──
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500 Mo
ALLOWED_EXTENSIONS = {".mp4", ".webm", ".mkv", ".avi", ".mov"}
ALLOWED_THUMB_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

# ── XP recompense pour completion d'une video ──
VIDEO_COMPLETION_XP = 15


# ══════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════

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


def _check_video_access(db: Session, user: User, video: VideoCourse) -> bool:
    """Verifie si l'utilisateur a acces a la video."""
    # Admin a toujours acces
    if user.role in ("admin", "super_admin"):
        return True
    # Video gratuite
    if video.is_free:
        return True
    # Video ne requiert pas d'abonnement
    if not video.requires_subscription:
        return True
    # Verifier l'abonnement
    return _user_has_active_subscription(db, user.id)


# ══════════════════════════════════════════════════
#  ENDPOINTS UTILISATEURS - CATALOGUE
# ══════════════════════════════════════════════════

@router.get("/catalog", response_model=VideoCatalogResponse)
def get_video_catalog(
    page: int = Query(1, ge=1, description="Numero de page"),
    per_page: int = Query(12, ge=1, le=50, description="Videos par page"),
    subject: Optional[str] = Query(None, description="Filtrer par sujet"),
    category: Optional[str] = Query(None, description="Filtrer par categorie"),
    difficulty: Optional[str] = Query(None, description="Filtrer par difficulte"),
    search: Optional[str] = Query(None, description="Rechercher dans titre/description"),
    is_free: Optional[bool] = Query(None, description="Filtrer les videos gratuites"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Catalogue de videos avec filtrage et pagination.
    Affiche uniquement les videos publiees.
    """
    query = db.query(VideoCourse).filter(VideoCourse.is_published == True)

    # Filtres
    if subject:
        query = query.filter(VideoCourse.subject.ilike(f"%{subject}%"))
    if category:
        query = query.filter(VideoCourse.category.ilike(f"%{category}%"))
    if difficulty:
        query = query.filter(VideoCourse.difficulty == difficulty)
    if is_free is not None:
        query = query.filter(VideoCourse.is_free == is_free)
    if search:
        query = query.filter(
            or_(
                VideoCourse.title.ilike(f"%{search}%"),
                VideoCourse.description.ilike(f"%{search}%"),
                VideoCourse.tags.ilike(f"%{search}%"),
            )
        )

    # Comptage total
    total = query.count()
    total_pages = math.ceil(total / per_page) if total > 0 else 1

    # Pagination
    videos = (
        query
        .order_by(VideoCourse.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return VideoCatalogResponse(
        videos=[VideoCourseListResponse.model_validate(v) for v in videos],
        total=total,
        page=page,
        per_page=per_page,
        total_pages=total_pages,
    )


@router.get("/subjects", response_model=List[dict])
def get_video_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste des sujets disponibles avec le nombre de videos."""
    results = (
        db.query(
            VideoCourse.subject,
            func.count(VideoCourse.id).label("count"),
        )
        .filter(VideoCourse.is_published == True)
        .group_by(VideoCourse.subject)
        .order_by(func.count(VideoCourse.id).desc())
        .all()
    )
    return [{"subject": s, "count": c} for s, c in results]


@router.get("/categories", response_model=List[dict])
def get_video_categories(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Liste des categories disponibles avec le nombre de videos."""
    results = (
        db.query(
            VideoCourse.category,
            func.count(VideoCourse.id).label("count"),
        )
        .filter(VideoCourse.is_published == True, VideoCourse.category.isnot(None))
        .group_by(VideoCourse.category)
        .order_by(func.count(VideoCourse.id).desc())
        .all()
    )
    return [{"category": c, "count": n} for c, n in results]


# ══════════════════════════════════════════════════
#  ENDPOINTS UTILISATEURS - VIDEO INDIVIDUELLE
# ══════════════════════════════════════════════════

@router.get("/{video_id}", response_model=VideoWithProgressResponse)
def get_video_detail(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Detail d'une video avec la progression de l'utilisateur.
    Verifie l'acces (abonnement) si la video n'est pas gratuite.
    """
    video = db.query(VideoCourse).filter(VideoCourse.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video introuvable.")

    if not video.is_published and current_user.role not in ("admin", "super_admin"):
        raise HTTPException(status_code=404, detail="Video introuvable.")

    # Verifier l'acces
    if not _check_video_access(db, current_user, video):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Abonnement requis pour acceder a cette video. "
                   "Consultez GET /api/subscriptions/plans pour decouvrir nos offres.",
        )

    # Incrementer les vues
    video.views_count += 1
    db.flush()

    # Recuperer ou creer la progression
    progress = (
        db.query(VideoProgress)
        .filter(VideoProgress.user_id == current_user.id, VideoProgress.video_id == video_id)
        .first()
    )

    db.commit()

    return VideoWithProgressResponse(
        video=VideoCourseResponse.model_validate(video),
        progress=VideoProgressResponse.model_validate(progress) if progress else None,
    )


@router.put("/{video_id}/progress", response_model=VideoProgressResponse)
def update_video_progress(
    video_id: str,
    progress_data: VideoProgressUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mettre a jour la progression de lecture d'une video.
    Envoyer regulierement (ex: toutes les 10s) pour sauvegarder la position.
    Attribue des XP quand la video est terminee (>= 90%).
    """
    video = db.query(VideoCourse).filter(VideoCourse.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video introuvable.")

    # Verifier l'acces
    if not _check_video_access(db, current_user, video):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Abonnement requis pour acceder a cette video.",
        )

    # Recuperer ou creer la progression
    progress = (
        db.query(VideoProgress)
        .filter(VideoProgress.user_id == current_user.id, VideoProgress.video_id == video_id)
        .first()
    )

    was_completed = False
    if not progress:
        progress = VideoProgress(
            user_id=current_user.id,
            video_id=video_id,
            watched_seconds=0,
            watch_count=1,
        )
        db.add(progress)
    else:
        was_completed = progress.is_completed

    # Mettre a jour la position (ne recule jamais sauf si rewatch)
    progress.watched_seconds = max(progress.watched_seconds, progress_data.watched_seconds)
    progress.last_watched_at = datetime.utcnow()

    # Calculer le pourcentage
    if video.duration_seconds > 0:
        progress.progress_percent = min(
            round((progress.watched_seconds / video.duration_seconds) * 100, 2),
            100.0,
        )
    else:
        progress.progress_percent = 100.0

    # Verifier si la video est terminee (>= 90%)
    if not was_completed and progress.progress_percent >= 90:
        progress.is_completed = True
        progress.completed_at = datetime.utcnow()

        # Attribuer les XP
        progress.xp_earned = VIDEO_COMPLETION_XP
        current_user.total_xp += VIDEO_COMPLETION_XP

    db.commit()
    db.refresh(progress)

    return VideoProgressResponse.model_validate(progress)


@router.get("/{video_id}/progress", response_model=VideoProgressResponse)
def get_video_progress(
    video_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recuperer la progression sur une video specifique."""
    progress = (
        db.query(VideoProgress)
        .filter(VideoProgress.user_id == current_user.id, VideoProgress.video_id == video_id)
        .first()
    )
    if not progress:
        raise HTTPException(status_code=404, detail="Aucune progression trouvee pour cette video.")
    return VideoProgressResponse.model_validate(progress)


@router.get("/me/history", response_model=List[VideoWithProgressResponse])
def get_my_video_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Historique des videos regardees par l'utilisateur.
    Retourne les videos avec leur progression, triees par derniere activite.
    """
    progress_records = (
        db.query(VideoProgress)
        .filter(VideoProgress.user_id == current_user.id)
        .order_by(VideoProgress.last_watched_at.desc())
        .all()
    )

    result = []
    for prog in progress_records:
        video = db.query(VideoCourse).filter(VideoCourse.id == prog.video_id).first()
        if video:
            result.append(VideoWithProgressResponse(
                video=VideoCourseResponse.model_validate(video),
                progress=VideoProgressResponse.model_validate(prog),
            ))

    return result


# ══════════════════════════════════════════════════
#  ENDPOINTS ADMIN - CRUD VIDEOS
# ══════════════════════════════════════════════════

@router.post("/admin/create", response_model=VideoCourseResponse, status_code=201)
def admin_create_video(
    video_data: VideoCourseCreate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Creer un nouveau cours video (admin uniquement).
    Supporte YouTube, Vimeo, URLs externes.
    """
    video = VideoCourse(
        title=video_data.title,
        description=video_data.description,
        subject=video_data.subject,
        category=video_data.category,
        difficulty=video_data.difficulty or "debutant",
        language=video_data.language or "fr",
        tags=video_data.tags,
        video_url=video_data.video_url,
        video_type=video_data.video_type or "youtube",
        thumbnail_url=video_data.thumbnail_url,
        duration_seconds=video_data.duration_seconds or 0,
        learning_path_id=video_data.learning_path_id,
        order_index=video_data.order_index or 0,
        is_free=video_data.is_free or False,
        is_published=video_data.is_published or False,
        requires_subscription=video_data.requires_subscription if video_data.requires_subscription is not None else (not video_data.is_free),
        created_by=current_user.id,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return VideoCourseResponse.model_validate(video)


@router.post("/admin/upload", response_model=VideoCourseResponse, status_code=201)
async def admin_upload_video(
    title: str = Query(..., description="Titre de la video"),
    subject: str = Query(..., description="Sujet de la video"),
    description: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    difficulty: str = Query("debutant"),
    is_free: bool = Query(False),
    is_published: bool = Query(False),
    file: UploadFile = File(..., description="Fichier video (mp4, webm, mkv, avi, mov)"),
    thumbnail: Optional[UploadFile] = File(None, description="Vignette (jpg, png, webp)"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Uploader un fichier video directement sur le serveur (admin uniquement).
    Taille max : 500 Mo. Formats : mp4, webm, mkv, avi, mov.
    """
    # Verifier l'extension
    _, ext = os.path.splitext(file.filename or "")
    if ext.lower() not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Format non supporte. Formats autorises : {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # Lire et verifier la taille
    contents = await file.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"Fichier trop volumineux. Taille max : {MAX_FILE_SIZE // (1024 * 1024)} Mo.",
        )

    # Sauvegarder le fichier
    file_id = str(uuid.uuid4())
    filename = f"{file_id}{ext.lower()}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    video_url = f"/api/videos/stream/{filename}"

    # Sauvegarder la vignette si fournie
    thumbnail_url = None
    if thumbnail and thumbnail.filename:
        _, thumb_ext = os.path.splitext(thumbnail.filename)
        if thumb_ext.lower() in ALLOWED_THUMB_EXTENSIONS:
            thumb_filename = f"{file_id}_thumb{thumb_ext.lower()}"
            thumb_path = os.path.join(UPLOAD_DIR, thumb_filename)
            thumb_contents = await thumbnail.read()
            with open(thumb_path, "wb") as f:
                f.write(thumb_contents)
            thumbnail_url = f"/api/videos/stream/{thumb_filename}"

    # Creer l'entree en base
    video = VideoCourse(
        title=title,
        description=description,
        subject=subject,
        category=category,
        difficulty=difficulty,
        video_url=video_url,
        video_type="upload",
        thumbnail_url=thumbnail_url,
        is_free=is_free,
        is_published=is_published,
        requires_subscription=not is_free,
        created_by=current_user.id,
    )
    db.add(video)
    db.commit()
    db.refresh(video)
    return VideoCourseResponse.model_validate(video)


@router.get("/stream/{filename}")
def stream_video(filename: str):
    """
    Servir un fichier video ou une vignette uploadee.
    En production, utiliser Nginx pour servir les fichiers statiques.
    """
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Fichier introuvable.")
    return FileResponse(filepath)


@router.put("/admin/{video_id}", response_model=VideoCourseResponse)
def admin_update_video(
    video_id: str,
    update_data: VideoCourseUpdate,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Modifier un cours video existant (admin uniquement)."""
    video = db.query(VideoCourse).filter(VideoCourse.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video introuvable.")

    # Mettre a jour les champs fournis
    update_fields = update_data.model_dump(exclude_unset=True)
    for field, value in update_fields.items():
        if value is not None:
            setattr(video, field, value)

    video.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(video)
    return VideoCourseResponse.model_validate(video)


@router.delete("/admin/{video_id}")
def admin_delete_video(
    video_id: str,
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Supprimer un cours video et toutes les progressions associees (admin uniquement).
    Si la video est un upload, le fichier est egalement supprime du serveur.
    """
    video = db.query(VideoCourse).filter(VideoCourse.id == video_id).first()
    if not video:
        raise HTTPException(status_code=404, detail="Video introuvable.")

    # Supprimer le fichier physique si c'est un upload
    if video.video_type == "upload" and video.video_url:
        filename = video.video_url.split("/")[-1]
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(filepath):
            os.remove(filepath)
        # Supprimer aussi la vignette
        if video.thumbnail_url:
            thumb_filename = video.thumbnail_url.split("/")[-1]
            thumb_path = os.path.join(UPLOAD_DIR, thumb_filename)
            if os.path.exists(thumb_path):
                os.remove(thumb_path)

    db.delete(video)
    db.commit()
    return {"message": f"Video '{video.title}' supprimee avec succes.", "video_id": video_id}


@router.get("/admin/list", response_model=List[VideoCourseResponse])
def admin_list_all_videos(
    include_unpublished: bool = Query(True, description="Inclure les videos non publiees"),
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Lister toutes les videos (admin uniquement, inclut les non publiees)."""
    query = db.query(VideoCourse)
    if not include_unpublished:
        query = query.filter(VideoCourse.is_published == True)
    return query.order_by(VideoCourse.created_at.desc()).all()


@router.get("/admin/stats", response_model=VideoStatsResponse)
def admin_video_stats(
    current_user: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Statistiques globales des videos (admin uniquement)."""
    total = db.query(func.count(VideoCourse.id)).scalar() or 0
    published = db.query(func.count(VideoCourse.id)).filter(VideoCourse.is_published == True).scalar() or 0
    free = db.query(func.count(VideoCourse.id)).filter(VideoCourse.is_free == True).scalar() or 0
    total_views = db.query(func.sum(VideoCourse.views_count)).scalar() or 0

    # Temps total regarde (en heures)
    total_watched = db.query(func.sum(VideoProgress.watched_seconds)).scalar() or 0
    total_watch_hours = round(total_watched / 3600, 2)

    # Completions
    completions = (
        db.query(func.count(VideoProgress.id))
        .filter(VideoProgress.is_completed == True)
        .scalar() or 0
    )

    # Sujets populaires
    subjects = (
        db.query(
            VideoCourse.subject,
            func.count(VideoCourse.id).label("count"),
            func.sum(VideoCourse.views_count).label("views"),
        )
        .group_by(VideoCourse.subject)
        .order_by(func.sum(VideoCourse.views_count).desc())
        .limit(10)
        .all()
    )

    return VideoStatsResponse(
        total_videos=total,
        published_videos=published,
        free_videos=free,
        total_views=total_views,
        total_watch_time_hours=total_watch_hours,
        completions=completions,
        subjects=[
            {"subject": s, "count": c, "views": v or 0}
            for s, c, v in subjects
        ],
    )
