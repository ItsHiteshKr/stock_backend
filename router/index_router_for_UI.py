from fastapi import APIRouter, Depends,Query
from sqlalchemy.orm import Session
from sqlalchemy import func,desc
from db.database import get_db
from model.index import IndexStock
from model.daily_data import DailyData

from schema.index_schema_UI import IndexBase, IndexListResponse, PopularIndexResponse
from datetime import datetime, timedelta

router = APIRouter(prefix="/indices",)

# -----------------------------------------
# 1️⃣ LIST ALL INDICES
# /indices/list
# -----------------------------------------
@router.get("/list", response_model=list[str])
def list_indices(db: Session = Depends(get_db)):
    result = db.query(IndexStock.index_name).distinct().all()
    return [row[0] for row in result]


# -----------------------------------------
# 2️⃣ GET STOCKS UNDER A GIVEN INDEX
# /indices/NIFTY50
# -----------------------------------------
@router.get("/{index_name}", response_model=list[IndexBase])
def index_stocks(index_name: str, db: Session = Depends(get_db)):
    result = db.query(IndexStock).filter(IndexStock.index_name == index_name).all()
    return result


# -----------------------------------------
# 3️⃣ SEARCH INSIDE AN INDEX
# /indices/search?index=NIFTY50&q=INF
# -----------------------------------------
@router.get("/search", response_model=list[IndexBase])
def search_index(index: str, q: str, db: Session = Depends(get_db)):
    result = db.query(IndexStock).filter(
        IndexStock.index_name == index,
        IndexStock.stock_symbol.like(f"%{q}%")
    ).all()
    return result




