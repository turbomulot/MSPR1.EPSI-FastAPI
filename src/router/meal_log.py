from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.meal_log import MealLog
from src.schemas import MealLogCreate, MealLogRead

router = APIRouter(prefix="/meal-logs", tags=["meal-logs"])
DB = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=MealLogRead, status_code=201)
def create_meal_log(meal_log: MealLogCreate, db: DB):
    db_log = MealLog(**meal_log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/", response_model=list[MealLogRead])
def get_meal_logs(db: DB, skip: int = 0, limit: int = 100):
    return db.query(MealLog).offset(skip).limit(limit).all()


@router.get("/{log_id}", response_model=MealLogRead)
def get_meal_log(log_id: int, db: DB):
    log = db.query(MealLog).filter(MealLog.Log_ID == log_id).first()
    if not log:
        raise HTTPException(404, "Meal log not found")
    return log


@router.put("/{log_id}", response_model=MealLogRead)
def update_meal_log(log_id: int, payload: MealLogCreate, db: DB):
    log = db.query(MealLog).filter(MealLog.Log_ID == log_id).first()
    if not log:
        raise HTTPException(404, "Meal log not found")
    for key, value in payload.model_dump().items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=204)
def delete_meal_log(log_id: int, db: DB):
    log = db.query(MealLog).filter(MealLog.Log_ID == log_id).first()
    if not log:
        raise HTTPException(404, "Meal log not found")
    db.delete(log)
    db.commit()
