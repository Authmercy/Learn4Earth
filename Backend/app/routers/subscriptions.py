from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.subscription import Subscription
from app.schemas.subscription import SubscriptionCreate, SubscriptionResponse
from app.schemas.payment import PaymentResponse
from app.services.payment_service import (
    create_subscription_mobile_money,
    create_subscription_pending,
    initiate_moko_payment,
    get_all_active_plans,
)
from app.services.sms_service import send_payment_confirmation_sms
from app.utils.security import get_current_user

router = APIRouter(prefix="/api/subscriptions", tags=["Abonnements"])


@router.get("/plans")
def get_plans(db: Session = Depends(get_db)):
    """Lister les plans d'abonnement disponibles (lus depuis la base de donnees)."""
    plans = get_all_active_plans(db)
    return {
        "plans": [
            {
                "code": p["code"],
                "name": p["name"],
                "description": p.get("description"),
                "price": p["price"],
                "currency": p["currency"],
                "duration_days": p["duration_days"],
                "features": p.get("features"),
            }
            for p in plans
        ],
        "payment_methods": [
            {"code": "carte_bancaire", "label": "Carte bancaire (Visa, Mastercard)", "provider": "Umoja / FreshPay"},
            {"code": "mobile_money", "label": "Mobile Money (Orange, MTN, Airtel, Wave)"},
        ],
    }


@router.post("/subscribe", response_model=dict)
async def subscribe(
    sub_data: SubscriptionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Souscrire a un abonnement.

    - **carte_bancaire** : initie un paiement via Moko Checkout.
      Retourne une URL de redirection vers la page de paiement securisee.
      L'abonnement sera active automatiquement apres confirmation du paiement.

    - **mobile_money** : paiement simule et abonnement active immediatement.
    """
    if sub_data.payment_method not in ("carte_bancaire", "mobile_money"):
        raise HTTPException(
            status_code=400,
            detail="Methode de paiement invalide. Utilisez 'carte_bancaire' ou 'mobile_money'.",
        )

    try:
        if sub_data.payment_method == "mobile_money":
            # ── Flux Mobile Money : paiement immediat ──
            subscription, payment = create_subscription_mobile_money(
                db=db,
                user_id=current_user.id,
                plan=sub_data.plan,
            )

            # Envoyer SMS de confirmation de paiement
            if current_user.phone_number:
                await send_payment_confirmation_sms(
                    to_number=current_user.phone_number,
                    full_name=current_user.full_name,
                    amount=payment.amount,
                    currency=payment.currency,
                    plan=sub_data.plan,
                    transaction_ref=payment.transaction_ref,
                )

            return {
                "message": f"Abonnement {sub_data.plan} active avec succes !",
                "payment_method": "mobile_money",
                "status": "completed",
                "subscription": SubscriptionResponse.model_validate(subscription),
                "payment": PaymentResponse.model_validate(payment),
            }

        else:
            # ── Flux Carte Bancaire : paiement via Moko Checkout ──

            # 1. Creer l'abonnement et le paiement en attente
            subscription, payment = create_subscription_pending(
                db=db,
                user_id=current_user.id,
                plan=sub_data.plan,
            )

            # 2. Extraire prenom/nom du full_name
            name_parts = current_user.full_name.strip().split(" ", 1)
            first_name = name_parts[0]
            last_name = name_parts[1] if len(name_parts) > 1 else first_name

            # 3. Recuperer le telephone et l'adresse de l'utilisateur
            from app.utils.encryption import decrypt_optional
            customer_phone = current_user.phone_number or "+000000000"
            billing_address = {
                "line1": decrypt_optional(current_user.encrypted_address_line) or "N/A",
                "city": decrypt_optional(current_user.encrypted_address_city) or "N/A",
                "state": decrypt_optional(current_user.encrypted_address_city) or "N/A",
                "postal_code": decrypt_optional(current_user.encrypted_address_postal_code) or "00000",
                "country": decrypt_optional(current_user.encrypted_address_country) or "CD",
            }

            # 4. Initier le paiement via l'API Moko
            moko_result = await initiate_moko_payment(
                db=db,
                payment=payment,
                customer_first_name=first_name,
                customer_last_name=last_name,
                customer_email=current_user.email,
                customer_phone=customer_phone,
                billing_address=billing_address,
            )

            if moko_result["success"]:
                return {
                    "message": "Paiement initie. Completez le paiement via le lien ci-dessous.",
                    "payment_method": "carte_bancaire",
                    "status": "pending",
                    "payment_url": moko_result["payment_url"],
                    "transaction_uuid": moko_result["transaction_uuid"],
                    "subscription": SubscriptionResponse.model_validate(subscription),
                    "payment": PaymentResponse.model_validate(payment),
                }
            else:
                # Echec d'initiation : marquer le paiement comme echoue
                payment.status = "failed"
                db.commit()
                raise HTTPException(
                    status_code=502,
                    detail=f"Echec de l'initiation du paiement : {moko_result.get('error', 'Erreur inconnue')}",
                )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/my", response_model=List[SubscriptionResponse])
def get_my_subscriptions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lister mes abonnements."""
    return (
        db.query(Subscription)
        .filter(Subscription.user_id == current_user.id)
        .order_by(Subscription.created_at.desc())
        .all()
    )
