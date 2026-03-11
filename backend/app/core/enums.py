from enum import StrEnum


class PaymentStatus(StrEnum):
    NOT_PAID = "not_paid"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"


class PaymentType(StrEnum):
    CASH = "cash"
    ACQUIRING = "acquiring"


class TransactionStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    REFUNDED = "refunded"
    FAILED = "failed"
