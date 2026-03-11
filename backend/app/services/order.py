from uuid import UUID

from app.utils.unitofwork import UnitOfWork


class OrderService:
    @staticmethod
    async def get_orders(uow: UnitOfWork):
        return await uow.orders.find_all()

    @staticmethod
    async def get_order(uow: UnitOfWork, order_id: UUID):
        order = await uow.orders.get_by_id(order_id)
        if not order:
            raise ValueError("Заказ не найден")
        return order
