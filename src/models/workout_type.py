from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String

from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class WorkoutType(Base):
    __tablename__ = "workout_types"

    WorkoutType_ID = Column(Integer, primary_key=True, index=True)
    WorkoutType_Name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
