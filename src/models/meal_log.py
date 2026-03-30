from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class MealLog(Base):
    __tablename__ = "meal_logs"

    Log_ID = Column(Integer, primary_key=True, index=True)
    User_ID = Column(Integer, ForeignKey("users.User_ID"))
    Product_ID = Column(Integer, ForeignKey("products.Product_ID"))
    Log_Date = Column(Date)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
