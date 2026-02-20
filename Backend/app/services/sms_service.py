"""
Service d'envoi de SMS via l'API MGT-SMS (MagicTech SMS).

Fonctionnalites :
- Envoi de SMS generique
- Envoi de code OTP pour validation d'inscription
- Notification de paiement recu
- Generation de codes de verification
"""

import random
import logging
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


# ── Envoi de SMS generique ─────────────────────────────

async def send_sms(
    to_number: str,
    message_body: str,
    sender_id: Optional[str] = None,
) -> dict:
    """
    Envoyer un SMS via l'API MGT-SMS.

    Args:
        to_number: Numero au format international E.164 (ex: +243898900119)
        message_body: Contenu du message
        sender_id: Nom de l'expediteur (max 11 chars, A-Z 0-9, sans espaces)

    Returns:
        dict avec success, sms_id, error
    """
    if not settings.SMS_API_KEY:
        logger.warning("SMS : cle API non configuree, envoi ignore")
        return {"success": False, "error": "Cle API SMS non configuree", "sms_id": None}

    payload = {
        "to_number": to_number,
        "message_body": message_body,
    }
    if sender_id:
        payload["sender_id"] = sender_id
    elif settings.SMS_SENDER_ID:
        payload["sender_id"] = settings.SMS_SENDER_ID

    headers = {
        "x-api-key": settings.SMS_API_KEY,
        "Content-Type": "application/json",
    }

    logger.info("SMS : envoi vers %s (sender=%s)", to_number, payload.get("sender_id"))

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                settings.SMS_API_URL,
                json=payload,
                headers=headers,
            )

        if response.status_code == 200:
            data = response.json()
            sms_id = data.get("twilio_id", "")
            logger.info("SMS : envoye avec succes - id=%s, dest=%s", sms_id, to_number)
            return {
                "success": True,
                "sms_id": sms_id,
                "error": None,
            }
        else:
            logger.error("SMS : echec envoi - status=%d, body=%s", response.status_code, response.text)
            return {
                "success": False,
                "sms_id": None,
                "error": f"Erreur API SMS (HTTP {response.status_code}): {response.text}",
            }

    except httpx.TimeoutException:
        logger.error("SMS : timeout lors de l'envoi vers %s", to_number)
        return {"success": False, "sms_id": None, "error": "Timeout du service SMS"}
    except Exception as e:
        logger.error("SMS : erreur inattendue - %s", str(e))
        return {"success": False, "sms_id": None, "error": f"Erreur inattendue: {str(e)}"}


# ── Generation de code OTP ─────────────────────────────

def generate_otp_code(length: int = 6) -> str:
    """Generer un code OTP numerique."""
    return "".join(str(random.randint(0, 9)) for _ in range(length))


# ── SMS pre-formates ───────────────────────────────────

async def send_verification_sms(to_number: str, code: str, full_name: str) -> dict:
    """
    Envoyer un SMS de verification d'inscription avec code OTP.
    """
    message = (
        f"EcoLearn AI - Bienvenue {full_name} !\n"
        f"Votre code de verification est : {code}\n"
        f"Ce code expire dans 10 minutes.\n"
        f"Ne partagez ce code avec personne."
    )
    return await send_sms(to_number, message)


async def send_payment_confirmation_sms(
    to_number: str,
    full_name: str,
    amount: float,
    currency: str,
    plan: str,
    transaction_ref: str,
) -> dict:
    """
    Envoyer une notification SMS de confirmation de paiement.
    """
    message = (
        f"EcoLearn AI - Paiement confirme !\n"
        f"Bonjour {full_name},\n"
        f"Votre paiement de {amount:.2f} {currency} "
        f"pour l'abonnement {plan.capitalize()} a ete recu.\n"
        f"Ref: {transaction_ref}\n"
        f"Votre abonnement est maintenant actif. Bon apprentissage !"
    )
    return await send_sms(to_number, message)


async def send_payment_failed_sms(
    to_number: str,
    full_name: str,
    amount: float,
    currency: str,
) -> dict:
    """
    Envoyer une notification SMS d'echec de paiement.
    """
    message = (
        f"EcoLearn AI - Echec de paiement\n"
        f"Bonjour {full_name},\n"
        f"Votre paiement de {amount:.2f} {currency} n'a pas abouti.\n"
        f"Veuillez reessayer ou contacter le support."
    )
    return await send_sms(to_number, message)


async def send_resend_otp_sms(to_number: str, code: str) -> dict:
    """
    Renvoyer un code OTP de verification.
    """
    message = (
        f"EcoLearn AI - Nouveau code de verification\n"
        f"Votre nouveau code est : {code}\n"
        f"Ce code expire dans 10 minutes."
    )
    return await send_sms(to_number, message)
