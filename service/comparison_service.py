import pandas as pd
import numpy as np
from sqlalchemy.orm import Session
from model.daily_data import DailyData
from service.analysis_service import (
    calculate_sma, calculate_ema, calculate_rsi,
    calculate_macd, calculate_bollinger
)

# ---------------------------------------------------------
# Fetch price data for multiple stocks (latest 200 candles)
# ---------------------------------------------------------
def get_multiple_stocks_df(db: Session, symbols: list, limit: int = 200):
    data = {}

    for symbol in symbols:
        rows = (
            db.query(DailyData)
            .filter(DailyData.symbol == symbol)
            .order_by(DailyData.date.desc())
            .limit(limit)
            .all()
        )

        if not rows:
            data[symbol] = None
            continue

        rows.reverse()

        df = pd.DataFrame([{
            "date": r.date,
            "open": r.open,
            "high": r.high,
            "low": r.low,
            "close": r.close,
            "volume": r.volume,
        } for r in rows])

        data[symbol] = df

    return data


# ---------------------------------------------------------
# 1️⃣ STOCK PRICE COMPARISON
# ---------------------------------------------------------
def compare_stocks(db: Session, symbols: list):
    result = {}
    stocks = get_multiple_stocks_df(db, symbols)

    for sym, df in stocks.items():
        if df is None:
            result[sym] = {"error": "No data found"}
            continue

        result[sym] = {
            "latest_close": float(df["close"].iloc[-1]),
            "1_day_change": float(df["close"].pct_change().iloc[-1] * 100),
            "7_day_change": float(df["close"].pct_change(7).iloc[-1] * 100) if len(df) >= 7 else None,
            "30_day_change": float(df["close"].pct_change(30).iloc[-1] * 100) if len(df) >= 30 else None,
        }

    return result


# ---------------------------------------------------------
# 2️⃣ INDICATOR COMPARISON
# ---------------------------------------------------------
def compare_indicators(db: Session, symbols: list):
    result = {}
    stocks = get_multiple_stocks_df(db, symbols, limit=300)

    for sym, df in stocks.items():
        if df is None:
            result[sym] = {"error": "No data"}
            continue

        result[sym] = {
            "SMA_20": calculate_sma(df.copy(), 20).tail(1).to_dict(orient="records")[0],
            "EMA_20": calculate_ema(df.copy(), 20).tail(1).to_dict(orient="records")[0],
            "RSI": calculate_rsi(df.copy()).tail(1).to_dict(orient="records")[0],
            "MACD": calculate_macd(df.copy()).tail(1).to_dict(orient="records")[0],
            "Bollinger": calculate_bollinger(df.copy()).tail(1).to_dict(orient="records")[0],
        }

    return result


# ---------------------------------------------------------
# 3️⃣ PERFORMANCE COMPARISON (Returns, Volatility)
# ---------------------------------------------------------
def compare_performance(db: Session, symbols: list):
    stocks = get_multiple_stocks_df(db, symbols, limit=200)
    result = {}

    for sym, df in stocks.items():
        if df is None:
            result[sym] = {"error": "No data"}
            continue

        df["returns"] = df["close"].pct_change()

        result[sym] = {
            "avg_daily_return": float(df["returns"].mean() * 100),
            "volatility": float(df["returns"].std() * np.sqrt(252) * 100),  # annualized %
            "total_return_30d": float(df["close"].pct_change(30).iloc[-1] * 100) if len(df) >= 30 else None,
            "total_return_90d": float(df["close"].pct_change(90).iloc[-1] * 100) if len(df) >= 90 else None,
        }

    return result
