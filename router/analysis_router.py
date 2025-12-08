from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db
from service.analysis_service import (
    get_monthly_summary,
    get_yearly_summary,
    get_period_summary,
    parse_date
)

router = APIRouter()


@router.get("/monthly/{symbol}")
def monthly(symbol: str, db: Session = Depends(get_db)):
    return get_monthly_summary(db, symbol)


@router.get("/yearly/{symbol}")
def yearly(symbol: str, db: Session = Depends(get_db)):
    return get_yearly_summary(db, symbol)


@router.get("/analysis/period/{symbol}")
def custom_period(symbol: str, start_date: str, end_date: str, db: Session = Depends(get_db)):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    return get_period_summary(db, symbol, start_date, end_date)
