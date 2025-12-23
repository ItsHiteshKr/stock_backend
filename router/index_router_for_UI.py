from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from db.database import get_db
from model.index import IndexStock, Index
from model.stock import Stock

from schema.index_schema_UI import IndexBase
from datetime import datetime, timedelta

router = APIRouter(prefix="/indices",)

# -----------------------------------------
# 1️⃣ LIST ALL INDICES
# /indices/list
# -----------------------------------------
@router.get("/list", response_model=list[str])
def list_indices(db: Session = Depends(get_db)):
    result = db.query(Index.name).distinct().all()
    return [row[0] for row in result]

# -----------------------------------------
# 2️⃣ GET STOCKS UNDER A GIVEN INDEX
# /indices/{index_name}
# -----------------------------------------
@router.get("/{index_name}", response_model=list[IndexBase])
def index_stocks(index_name: str, db: Session = Depends(get_db)):
    # join IndexStock -> Index -> Stock
    result = (
        db.query(Stock.symbol.label("stock_symbol"), Stock.name.label("stock_name"))
        .join(IndexStock, IndexStock.stock_id == Stock.id)
        .join(Index, IndexStock.index_id == Index.id)
        .filter(Index.name == index_name)
        .all()
    )
    # convert to IndexBase objects
    return [IndexBase(stock_symbol=r.stock_symbol, stock_name=r.stock_name) for r in result]

# -----------------------------------------
# 3️⃣ SEARCH INSIDE AN INDEX
# /indices/search?index=NIFTY50&q=INF
# -----------------------------------------
@router.get("/search", response_model=list[IndexBase])
def search_index(index: str, q: str, db: Session = Depends(get_db)):
    result = (
        db.query(Stock.symbol.label("stock_symbol"), Stock.name.label("stock_name"))
        .join(IndexStock, IndexStock.stock_id == Stock.id)
        .join(Index, IndexStock.index_id == Index.id)
        .filter(
            Index.name == index,
            Stock.symbol.ilike(f"%{q}%")   # ilike for case-insensitive search
        )
        .all()
    )
    return [IndexBase(stock_symbol=r.stock_symbol, stock_name=r.stock_name) for r in result]
