from sqlalchemy import extract, func, and_
from model.daily_data import DailyData
from datetime import datetime
import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
import ta

# ---------------------------------------------------------
# 1. MONTHLY ANALYSIS (Open / Close / High / Low)
# ---------------------------------------------------------
def get_monthly_summary(db, symbol):
    grouped = (
        db.query(
            extract('year', DailyData.date).label("year"),
            extract('month', DailyData.date).label("month"),
            func.min(DailyData.low).label("low"),
            func.max(DailyData.high).label("high"),
            func.min(DailyData.date).label("start_date"),
            func.max(DailyData.date).label("end_date")
        )
        .filter(DailyData.symbol == symbol)
        .group_by(extract('year', DailyData.date), extract('month', DailyData.date))
        .order_by("year", "month")
        .all()
    )

    result = []

    for row in grouped:
        # OPEN = price on first trading day of month
        open_price = db.query(DailyData.open).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.start_date
        ).scalar()

        # CLOSE = price on last trading day of month
        close_price = db.query(DailyData.close).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.end_date
        ).scalar()

        result.append({
            "year": int(row.year),
            "month": int(row.month),
            "open": float(open_price) if open_price else None,
            "close": float(close_price) if close_price else None,
            "high": float(row.high),
            "low": float(row.low),
        })

    return result


# ---------------------------------------------------------
# 2. YEARLY ANALYSIS (Open / Close / High / Low)
# ---------------------------------------------------------
def get_yearly_summary(db, symbol):
    grouped = (
        db.query(
            extract('year', DailyData.date).label("year"),
            func.min(DailyData.low).label("low"),
            func.max(DailyData.high).label("high"),
            func.min(DailyData.date).label("start_date"),
            func.max(DailyData.date).label("end_date"),
        )
        .filter(DailyData.symbol == symbol)
        .group_by(extract('year', DailyData.date))
        .order_by("year")
        .all()
    )

    result = []

    for row in grouped:
        open_price = db.query(DailyData.open).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.start_date
        ).scalar()

        close_price = db.query(DailyData.close).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.end_date
        ).scalar()

        result.append({
            "year": int(row.year),
            "open": float(open_price) if open_price else None,
            "close": float(close_price) if close_price else None,
            "high": float(row.high),
            "low": float(row.low)
        })

    return result


# ---------------------------------------------------------
# 3. CUSTOM DATE RANGE ANALYSIS
# ---------------------------------------------------------
def get_period_summary(db, symbol, start_date, end_date):
    data = (
        db.query(
            func.min(DailyData.low).label("low"),
            func.max(DailyData.high).label("high"),
            func.min(DailyData.date).label("start_date"),
            func.max(DailyData.date).label("end_date")
        )
        .filter(
            DailyData.symbol == symbol,
            DailyData.date >= start_date,
            DailyData.date <= end_date
        )
        .first()
    )

    if not data.start_date:
        return None  # No trading data

    open_price = db.query(DailyData.open).filter(
        DailyData.symbol == symbol,
        DailyData.date == data.start_date
    ).scalar()

    close_price = db.query(DailyData.close).filter(
        DailyData.symbol == symbol,
        DailyData.date == data.end_date
    ).scalar()

    return {
        "start_date": str(data.start_date),
        "end_date": str(data.end_date),
        "open": float(open_price) if open_price else None,
        "close": float(close_price) if close_price else None,
        "high": float(data.high),
        "low": float(data.low)
    }

from datetime import datetime

def parse_date(date_str: str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}. Allowed formats: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY")


def get_price_dataframe(db: Session, symbol: str, limit: int = 200):
    """
    Fetch latest 'limit' candles for the symbol.
    Oldest first (required for indicators).
    """
    rows = (
        db.query(DailyData)
        .filter(DailyData.symbol == symbol)
        .order_by(DailyData.date.desc())
        .limit(limit)
        .all()
    )

    if not rows:
        return None

    rows.reverse()

    df = pd.DataFrame([{
        "date": r.date,
        "open": r.open,
        "high": r.high,
        "low": r.low,
        "close": r.close,
        "volume": r.volume,
    } for r in rows])

    return df


# ---------------------------------------------
# 2) Simple Moving Average (SMA)
# ---------------------------------------------
def calculate_sma(df: pd.DataFrame, period: int = 20):
    df["SMA"] = df["close"].rolling(period).mean()
    return df[["date", "close", "SMA"]].dropna()


# ---------------------------------------------
# 3) Exponential Moving Average (EMA)
# ---------------------------------------------
def calculate_ema(df: pd.DataFrame, period: int = 20):
    df["EMA"] = df["close"].ewm(span=period, adjust=False).mean()
    return df[["date", "close", "EMA"]]


# ---------------------------------------------
# 4) Relative Strength Index (RSI)
# ---------------------------------------------
def calculate_rsi(df: pd.DataFrame, period: int = 14):
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss
    df["RSI"] = 100 - (100 / (1 + rs))

    return df[["date", "close", "RSI"]].dropna()


# ---------------------------------------------
# 5) MACD (12-26-9)
# ---------------------------------------------
def calculate_macd(df: pd.DataFrame):
    ema12 = df["close"].ewm(span=12, adjust=False).mean()
    ema26 = df["close"].ewm(span=26, adjust=False).mean()

    df["MACD"] = ema12 - ema26
    df["Signal"] = df["MACD"].ewm(span=9, adjust=False).mean()
    df["Histogram"] = df["MACD"] - df["Signal"]

    return df[["date", "MACD", "Signal", "Histogram"]]


# ---------------------------------------------
# 6) Bollinger Bands (20-period)
# ---------------------------------------------
def calculate_bollinger(df: pd.DataFrame, period: int = 20):
    sma = df["close"].rolling(period).mean()
    std = df["close"].rolling(period).std()

    df["Middle"] = sma
    df["Upper"] = sma + (std * 2)
    df["Lower"] = sma - (std * 2)

    return df[["date", "close", "Upper", "Middle", "Lower"]].dropna()


# ---------------------------------------------
# 7) Return ALL indicators at once
# ---------------------------------------------
def calculate_all_indicators(df: pd.DataFrame):
    """
    Returns SMA, EMA, RSI, MACD, Bollinger in a single response.
    """
    return {
        "SMA_20": calculate_sma(df.copy(), 20).tail(1).to_dict(orient="records")[0],
        "EMA_20": calculate_ema(df.copy(), 20).tail(1).to_dict(orient="records")[0],
        "RSI_14": calculate_rsi(df.copy(), 14).tail(1).to_dict(orient="records")[0],
        "MACD": calculate_macd(df.copy()).tail(1).to_dict(orient="records")[0],
        "Bollinger": calculate_bollinger(df.copy(), 20).tail(1).to_dict(orient="records")[0],
    }