from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from service.comparison_service import (
    compare_stocks,
    compare_indicators,
    compare_performance
)

router = APIRouter()

# ---------------------------------------------------------
# 1️⃣ Compare multiple stock prices
# ---------------------------------------------------------
@router.post("/stocks")
def api_compare_stocks(symbols: list[str], db: Session = Depends(get_db)):
    if len(symbols) < 2 or len(symbols) > 5:
        raise HTTPException(400, "Provide between 2 and 5 symbols")

    return compare_stocks(db, symbols)


# ---------------------------------------------------------
# 2️⃣ Compare indicators
# ---------------------------------------------------------
@router.post("/indicators")
def api_compare_indicators(symbols: list[str], db: Session = Depends(get_db)):
    if len(symbols) < 2 or len(symbols) > 5:
        raise HTTPException(400, "Provide between 2 and 5 symbols")

    return compare_indicators(db, symbols)


# ---------------------------------------------------------
# 3️⃣ Performance comparison
# ---------------------------------------------------------
@router.post("/performance")
def api_compare_performance(symbols: list[str], db: Session = Depends(get_db)):
    if len(symbols) < 2 or len(symbols) > 5:
        raise HTTPException(400, "Provide between 2 and 5 symbols")

    return compare_performance(db, symbols)
