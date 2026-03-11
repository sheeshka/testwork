from abc import ABC, abstractmethod
from typing import Any

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession


class AbstractRepository(ABC):
    @abstractmethod
    async def create(self, **kwargs) -> Any: ...

    @abstractmethod
    async def get_by_id(self, id: Any) -> Any | None: ...

    @abstractmethod
    async def get_by_field(self, field: str, value: Any) -> Any | None: ...

    @abstractmethod
    async def find_all(self, skip: int = 0, limit: int = 100) -> list[Any]: ...

    @abstractmethod
    async def update(self, id: Any, **kwargs) -> Any | None: ...

    @abstractmethod
    async def count(self) -> int: ...

    @abstractmethod
    async def delete(self, id: Any) -> bool: ...


class SQLAlchemyRepository(AbstractRepository):
    model = None

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.model is None:
            raise TypeError(f"{cls.__name__} must define 'model' attribute")

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, **kwargs) -> Any:
        instance = self.model(**kwargs)
        self.session.add(instance)
        await self.session.flush()
        return instance

    async def get_by_id(self, id: Any) -> Any | None:
        return await self.session.get(self.model, id)

    async def get_by_field(self, field: str, value: Any) -> Any | None:
        if not hasattr(self.model, field):
            raise ValueError(f"{self.model.__name__} has no field '{field}'")
        stmt = select(self.model).where(getattr(self.model, field) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def find_all(self, skip: int = 0, limit: int = 100) -> list[Any]:
        stmt = select(self.model).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def update(self, id: Any, **kwargs) -> Any | None:
        instance = await self.session.get(self.model, id)
        if not instance:
            return None
        for key, value in kwargs.items():
            setattr(instance, key, value)
        await self.session.flush()
        return instance

    async def count(self) -> int:
        stmt = select(func.count()).select_from(self.model)
        result = await self.session.execute(stmt)
        return result.scalar_one()

    async def delete(self, id: Any) -> bool:
        stmt = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(stmt)
        return result.rowcount > 0
