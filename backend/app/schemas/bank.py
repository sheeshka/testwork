from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class AcquiringStartRequest(BaseModel):
    """Запрос на создание платежа в банке"""
    order_id: str
    amount: Decimal = Field(max_digits=12, decimal_places=2)


class AcquiringStartResponse(BaseModel):
    """Ответ банка на создание платежа"""
    payment_id: str


class AcquiringCheckResponse(BaseModel):
    """Ответ банка на проверку статуса платежа"""
    payment_id: str
    amount: Decimal
    status: str
    paid_at: datetime | None = None
