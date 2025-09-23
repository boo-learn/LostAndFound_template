from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from pydantic import BaseModel

from database import get_session
import models
import schemas
from services.storage import BaseCRUD

router = APIRouter()


@router.post("/", response_model=schemas.TagRead)
async def create_tag(tag: schemas.TagCreate, session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Tag)
    db_tag = await crud.create(session, tag.model_dump())
    return db_tag


@router.get("/", response_model=list[schemas.TagRead])
async def read_tags(session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Tag)
    tags = await crud.get_all(session)
    return tags


@router.get("/{tag_id}", response_model=schemas.TagRead)
async def read_tag(tag_id: int, session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Tag)
    tag = await crud.get_by_id(session, tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.put("/{tag_id}", response_model=schemas.TagRead)
async def update_tag(tag_id: int, tag_update: schemas.TagUpdate,
                     session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.Tag)
    tag = await crud.update(session, tag_id, tag_update.model_dump(exclude_unset=True))
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.delete("/{tag_id}", response_model=dict)
async def delete_tag(tag_id: int, session: AsyncSession = Depends(get_session)):
    raise NotImplementedError("Функция еще не реализована")


# --- Привязка/отвязка к LostItem ---
@router.put("/lost/{lost_item_id}", response_model=dict)
async def attach_tags_to_lost_item(
        lost_item_id: int, payload: schemas.TagIds,
        session: AsyncSession = Depends(get_session)):
    result = await session.execute(
        select(models.LostItem)
        .where(models.LostItem.id == lost_item_id)
        .options(selectinload(models.LostItem.tags))
    )
    lost_item_db = result.scalar_one_or_none()
    if not lost_item_db:
        raise HTTPException(status_code=404, detail="LostItem not found")
    tag_ids = payload.tag_ids
    results = await session.execute(
        select(models.Tag).where(models.Tag.id.in_(tag_ids))
    )
    tags = results.scalars().all()
    for tag in tags:
        lost_item_db.tags.append(tag)
    await session.commit()
    return {"success": True}


@router.delete("/{tag_id}/lost/{lost_item_id}", response_model=dict)
async def detach_tag_from_lost_item(tag_id: int, lost_item_id: int, session: AsyncSession = Depends(get_session)):
    raise NotImplementedError("Функция еще не реализована")


# --- Привязка/отвязка к FoundItem ---
@router.put("/found/{found_item_id}", response_model=dict)
async def attach_tags_to_found_item(found_item_id: int, payload: schemas.TagIds,
                                    session: AsyncSession = Depends(get_session)):
    raise NotImplementedError("Функция еще не реализована")


@router.delete("/{tag_id}/found/{found_item_id}", response_model=dict)
async def detach_tag_from_found_item(tag_id: int, found_item_id: int, session: AsyncSession = Depends(get_session)):
    raise NotImplementedError("Функция еще не реализована")
