from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from db.batabase import get_db
from schema.nifty_schema import NiftyDataCreate, NiftyDataResponse, NiftyDataUpdate
from service import nifty_service

router = APIRouter(
    prefix="/nifty"
)


@router.post("/upload-csv")
def upload_csv(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload CSV file with Nifty stock data"""
    return nifty_service.upload_csv_data(file, db)


@router.post("/", response_model=NiftyDataResponse)
def create_nifty_data(nifty: NiftyDataCreate, db: Session = Depends(get_db)):
    """Create new Nifty data entry"""
    return nifty_service.create_nifty_data(nifty, db)


@router.get("/", response_model=List[NiftyDataResponse])
def get_all_nifty_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all Nifty data with pagination"""
    return nifty_service.get_all_nifty_data(db, skip, limit)


@router.get("/{date}", response_model=NiftyDataResponse)
def get_nifty_by_date(date: date, db: Session = Depends(get_db)):
    """Get Nifty data by specific date"""
    return nifty_service.get_nifty_by_date(date, db)


@router.put("/{date}", response_model=NiftyDataUpdate)
def update_nifty_data(date: date, nifty: NiftyDataUpdate, db: Session = Depends(get_db)):
    """Update Nifty data for a specific date"""
    return nifty_service.update_nifty_data(date, nifty, db)


@router.delete("/{date}")
def delete_nifty_data(date: date, db: Session = Depends(get_db)):
    """Delete Nifty data for a specific date"""
    return nifty_service.delete_nifty_data(date, db)
