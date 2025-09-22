from database import Base
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

class BaseCRUD:
    def __init__(self, model: type[Base]):
        self.model = model

    async def get_all(self, session: AsyncSession):
        stmp = select(self.model)
        results = await session.execute(stmp)
        objects = results.scalars().all()
        return objects

    async def create(self, session: AsyncSession, obj_data: dict):
        db_obj = self.model(**obj_data)
        session.add(db_obj)
        await session.commit()
        await session.refresh(db_obj)
        return db_obj