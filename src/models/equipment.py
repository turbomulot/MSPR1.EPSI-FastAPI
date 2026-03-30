from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Equipment(Base):
    __tablename__ = "equipment"

    Equipment_ID = Column(Integer, primary_key=True, index=True)
    Equipment_Name = Column(String, index=True)
    Equipment_Category = Column(String, nullable=True)
    Equipment_Location = Column(String, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    users = relationship("User", secondary="user_equipment", back_populates="equipment")
