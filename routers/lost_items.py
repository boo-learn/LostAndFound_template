import schemas
import models
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session
from utils import get_object_or_404
from services.storage import BaseCRUD

router = APIRouter()


@router.post("/", response_model=schemas.LostItem)
async def create_lost_item(item: schemas.LostItemCreate, session: AsyncSession = Depends(get_session)):
    db_item = models.LostItem(**item.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item

# GET: lost_items?skip=10&limit=15
@router.get("/", response_model=list[schemas.LostItem])
async def read_lost_items(
        skip: int=0, limit: int=20,
        session: AsyncSession = Depends(get_session)
):
    crud = BaseCRUD(models.LostItem)
    items = await crud.get_all(session, skip, limit)
    # result = await session.execute(select(models.LostItem))
    # items = result.scalars().all()
    return items


@router.get("/{item_id}", response_model=schemas.LostItem)
async def read_lost_item(item_id: int, session: AsyncSession = Depends(get_session)):
    # TODO: напишите реализацию функции
    raise NotImplementedError("Функция еще не реализована")


@router.get("/search", response_model=list[schemas.LostItem])
async def search_lost_items(query: str, session: AsyncSession = Depends(get_session)):
    """
    Вернет список потерянных предметов, у которых имя, описание или местоположение содержат слово query.
    """
    # TODO: напишите реализацию функции
    raise NotImplementedError("Функция еще не реализована")


@router.put("/{item_id}", response_model=schemas.LostItem)
async def update_lost_item(item_id: int, item: schemas.LostItemUpdate, session: AsyncSession = Depends(get_session)):
    # TODO: доработайте функцию, чтобы все тесты на нее проходили
    db_item = await session.get(models.LostItem, item_id)
    for field, value in item.model_dump(exclude_none=True).items():
        setattr(db_item, field, value)
    await session.commit()
    await session.refresh(db_item)
    return db_item

# PUT /lost_items/1/category
# body:
# { "category_id": 456 }
@router.put("/{item_id}/category", response_model=schemas.LostItem)
async def update_lost_item_category(item_id: int, payload: schemas.LostItemCategoryUpdate, session: AsyncSession = Depends(get_session)):
    # TODO: напишите реализацию функции
    raise NotImplementedError("Функция еще не реализована")
    

@router.delete("/{item_id}")
async def delete_lost_item(item_id: int, session: AsyncSession = Depends(get_session)):
    # TODO: напишите реализацию функции
    raise NotImplementedError("Функция еще не реализована")
