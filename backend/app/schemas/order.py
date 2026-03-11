from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.core.enums import PaymentStatus


class OrderRead(BaseModel):
    """Ответ с данными заказа"""
    id: UUID
    amount: Decimal = Field(max_digits=12, decimal_places=2)
    payment_status: PaymentStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
