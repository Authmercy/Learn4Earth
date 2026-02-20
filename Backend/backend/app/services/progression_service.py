"""
Service de gestion de la progression utilisateur.

Responsabilites :
- Calcul et attribution de l'XP
- Gestion du streak (serie de jours consecutifs)
- Montee de niveau automatique
- Verification et deblocage des badges
- Statistiques de progression detaillees
"""

from datetime import date, timedelta
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.models.learning_path import LearningPath
from app.models.session import LearningSession
from app.models.achievement import Achievement, UserAchievement
from app.models.compensation import EcoCompensation


# ── Configuration XP ───────────────────────────────────

XP_PER_SESSION_COMPLETED = 50
XP_PER_PERFECT_SCORE = 30       # bonus si score >= 90
XP_PER_PATH_COMPLETED = 200
XP_STREAK_BONUS_MULTIPLIER = 5  # +5 XP par jour de streak actif

LEVEL_THRESHOLDS = {
    "debutant": 0,
    "intermediaire": 500,
    "avance": 2000,
    "expert": 5000,
}


# ── Catalogue de badges par defaut ─────────────────────

DEFAULT_ACHIEVEMENTS = [
    # Pedagogie
    {"code": "first_session", "name": "Premier pas", "description": "Terminer sa premiere session d'apprentissage", "icon": "book", "category": "pedagogie", "xp_reward": 20, "condition_type": "sessions_completed", "condition_value": 1},
    {"code": "10_sessions", "name": "Apprenant assidu", "description": "Terminer 10 sessions d'apprentissage", "icon": "book", "category": "pedagogie", "xp_reward": 100, "condition_type": "sessions_completed", "condition_value": 10},
    {"code": "50_sessions", "name": "Scholar", "description": "Terminer 50 sessions d'apprentissage", "icon": "trophy", "category": "pedagogie", "xp_reward": 500, "condition_type": "sessions_completed", "condition_value": 50},
    {"code": "first_path", "name": "Parcours accompli", "description": "Terminer un parcours d'apprentissage complet", "icon": "flag", "category": "pedagogie", "xp_reward": 100, "condition_type": "paths_completed", "condition_value": 1},
    {"code": "5_paths", "name": "Explorateur", "description": "Terminer 5 parcours d'apprentissage", "icon": "compass", "category": "pedagogie", "xp_reward": 300, "condition_type": "paths_completed", "condition_value": 5},
    {"code": "high_scorer", "name": "Excellent eleve", "description": "Obtenir un score moyen superieur a 85", "icon": "star", "category": "performance", "xp_reward": 150, "condition_type": "score_avg", "condition_value": 85},
    {"code": "perfect_score", "name": "Perfection", "description": "Obtenir un score de 100 sur une session", "icon": "zap", "category": "performance", "xp_reward": 50, "condition_type": "best_score", "condition_value": 100},

    # Engagement
    {"code": "streak_7", "name": "Semaine productive", "description": "Maintenir une serie de 7 jours consecutifs", "icon": "fire", "category": "engagement", "xp_reward": 100, "condition_type": "streak_days", "condition_value": 7},
    {"code": "streak_30", "name": "Mois d'excellence", "description": "Maintenir une serie de 30 jours consecutifs", "icon": "fire", "category": "engagement", "xp_reward": 500, "condition_type": "streak_days", "condition_value": 30},
    {"code": "10_hours", "name": "10 heures de savoir", "description": "Cumuler 10 heures d'apprentissage", "icon": "clock", "category": "engagement", "xp_reward": 100, "condition_type": "learning_hours", "condition_value": 10},
    {"code": "50_hours", "name": "Marathonien", "description": "Cumuler 50 heures d'apprentissage", "icon": "clock", "category": "engagement", "xp_reward": 400, "condition_type": "learning_hours", "condition_value": 50},

    # Ecologie
    {"code": "first_tree", "name": "Planteur", "description": "Planter son premier arbre via la compensation carbone", "icon": "tree", "category": "ecologie", "xp_reward": 50, "condition_type": "trees_planted", "condition_value": 1},
    {"code": "10_trees", "name": "Eco-champion", "description": "Avoir contribue a la plantation de 10 arbres", "icon": "tree", "category": "ecologie", "xp_reward": 300, "condition_type": "trees_planted", "condition_value": 10},

    # XP
    {"code": "xp_500", "name": "Intermediaire", "description": "Atteindre 500 XP", "icon": "award", "category": "progression", "xp_reward": 0, "condition_type": "xp_total", "condition_value": 500},
    {"code": "xp_2000", "name": "Avance", "description": "Atteindre 2000 XP", "icon": "award", "category": "progression", "xp_reward": 0, "condition_type": "xp_total", "condition_value": 2000},
    {"code": "xp_5000", "name": "Expert", "description": "Atteindre 5000 XP", "icon": "award", "category": "progression", "xp_reward": 0, "condition_type": "xp_total", "condition_value": 5000},
]


