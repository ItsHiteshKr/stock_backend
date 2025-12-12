from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from sqlalchemy import func, desc
from db.database import get_db
from model.stock import Stock
from model.daily_data import DailyData
from schema.stock_schema_UI import StockBase, PopularStockResponse

router = APIRouter(prefix="/stocks")


# -----------------------------------------
# 1️⃣ LIST ALL STOCKS
# -----------------------------------------
@router.get("/list", response_model=list[StockBase])
def list_stocks(db: Session = Depends(get_db)):
    stocks = db.query(Stock).all()
    return stocks


# -----------------------------------------
# 2️⃣ SEARCH STOCKS (symbol or name)
# /stocks/search?q=TAT
# -----------------------------------------
@router.get("/search", response_model=list[StockBase])
def search_stocks(q: str, db: Session = Depends(get_db)):
    result = db.query(Stock).filter(
        (Stock.symbol.like(f"%{q}%")) |
        (Stock.name.like(f"%{q}%"))
    ).all()

    return result


# -----------------------------------------
# 3️⃣ POPULAR STOCKS (based on high traded volume)
# -----------------------------------------
@router.get("/popular", response_model=list[PopularStockResponse])
def popular_stocks(limit: int = 20, db: Session = Depends(get_db)):
    from datetime import datetime, timedelta
    last_30 = datetime.now().date() - timedelta(days=30)

    result = (
        db.query(DailyData.symbol, func.sum(DailyData.volume).label("volume"))
        .filter(DailyData.date >= last_30)
        .group_by(DailyData.symbol)
        .order_by(func.sum(DailyData.volume).desc())
        .limit(limit)
        .all()
    )
    return [{"symbol": r[0], "volume": float(r[1])} for r in result]