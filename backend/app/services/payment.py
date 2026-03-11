from datetime import datetime
from decimal import Decimal
from uuid import UUID

from app.clients.bank import BankClient, BankClientError
from app.core.enums import PaymentStatus, PaymentType, TransactionStatus
from app.utils.unitofwork import UnitOfWork


class PaymentService:
    def __init__(self):
        self.bank_client = BankClient()

    async def deposit(self, uow: UnitOfWork, order_id: UUID, payment_type: PaymentType, amount: Decimal):
        order = await uow.orders.get_by_id(order_id)
        if not order:
            raise ValueError("Заказ не найден")

        paid_sum = await self._get_paid_sum(uow, order_id)
        if paid_sum + amount > order.amount:
            raise ValueError("Сумма платежей превышает сумму заказа")

        if payment_type == PaymentType.ACQUIRING:
            try:
                bank_response = await self.bank_client.acquiring_start(
                    order_id=str(order_id), amount=amount
                )
            except BankClientError as e:
                raise RuntimeError(e.message)

            payment = await uow.payments.create(
                order_id=order_id,
                type=payment_type,
                status=TransactionStatus.PENDING,
                amount=amount,
                bank_payment_id=bank_response.payment_id,
            )
        else:
            payment = await uow.payments.create(
                order_id=order_id,
                type=payment_type,
                status=TransactionStatus.COMPLETED,
                amount=amount,
                paid_at=datetime.utcnow(),
            )

        await self._recalculate_order_status(uow, order)
        return payment

    async def refund(self, uow: UnitOfWork, payment_id: UUID):
        payment = await uow.payments.get_by_id(payment_id)
        if not payment:
            raise ValueError("Платёж не найден")

        if payment.status != TransactionStatus.COMPLETED:
            raise ValueError("Возврат возможен только для завершённых платежей")

        await uow.payments.update(payment_id, status=TransactionStatus.REFUNDED)

        order = await uow.orders.get_by_id(payment.order_id)
        await self._recalculate_order_status(uow, order)
        return await uow.payments.get_by_id(payment_id)

    async def sync_payment(self, uow: UnitOfWork, payment_id: UUID):
        payment = await uow.payments.get_by_id(payment_id)
        if not payment:
            raise ValueError("Платёж не найден")

        if not payment.bank_payment_id:
            raise ValueError("Платёж не является банковским")

        try:
            bank_data = await self.bank_client.acquiring_check(payment.bank_payment_id)
        except BankClientError as e:
            raise RuntimeError(e.message)

        update_data = {"status": bank_data.status}
        if bank_data.paid_at:
            update_data["paid_at"] = bank_data.paid_at

        await uow.payments.update(payment_id, **update_data)

        order = await uow.orders.get_by_id(payment.order_id)
        await self._recalculate_order_status(uow, order)
        return await uow.payments.get_by_id(payment_id)

    async def get_payments_by_order(self, uow: UnitOfWork, order_id: UUID):
        order = await uow.orders.get_by_id(order_id)
        if not order:
            raise ValueError("Заказ не найден")
        return await uow.payments.find_by_order(order_id)

    async def _get_paid_sum(self, uow: UnitOfWork, order_id: UUID) -> Decimal:
        payments = await uow.payments.find_by_order(order_id)
        return sum(
            p.amount for p in payments
            if p.status == TransactionStatus.COMPLETED
        )

    async def _recalculate_order_status(self, uow: UnitOfWork, order):
        paid_sum = await self._get_paid_sum(uow, order.id)

        if paid_sum == Decimal(0):
            new_status = PaymentStatus.NOT_PAID
        elif paid_sum >= order.amount:
            new_status = PaymentStatus.PAID
        else:
            new_status = PaymentStatus.PARTIALLY_PAID

        await uow.orders.update(order.id, payment_status=new_status)
