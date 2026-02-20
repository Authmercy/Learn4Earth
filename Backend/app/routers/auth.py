"""
Router d'authentification avec conformite RGPD.

- Inscription avec consentement RGPD obligatoire
- Chiffrement des donnees sensibles avant stockage (Fernet/AES)
- Verification par SMS et Email (meme code OTP envoye sur les deux canaux)
- Validation du mot de passe robuste
"""

from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token, VerifySMS, ResendOTP
from app.utils.security import hash_password, verify_password, create_access_token
from app.utils.encryption import encrypt_data, encrypt_optional, decrypt_optional
from app.config import settings
from app.services.sms_service import (
    generate_otp_code,
    send_verification_sms,
    send_resend_otp_sms,
)
from app.services.email_service import (
    send_verification_email,
    send_resend_otp_email,
)

router = APIRouter(prefix="/api/auth", tags=["Authentification"])


def _build_user_response(user: User) -> UserResponse:
    """
    Construire une reponse utilisateur en dechiffrant les donnees sensibles.
    Applique le principe de minimisation RGPD (masquage partiel).
    """
    # Dechiffrer les donnees sensibles
    date_of_birth = decrypt_optional(user.encrypted_date_of_birth)
    address_line = decrypt_optional(user.encrypted_address_line)
    address_city = decrypt_optional(user.encrypted_address_city)
    address_postal_code = decrypt_optional(user.encrypted_address_postal_code)
    address_country = decrypt_optional(user.encrypted_address_country)

    # Masquage partiel de l'adresse (principe de minimisation)
    address_line_masked = None
    if address_line:
        # Montrer les 5 premiers caracteres + "***"
        address_line_masked = address_line[:5] + "***" if len(address_line) > 5 else address_line

    address_postal_code_masked = None
    if address_postal_code:
        # Montrer les 2 premiers chiffres + "***"
        address_postal_code_masked = address_postal_code[:2] + "***" if len(address_postal_code) > 2 else address_postal_code

    return UserResponse(
        id=user.id,
        email=user.email,
        phone_number=user.phone_number,
        full_name=user.full_name,
        date_of_birth=date_of_birth,
        address_city=address_city,
        address_country=address_country,
        address_line_masked=address_line_masked,
        address_postal_code_masked=address_postal_code_masked,
        gdpr_consent=user.gdpr_consent,
        gdpr_consent_at=user.gdpr_consent_at,
        gdpr_marketing_consent=user.gdpr_marketing_consent,
        gdpr_data_retention_consent=user.gdpr_data_retention_consent,
        avatar_url=user.avatar_url,
        bio=user.bio,
        language=user.language,
        timezone=user.timezone,
        level=user.level,
        objectives=user.objectives,
        preferences=user.preferences,
        free_courses_remaining=user.free_courses_remaining if user.free_courses_remaining is not None else 5,
        total_xp=user.total_xp,
        current_streak=user.current_streak,
        longest_streak=user.longest_streak,
        last_activity_date=user.last_activity_date,
        total_learning_minutes=user.total_learning_minutes,
        is_active=user.is_active,
        is_verified=user.is_verified,
        last_login_at=user.last_login_at,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


@router.post("/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Inscription d'un nouvel utilisateur avec conformite RGPD.

    Donnees collectees :
    - Identite (nom, email, telephone, genre, date de naissance)
    - Adresse complete
    - Piece d'identite (optionnel)
    - Consentement RGPD obligatoire

    Les donnees sensibles sont chiffrees avant stockage (AES-128-CBC via Fernet).
    Un code OTP est envoye par SMS pour verification du compte.
    """
    # Verifier email unique
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec cet email existe deja.",
        )

    # Verifier numero unique
    existing_phone = db.query(User).filter(User.phone_number == user_data.phone_number).first()
    if existing_phone:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Un compte avec ce numero de telephone existe deja.",
        )

    # Generer le code OTP
    otp_code = generate_otp_code()
    otp_expires = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

    # Chiffrer les donnees sensibles RGPD avant stockage
    encrypted_dob = encrypt_data(user_data.date_of_birth) if user_data.date_of_birth else None
    encrypted_address_line = encrypt_optional(user_data.address_line)
    encrypted_address_city = encrypt_optional(user_data.address_city)
    encrypted_address_postal_code = encrypt_optional(user_data.address_postal_code)
    encrypted_address_country = encrypt_optional(user_data.address_country)

    # Creer l'utilisateur (non verifie)
    user = User(
        email=user_data.email,
        phone_number=user_data.phone_number,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        # Donnees sensibles chiffrees
        encrypted_date_of_birth=encrypted_dob,
        encrypted_address_line=encrypted_address_line,
        encrypted_address_city=encrypted_address_city,
        encrypted_address_postal_code=encrypted_address_postal_code,
        encrypted_address_country=encrypted_address_country,
        # Consentements RGPD
        gdpr_consent=user_data.gdpr_consent,
        gdpr_consent_at=datetime.utcnow(),
        gdpr_marketing_consent=user_data.gdpr_marketing_consent or False,
        gdpr_data_retention_consent=user_data.gdpr_data_retention_consent or False,
        # Apprentissage
        level=user_data.level,
        objectives=user_data.objectives,
        preferences=user_data.preferences,
        # Verification SMS
        is_verified=False,
        verification_code=otp_code,
        verification_code_expires_at=otp_expires,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    # Envoyer le code de verification par SMS
    sms_result = await send_verification_sms(
        to_number=user.phone_number,
        code=otp_code,
        full_name=user.full_name,
    )

    # Envoyer le meme code de verification par Email
    email_result = send_verification_email(
        to_email=user.email,
        code=otp_code,
        full_name=user.full_name,
    )

    return {
        "message": "Inscription reussie ! Un code de verification a ete envoye par SMS et par email.",
        "user": _build_user_response(user),
        "sms_sent": sms_result["success"],
        "sms_error": sms_result.get("error") if not sms_result["success"] else None,
        "email_sent": email_result["success"],
        "email_error": email_result.get("error") if not email_result["success"] else None,
        "verification_required": True,
        "rgpd_info": {
            "consent_recorded": True,
            "consent_date": user.gdpr_consent_at.isoformat() if user.gdpr_consent_at else None,
            "sensitive_data_encrypted": True,
            "encryption_method": "Fernet (AES-128-CBC + HMAC-SHA256)",
        },
    }


@router.post("/verify-sms", response_model=dict)
def verify_sms(data: VerifySMS, db: Session = Depends(get_db)):
    """
    Verifier le code SMS recu lors de l'inscription.

    Une fois le code valide, le compte est active (is_verified = True)
    et l'utilisateur peut se connecter.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte trouve avec cet email.",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est deja verifie.",
        )

    if not user.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun code de verification en attente. Demandez un nouveau code.",
        )

    # Verifier l'expiration
    if user.verification_code_expires_at and user.verification_code_expires_at < datetime.utcnow():
        user.verification_code = None
        user.verification_code_expires_at = None
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code expire. Demandez un nouveau code via /resend-otp.",
        )

    # Verifier le code
    if user.verification_code != data.code.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Code de verification incorrect.",
        )

    # Valider le compte (SMS + Email verifies en meme temps car meme code)
    user.is_verified = True
    user.is_email_verified = True
    user.verification_code = None
    user.verification_code_expires_at = None
    db.commit()
    db.refresh(user)

    return {
        "message": "Compte verifie avec succes ! Vous pouvez maintenant vous connecter.",
        "user": _build_user_response(user),
    }


