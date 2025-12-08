# router/nifty_router.py
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from service.screener_service import filter_stocks, advanced_filter, filter_by_sector, save_screener, list_screeners
from schema.stock_schema import ScreenerFilter, ScreenerAdvanced

router = APIRouter()

@router.post("/screener/filter")
def screener_filter(
    min_price: float = Query(0),
    max_price: float = Query(1e6),
    min_pe: float = Query(0),
    max_pe: float = Query(1000),
    db: Session = Depends(get_db)
):
    return filter_stocks(db, min_price, max_price, min_pe, max_pe)

@router.post("/screener/advanced")
def screener_advanced(filter: ScreenerAdvanced, db: Session = Depends(get_db)):
    return advanced_filter(db, filter)

@router.get("/screener/sector/{sector}")
def screener_sector(sector: str, db: Session = Depends(get_db)):
    return filter_by_sector(db, sector)

@router.post("/screener/save")
def screener_save(filter: ScreenerFilter, db: Session = Depends(get_db)):
    return save_screener(db, filter)

@router.get("/screener/list")
def screener_list(db: Session = Depends(get_db)):
    return list_screeners(db)
