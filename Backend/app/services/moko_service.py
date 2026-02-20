"""
Service d'integration avec l'API Umoja Card / FreshPay (PRODUCTION).

Credentials live :
- Merchant Code : m3Z4PQ2xawz3p
- Base URL : https://card.gofreshpay.com
- Endpoint paiement : /api/v1/payment/orders
- Commission : 3.50%

Gere :
- La generation de la signature HMAC-SHA256
- L'initiation d'un paiement par carte bancaire
- La verification des callbacks de confirmation (callback_secret distinct)
"""

import json
import hmac
import hashlib
import logging
from datetime import datetime, timezone
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def _generate_signature(payload_json: str, timestamp: str) -> str:
    """
    Generer la signature HMAC-SHA256 requise par l'API Umoja/FreshPay.
    signature = HMAC_SHA256(api_secret, payload_json + timestamp)
    """
    message = payload_json + timestamp
    signature = hmac.new(
        settings.MOKO_API_SECRET.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()
    return signature


def _build_headers(payload_json: str) -> dict:
    """Construire les headers d'authentification pour l'API Umoja/FreshPay."""
    timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    signature = _generate_signature(payload_json, timestamp)

    return {
        "X-API-Key": settings.MOKO_API_KEY,
        "X-Timestamp": timestamp,
        "X-Signature": signature,
        "Content-Type": "application/json",
    }


# Mapping noms de pays courants vers codes ISO 3166-1 alpha-2
_COUNTRY_MAP = {
    "congo": "CD", "rdc": "CD", "rd congo": "CD", "republique democratique du congo": "CD",
    "congo-kinshasa": "CD", "congo kinshasa": "CD", "democratic republic of the congo": "CD",
    "congo-brazzaville": "CG", "congo brazzaville": "CG", "republic of the congo": "CG",
    "france": "FR", "belgique": "BE", "belgium": "BE", "suisse": "CH", "switzerland": "CH",
    "canada": "CA", "etats-unis": "US", "united states": "US", "usa": "US",
    "cameroun": "CM", "cameroon": "CM", "senegal": "SN", "cote d'ivoire": "CI",
    "cote divoire": "CI", "ivory coast": "CI", "mali": "ML", "burkina faso": "BF",
    "gabon": "GA", "togo": "TG", "benin": "BJ", "niger": "NE", "tchad": "TD", "chad": "TD",
    "guinee": "GN", "guinea": "GN", "rwanda": "RW", "burundi": "BI",
    "angola": "AO", "mozambique": "MZ", "zambie": "ZM", "zambia": "ZM",
    "tanzanie": "TZ", "tanzania": "TZ", "kenya": "KE", "ouganda": "UG", "uganda": "UG",
    "afrique du sud": "ZA", "south africa": "ZA", "maroc": "MA", "morocco": "MA",
    "algerie": "DZ", "algeria": "DZ", "tunisie": "TN", "tunisia": "TN",
    "madagascar": "MG", "nigeria": "NG", "ghana": "GH", "ethiopie": "ET", "ethiopia": "ET",
    "egypte": "EG", "egypt": "EG", "libye": "LY", "libya": "LY",
    "royaume-uni": "GB", "united kingdom": "GB", "uk": "GB", "england": "GB",
    "allemagne": "DE", "germany": "DE", "espagne": "ES", "spain": "ES",
    "italie": "IT", "italy": "IT", "portugal": "PT", "pays-bas": "NL", "netherlands": "NL",
    "chine": "CN", "china": "CN", "japon": "JP", "japan": "JP", "inde": "IN", "india": "IN",
    "bresil": "BR", "brazil": "BR", "mexique": "MX", "mexico": "MX",
    "congolaise": "CD", "francaise": "FR", "belge": "BE",
}


def _to_country_code(value: str) -> str:
    """
    Convertir un nom de pays ou une nationalite en code ISO 3166-1 alpha-2.
    Si la valeur fait deja 2 caracteres, on la retourne telle quelle (deja un code ISO).
    """
    if not value:
        return ""
    v = value.strip()
    # Deja un code ISO 2 lettres
    if len(v) == 2:
        return v.upper()
    # Recherche dans le mapping (insensible a la casse)
    code = _COUNTRY_MAP.get(v.lower())
    if code:
        return code
    # Fallback : prendre les 2 premieres lettres en majuscules
    return v[:2].upper()


async def initiate_card_payment(
    amount: float,
    currency: str,
    merchant_reference: str,
    customer_first_name: str,
    customer_last_name: str,
    customer_email: str,
    customer_phone: str = "",
    billing_address: Optional[dict] = None,
) -> dict:
    """
    Initier un paiement par carte bancaire via l'API Umoja Card / FreshPay.

    Endpoint PRODUCTION : POST https://card.gofreshpay.com/api/v1/payment/orders

    Retourne:
    - success: True/False
    - transaction_uuid: identifiant unique de la transaction
    - payment_url: URL de redirection vers la page de paiement securisee
    - error: message d'erreur en cas d'echec
    """
    # Construire les donnees de paiement
    # L'API Umoja exige des valeurs non vides pour phone (min 5) et country (min 2)
    address = billing_address or {}
    phone = customer_phone.strip() if customer_phone else ""
    if len(phone) < 5:
        phone = "+000000000"

    country = _to_country_code(address.get("country", "").strip())
    if len(country) < 2:
        country = "CD"

    payment_data = {
        "merchant_code": settings.MOKO_MERCHANT_CODE,
        "amount": amount,
        "currency": currency,
        "merchant_reference": merchant_reference,
        "bill_to_forename": customer_first_name or "N/A",
        "bill_to_surname": customer_last_name or "N/A",
        "bill_to_email": customer_email,
        "bill_to_phone": phone,
        "bill_to_address_line1": address.get("line1", "") or "N/A",
        "bill_to_address_city": address.get("city", "") or "N/A",
        "bill_to_address_state": address.get("state", "") or "N/A",
        "bill_to_address_postal_code": address.get("postal_code", "") or "00000",
        "bill_to_address_country": country,
        "callback_url": settings.MOKO_CALLBACK_URL,
    }

    payload_json = json.dumps(payment_data)
    headers = _build_headers(payload_json)

    logger.info(
        "Umoja CardAPI : initiation paiement LIVE - ref=%s, montant=%.2f %s, merchant=%s",
        merchant_reference, amount, currency, settings.MOKO_MERCHANT_CODE,
    )

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.post(
                f"{settings.MOKO_BASE_URL}/api/v1/payment/orders",
                json=payment_data,
                headers=headers,
            )

        if response.status_code in (200, 201):
            data = response.json()
            transaction_uuid = data.get("data", {}).get("transaction_uuid", "")
            payment_url = data.get("data", {}).get("links", "")

            logger.info(
                "Umoja CardAPI : paiement initie OK - uuid=%s, url=%s",
                transaction_uuid, payment_url,
            )

            return {
                "success": True,
                "transaction_uuid": transaction_uuid,
                "payment_url": payment_url,
                "raw_response": data,
            }
        else:
            logger.error(
                "Umoja CardAPI : echec initiation - status=%d, body=%s",
                response.status_code, response.text,
            )
            return {
                "success": False,
                "error": f"Erreur Umoja API (HTTP {response.status_code}): {response.text}",
                "transaction_uuid": None,
                "payment_url": None,
            }

    except httpx.TimeoutException:
        logger.error("Umoja CardAPI : timeout lors de l'appel API")
        return {
            "success": False,
            "error": "Timeout : le service de paiement ne repond pas. Reessayez.",
            "transaction_uuid": None,
            "payment_url": None,
        }
    except Exception as e:
        logger.error("Umoja CardAPI : erreur inattendue - %s", str(e))
        return {
            "success": False,
            "error": f"Erreur inattendue : {str(e)}",
            "transaction_uuid": None,
            "payment_url": None,
        }


def verify_callback_signature(payload_body: bytes, received_signature: str, received_timestamp: str) -> bool:
    """
    Verifier la signature d'un callback Umoja/FreshPay pour s'assurer de son authenticite.

    Utilise le CALLBACK_SECRET (distinct du API_SECRET) pour la verification
    des webhooks de confirmation de paiement.
    """
    callback_secret = settings.MOKO_CALLBACK_SECRET
    if not callback_secret:
        logger.warning("Umoja : verification de signature ignoree (pas de callback_secret configure)")
        return True

    message = payload_body.decode() + received_timestamp
    expected_signature = hmac.new(
        callback_secret.encode(),
        message.encode(),
        hashlib.sha256,
    ).hexdigest()

    is_valid = hmac.compare_digest(expected_signature, received_signature)
    if not is_valid:
        logger.warning("Umoja CardAPI : signature callback invalide")
    return is_valid
