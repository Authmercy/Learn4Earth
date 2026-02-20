from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class PaymentResponse(BaseModel):
    id: UUID
    user_id: UUID
    subscription_id: UUID
    amount: float
    currency: str
    payment_method: str
    status: str
    transaction_ref: str
    invoice_number: str
    invoice_details: Optional[str]
    moko_transaction_uuid: Optional[str]
    moko_payment_url: Optional[str]
    paid_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class MokoCallbackPayload(BaseModel):
    """Schema pour le callback Moko Checkout."""
    transaction_uuid: Optional[str] = None
    merchant_reference: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None

    class Config:
        extra = "allow"  # Accepter des champs supplementaires du callback
