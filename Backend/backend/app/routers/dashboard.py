from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.user import User
from app.models.learning_path import LearningPath
from app.models.session import LearningSession
from app.models.compensation import EcoCompensation
from app.models.achievement import UserAchievement
from app.schemas.carbon import DashboardData, CarbonSummary, CompensationResponse
from app.services.carbon_service import get_user_carbon_summary
from app.services.cache_service import cache_get_user_dashboard, cache_set_user_dashboard
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["Tableau de Bord"])


@router.get("/", response_model=DashboardData)
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Tableau de bord interactif :
    - Progression pedagogique
    - Gamification (XP, streak, badges)
    - Impact carbone
    - Actions ecologiques

    Les donnees sont mises en cache Redis pendant 3 minutes.
    """
    user_id = current_user.id

    # Verifier le cache Redis
    cached = cache_get_user_dashboard(user_id)
    if cached:
        return DashboardData(**cached)

    # Pedagogical stats
    total_paths = db.query(LearningPath).filter(LearningPath.user_id == user_id).count()
    active_paths = db.query(LearningPath).filter(LearningPath.user_id == user_id, LearningPath.status == "en_cours").count()
    completed_paths = db.query(LearningPath).filter(LearningPath.user_id == user_id, LearningPath.status == "termine").count()

    total_sessions = db.query(LearningSession).filter(LearningSession.user_id == user_id).count()
    completed_sessions = db.query(LearningSession).filter(LearningSession.user_id == user_id, LearningSession.status == "terminee").count()

    avg_score = db.query(func.avg(LearningSession.score)).filter(
        LearningSession.user_id == user_id,
        LearningSession.score.isnot(None),
    ).scalar()

    total_minutes = db.query(func.coalesce(func.sum(LearningSession.duration_minutes), 0)).filter(
        LearningSession.user_id == user_id,
    ).scalar()

    # Carbon summary
    carbon_summary = get_user_carbon_summary(db, user_id)

    # Compensations
    compensations = (
        db.query(EcoCompensation)
        .filter(EcoCompensation.user_id == user_id)
        .order_by(EcoCompensation.created_at.desc())
        .limit(10)
        .all()
    )

    # Achievements count
    achievements_unlocked = db.query(UserAchievement).filter(UserAchievement.user_id == user_id).count()

    result = DashboardData(
        total_learning_paths=total_paths,
        active_learning_paths=active_paths,
        completed_learning_paths=completed_paths,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        average_score=round(float(avg_score), 2) if avg_score else None,
        total_learning_hours=round(float(total_minutes) / 60, 2),
        # Gamification
        total_xp=current_user.total_xp,
        level=current_user.level,
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        achievements_unlocked=achievements_unlocked,
        # Carbon & Eco
        carbon_summary=CarbonSummary(**carbon_summary),
        compensations=[CompensationResponse.model_validate(c) for c in compensations],
    )

    # Mettre en cache Redis (3 minutes)
    cache_set_user_dashboard(user_id, result.model_dump())

    return result