def seed_achievements(db: Session) -> None:
    """Inserer les badges par defaut s'ils n'existent pas encore."""
    existing = {a.code for a in db.query(Achievement.code).all()}
    for ach_data in DEFAULT_ACHIEVEMENTS:
        if ach_data["code"] not in existing:
            db.add(Achievement(**ach_data))
    db.commit()


# ── XP ─────────────────────────────────────────────────

def award_session_xp(db: Session, user: User, score: Optional[float] = None) -> int:
    """Attribuer de l'XP apres une session terminee."""
    xp_earned = XP_PER_SESSION_COMPLETED

    # Bonus streak
    if user.current_streak > 0:
        xp_earned += user.current_streak * XP_STREAK_BONUS_MULTIPLIER

    # Bonus score parfait
    if score is not None and score >= 90:
        xp_earned += XP_PER_PERFECT_SCORE

    user.total_xp += xp_earned
    db.flush()
    return xp_earned


def award_path_completion_xp(db: Session, user: User) -> int:
    """Attribuer de l'XP apres un parcours termine."""
    xp_earned = XP_PER_PATH_COMPLETED
    user.total_xp += xp_earned
    db.flush()
    return xp_earned


# ── Niveau automatique ─────────────────────────────────

def auto_update_level(db: Session, user: User) -> Optional[str]:
    """
    Met a jour le niveau de l'utilisateur en fonction de son XP.
    Retourne le nouveau niveau si changement, None sinon.
    """
    old_level = user.level

    # Determiner le niveau en fonction de l'XP
    new_level = "debutant"
    for level_name, threshold in sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1], reverse=True):
        if user.total_xp >= threshold:
            new_level = level_name
            break

    if new_level != old_level:
        user.level = new_level
        db.flush()
        return new_level
    return None


# ── Streak ─────────────────────────────────────────────

def update_streak(db: Session, user: User) -> dict:
    """
    Met a jour le streak (serie de jours consecutifs) de l'utilisateur.
    Appelee a chaque session terminee.
    """
    today = date.today()
    result = {"streak_continued": False, "streak_broken": False, "new_streak": user.current_streak}

    if user.last_activity_date is None:
        # Premiere activite
        user.current_streak = 1
        user.longest_streak = 1
        result["streak_continued"] = True
    elif user.last_activity_date == today:
        # Deja actif aujourd'hui, pas de changement
        pass
    elif user.last_activity_date == today - timedelta(days=1):
        # Jour consecutif -> increment
        user.current_streak += 1
        if user.current_streak > user.longest_streak:
            user.longest_streak = user.current_streak
        result["streak_continued"] = True
    else:
        # Serie brisee -> reset
        result["streak_broken"] = True
        user.current_streak = 1

    user.last_activity_date = today
    result["new_streak"] = user.current_streak
    db.flush()
    return result


# ── Badges / Achievements ─────────────────────────────

def check_and_unlock_achievements(db: Session, user: User) -> list:
    """
    Verifie tous les badges et debloque ceux dont les conditions sont remplies.
    Retourne la liste des nouveaux badges debloques.
    """
    # Badges deja obtenus
    unlocked_ids = {
        ua.achievement_id
        for ua in db.query(UserAchievement.achievement_id).filter(UserAchievement.user_id == user.id).all()
    }

    # Tous les badges disponibles
    all_achievements = db.query(Achievement).all()

    # Calculer les metriques actuelles de l'utilisateur
    metrics = _compute_user_metrics(db, user)

    newly_unlocked = []
    for ach in all_achievements:
        if ach.id in unlocked_ids:
            continue

        if _condition_met(ach, metrics):
            ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
            db.add(ua)

            # Attribuer l'XP du badge
            if ach.xp_reward > 0:
                user.total_xp += ach.xp_reward

            newly_unlocked.append(ach)

    if newly_unlocked:
        db.flush()

    return newly_unlocked


def _compute_user_metrics(db: Session, user: User) -> dict:
    """Calculer toutes les metriques necessaires pour evaluer les badges."""
    user_id = user.id

    completed_sessions = db.query(LearningSession).filter(
        LearningSession.user_id == user_id,
        LearningSession.status == "terminee",
    ).count()

    completed_paths = db.query(LearningPath).filter(
        LearningPath.user_id == user_id,
        LearningPath.status == "termine",
    ).count()

    avg_score = db.query(func.avg(LearningSession.score)).filter(
        LearningSession.user_id == user_id,
        LearningSession.score.isnot(None),
    ).scalar()

    best_score = db.query(func.max(LearningSession.score)).filter(
        LearningSession.user_id == user_id,
        LearningSession.score.isnot(None),
    ).scalar()

    total_minutes = db.query(func.coalesce(func.sum(LearningSession.duration_minutes), 0)).filter(
        LearningSession.user_id == user_id,
    ).scalar()

    total_trees = db.query(func.coalesce(func.sum(EcoCompensation.trees_planted), 0)).filter(
        EcoCompensation.user_id == user_id,
    ).scalar()

    return {
        "sessions_completed": completed_sessions,
        "paths_completed": completed_paths,
        "score_avg": float(avg_score) if avg_score else 0,
        "best_score": float(best_score) if best_score else 0,
        "learning_hours": float(total_minutes) / 60,
        "trees_planted": int(total_trees),
        "streak_days": user.current_streak,
        "xp_total": user.total_xp,
    }


