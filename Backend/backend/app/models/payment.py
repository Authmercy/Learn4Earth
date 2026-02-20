import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.database import Base


class Payment(Base):
    __tablename__ = "payments"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False)
    subscription_id = Column(String(36), ForeignKey("subscriptions.id"), nullable=False)
    amount = Column(Float, nullable=False)
    currency = Column(String(10), default="USD")
    payment_method = Column(String(50), nullable=False)  # carte_bancaire, mobile_money
    status = Column(String(30), default="pending")  # pending, completed, failed, refunded
    transaction_ref = Column(String(255), unique=True, nullable=False)
    invoice_number = Column(String(100), unique=True, nullable=False)
    invoice_details = Column(Text, nullable=True)
    paid_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Moko Checkout / FreshPay
    moko_transaction_uuid = Column(String(255), nullable=True, index=True)
    moko_payment_url = Column(Text, nullable=True)

    # Relations
    user = relationship("User", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
