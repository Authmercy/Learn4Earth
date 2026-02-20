from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID


class SubscriptionCreate(BaseModel):
    plan: str  # mensuel, annuel
    payment_method: str  # carte_bancaire, mobile_money


class SubscriptionResponse(BaseModel):
    id: UUID
    user_id: UUID
    plan: str
    price: float
    currency: str
    is_active: bool
    start_date: datetime
    end_date: datetime
    auto_renew: bool
    created_at: datetime

    class Config:
        from_attributes = True
