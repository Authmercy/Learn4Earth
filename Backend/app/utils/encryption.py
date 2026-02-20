"""
Module de chiffrement des donnees sensibles (RGPD / GDPR).

Utilise Fernet (AES-128-CBC + HMAC-SHA256) pour un chiffrement symetrique
authentifie. Les donnees sensibles sont chiffrees avant stockage en base
et dechiffrees a la lecture.

Conformite RGPD :
- Article 32 : Mesures de securite appropriees (chiffrement)
- Article 25 : Protection des donnees des la conception (privacy by design)
- Les donnees sensibles ne sont jamais stockees en clair en base de donnees
"""

import logging
from typing import Optional
from cryptography.fernet import Fernet, InvalidToken
from app.config import settings

logger = logging.getLogger(__name__)

# Initialiser le chiffreur Fernet avec la cle de configuration
_fernet: Optional[Fernet] = None


def _get_fernet() -> Fernet:
    """Obtenir l'instance Fernet (singleton)."""
    global _fernet
    if _fernet is None:
        if not settings.ENCRYPTION_KEY:
            raise RuntimeError(
                "ENCRYPTION_KEY non configuree. "
                "Generez une cle avec: python -c \"from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())\""
            )
        _fernet = Fernet(settings.ENCRYPTION_KEY.encode())
    return _fernet


def encrypt_data(plain_text: str) -> str:
    """
    Chiffrer une chaine de caracteres.

    Args:
        plain_text: Donnee en clair a chiffrer

    Returns:
        Donnee chiffree encodee en base64 (stockable en DB comme string)
    """
    if not plain_text:
        return ""
    try:
        f = _get_fernet()
        encrypted = f.encrypt(plain_text.encode("utf-8"))
        return encrypted.decode("utf-8")
    except Exception as e:
        logger.error("Erreur de chiffrement : %s", str(e))
        raise


def decrypt_data(encrypted_text: str) -> str:
    """
    Dechiffrer une chaine chiffree.

    Args:
        encrypted_text: Donnee chiffree (base64)

    Returns:
        Donnee en clair
    """
    if not encrypted_text:
        return ""
    try:
        f = _get_fernet()
        decrypted = f.decrypt(encrypted_text.encode("utf-8"))
        return decrypted.decode("utf-8")
    except InvalidToken:
        logger.error("Echec de dechiffrement : token invalide ou cle incorrecte")
        return "[donnee illisible - cle de chiffrement incorrecte]"
    except Exception as e:
        logger.error("Erreur de dechiffrement : %s", str(e))
        return ""


def encrypt_optional(value: Optional[str]) -> Optional[str]:
    """Chiffrer une valeur optionnelle (retourne None si None)."""
    if value is None:
        return None
    return encrypt_data(value)


def decrypt_optional(value: Optional[str]) -> Optional[str]:
    """Dechiffrer une valeur optionnelle (retourne None si None)."""
    if value is None:
        return None
    return decrypt_data(value)
