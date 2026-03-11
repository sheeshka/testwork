from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.payment import PaymentCreate, PaymentRead, PaymentRefund
from app.services.payment import PaymentService
from app.utils.dependencies import UOWDep

router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()


@router.post("/deposit", response_model=PaymentRead, status_code=201)
async def deposit(data: PaymentCreate, uow: UOWDep):
    try:
        return await payment_service.deposit(
            uow, data.order_id, data.type, data.amount
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.post("/refund", response_model=PaymentRead)
async def refund(data: PaymentRefund, uow: UOWDep):
    try:
        return await payment_service.refund(uow, data.payment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{payment_id}/sync", response_model=PaymentRead)
async def sync_payment(payment_id: UUID, uow: UOWDep):
    try:
        return await payment_service.sync_payment(uow, payment_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=502, detail=str(e))


@router.get("/order/{order_id}", response_model=list[PaymentRead])
async def get_payments_by_order(order_id: UUID, uow: UOWDep):
    try:
        return await payment_service.get_payments_by_order(uow, order_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
