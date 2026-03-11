from uuid import UUID

from fastapi import APIRouter, HTTPException

from app.schemas.order import OrderRead
from app.services.order import OrderService
from app.utils.dependencies import UOWDep

router = APIRouter(prefix="/orders", tags=["orders"])


@router.get("", response_model=list[OrderRead])
async def get_orders(uow: UOWDep):
    return await OrderService.get_orders(uow)


@router.get("/{order_id}", response_model=OrderRead)
async def get_order(order_id: UUID, uow: UOWDep):
    try:
        return await OrderService.get_order(uow, order_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
