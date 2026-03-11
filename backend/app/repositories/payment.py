from app.models.payment import Payment
from app.utils.repository import SQLAlchemyRepository


class PaymentRepository(SQLAlchemyRepository):
    model = Payment
