import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.payment import Payment
from app.schemas.payment import PaymentResponse, MokoCallbackPayload
from app.services.payment_service import confirm_moko_payment
from app.services.moko_service import verify_callback_signature
from app.services.sms_service import send_payment_confirmation_sms, send_payment_failed_sms
from app.services.email_service import send_payment_confirmation_email, send_payment_failed_email
from app.utils.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/payments", tags=["Paiements & Factures"])


# ── Mes paiements ──────────────────────────────────────

@router.get("/my", response_model=List[PaymentResponse])
def get_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister mes paiements et factures."""
    return (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )


# ── Detail d'une facture ───────────────────────────────

@router.get("/{payment_id}/invoice")
def get_invoice(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Consulter une facture specifique."""
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.user_id == current_user.id)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Facture introuvable.")

    return {
        "invoice_number": payment.invoice_number,
        "amount": payment.amount,
        "currency": payment.currency,
        "payment_method": payment.payment_method,
        "status": payment.status,
        "transaction_ref": payment.transaction_ref,
        "moko_transaction_uuid": payment.moko_transaction_uuid,
        "paid_at": payment.paid_at,
        "invoice_details": payment.invoice_details,
    }


# ── Verifier le statut d'un paiement en attente ───────

@router.get("/{payment_id}/status")
def check_payment_status(
    payment_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Verifier le statut d'un paiement (utile pour le polling apres paiement carte)."""
    payment = (
        db.query(Payment)
        .filter(Payment.id == payment_id, Payment.user_id == current_user.id)
        .first()
    )
    if not payment:
        raise HTTPException(status_code=404, detail="Paiement introuvable.")

    return {
        "payment_id": str(payment.id),
        "status": payment.status,
        "payment_method": payment.payment_method,
        "moko_transaction_uuid": payment.moko_transaction_uuid,
        "paid_at": payment.paid_at,
        "subscription_active": payment.subscription.is_active if payment.subscription else False,
    }


# ── Callback Moko Checkout ─────────────────────────────

@router.post("/moko/callback")
async def moko_callback(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Endpoint de callback appele par Moko Checkout / FreshPay
    apres qu'un paiement par carte bancaire a ete traite.

    Ce endpoint :
    1. Verifie la signature HMAC du callback
    2. Identifie le paiement concerne
    3. Met a jour le statut du paiement
    4. Active l'abonnement si le paiement est confirme
    5. Genere la facture finale
    """
    # Lire le body brut pour verification de signature
    body = await request.body()

    # Verifier la signature si les headers sont presents
    received_signature = request.headers.get("X-Signature", "")
    received_timestamp = request.headers.get("X-Timestamp", "")

    if received_signature and received_timestamp:
        if not verify_callback_signature(body, received_signature, received_timestamp):
            logger.warning("Moko callback : signature invalide rejetee")
            raise HTTPException(status_code=401, detail="Signature invalide.")

    # Parser le payload
    try:
        payload = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Payload JSON invalide.")

    logger.info("Moko callback recu : %s", payload)

    # Extraire les informations cles
    # L'API Moko peut envoyer les donnees dans data ou directement
    data = payload.get("data", payload)
    transaction_uuid = data.get("transaction_uuid")
    merchant_reference = data.get("merchant_reference")
    callback_status = data.get("status", "")

    if not transaction_uuid and not merchant_reference:
        logger.warning("Moko callback : aucun identifiant de transaction")
        raise HTTPException(status_code=400, detail="Identifiant de transaction manquant.")

    # Confirmer le paiement
    payment = confirm_moko_payment(
        db=db,
        transaction_uuid=transaction_uuid,
        merchant_reference=merchant_reference,
        callback_status=callback_status,
    )

    if payment is None:
        raise HTTPException(status_code=404, detail="Paiement introuvable pour ce callback.")

    # Envoyer les notifications a l'utilisateur (SMS + Email)
    user = db.query(User).filter(User.id == payment.user_id).first()
    if user:
        plan_name = payment.subscription.plan if payment.subscription else "Standard"

        if payment.status == "completed":
            # SMS de confirmation
            if user.phone_number:
                await send_payment_confirmation_sms(
                    to_number=user.phone_number,
                    full_name=user.full_name,
                    amount=payment.amount,
                    currency=payment.currency,
                    plan=plan_name,
                    transaction_ref=payment.transaction_ref,
                )
            # Email de confirmation
            send_payment_confirmation_email(
                to_email=user.email,
                full_name=user.full_name,
                amount=payment.amount,
                currency=payment.currency,
                plan=plan_name,
                transaction_ref=payment.transaction_ref,
            )

        elif payment.status == "failed":
            # SMS d'echec
            if user.phone_number:
                await send_payment_failed_sms(
                    to_number=user.phone_number,
                    full_name=user.full_name,
                    amount=payment.amount,
                    currency=payment.currency,
                )
            # Email d'echec
            send_payment_failed_email(
                to_email=user.email,
                full_name=user.full_name,
                amount=payment.amount,
                currency=payment.currency,
            )

    return {
        "status": "received",
        "payment_status": payment.status,
        "transaction_ref": payment.transaction_ref,
    }
