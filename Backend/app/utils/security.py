from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session as DBSession
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: DBSession = Depends(get_db),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Identifiants invalides",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Ce compte a ete desactive.",
        )
    return user


def get_current_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency qui verifie que l'utilisateur connecte est administrateur.
    Roles autorises : admin, super_admin
    """
    if current_user.role not in ("admin", "super_admin"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve aux administrateurs.",
        )
    return current_user


def get_current_super_admin(
    current_user: User = Depends(get_current_user),
) -> User:
    """
    Dependency qui verifie que l'utilisateur est super administrateur.
    Seul le super_admin peut creer d'autres admins.
    """
    if current_user.role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acces reserve au super administrateur.",
        )
    return current_user


def require_active_subscription(
    current_user: User = Depends(get_current_user),
    db: DBSession = Depends(get_db),
) -> User:
    """
    Dependency qui verifie que l'utilisateur peut generer un cours.
    Ordre de priorite :
    1. Admins / super_admins : toujours autorises
    2. Abonnement actif : autorises
    3. Cours gratuits restants (free_courses_remaining > 0) : autorises, decremente le compteur
    4. Sinon : 403 Forbidden
    """
    # Les admins / super_admins n'ont pas besoin d'abonnement
    if current_user.role in ("admin", "super_admin"):
        return current_user

    # Rechercher un abonnement actif dont la date de fin n'est pas depassee
    active_sub = (
        db.query(Subscription)
        .filter(
            Subscription.user_id == current_user.id,
            Subscription.is_active == True,
            Subscription.end_date > datetime.utcnow(),
        )
        .first()
    )

    if active_sub:
        return current_user

    # Verifier les cours gratuits restants
    remaining = current_user.free_courses_remaining if current_user.free_courses_remaining is not None else 0
    if remaining > 0:
        # Decrementer le compteur de cours gratuits
        current_user.free_courses_remaining = remaining - 1
        db.flush()
        return current_user

    # Ni abonnement ni cours gratuits
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=(
            "Vous avez utilise vos 5 cours gratuits. "
            "Souscrivez a un abonnement pour continuer a generer des cours. "
            "Consultez GET /api/subscriptions/plans pour voir les offres disponibles."
        ),
    )