@router.post("/resend-otp", response_model=dict)
async def resend_otp(data: ResendOTP, db: Session = Depends(get_db)):
    """
    Renvoyer un nouveau code OTP par SMS.

    Utile si le code precedent a expire ou n'a pas ete recu.
    """
    user = db.query(User).filter(User.email == data.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aucun compte trouve avec cet email.",
        )

    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ce compte est deja verifie.",
        )

    if not user.phone_number:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Aucun numero de telephone associe a ce compte.",
        )

    # Generer un nouveau code
    otp_code = generate_otp_code()
    otp_expires = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRY_MINUTES)

    user.verification_code = otp_code
    user.verification_code_expires_at = otp_expires
    db.commit()

    # Envoyer le code par SMS
    sms_result = await send_resend_otp_sms(
        to_number=user.phone_number,
        code=otp_code,
    )

    # Envoyer le meme code par Email
    email_result = send_resend_otp_email(
        to_email=user.email,
        code=otp_code,
    )

    return {
        "message": "Un nouveau code de verification a ete envoye par SMS et par email.",
        "sms_sent": sms_result["success"],
        "sms_error": sms_result.get("error") if not sms_result["success"] else None,
        "email_sent": email_result["success"],
        "email_error": email_result.get("error") if not email_result["success"] else None,
    }


@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Connexion et obtention du token JWT."""
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou mot de passe incorrect.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verifier que le compte est verifie par SMS
    if not user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Votre compte n'est pas encore verifie. Verifiez le code SMS envoye a votre telephone.",
        )

    # Verifier que le compte est actif
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte a ete desactive. Contactez le support.",
        )

    # Enregistrer la date de derniere connexion
    user.last_login_at = datetime.utcnow()
    db.commit()
    db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id)})
    return Token(
        access_token=access_token,
        user=_build_user_response(user),
    )
