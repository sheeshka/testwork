from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.core.enums import PaymentType, TransactionStatus


class PaymentCreate(BaseModel):
    """Депозит — создание платежа по заказу"""
    order_id: UUID
    type: PaymentType
    amount: Decimal

    @field_validator("amount")
    @classmethod
    def amount_must_be_positive(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Сумма должна быть больше нуля")
        return v


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
