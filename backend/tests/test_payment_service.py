import uuid
from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.clients.bank import BankClientError
from app.core.enums import PaymentStatus, PaymentType, TransactionStatus
from app.schemas.bank import AcquiringStartResponse
from app.services.payment import NotFoundError, PaymentService
from tests.conftest import make_order, make_payment


@pytest.fixture
def service():
    svc = PaymentService()
    svc.bank_client = AsyncMock()
    return svc


# --- deposit ---

class TestDeposit:
    async def test_cash_deposit_creates_completed_payment(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = []
        uow.payments.create.return_value = make_payment(
            order_id=order.id, status=TransactionStatus.COMPLETED, amount=Decimal("500.00")
        )

        result = await service.deposit(uow, order.id, PaymentType.CASH, Decimal("500.00"))

        uow.payments.create.assert_called_once()
        call_kwargs = uow.payments.create.call_args.kwargs
        assert call_kwargs["status"] == TransactionStatus.COMPLETED
        assert call_kwargs["type"] == PaymentType.CASH
        assert result.status == TransactionStatus.COMPLETED

    async def test_deposit_order_not_found(self, uow, service):
        uow.orders.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Заказ не найден"):
            await service.deposit(uow, uuid.uuid4(), PaymentType.CASH, Decimal("100.00"))

    async def test_deposit_exceeds_order_amount(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = [
            make_payment(order_id=order.id, amount=Decimal("800.00"))
        ]

        with pytest.raises(ValueError, match="Сумма платежей превышает сумму заказа"):
            await service.deposit(uow, order.id, PaymentType.CASH, Decimal("300.00"))

    async def test_deposit_counts_pending_in_limit(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = [
            make_payment(order_id=order.id, status=TransactionStatus.PENDING, amount=Decimal("800.00"))
        ]

        with pytest.raises(ValueError, match="Сумма платежей превышает сумму заказа"):
            await service.deposit(uow, order.id, PaymentType.CASH, Decimal("300.00"))

    async def test_deposit_ignores_refunded_in_limit(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = [
            make_payment(order_id=order.id, status=TransactionStatus.REFUNDED, amount=Decimal("800.00"))
        ]
        uow.payments.create.return_value = make_payment(
            order_id=order.id, amount=Decimal("900.00")
        )

        result = await service.deposit(uow, order.id, PaymentType.CASH, Decimal("900.00"))
        assert result is not None

    async def test_acquiring_deposit_calls_bank(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = []
        service.bank_client.acquiring_start.return_value = AcquiringStartResponse(payment_id="bank_123")
        uow.payments.create.return_value = make_payment(
            order_id=order.id, status=TransactionStatus.PENDING, bank_payment_id="bank_123"
        )

        result = await service.deposit(uow, order.id, PaymentType.ACQUIRING, Decimal("500.00"))

        service.bank_client.acquiring_start.assert_called_once()
        call_kwargs = uow.payments.create.call_args.kwargs
        assert call_kwargs["status"] == TransactionStatus.PENDING
        assert call_kwargs["bank_payment_id"] == "bank_123"

    async def test_acquiring_deposit_bank_error(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = []
        service.bank_client.acquiring_start.side_effect = BankClientError("Банк недоступен")

        with pytest.raises(RuntimeError, match="Банк недоступен"):
            await service.deposit(uow, order.id, PaymentType.ACQUIRING, Decimal("500.00"))


# --- refund ---

class TestRefund:
    async def test_refund_completed_payment(self, uow, service):
        payment = make_payment(status=TransactionStatus.COMPLETED)
        order = make_order()
        uow.payments.get_by_id.return_value = payment
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = []

        refunded = make_payment(status=TransactionStatus.REFUNDED)
        uow.payments.get_by_id.side_effect = [payment, refunded]

        result = await service.refund(uow, payment.id)

        uow.payments.update.assert_called_once_with(payment.id, status=TransactionStatus.REFUNDED)
        assert result.status == TransactionStatus.REFUNDED

    async def test_refund_payment_not_found(self, uow, service):
        uow.payments.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Платёж не найден"):
            await service.refund(uow, uuid.uuid4())

    async def test_refund_non_completed_payment(self, uow, service):
        payment = make_payment(status=TransactionStatus.PENDING)
        uow.payments.get_by_id.return_value = payment

        with pytest.raises(ValueError, match="Возврат возможен только для завершённых платежей"):
            await service.refund(uow, payment.id)


# --- sync ---

class TestSync:
    async def test_sync_payment_not_found(self, uow, service):
        uow.payments.get_by_id.return_value = None

        with pytest.raises(NotFoundError, match="Платёж не найден"):
            await service.sync_payment(uow, uuid.uuid4())

    async def test_sync_non_bank_payment(self, uow, service):
        payment = make_payment(bank_payment_id=None)
        uow.payments.get_by_id.return_value = payment

        with pytest.raises(ValueError, match="Платёж не является банковским"):
            await service.sync_payment(uow, payment.id)

    async def test_sync_bank_error(self, uow, service):
        payment = make_payment(bank_payment_id="bank_123")
        uow.payments.get_by_id.return_value = payment
        service.bank_client.acquiring_check.side_effect = BankClientError("Банк не ответил: таймаут")

        with pytest.raises(RuntimeError, match="таймаут"):
            await service.sync_payment(uow, payment.id)


# --- recalculate order status ---

class TestRecalculateStatus:
    async def test_no_payments_sets_not_paid(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        uow.payments.find_by_order.return_value = []
        uow.payments.create.return_value = make_payment(
            order_id=order.id, amount=Decimal("100.00")
        )

        # deposit triggers recalculate; mock find_by_order to return [] for active_sum, then [] for paid_sum
        uow.payments.find_by_order.side_effect = [[], []]
        await service.deposit(uow, order.id, PaymentType.CASH, Decimal("100.00"))

        uow.orders.update.assert_called_once_with(order.id, payment_status=PaymentStatus.NOT_PAID)

    async def test_partial_payment_sets_partially_paid(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        created_payment = make_payment(order_id=order.id, amount=Decimal("500.00"))
        uow.payments.create.return_value = created_payment

        uow.payments.find_by_order.side_effect = [
            [],  # _get_active_sum
            [created_payment],  # _get_paid_sum
        ]

        await service.deposit(uow, order.id, PaymentType.CASH, Decimal("500.00"))
        uow.orders.update.assert_called_once_with(order.id, payment_status=PaymentStatus.PARTIALLY_PAID)

    async def test_full_payment_sets_paid(self, uow, service):
        order = make_order(amount=Decimal("1000.00"))
        uow.orders.get_by_id.return_value = order
        created_payment = make_payment(order_id=order.id, amount=Decimal("1000.00"))
        uow.payments.create.return_value = created_payment

        uow.payments.find_by_order.side_effect = [
            [],  # _get_active_sum
            [created_payment],  # _get_paid_sum
        ]

        await service.deposit(uow, order.id, PaymentType.CASH, Decimal("1000.00"))
        uow.orders.update.assert_called_once_with(order.id, payment_status=PaymentStatus.PAID)
