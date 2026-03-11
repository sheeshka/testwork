from uuid import UUID

from sqlalchemy import select

from app.models.payment import Payment
from app.utils.repository import SQLAlchemyRepository


class PaymentRepository(SQLAlchemyRepository):
    model = Payment

    async def find_by_order(self, order_id: UUID) -> list[Payment]:
        stmt = select(Payment).where(Payment.order_id == order_id)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
