import schemas
import models
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import get_session
from utils import get_object_or_404
from services.storage import BaseCRUD

router = APIRouter()


@router.post("/", response_model=schemas.FoundItem)
async def create_found_item(item: schemas.FoundItemCreate, session: AsyncSession = Depends(get_session)):
    db_item = models.FoundItem(**item.model_dump())
    session.add(db_item)
    await session.commit()
    await session.refresh(db_item)
    return db_item


@router.get("/", response_model=list[schemas.FoundItem])
async def read_found_items(session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.FoundItem)
    items = await crud.get_all(session)
    return items


@router.get("/{item_id}", response_model=schemas.FoundItem)
async def read_found_item(item_id: int, session: AsyncSession = Depends(get_session)):
    db_item = await get_object_or_404(session, models.FoundItem, item_id)
    return db_item


@router.put("/{item_id}", response_model=schemas.FoundItem)
async def update_found_item(item_id: int, item: schemas.FoundItemUpdate, session: AsyncSession = Depends(get_session)):
    # TODO: доработайте функцию, чтобы все тесты на нее проходили
    db_item = await get_object_or_404(session, models.FoundItem, item_id)
    for field, value in item.model_dump(exclude_none=True).items():
        setattr(db_item, field, value)
    await session.commit()
    await session.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
async def delete_found_item(item_id: int, session: AsyncSession = Depends(get_session)):
    # TODO: напишите реализацию функции
    raise NotImplementedError("Функция еще не реализована")
