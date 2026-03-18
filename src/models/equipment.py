from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from src.database import Base

class Equipment(Base):
    __tablename__ = "equipment"

    Equipment_ID = Column(Integer, primary_key=True, index=True)
    Equipment_Name = Column(String, index=True)
    Equipment_Category = Column(String, nullable=True)
    Equipment_Location = Column(String, nullable=True)

    users = relationship("User", secondary="user_equipment", back_populates="equipment")
