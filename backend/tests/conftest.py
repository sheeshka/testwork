import uuid
from datetime import datetime
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.core.enums import PaymentStatus, PaymentType, TransactionStatus


def make_order(amount=Decimal("1000.00"), payment_status=PaymentStatus.NOT_PAID):
    order = MagicMock()
    order.id = uuid.uuid4()
    order.amount = amount
    order.payment_status = payment_status
    return order


def make_payment(
    order_id=None,
    payment_type=PaymentType.CASH,
    status=TransactionStatus.COMPLETED,
    amount=Decimal("500.00"),
    bank_payment_id=None,
):
    payment = MagicMock()
    payment.id = uuid.uuid4()
    payment.order_id = order_id or uuid.uuid4()
    payment.type = payment_type
    payment.status = status
    payment.amount = amount
    payment.bank_payment_id = bank_payment_id
    payment.paid_at = datetime.utcnow() if status == TransactionStatus.COMPLETED else None
    return payment


@pytest.fixture
def uow():
    uow = AsyncMock()
    uow.orders = AsyncMock()
    uow.payments = AsyncMock()
    return uow
