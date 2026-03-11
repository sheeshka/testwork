from abc import ABC, abstractmethod
from typing import Type

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.repositories.order import OrderRepository
from app.repositories.payment import PaymentRepository
from app.utils.repository import AbstractRepository


class AbstractUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self): ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb): ...

    @abstractmethod
    async def commit(self): ...

    @abstractmethod
    async def rollback(self): ...


class UnitOfWork(AbstractUnitOfWork):
    _repo_map: dict[str, Type[AbstractRepository]] = {
        "orders": OrderRepository,
        "payments": PaymentRepository,
    }

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self._session_factory = session_factory

    async def __aenter__(self):
        self.session = self._session_factory()
        for attr_name, repo_class in self._repo_map.items():
            setattr(self, attr_name, repo_class(self.session))
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type:
                await self.rollback()
            else:
                await self.commit()
        finally:
            await self.session.close()

    async def commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()
