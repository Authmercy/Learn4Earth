"""
Service de gestion des paiements et abonnements.

Deux flux :
1. Carte bancaire (Moko Checkout) : paiement asynchrone
   - Creer abonnement + payment en statut "pending"
   - Initier le paiement via l'API Moko -> URL de redirection
   - Le callback Moko confirme le paiement -> statut "completed"

2. Mobile Money : paiement simule (synchrone)
   - Creer abonnement + payment directement en statut "completed"
"""

import uuid
import logging
from datetime import datetime, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.subscription import Subscription
from app.models.subscription_plan import SubscriptionPlan
from app.models.payment import Payment
from app.services.moko_service import initiate_card_payment

logger = logging.getLogger(__name__)

# Pricing par defaut (utilise si aucun plan n'existe en DB)
PLANS_DEFAULT = {
    "mensuel": {"price": 9.99, "duration_days": 30},
    "annuel": {"price": 89.99, "duration_days": 365},
}


def get_plan_info(db: Session, plan_code: str) -> dict:
    """
    Recuperer les informations d'un plan depuis la base de donnees.
    Si le plan n'existe pas en DB, utiliser les valeurs par defaut.
    """
    db_plan = db.query(SubscriptionPlan).filter(
        SubscriptionPlan.code == plan_code,
        SubscriptionPlan.is_active == True,
    ).first()

    if db_plan:
        return {
            "price": db_plan.price,
            "duration_days": db_plan.duration_days,
            "currency": db_plan.currency,
            "name": db_plan.name,
        }

    # Fallback sur les plans par defaut
    if plan_code in PLANS_DEFAULT:
        return {
            **PLANS_DEFAULT[plan_code],
            "currency": "USD",
            "name": plan_code.capitalize(),
        }

    return None


def get_all_active_plans(db: Session) -> list:
    """Recuperer tous les plans actifs depuis la DB, avec fallback."""
    db_plans = (
        db.query(SubscriptionPlan)
        .filter(SubscriptionPlan.is_active == True)
        .order_by(SubscriptionPlan.sort_order, SubscriptionPlan.price)
        .all()
    )

    if db_plans:
        return [
            {
                "code": p.code,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "currency": p.currency,
                "duration_days": p.duration_days,
                "features": p.features,
            }
            for p in db_plans
        ]

    # Fallback
    return [
        {"code": "mensuel", "name": "Mensuel", "price": 9.99, "currency": "USD", "duration_days": 30, "description": None, "features": None},
        {"code": "annuel", "name": "Annuel", "price": 89.99, "currency": "USD", "duration_days": 365, "description": None, "features": None},
    ]


def _generate_refs() -> tuple[str, str]:
    """Generer un numero de facture et une reference de transaction uniques."""
    now = datetime.utcnow()
    invoice_number = f"ECO-{now.strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
    transaction_ref = f"TXN-{str(uuid.uuid4())[:12].upper()}"
    return invoice_number, transaction_ref


def _build_invoice(
    invoice_number: str,
    plan: str,
    amount: float,
    currency: str,
    payment_method: str,
    transaction_ref: str,
    status: str = "completed",
) -> str:
    """Generer le texte de la facture."""
    now = datetime.utcnow()
    return (
        f"EcoLearn AI - Facture\n"
        f"{'=' * 40}\n"
        f"Numero de facture : {invoice_number}\n"
        f"Date : {now.strftime('%d/%m/%Y %H:%M')}\n"
        f"Plan : {plan.capitalize()}\n"
        f"Montant : {amount:.2f} {currency}\n"
        f"Methode : {payment_method.replace('_', ' ').title()}\n"
        f"Reference transaction : {transaction_ref}\n"
        f"Statut : {status}\n"
        f"{'=' * 40}\n"
        f"Merci pour votre abonnement !"
    )


# ── Flux Mobile Money (synchrone) ─────────────────────

def create_subscription_mobile_money(
    db: Session,
    user_id,
    plan: str,
) -> tuple[Subscription, Payment]:
    """
    Creer un abonnement avec paiement Mobile Money (simule, immediat).
    Le paiement est directement marque comme completed.
    """
    plan_info = get_plan_info(db, plan)
    if not plan_info:
        raise ValueError(f"Plan invalide ou inactif: {plan}.")
    now = datetime.utcnow()

    currency = plan_info.get("currency", "USD")

    # Creer l'abonnement (actif immediatement)
    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        price=plan_info["price"],
        currency=currency,
        is_active=True,
        start_date=now,
        end_date=now + timedelta(days=plan_info["duration_days"]),
        auto_renew=True,
    )
    db.add(subscription)
    db.flush()

    invoice_number, transaction_ref = _generate_refs()

    payment = Payment(
        user_id=user_id,
        subscription_id=subscription.id,
        amount=plan_info["price"],
        currency=currency,
        payment_method="mobile_money",
        status="completed",
        transaction_ref=transaction_ref,
        invoice_number=invoice_number,
        invoice_details=_build_invoice(
            invoice_number, plan, plan_info["price"], currency,
            "mobile_money", transaction_ref, "completed",
        ),
        paid_at=now,
    )
    db.add(payment)
    db.commit()
    db.refresh(subscription)
    db.refresh(payment)

    return subscription, payment


