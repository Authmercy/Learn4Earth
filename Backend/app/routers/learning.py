from typing import List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import httpx
from app.database import get_db
from app.config import settings
from app.models.user import User
from app.models.learning_path import LearningPath
from app.models.session import LearningSession
from app.schemas.learning import (
    LearningPathCreate,
    LearningPathResponse,
    SessionCreate,
    SessionComplete,
    SessionResponse,
)
from app.services.carbon_service import create_carbon_record, check_and_trigger_compensation
from app.services.progression_service import (
    award_session_xp,
    award_path_completion_xp,
    auto_update_level,
    update_streak,
    check_and_unlock_achievements,
    update_total_learning_minutes,
)
from app.utils.security import get_current_user, require_active_subscription

router = APIRouter(prefix="/api/learning", tags=["Apprentissage"])


# ── Learning Paths ─────────────────────────────────────

@router.post("/paths", response_model=LearningPathResponse, status_code=201)
def create_learning_path(
    path_data: LearningPathCreate,
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db),
):
    """
    Creer un nouveau parcours d'apprentissage.
    Necessite un abonnement actif.
    """
    path = LearningPath(
        user_id=current_user.id,
        title=path_data.title,
        subject=path_data.subject,
        description=path_data.description,
        difficulty=path_data.difficulty or current_user.level,
        total_sessions=path_data.total_sessions or 5,
    )
    db.add(path)
    db.commit()
    db.refresh(path)
    return path


