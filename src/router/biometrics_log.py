from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.biometrics_log import BiometricsLog
from src.schemas import BiometricsLogCreate, BiometricsLogRead

router = APIRouter(prefix="/biometrics-logs", tags=["biometrics-logs"])
DB = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=BiometricsLogRead, status_code=201)
def create_biometrics_log(biometrics_log: BiometricsLogCreate, db: DB):
    db_log = BiometricsLog(**biometrics_log.model_dump())
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


@router.get("/", response_model=list[BiometricsLogRead])
def get_biometrics_logs(db: DB, skip: int = 0, limit: int = 100):
    return db.query(BiometricsLog).offset(skip).limit(limit).all()


@router.get("/{log_id}", response_model=BiometricsLogRead)
def get_biometrics_log(log_id: int, db: DB):
    log = db.query(BiometricsLog).filter(BiometricsLog.Log_ID == log_id).first()
    if not log:
        raise HTTPException(404, "Biometrics log not found")
    return log


@router.put("/{log_id}", response_model=BiometricsLogRead)
def update_biometrics_log(log_id: int, payload: BiometricsLogCreate, db: DB):
    log = db.query(BiometricsLog).filter(BiometricsLog.Log_ID == log_id).first()
    if not log:
        raise HTTPException(404, "Biometrics log not found")
    for key, value in payload.model_dump().items():
        setattr(log, key, value)
    db.commit()
    db.refresh(log)
    return log


@router.delete("/{log_id}", status_code=204)
def delete_biometrics_log(log_id: int, db: DB):
    log = db.query(BiometricsLog).filter(BiometricsLog.Log_ID == log_id).first()
    if not log:
        raise HTTPException(404, "Biometrics log not found")
    db.delete(log)
    db.commit()
