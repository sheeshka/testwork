from decimal import Decimal
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.core.enums import PaymentType
from app.schemas.payment import PaymentCreate


class TestPaymentCreate:
    def test_valid_cash_payment(self):
        data = PaymentCreate(order_id=uuid4(), type=PaymentType.CASH, amount=Decimal("100.50"))
        assert data.amount == Decimal("100.50")

    def test_zero_amount_rejected(self):
        with pytest.raises(ValidationError, match="Сумма должна быть больше нуля"):
            PaymentCreate(order_id=uuid4(), type=PaymentType.CASH, amount=Decimal("0"))

    def test_negative_amount_rejected(self):
        with pytest.raises(ValidationError, match="Сумма должна быть больше нуля"):
            PaymentCreate(order_id=uuid4(), type=PaymentType.CASH, amount=Decimal("-50.00"))

    def test_too_many_digits_rejected(self):
        with pytest.raises(ValidationError):
            PaymentCreate(order_id=uuid4(), type=PaymentType.CASH, amount=Decimal("1234567890123.00"))

    def test_too_many_decimal_places_rejected(self):
        with pytest.raises(ValidationError):
            PaymentCreate(order_id=uuid4(), type=PaymentType.CASH, amount=Decimal("100.123"))

    def test_invalid_type_rejected(self):
        with pytest.raises(ValidationError):
            PaymentCreate(order_id=uuid4(), type="invalid", amount=Decimal("100.00"))
