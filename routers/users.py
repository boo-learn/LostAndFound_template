from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_session
import models
import schemas
from services.storage import BaseCRUD
from services.auth import get_password_hash, get_current_user


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=schemas.UserRead, status_code=status.HTTP_201_CREATED)
async def create_user(user: schemas.UserCreate, session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.User)
    # Проверка уникальности username
    result = await session.execute(select(models.User).where(models.User.username == user.username))
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    data = user.model_dump()
    password = data.pop("password")
    data["hashed_password"] = get_password_hash(password)
    db_user = await crud.create(session, data)
    return db_user


@router.get("/", response_model=list[schemas.UserRead])
async def read_users(session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.User)
    users = await crud.get_all(session)
    return users


@router.get("/{user_id}", response_model=schemas.UserRead)
async def read_user(user_id: int, session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.User)
    user = await crud.get_by_id(session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=schemas.UserRead)
async def update_user(user_id: int, user_update: schemas.UserUpdate, session: AsyncSession = Depends(get_session)):
    crud = BaseCRUD(models.User)
    data = user_update.model_dump(exclude_unset=True)
    if "password" in data and data["password"] is not None:
        data["hashed_password"] = get_password_hash(data.pop("password"))
    user = await crud.update(session, user_id, data)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
        user_id: int, session: AsyncSession = Depends(get_session),
        current_user:models.User = Depends(get_current_user)
):
    crud = BaseCRUD(models.User)
    res = await crud.delete(session, user_id)
    if res is None:
        raise HTTPException(status_code=404, detail="User not found")
    return {"success": True}

