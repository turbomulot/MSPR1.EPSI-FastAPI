from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.schemas import UserCreate, UserRead

router = APIRouter(prefix="/users", tags=["users"])
DB = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db: DB):
    db_user = User(**user.model_dump())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.get("/", response_model=list[UserRead])
def get_users(db: DB, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: DB):
    user = db.query(User).filter(User.User_ID == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(user_id: int, payload: UserCreate, db: DB):
    user = db.query(User).filter(User.User_ID == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    for key, value in payload.model_dump().items():
        setattr(user, key, value)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: DB):
    user = db.query(User).filter(User.User_ID == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
