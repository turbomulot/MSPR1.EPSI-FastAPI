from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import get_db
from src.models.user import User
from src.models.workout_session import WorkoutSession
from src.models.workout_type import WorkoutType
from src.schemas import WorkoutTypeCreate, WorkoutTypeRead

router = APIRouter(prefix="/workout-types", tags=["workout-types"])
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def ensure_admin(current_user: User) -> None:
    if not current_user.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can manage workout types",
        )


@router.post("/", response_model=WorkoutTypeRead, status_code=201)
def create_workout_type(payload: WorkoutTypeCreate, db: DB, current_user: CurrentUser):
    ensure_admin(current_user)

    existing = (
        db.query(WorkoutType)
        .filter(WorkoutType.WorkoutType_Name == payload.WorkoutType_Name)
        .first()
    )
    if existing:
        raise HTTPException(409, "Workout type already exists")

    workout_type = WorkoutType(**payload.model_dump())
    db.add(workout_type)
    db.commit()
    db.refresh(workout_type)
    return workout_type


@router.get("/", response_model=list[WorkoutTypeRead])
def get_workout_types(db: DB, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    return db.query(WorkoutType).order_by(WorkoutType.WorkoutType_ID.asc()).offset(skip).limit(limit).all()


@router.get("/{workout_type_id}", response_model=WorkoutTypeRead)
def get_workout_type(workout_type_id: int, db: DB, current_user: CurrentUser):
    workout_type = db.query(WorkoutType).filter(WorkoutType.WorkoutType_ID == workout_type_id).first()
    if not workout_type:
        raise HTTPException(404, "Workout type not found")
    return workout_type


@router.put("/{workout_type_id}", response_model=WorkoutTypeRead)
def update_workout_type(workout_type_id: int, payload: WorkoutTypeCreate, db: DB, current_user: CurrentUser):
    ensure_admin(current_user)

    workout_type = db.query(WorkoutType).filter(WorkoutType.WorkoutType_ID == workout_type_id).first()
    if not workout_type:
        raise HTTPException(404, "Workout type not found")

    duplicate = (
        db.query(WorkoutType)
        .filter(
            WorkoutType.WorkoutType_Name == payload.WorkoutType_Name,
            WorkoutType.WorkoutType_ID != workout_type_id,
        )
        .first()
    )
    if duplicate:
        raise HTTPException(409, "Workout type already exists")

    for key, value in payload.model_dump().items():
        setattr(workout_type, key, value)

    db.commit()
    db.refresh(workout_type)
    return workout_type


@router.delete("/{workout_type_id}", status_code=204)
def delete_workout_type(workout_type_id: int, db: DB, current_user: CurrentUser):
    ensure_admin(current_user)

    workout_type = db.query(WorkoutType).filter(WorkoutType.WorkoutType_ID == workout_type_id).first()
    if not workout_type:
        raise HTTPException(404, "Workout type not found")

    has_sessions = (
        db.query(WorkoutSession)
        .filter(WorkoutSession.WorkoutType_ID == workout_type_id)
        .first()
    )
    if has_sessions:
        raise HTTPException(409, "Workout type is used by existing workout sessions")

    db.delete(workout_type)
    db.commit()
