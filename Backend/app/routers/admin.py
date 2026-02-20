"""
Router d'administration.

Endpoints reserves aux administrateurs (role: admin ou super_admin) :
- CRUD des plans d'abonnement (prix mensuel, annuel, etc.)
- Gestion des utilisateurs (liste, roles, activation/desactivation)
- Dashboard admin (statistiques, revenus, KPIs)
- Gestion des paiements (liste globale)
"""

from datetime import datetime, date
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.models.subscription_plan import SubscriptionPlan
from app.models.payment import Payment
from app.models.learning_path import LearningPath
from app.models.session import LearningSession
from app.models.carbon import CarbonFootprint
from app.models.compensation import EcoCompensation
from app.schemas.admin import (
    PlanCreate,
    PlanUpdate,
    PlanResponse,
    AdminUserResponse,
    AdminUserRoleUpdate,
    AdminUsersList,
    AdminStats,
)
from app.schemas.payment import PaymentResponse
from app.utils.security import get_current_admin, get_current_super_admin
from app.services.cache_service import (
    cache_get_plans, cache_set_plans, cache_invalidate_plans,
    cache_get_admin_dashboard, cache_set_admin_dashboard, cache_invalidate_admin_dashboard,
)

router = APIRouter(prefix="/api/admin", tags=["Administration"])


# ══════════════════════════════════════════════════════════
#  PLANS D'ABONNEMENT (CRUD)
# ══════════════════════════════════════════════════════════

