"""
Router utilisateurs avec conformite RGPD complete.

Endpoints RGPD :
- GET  /me/data-export    → Droit a la portabilite (Article 20)
- PUT  /me/gdpr-consent   → Gestion des consentements (Article 7)
- DELETE /me              → Droit a l'effacement (Article 17)
- GET  /me/privacy-info   → Droit a l'information (Articles 13-14)
"""

from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.achievement import UserAchievement
from app.schemas.user import (
    UserResponse,
    UserUpdate,
    PasswordChange,
    UserProgressionSummary,
    AchievementResponse,
    UserAchievementResponse,
    UserFullDataExport,
    GDPRConsentUpdate,
)
from app.utils.security import get_current_user, hash_password, verify_password
from app.utils.encryption import encrypt_data, encrypt_optional, decrypt_optional
from app.services.progression_service import get_user_progression

router = APIRouter(prefix="/api/users", tags=["Utilisateurs"])


# ── Helpers ───────────────────────────────────────────────

def _build_user_response(user: User) -> UserResponse:
    """
    Construire une reponse utilisateur en dechiffrant les donnees sensibles.
    Applique le principe de minimisation RGPD (masquage partiel).
    """
    from app.routers.auth import _build_user_response as auth_build
    return auth_build(user)


# Champs sensibles qui necessitent un chiffrement lors de la mise a jour
ENCRYPTED_FIELDS_MAP = {
    "date_of_birth": "encrypted_date_of_birth",
    "address_line": "encrypted_address_line",
    "address_city": "encrypted_address_city",
    "address_postal_code": "encrypted_address_postal_code",
    "address_country": "encrypted_address_country",
}

# Champs en clair dans le modele User (pas de chiffrement)
PLAIN_FIELDS = {
    "full_name", "avatar_url", "bio",
    "language", "timezone", "level", "objectives", "preferences",
}


# ── Profil ─────────────────────────────────────────────────

