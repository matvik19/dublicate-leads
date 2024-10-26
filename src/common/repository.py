from abc import ABC, abstractmethod
from typing import TypeVar, Generic, Protocol
from sqlalchemy import insert, select, update, delete
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.common.database import async_session_maker


class HasId(Protocol):
    id: int


T = TypeVar("T", bound=HasId)


class AbstractRepository(ABC, Generic[T]):
    @abstractmethod
    async def add_one(self, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def find_one(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def find_all(self):
        raise NotImplementedError

    @abstractmethod
    async def update_one(self, id: int, data: dict):
        raise NotImplementedError

    @abstractmethod
    async def delete_one(self, id: int):
        raise NotImplementedError

    @abstractmethod
    async def find_one_or_create(self, **kwargs):
        raise NotImplementedError


class SQLAlchemyRepository(AbstractRepository[T]):
    model: type[T]

    async def add_one(self, data: dict) -> int:
        async with async_session_maker() as session:
            stmt = insert(self.model).values(**data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def find_one(self, id: int):
        async with async_session_maker() as session:
            stmt = select(self.model).where(self.model.id == id)
            res = await session.execute(stmt)
            return res.scalar_one()

    async def find_all(self):
        async with async_session_maker() as session:
            stmt = select(self.model)
            res = await session.execute(stmt)
            return res.scalars().all()

    async def update_one(self, id: int, data: dict):
        async with async_session_maker() as session:
            stmt = update(self.model).where(self.model.id == id).values(**data).returning(self.model)
            res = await session.execute(stmt)
            await session.commit()
            return res.scalar_one()

    async def delete_one(self, id: int):
        async with async_session_maker() as session:
            stmt = delete(self.model).where(self.model.id == id)
            res = await session.execute(stmt)
            await session.commit()
            if res.rowcount == 0:
                raise Exception

    async def find_one_or_create(self, **kwargs):
        async with async_session_maker() as session:
            stmt = select(self.model).filter_by(**kwargs)
            res = (await session.execute(stmt)).scalar_one_or_none()
            if res:
                return res
            try:
                insert_dict = kwargs.copy()
                stmt = insert(self.model).values(**insert_dict).returning(self.model)
                res = await session.execute(stmt)
                await session.commit()
                return res.scalar_one()
            except Exception:
                await session.rollback()
                stmt = select(self.model).filter_by(**kwargs)
                res = await session.execute(stmt)
                return res.scalar_one()

    async def classical_insert_or_update(self, unique_columns: list, data: dict):
        async with async_session_maker() as session:
            stmt = pg_insert(self.model).values(**data).returning(self.model)
            do_update_stmt = stmt.on_conflict_do_update(index_elements=unique_columns, set_=data)
            res = await session.execute(do_update_stmt)
            await session.commit()
            return res.scalar_one()
