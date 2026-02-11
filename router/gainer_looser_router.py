from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from db.database import get_db
from model.index import IndexStock, Index
from model.stock import Stock
from model.daily_data import DailyData
from schema.gainer_looser_schema import IndexBase

router = APIRouter(prefix="/indices")


# Helper: calculate percent change for latest day
def get_latest_percent_change(db: Session, stock_ids: list[int]):
    """
    Returns a dict {stock_id: percent_change} for the latest available day
    """
    changes = {}
    for stock_id in stock_ids:
        # Get last 2 days of close
        data = (
            db.query(DailyData)
            .filter(DailyData.stock_id == stock_id)
            .order_by(DailyData.date.desc())
            .limit(2)
            .all()
        )
        if len(data) < 2:
            continue
        today_close = data[0].close
        prev_close = data[1].close
        percent_change = ((today_close - prev_close) / prev_close) * 100
        changes[stock_id] = percent_change
    return changes


# -----------------------------------------
# GET TOP GAINERS
# /indices/{index_name}/gainers?limit=5
# -----------------------------------------
@router.get("/{index_name}/gainers", response_model=list[IndexBase])
def top_gainers(index_name: str, limit: int = Query(5, ge=1), db: Session = Depends(get_db)):
    # Get all stock_ids for the index
    stock_ids = (
        db.query(IndexStock.stock_id)
        .join(Index)
        .filter(Index.name == index_name)
        .all()
    )
    stock_ids = [s[0] for s in stock_ids]

    changes = get_latest_percent_change(db, stock_ids)
    top_ids = sorted(changes.items(), key=lambda x: x[1], reverse=True)[:limit]

    # Fetch stock info
    result = db.query(Stock).filter(Stock.id.in_([s[0] for s in top_ids])).all()
    stock_map = {s.id: s for s in result}

    return [
        IndexBase(
            stock_symbol=stock_map[sid].symbol,
            stock_name=stock_map[sid].name,
            percent_change=round(change, 2)
        )
        for sid, change in top_ids
    ]


# -----------------------------------------
# GET TOP LOSERS
# /indices/{index_name}/losers?limit=5
# -----------------------------------------
@router.get("/{index_name}/losers", response_model=list[IndexBase])
def top_losers(index_name: str, limit: int = Query(5, ge=1), db: Session = Depends(get_db)):
    # Get all stock_ids for the index
    stock_ids = (
        db.query(IndexStock.stock_id)
        .join(Index)
        .filter(Index.name == index_name)
        .all()
    )
    stock_ids = [s[0] for s in stock_ids]

    changes = get_latest_percent_change(db, stock_ids)
    bottom_ids = sorted(changes.items(), key=lambda x: x[1])[:limit]

    # Fetch stock info
    result = db.query(Stock).filter(Stock.id.in_([s[0] for s in bottom_ids])).all()
    stock_map = {s.id: s for s in result}

    return [
        IndexBase(
            stock_symbol=stock_map[sid].symbol,
            stock_name=stock_map[sid].name,
            percent_change=round(change, 2)
        )
        for sid, change in bottom_ids
    ]