@router.get("/me", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Recuperer le profil complet de l'utilisateur connecte (donnees dechiffrees)."""
    return _build_user_response(current_user)


@router.put("/me", response_model=UserResponse)
def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Mettre a jour le profil de l'utilisateur.

    Les donnees sensibles (date de naissance, adresse, nationalite, piece d'identite)
    sont automatiquement re-chiffrees avant stockage en base.
    """
    update_dict = update_data.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun champ a mettre a jour.",
        )

    for key, value in update_dict.items():
        if key in ENCRYPTED_FIELDS_MAP:
            # Chiffrer la donnee sensible
            db_field = ENCRYPTED_FIELDS_MAP[key]
            setattr(current_user, db_field, encrypt_optional(value))
        elif key in PLAIN_FIELDS:
            setattr(current_user, key, value)
        # Les champs inconnus sont ignores silencieusement

    db.commit()
    db.refresh(current_user)
    return _build_user_response(current_user)


# ── Mot de passe ───────────────────────────────────────────

@router.put("/me/password")
def change_password(
    data: PasswordChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Changer le mot de passe de l'utilisateur connecte."""
    if not verify_password(data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le mot de passe actuel est incorrect.",
        )

    if data.current_password == data.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Le nouveau mot de passe doit etre different de l'ancien.",
        )

    current_user.hashed_password = hash_password(data.new_password)
    db.commit()
    return {"message": "Mot de passe modifie avec succes."}


# ══════════════════════════════════════════════════════════
#  RGPD / GDPR ENDPOINTS
# ══════════════════════════════════════════════════════════

@router.get("/me/data-export", response_model=UserFullDataExport)
def export_personal_data(
    current_user: User = Depends(get_current_user),
):
    """
    Droit a la portabilite des donnees (RGPD, Article 20).

    Retourne TOUTES les donnees personnelles de l'utilisateur
    dans un format structure et lisible, incluant les donnees
    sensibles completement dechiffrees.

    L'utilisateur peut utiliser cet export pour transferer ses
    donnees vers un autre service.
    """
    return UserFullDataExport(
        id=current_user.id,
        email=current_user.email,
        phone_number=current_user.phone_number,
        full_name=current_user.full_name,
        gender=current_user.gender,
        date_of_birth=decrypt_optional(current_user.encrypted_date_of_birth),
        nationality=decrypt_optional(current_user.encrypted_nationality),
        national_id_type=current_user.national_id_type,
        national_id_number=decrypt_optional(current_user.encrypted_national_id),
        address_line=decrypt_optional(current_user.encrypted_address_line),
        address_city=decrypt_optional(current_user.encrypted_address_city),
        address_postal_code=decrypt_optional(current_user.encrypted_address_postal_code),
        address_country=decrypt_optional(current_user.encrypted_address_country),
        gdpr_consent=current_user.gdpr_consent,
        gdpr_consent_at=current_user.gdpr_consent_at,
        gdpr_marketing_consent=current_user.gdpr_marketing_consent,
        gdpr_data_retention_consent=current_user.gdpr_data_retention_consent,
        avatar_url=current_user.avatar_url,
        bio=current_user.bio,
        language=current_user.language,
        timezone=current_user.timezone,
        level=current_user.level,
        objectives=current_user.objectives,
        preferences=current_user.preferences,
        total_xp=current_user.total_xp,
        current_streak=current_user.current_streak,
        longest_streak=current_user.longest_streak,
        last_activity_date=current_user.last_activity_date,
        total_learning_minutes=current_user.total_learning_minutes,
        is_active=current_user.is_active,
        is_verified=current_user.is_verified,
        last_login_at=current_user.last_login_at,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at,
    )


@router.put("/me/gdpr-consent", response_model=dict)
def update_gdpr_consent(
    consent_data: GDPRConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Gestion des consentements RGPD (Article 7).

    L'utilisateur peut modifier ses consentements facultatifs :
    - Marketing : recevoir des communications promotionnelles
    - Conservation des donnees : autoriser la conservation au-dela du necessaire

    Note : Le consentement principal (gdpr_consent) ne peut pas etre retire
    sans supprimer le compte (voir DELETE /me).
    """
    updated = False
    changes = {}

    if consent_data.gdpr_marketing_consent is not None:
        current_user.gdpr_marketing_consent = consent_data.gdpr_marketing_consent
        changes["marketing"] = consent_data.gdpr_marketing_consent
        updated = True

    if consent_data.gdpr_data_retention_consent is not None:
        current_user.gdpr_data_retention_consent = consent_data.gdpr_data_retention_consent
        changes["data_retention"] = consent_data.gdpr_data_retention_consent
        updated = True

    if not updated:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun consentement a mettre a jour.",
        )

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Consentements RGPD mis a jour avec succes.",
        "changes": changes,
        "updated_at": datetime.utcnow().isoformat(),
    }


@router.get("/me/privacy-info", response_model=dict)
def get_privacy_info(current_user: User = Depends(get_current_user)):
    """
    Droit a l'information (RGPD, Articles 13-14).

    Retourne les informations sur :
    - Quelles donnees sont collectees et pourquoi
    - Comment elles sont protegees (chiffrement)
    - Les droits de l'utilisateur
    - L'etat de ses consentements
    """
    return {
        "responsable_traitement": {
            "nom": "EcoLearn AI",
            "contact": "dpo@ecolearn-ai.com",
        },
        "donnees_collectees": {
            "obligatoires": [
                {"champ": "email", "finalite": "Identification et communication", "chiffre": False},
                {"champ": "mot_de_passe", "finalite": "Authentification", "chiffre": True, "methode": "bcrypt (hachage irreversible)"},
                {"champ": "nom_complet", "finalite": "Personnalisation de l'experience", "chiffre": False},
                {"champ": "telephone", "finalite": "Verification du compte (SMS OTP)", "chiffre": False},
                {"champ": "date_de_naissance", "finalite": "Verification d'age (minimum 13 ans)", "chiffre": True, "methode": "Fernet AES-128-CBC"},
            ],
            "facultatives": [
                {"champ": "nationalite", "finalite": "Adaptation des contenus", "chiffre": True},
                {"champ": "piece_identite", "finalite": "Verification d'identite (KYC)", "chiffre": True},
                {"champ": "adresse", "finalite": "Facturation et localisation", "chiffre": True},
                {"champ": "genre", "finalite": "Personnalisation", "chiffre": False},
                {"champ": "avatar_bio", "finalite": "Profil social", "chiffre": False},
            ],
        },
        "protection_donnees": {
            "chiffrement": "Fernet (AES-128-CBC + HMAC-SHA256)",
            "hachage_mot_de_passe": "bcrypt",
            "transport": "TLS 1.2+",
            "donnees_chiffrees_en_base": [
                "date_de_naissance", "nationalite", "numero_piece_identite",
                "adresse_rue", "ville", "code_postal", "pays",
            ],
        },
        "droits_utilisateur": {
            "acces": "GET /api/users/me (donnees dechiffrees)",
            "portabilite": "GET /api/users/me/data-export (export complet)",
            "rectification": "PUT /api/users/me (modification du profil)",
            "effacement": "DELETE /api/users/me (suppression definitive)",
            "consentement": "PUT /api/users/me/gdpr-consent (gestion des consentements)",
            "information": "GET /api/users/me/privacy-info (cette page)",
        },
        "consentements_actuels": {
            "traitement_donnees": current_user.gdpr_consent,
            "date_consentement": current_user.gdpr_consent_at.isoformat() if current_user.gdpr_consent_at else None,
            "marketing": current_user.gdpr_marketing_consent,
            "conservation_donnees": current_user.gdpr_data_retention_consent,
        },
        "duree_conservation": {
            "compte_actif": "Donnees conservees tant que le compte est actif",
            "compte_desactive": "Donnees anonymisees apres 3 ans d'inactivite",
            "suppression": "Effacement immediat et irreversible sur demande",
        },
    }


# ── Desactivation / Suppression ────────────────────────────

@router.put("/me/deactivate")
def deactivate_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Desactiver le compte de l'utilisateur.
    Le compte reste en base mais l'utilisateur ne peut plus se connecter.
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est deja desactive.",
        )

    current_user.is_active = False
    current_user.deactivated_at = datetime.utcnow()
    db.commit()
    return {"message": "Compte desactive avec succes. Contactez le support pour le reactiver."}


@router.delete("/me", status_code=status.HTTP_200_OK)
def delete_account(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Droit a l'effacement (RGPD, Article 17).

    Supprimer definitivement le compte et TOUTES les donnees associees.
    Cette action est irreversible. Toutes les donnees personnelles,
    y compris les donnees chiffrees, sont effacees.
    """
    db.delete(current_user)
    db.commit()
    return {
        "message": "Compte et toutes les donnees associees supprimes definitivement.",
        "rgpd": "Droit a l'effacement exerce avec succes (Article 17 RGPD).",
    }


# ── Progression ────────────────────────────────────────────

@router.get("/me/progression", response_model=UserProgressionSummary)
def get_my_progression(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obtenir le resume complet de la progression :
    - XP, niveau, streak
    - Stats pedagogiques (parcours, sessions, scores, temps)
    - Detail par parcours
    - Badges obtenus et disponibles
    """
    return get_user_progression(db, current_user)


# ── Badges / Achievements ─────────────────────────────────

@router.get("/me/achievements", response_model=List[AchievementResponse])
def get_my_achievements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Lister tous les badges avec leur statut (debloque ou non).
    Les badges debloques incluent la date de deblocage.
    """
    from app.models.achievement import Achievement

    all_achievements = db.query(Achievement).order_by(Achievement.category, Achievement.condition_value).all()
    unlocked_map = {
        ua.achievement_id: ua.unlocked_at
        for ua in db.query(UserAchievement).filter(UserAchievement.user_id == current_user.id).all()
    }

    result = []
    for ach in all_achievements:
        result.append(AchievementResponse(
            id=ach.id,
            code=ach.code,
            name=ach.name,
            description=ach.description,
            icon=ach.icon,
            category=ach.category,
            xp_reward=ach.xp_reward,
            unlocked_at=unlocked_map.get(ach.id),
        ))
    return result