def _condition_met(achievement: Achievement, metrics: dict) -> bool:
    """Verifier si la condition d'un badge est remplie."""
    metric_value = metrics.get(achievement.condition_type, 0)
    return metric_value >= achievement.condition_value


# ── Statistiques de progression ────────────────────────

def get_user_progression(db: Session, user: User) -> dict:
    """
    Retourne un resume complet de la progression de l'utilisateur :
    - Stats pedagogiques (parcours, sessions, scores, temps)
    - XP et niveau
    - Streak
    - Badges
    """
    user_id = user.id
    metrics = _compute_user_metrics(db, user)

    # Detail par parcours
    paths = (
        db.query(LearningPath)
        .filter(LearningPath.user_id == user_id)
        .order_by(LearningPath.created_at.desc())
        .all()
    )

    path_details = []
    for p in paths:
        path_avg_score = db.query(func.avg(LearningSession.score)).filter(
            LearningSession.learning_path_id == p.id,
            LearningSession.score.isnot(None),
        ).scalar()

        path_total_minutes = db.query(func.coalesce(func.sum(LearningSession.duration_minutes), 0)).filter(
            LearningSession.learning_path_id == p.id,
        ).scalar()

        path_details.append({
            "path_id": p.id,
            "title": p.title,
            "subject": p.subject,
            "difficulty": p.difficulty,
            "total_sessions": p.total_sessions,
            "completed_sessions": p.completed_sessions,
            "progress_percent": p.progress_percent,
            "status": p.status,
            "average_score": round(float(path_avg_score), 2) if path_avg_score else None,
            "total_duration_minutes": float(path_total_minutes),
            "created_at": p.created_at,
        })

    # Badges
    all_achievements = db.query(Achievement).all()
    unlocked_ids = {
        ua.achievement_id: ua.unlocked_at
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == user_id).all()
    }

    achievements_list = []
    for ach in all_achievements:
        achievements_list.append({
            "id": ach.id,
            "code": ach.code,
            "name": ach.name,
            "description": ach.description,
            "icon": ach.icon,
            "category": ach.category,
            "xp_reward": ach.xp_reward,
            "unlocked_at": unlocked_ids.get(ach.id),
        })

    # Calcul XP vers le prochain niveau
    xp_to_next = _xp_to_next_level(user)

    # Compteurs parcours
    active_paths = sum(1 for p in paths if p.status == "en_cours")
    completed_paths_count = sum(1 for p in paths if p.status == "termine")
    abandoned_paths = sum(1 for p in paths if p.status == "abandonne")

    total_minutes = metrics["learning_hours"] * 60

    return {
        "user_id": user.id,
        "full_name": user.full_name,
        "level": user.level,
        "total_xp": user.total_xp,
        "xp_to_next_level": xp_to_next,
        "current_streak": user.current_streak,
        "longest_streak": user.longest_streak,
        "total_paths": len(paths),
        "active_paths": active_paths,
        "completed_paths": completed_paths_count,
        "abandoned_paths": abandoned_paths,
        "total_sessions": metrics["sessions_completed"] + db.query(LearningSession).filter(
            LearningSession.user_id == user_id, LearningSession.status != "terminee"
        ).count(),
        "completed_sessions": metrics["sessions_completed"],
        "average_score": round(metrics["score_avg"], 2) if metrics["score_avg"] else None,
        "best_score": metrics["best_score"] if metrics["best_score"] else None,
        "total_learning_minutes": round(total_minutes, 2),
        "total_learning_hours": round(total_minutes / 60, 2),
        "paths": path_details,
        "total_achievements_unlocked": len(unlocked_ids),
        "total_achievements_available": len(all_achievements),
        "achievements": achievements_list,
    }


def _xp_to_next_level(user: User) -> int:
    """Calculer l'XP restant pour le prochain niveau."""
    sorted_levels = sorted(LEVEL_THRESHOLDS.items(), key=lambda x: x[1])
    for i, (level_name, threshold) in enumerate(sorted_levels):
        if user.total_xp < threshold:
            return threshold - user.total_xp
    return 0  # Deja au niveau max


def update_total_learning_minutes(db: Session, user: User, session_duration: float) -> None:
    """Met a jour le cumul du temps d'apprentissage."""
    user.total_learning_minutes += session_duration
    db.flush()
