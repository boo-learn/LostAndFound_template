from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from database import get_session
import models
import schemas
from services.storage import BaseCRUD

router = APIRouter()


@router.post("/", response_model=schemas.CategoryRead)
async def create_category(category: schemas.CategoryCreate, session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Category)
    db_category = await crud.create(session, category.model_dump())
    return db_category


@router.get("/", response_model=list[schemas.CategoryRead])
async def read_categories(session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Category)
    categories = await crud.get_all(session)
    return categories


@router.get("/{category_id}", response_model=schemas.CategoryRead)
async def read_category(category_id: int, session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Category)
    category = await crud.get_by_id(session, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.put("/{category_id}", response_model=schemas.CategoryRead)
async def update_category(category_id: int, category_update: schemas.CategoryUpdate,
                          session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Category)
    category = await crud.update(session, category_id, category_update.model_dump(exclude_unset=True))
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category


@router.delete("/{category_id}", response_model=dict)
async def delete_category(category_id: int, session: AsyncSession = Depends(get_session)):
    category = await session.execute(select(models.Category).where(models.Category.id == category_id))
    category = category.scalar_one_or_none()
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    await session.delete(category)
    await session.commit()
    return {"message": "Category deleted"}