@router.post("/plans", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
def create_plan(
    plan_data: PlanCreate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Creer un nouveau plan d'abonnement."""
    # Verifier que le code est unique
    existing = db.query(SubscriptionPlan).filter(SubscriptionPlan.code == plan_data.code).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Un plan avec le code '{plan_data.code}' existe deja.",
        )

    plan = SubscriptionPlan(
        code=plan_data.code,
        name=plan_data.name,
        description=plan_data.description,
        price=plan_data.price,
        currency=plan_data.currency,
        duration_days=plan_data.duration_days,
        is_active=plan_data.is_active,
        features=plan_data.features,
        max_sessions_per_day=plan_data.max_sessions_per_day,
        sort_order=plan_data.sort_order,
    )
    db.add(plan)
    db.commit()
    db.refresh(plan)
    cache_invalidate_plans()  # Invalider le cache des plans
    return plan


@router.get("/plans", response_model=List[PlanResponse])
def list_plans(
    include_inactive: bool = Query(False, description="Inclure les plans desactives"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Lister tous les plans d'abonnement (actifs et inactifs)."""
    query = db.query(SubscriptionPlan)
    if not include_inactive:
        query = query.filter(SubscriptionPlan.is_active == True)
    return query.order_by(SubscriptionPlan.sort_order, SubscriptionPlan.price).all()


@router.get("/plans/{plan_id}", response_model=PlanResponse)
def get_plan(
    plan_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Recuperer un plan specifique."""
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable.")
    return plan


@router.put("/plans/{plan_id}", response_model=PlanResponse)
def update_plan(
    plan_id: str,
    plan_data: PlanUpdate,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Modifier un plan d'abonnement (prix, duree, nom, etc.)."""
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable.")

    update_dict = plan_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="Aucun champ a mettre a jour.")

    for key, value in update_dict.items():
        setattr(plan, key, value)

    db.commit()
    db.refresh(plan)
    cache_invalidate_plans()  # Invalider le cache des plans
    return plan


@router.delete("/plans/{plan_id}")
def delete_plan(
    plan_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Supprimer un plan d'abonnement.
    Si des abonnements actifs utilisent ce plan, il est desactive au lieu d'etre supprime.
    """
    plan = db.query(SubscriptionPlan).filter(SubscriptionPlan.id == plan_id).first()
    if not plan:
        raise HTTPException(status_code=404, detail="Plan introuvable.")

    # Verifier si des abonnements actifs utilisent ce plan
    active_subs = db.query(Subscription).filter(
        Subscription.plan == plan.code,
        Subscription.is_active == True,
    ).count()

    if active_subs > 0:
        # Desactiver au lieu de supprimer
        plan.is_active = False
        db.commit()
        cache_invalidate_plans()  # Invalider le cache des plans
        return {
            "message": f"Plan desactive (encore {active_subs} abonnement(s) actif(s)).",
            "action": "deactivated",
        }

    db.delete(plan)
    db.commit()
    cache_invalidate_plans()  # Invalider le cache des plans
    return {"message": "Plan supprime definitivement.", "action": "deleted"}


# ══════════════════════════════════════════════════════════
#  GESTION DES UTILISATEURS
# ══════════════════════════════════════════════════════════

@router.get("/users", response_model=AdminUsersList)
def list_users(
    page: int = Query(1, ge=1, description="Numero de page"),
    per_page: int = Query(20, ge=1, le=100, description="Resultats par page"),
    search: Optional[str] = Query(None, description="Rechercher par nom ou email"),
    role: Optional[str] = Query(None, description="Filtrer par role"),
    is_active: Optional[bool] = Query(None, description="Filtrer par statut actif"),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Lister les utilisateurs avec pagination et filtres."""
    query = db.query(User)

    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            (User.full_name.ilike(search_pattern)) |
            (User.email.ilike(search_pattern))
        )

    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = (
        query
        .order_by(User.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )

    return AdminUsersList(
        total=total,
        page=page,
        per_page=per_page,
        users=[AdminUserResponse.model_validate(u) for u in users],
    )


@router.get("/users/{user_id}", response_model=AdminUserResponse)
def get_user_detail(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Voir le detail d'un utilisateur."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    return AdminUserResponse.model_validate(user)


@router.put("/users/{user_id}/role", response_model=AdminUserResponse)
def update_user_role(
    user_id: str,
    role_data: AdminUserRoleUpdate,
    admin: User = Depends(get_current_super_admin),
    db: Session = Depends(get_db),
):
    """
    Changer le role d'un utilisateur.
    Reserve au super_admin uniquement.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    if str(user.id) == str(admin.id):
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas modifier votre propre role.")

    user.role = role_data.role
    db.commit()
    db.refresh(user)
    return AdminUserResponse.model_validate(user)


@router.put("/users/{user_id}/activate")
def activate_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Reactiver un compte utilisateur desactive."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")
    if user.is_active:
        raise HTTPException(status_code=400, detail="Ce compte est deja actif.")

    user.is_active = True
    user.deactivated_at = None
    db.commit()
    return {"message": f"Compte de {user.full_name} reactive avec succes."}


@router.put("/users/{user_id}/deactivate")
def deactivate_user(
    user_id: str,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Desactiver un compte utilisateur."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Utilisateur introuvable.")

    if str(user.id) == str(admin.id):
        raise HTTPException(status_code=400, detail="Vous ne pouvez pas desactiver votre propre compte.")

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Ce compte est deja desactive.")

    user.is_active = False
    user.deactivated_at = datetime.utcnow()
    db.commit()
    return {"message": f"Compte de {user.full_name} desactive."}


# ══════════════════════════════════════════════════════════
#  PAIEMENTS (vue admin)
# ══════════════════════════════════════════════════════════

@router.get("/payments", response_model=List[PaymentResponse])
def list_all_payments(
    status_filter: Optional[str] = Query(None, alias="status", description="completed, pending, failed"),
    payment_method: Optional[str] = Query(None, description="carte_bancaire, mobile_money"),
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=200),
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Lister tous les paiements (toutes les utilisateurs)."""
    query = db.query(Payment)

    if status_filter:
        query = query.filter(Payment.status == status_filter)
    if payment_method:
        query = query.filter(Payment.payment_method == payment_method)

    return (
        query
        .order_by(Payment.created_at.desc())
        .offset((page - 1) * per_page)
        .limit(per_page)
        .all()
    )


# ══════════════════════════════════════════════════════════
#  DASHBOARD ADMIN (statistiques globales)
# ══════════════════════════════════════════════════════════

@router.get("/dashboard", response_model=AdminStats)
def admin_dashboard(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Dashboard administrateur avec toutes les statistiques globales :
    - Utilisateurs (total, actifs, nouveaux)
    - Abonnements (par plan, revenus)
    - Paiements (total, completes, echoues)
    - Apprentissage (parcours, sessions, heures)
    - Ecologie (carbone, arbres)

    Les donnees sont mises en cache Redis pendant 2 minutes.
    """
    # Verifier le cache Redis
    cached_data = cache_get_admin_dashboard()
    if cached_data:
        return AdminStats(**cached_data)

    today = date.today()
    first_of_month = today.replace(day=1)
    now = datetime.utcnow()

    # ── Utilisateurs ──
    total_users = db.query(User).filter(User.role == "user").count()
    active_users = db.query(User).filter(User.role == "user", User.is_active == True).count()
    verified_users = db.query(User).filter(User.role == "user", User.is_verified == True).count()
    new_users_today = db.query(User).filter(
        User.role == "user",
        func.date(User.created_at) == today,
    ).count()
    new_users_this_month = db.query(User).filter(
        User.role == "user",
        User.created_at >= datetime(first_of_month.year, first_of_month.month, first_of_month.day),
    ).count()

    # ── Abonnements ──
    total_subscriptions = db.query(Subscription).count()
    active_subscriptions = db.query(Subscription).filter(Subscription.is_active == True).count()

    # Abonnements par plan avec revenus
    subs_by_plan_raw = (
        db.query(
            Subscription.plan,
            func.count(Subscription.id).label("count"),
            func.coalesce(func.sum(Subscription.price), 0).label("revenue"),
        )
        .filter(Subscription.is_active == True)
        .group_by(Subscription.plan)
        .all()
    )
    subscriptions_by_plan = [
        {"plan": row.plan, "count": row.count, "revenue": round(float(row.revenue), 2)}
        for row in subs_by_plan_raw
    ]

    # ── Paiements & Revenus ──
    total_payments = db.query(Payment).count()
    completed_payments = db.query(Payment).filter(Payment.status == "completed").count()
    failed_payments = db.query(Payment).filter(Payment.status == "failed").count()
    pending_payments = db.query(Payment).filter(Payment.status == "pending").count()

    total_revenue = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(Payment.status == "completed").scalar()

    revenue_this_month = db.query(
        func.coalesce(func.sum(Payment.amount), 0)
    ).filter(
        Payment.status == "completed",
        Payment.paid_at >= datetime(first_of_month.year, first_of_month.month, first_of_month.day),
    ).scalar()

    # ── Apprentissage ──
    total_learning_paths = db.query(LearningPath).count()
    total_sessions = db.query(LearningSession).count()
    completed_sessions = db.query(LearningSession).filter(LearningSession.status == "terminee").count()
    total_minutes = db.query(
        func.coalesce(func.sum(LearningSession.duration_minutes), 0)
    ).scalar()

    # ── Ecologie ──
    total_carbon_kg = db.query(
        func.coalesce(func.sum(CarbonFootprint.carbon_kg), 0)
    ).scalar()
    total_trees = db.query(
        func.coalesce(func.sum(EcoCompensation.trees_planted), 0)
    ).scalar()
    total_co2_compensated = db.query(
        func.coalesce(func.sum(EcoCompensation.co2_compensated_kg), 0)
    ).scalar()

    stats = AdminStats(
        total_users=total_users,
        active_users=active_users,
        verified_users=verified_users,
        new_users_today=new_users_today,
        new_users_this_month=new_users_this_month,
        total_subscriptions=total_subscriptions,
        active_subscriptions=active_subscriptions,
        subscriptions_by_plan=subscriptions_by_plan,
        total_revenue=round(float(total_revenue), 2),
        revenue_this_month=round(float(revenue_this_month), 2),
        revenue_currency="USD",
        total_payments=total_payments,
        completed_payments=completed_payments,
        failed_payments=failed_payments,
        pending_payments=pending_payments,
        total_learning_paths=total_learning_paths,
        total_sessions=total_sessions,
        completed_sessions=completed_sessions,
        total_learning_hours=round(float(total_minutes) / 60, 2),
        total_carbon_kg=round(float(total_carbon_kg), 4),
        total_trees_planted=int(total_trees),
        total_co2_compensated_kg=round(float(total_co2_compensated), 4),
    )

    # Mettre en cache Redis (2 minutes)
    cache_set_admin_dashboard(stats.model_dump())

    return stats


# ══════════════════════════════════════════════════════════
#  INITIALISATION DU PREMIER ADMIN
# ══════════════════════════════════════════════════════════

@router.post("/seed-admin", response_model=dict)
def seed_initial_admin(
    db: Session = Depends(get_db),
):
    """
    Creer le premier super_admin si aucun admin n'existe.

    Ce endpoint ne fonctionne qu'une seule fois. Des qu'un admin existe,
    il retourne une erreur.

    Credentials par defaut :
    - Email : admin@ecolearnai.com
    - Password : Admin@2026!
    """
    existing_admin = db.query(User).filter(User.role.in_(["admin", "super_admin"])).first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un administrateur existe deja. Utilisez le panel admin pour gerer les roles.",
        )

    from app.utils.security import hash_password

    admin_user = User(
        email="admin@ecolearnai.com",
        phone_number="+000000000000",
        hashed_password=hash_password("Admin@2026!"),
        full_name="Super Administrateur",
        role="super_admin",
        is_active=True,
        is_verified=True,
        gdpr_consent=True,
        gdpr_consent_at=datetime.utcnow(),
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)

    return {
        "message": "Super administrateur cree avec succes.",
        "email": "admin@ecolearnai.com",
        "password": "Admin@2026!",
        "role": "super_admin",
        "warning": "Changez le mot de passe immediatement apres la premiere connexion !",
    }