# ── Flux Carte Bancaire via Moko (asynchrone) ─────────

def create_subscription_pending(
    db: Session,
    user_id,
    plan: str,
) -> tuple[Subscription, Payment]:
    """
    Creer un abonnement et un paiement en attente (pending).
    L'abonnement sera active une fois le callback Moko recu.
    """
    plan_info = get_plan_info(db, plan)
    if not plan_info:
        raise ValueError(f"Plan invalide ou inactif: {plan}.")
    now = datetime.utcnow()

    currency = plan_info.get("currency", "USD")

    # Creer l'abonnement (inactif en attendant le paiement)
    subscription = Subscription(
        user_id=user_id,
        plan=plan,
        price=plan_info["price"],
        currency=currency,
        is_active=False,
        start_date=now,
        end_date=now + timedelta(days=plan_info["duration_days"]),
        auto_renew=True,
    )
    db.add(subscription)
    db.flush()

    invoice_number, transaction_ref = _generate_refs()

    payment = Payment(
        user_id=user_id,
        subscription_id=subscription.id,
        amount=plan_info["price"],
        currency=currency,
        payment_method="carte_bancaire",
        status="pending",
        transaction_ref=transaction_ref,
        invoice_number=invoice_number,
        invoice_details=_build_invoice(
            invoice_number, plan, plan_info["price"], currency,
            "carte_bancaire", transaction_ref, "pending",
        ),
    )
    db.add(payment)
    db.commit()
    db.refresh(subscription)
    db.refresh(payment)

    return subscription, payment


async def initiate_moko_payment(
    db: Session,
    payment: Payment,
    customer_first_name: str,
    customer_last_name: str,
    customer_email: str,
    customer_phone: str = "",
    billing_address: Optional[dict] = None,
) -> dict:
    """
    Appeler l'API Moko Checkout pour initier le paiement par carte.
    Met a jour le Payment avec le transaction_uuid et l'URL de paiement.
    """
    result = await initiate_card_payment(
        amount=payment.amount,
        currency=payment.currency,
        merchant_reference=payment.transaction_ref,
        customer_first_name=customer_first_name,
        customer_last_name=customer_last_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        billing_address=billing_address,
    )

    if result["success"]:
        payment.moko_transaction_uuid = result["transaction_uuid"]
        payment.moko_payment_url = result["payment_url"]
        db.commit()
        db.refresh(payment)

    return result


def confirm_moko_payment(
    db: Session,
    transaction_uuid: Optional[str] = None,
    merchant_reference: Optional[str] = None,
    callback_status: str = "completed",
) -> Optional[Payment]:
    """
    Confirmer un paiement apres reception du callback Moko.
    Active l'abonnement et genere la facture finale.
    """
    # Trouver le payment par transaction_uuid ou merchant_reference
    payment = None
    if transaction_uuid:
        payment = db.query(Payment).filter(Payment.moko_transaction_uuid == transaction_uuid).first()
    if not payment and merchant_reference:
        payment = db.query(Payment).filter(Payment.transaction_ref == merchant_reference).first()

    if not payment:
        logger.warning("Moko callback : paiement introuvable - uuid=%s, ref=%s", transaction_uuid, merchant_reference)
        return None

    if payment.status == "completed":
        logger.info("Moko callback : paiement deja confirme - ref=%s", payment.transaction_ref)
        return payment

    now = datetime.utcnow()

    if callback_status in ("completed", "ACCEPT", "approved", "success"):
        # Marquer le paiement comme complete
        payment.status = "completed"
        payment.paid_at = now

        # Mettre a jour la facture
        payment.invoice_details = _build_invoice(
            payment.invoice_number,
            payment.subscription.plan,
            payment.amount,
            payment.currency,
            "carte_bancaire",
            payment.transaction_ref,
            "completed",
        )

        # Activer l'abonnement
        subscription = payment.subscription
        subscription.is_active = True
        subscription.start_date = now
        plan_info = get_plan_info(db, subscription.plan)
        duration_days = plan_info["duration_days"] if plan_info else 30
        subscription.end_date = now + timedelta(days=duration_days)

        logger.info("Moko callback : paiement confirme - ref=%s, abonnement active", payment.transaction_ref)
    else:
        payment.status = "failed"
        payment.invoice_details = _build_invoice(
            payment.invoice_number,
            payment.subscription.plan,
            payment.amount,
            payment.currency,
            "carte_bancaire",
            payment.transaction_ref,
            "failed",
        )
        logger.warning("Moko callback : paiement echoue - ref=%s, status=%s", payment.transaction_ref, callback_status)

    db.commit()
    db.refresh(payment)
    return payment
