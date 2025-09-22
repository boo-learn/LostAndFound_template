from typing import Sequence
from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BaseCRUD:
    def __init__(self, model: type[Base]):
        self.model = model

    async def get_by_id(self,session: AsyncSession, obj_id: int) -> Base | None:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(stmt)
        object = result.scalar_one_or_none()
        return object

    async def get_all(self, session: AsyncSession, skip:int=0, limit: int=20) -> Sequence[Base]:
        stmt = select(self.model).offset(skip).limit(limit)
        results = await session.execute(stmt)
        objects = results.scalars().all()
        return objects

    async def create(self, session: AsyncSession, obj_data: dict) -> Base:
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def update(self, session: AsyncSession,obj_id: int, new_obj_data: dict) -> type[Base] | None:
        db_obj = await session.get(self.model, obj_id)
        if db_obj is None:
            return None
        for field, value in new_obj_data.items():
            setattr(db_obj, field, value)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj

    async def delete(self, session: AsyncSession, obj_id: int) -> str | None:
        stmt = select(self.model).where(self.model.id == obj_id)
        result = await session.execute(stmt)
        category = result.scalar_one_or_none()
        if category is None:
            return None
        await session.delete(category)
        await session.commit()
        return "OK"