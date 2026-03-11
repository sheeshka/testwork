from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

from app.core.enums import PaymentType, TransactionStatus


class PaymentCreate(BaseModel):
    """Депозит — создание платежа по заказу"""
    order_id: UUID
    type: PaymentType
    amount: Decimal


class PaymentRead(BaseModel):
    """Ответ с данными платежа"""
    id: UUID
    order_id: UUID
    type: PaymentType
    status: TransactionStatus
    amount: Decimal
    bank_payment_id: str | None = None
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaymentRefund(BaseModel):
    """Возврат платежа"""
    payment_id: UUID
