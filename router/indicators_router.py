from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from db.database import get_db
from service.analysis_service import (
    get_price_dataframe,
    calculate_sma,
    calculate_ema,
    calculate_rsi,
    calculate_macd,
    calculate_bollinger,
    calculate_all_indicators,
)


router = APIRouter()
# ---------------------------------------------
# SMA
# ---------------------------------------------
@router.get("/sma/{symbol}")
def get_sma(symbol: str, period: int = 20, db: Session = Depends(get_db)):
    df = get_price_dataframe(db, symbol)
    if df is None:
        raise HTTPException(404, "No data found")
    return calculate_sma(df, period).to_dict(orient="records")


# ---------------------------------------------
# EMA
# ---------------------------------------------
@router.get("/ema/{symbol}")
def get_ema(symbol: str, period: int = 20, db: Session = Depends(get_db)):
    df = get_price_dataframe(db, symbol)
    if df is None:
        raise HTTPException(404, "No data found")
    return calculate_ema(df, period).to_dict(orient="records")


# ---------------------------------------------
# RSI
# ---------------------------------------------
@router.get("/rsi/{symbol}")
def get_rsi(symbol: str, period: int = 14, db: Session = Depends(get_db)):
    df = get_price_dataframe(db, symbol)
    if df is None:
        raise HTTPException(404, "No data found")
    return calculate_rsi(df, period).to_dict(orient="records")


# ---------------------------------------------
# MACD
# ---------------------------------------------
@router.get("/macd/{symbol}")
def get_macd(symbol: str, db: Session = Depends(get_db)):
    df = get_price_dataframe(db, symbol)  # MACD needs more data
    if df is None:
        raise HTTPException(404, "No data found")
    return calculate_macd(df).to_dict(orient="records")


# ---------------------------------------------
# Bollinger Bands
# ---------------------------------------------
@router.get("/bollinger/{symbol}")
def get_bollinger(
    symbol: str,
    period: int = 20,   # IMPORTANT
    db: Session = Depends(get_db)
):
    df = get_price_dataframe(db, symbol)
    if df is None or df.empty:
        return []

    # calculate bollinger with given period
    df['middle'] = df['close'].rolling(period).mean()
    df['std'] = df['close'].rolling(period).std()
    df['upper'] = df['middle'] + (2 * df['std'])
    df['lower'] = df['middle'] - (2 * df['std'])

    result = df[['date', 'upper', 'middle', 'lower']].dropna()
    return result.to_dict(orient="records")




# ---------------------------------------------
# ALL Indicators
# ---------------------------------------------
@router.get("/all/{symbol}")
def get_all_indicators(symbol: str, db: Session = Depends(get_db)):
    df = get_price_dataframe(db, symbol, limit=300)
    if df is None:
        raise HTTPException(404, "No data found")
    return calculate_all_indicators(df)
