from app.models.order import Order
from app.utils.repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository):
    model = Order