@router.get("/paths", response_model=List[LearningPathResponse])
def get_my_learning_paths(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister mes parcours d'apprentissage."""
    return (
        db.query(LearningPath)
        .filter(LearningPath.user_id == current_user.id)
        .order_by(LearningPath.created_at.desc())
        .all()
    )


@router.get("/paths/{path_id}", response_model=LearningPathResponse)
def get_learning_path(
    path_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Recuperer un parcours specifique."""
    path = (
        db.query(LearningPath)
        .filter(LearningPath.id == path_id, LearningPath.user_id == current_user.id)
        .first()
    )
    if not path:
        raise HTTPException(status_code=404, detail="Parcours introuvable.")
    return path


# ── Sessions ───────────────────────────────────────────

@router.post("/sessions", response_model=SessionResponse, status_code=201)
async def start_session(
    session_data: SessionCreate,
    current_user: User = Depends(require_active_subscription),
    db: Session = Depends(get_db),
):
    """
    Demarrer une nouvelle session d'apprentissage.
    Genere le contenu pedagogique via l'API Flask + OpenAI GPT.
    Necessite un abonnement actif.
    """
    # Verify learning path exists (str() pour compatibilite UUID/String(36))
    path = (
        db.query(LearningPath)
        .filter(LearningPath.id == str(session_data.learning_path_id), LearningPath.user_id == current_user.id)
        .first()
    )
    if not path:
        raise HTTPException(status_code=404, detail="Parcours introuvable.")

    # Determine session number
    existing_sessions = (
        db.query(LearningSession)
        .filter(LearningSession.learning_path_id == path.id)
        .count()
    )
    session_number = existing_sessions + 1

    # Call AI service to generate content
    ai_content = None
    ai_prompt = None
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{settings.AI_SERVICE_URL}/generate",
                json={
                    "user_level": current_user.level,
                    "objectives": current_user.objectives or "",
                    "preferences": current_user.preferences or "",
                    "subject": path.subject,
                    "session_title": session_data.title,
                    "session_number": session_number,
                    "total_sessions": path.total_sessions,
                    "difficulty": path.difficulty,
                },
            )
            if response.status_code == 200:
                ai_result = response.json()
                ai_content = ai_result.get("content", "")
                ai_prompt = ai_result.get("prompt_used", "")
    except Exception:
        ai_content = f"[Contenu par defaut] Session {session_number}: {session_data.title} - Sujet: {path.subject}"

    # Create session
    session = LearningSession(
        user_id=current_user.id,
        learning_path_id=path.id,
        title=session_data.title,
        content=ai_content,
        ai_prompt_used=ai_prompt,
        session_number=session_number,
        status="en_cours",
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.put("/sessions/{session_id}/complete", response_model=dict)
def complete_session(
    session_id: str,
    complete_data: SessionComplete,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Terminer une session.
    Declenche : calcul carbone, XP, streak, montee de niveau, badges, compensation eco.
    """
    session = (
        db.query(LearningSession)
        .filter(LearningSession.id == session_id, LearningSession.user_id == current_user.id)
        .first()
    )
    if not session:
        raise HTTPException(status_code=404, detail="Session introuvable.")

    if session.status == "terminee":
        raise HTTPException(status_code=400, detail="Cette session est deja terminee.")

    # ── 1. Mettre a jour la session ──
    session.status = "terminee"
    session.completed_at = datetime.utcnow()
    if complete_data.score is not None:
        session.score = complete_data.score
    if complete_data.duration_minutes is not None:
        session.duration_minutes = complete_data.duration_minutes
    else:
        delta = datetime.utcnow() - session.started_at
        session.duration_minutes = round(delta.total_seconds() / 60, 2)

    db.flush()

    # ── 2. Empreinte carbone ──
    carbon = create_carbon_record(
        db=db,
        user_id=current_user.id,
        session_id=session.id,
        duration_minutes=session.duration_minutes,
    )

    # ── 3. Progression : XP ──
    xp_earned = award_session_xp(db, current_user, score=session.score)

    # ── 4. Progression : Streak ──
    streak_info = update_streak(db, current_user)

    # ── 5. Progression : Temps cumule ──
    update_total_learning_minutes(db, current_user, session.duration_minutes)

    # ── 6. Mise a jour du parcours ──
    path = db.query(LearningPath).filter(LearningPath.id == session.learning_path_id).first()
    path_completed = False
    if path:
        completed = (
            db.query(LearningSession)
            .filter(
                LearningSession.learning_path_id == path.id,
                LearningSession.status == "terminee",
            )
            .count()
        )
        path.completed_sessions = completed
        path.progress_percent = round((completed / path.total_sessions) * 100, 2) if path.total_sessions > 0 else 0
        if path.progress_percent >= 100 and path.status != "termine":
            path.status = "termine"
            path_completed = True
            xp_earned += award_path_completion_xp(db, current_user)

    db.flush()

    # ── 7. Montee de niveau automatique ──
    level_up = auto_update_level(db, current_user)

    # ── 8. Verification des badges ──
    new_badges = check_and_unlock_achievements(db, current_user)

    # ── 9. Compensation ecologique ──
    compensation = check_and_trigger_compensation(db, current_user.id)

    # ── 10. Commit final ──
    db.commit()
    db.refresh(current_user)

    # ── Construire la reponse ──
    result = {
        "message": "Session terminee avec succes !",
        "session": SessionResponse.model_validate(session),
        "carbon_footprint": {
            "energy_kwh": carbon.energy_kwh,
            "carbon_kg": carbon.carbon_kg,
            "server_region": carbon.server_region,
        },
        "progression": {
            "xp_earned": xp_earned,
            "total_xp": current_user.total_xp,
            "level": current_user.level,
            "level_up": level_up,
            "streak": streak_info["new_streak"],
            "streak_continued": streak_info["streak_continued"],
            "new_badges": [
                {"name": b.name, "description": b.description, "icon": b.icon, "xp_reward": b.xp_reward}
                for b in new_badges
            ],
        },
    }

    if path_completed:
        result["progression"]["path_completed"] = {
            "title": path.title,
            "message": f"Felicitations ! Vous avez termine le parcours '{path.title}' !",
        }

    if compensation:
        result["eco_compensation"] = {
            "trees_planted": compensation.trees_planted,
            "co2_compensated_kg": compensation.co2_compensated_kg,
            "message": f"Bravo ! {compensation.trees_planted} arbre(s) plante(s) pour compenser {compensation.co2_compensated_kg:.2f} kg de CO2.",
        }

    return result


@router.get("/sessions", response_model=List[SessionResponse])
def get_my_sessions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister mes sessions d'apprentissage."""
    return (
        db.query(LearningSession)
        .filter(LearningSession.user_id == current_user.id)
        .order_by(LearningSession.created_at.desc())
        .all()
    )
