from typing import Annotated

from fastapi import Depends

from app.core.database import async_session
from app.utils.unitofwork import UnitOfWork


async def get_uow():
    uow = UnitOfWork(async_session)
    async with uow:
        yield uow


UOWDep = Annotated[UnitOfWork, Depends(get_uow)]
