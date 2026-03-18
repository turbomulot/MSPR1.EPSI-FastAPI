from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.equipment import Equipment
from src.schemas import EquipmentCreate, EquipmentRead

router = APIRouter(prefix="/equipment", tags=["equipment"])
DB = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=EquipmentRead, status_code=201)
def create_equipment(equipment: EquipmentCreate, db: DB):
    db_equipment = Equipment(**equipment.model_dump())
    db.add(db_equipment)
    db.commit()
    db.refresh(db_equipment)
    return db_equipment


@router.get("/", response_model=list[EquipmentRead])
def get_equipment(db: DB, skip: int = 0, limit: int = 100):
    return db.query(Equipment).offset(skip).limit(limit).all()


@router.get("/{equipment_id}", response_model=EquipmentRead)
def get_equipment_by_id(equipment_id: int, db: DB):
    equipment = db.query(Equipment).filter(Equipment.Equipment_ID == equipment_id).first()
    if not equipment:
        raise HTTPException(404, "Equipment not found")
    return equipment


@router.put("/{equipment_id}", response_model=EquipmentRead)
def update_equipment(equipment_id: int, payload: EquipmentCreate, db: DB):
    equipment = db.query(Equipment).filter(Equipment.Equipment_ID == equipment_id).first()
    if not equipment:
        raise HTTPException(404, "Equipment not found")
    for key, value in payload.model_dump().items():
        setattr(equipment, key, value)
    db.commit()
    db.refresh(equipment)
    return equipment


@router.delete("/{equipment_id}", status_code=204)
def delete_equipment(equipment_id: int, db: DB):
    equipment = db.query(Equipment).filter(Equipment.Equipment_ID == equipment_id).first()
    if not equipment:
        raise HTTPException(404, "Equipment not found")
    db.delete(equipment)
    db.commit()
