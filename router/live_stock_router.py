from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from model.intraday_model import IntradayData
from schema.live_stock_schema import StockPriceResponse
from service.live_stock_service import get_live_yf_price, _persist_intraday_batch  # updated
from db.database import get_db
import yfinance as yf
from datetime import datetime

# Celery tasks import (optional - for manual trigger)
try:
    from celery_tasks import fetch_intraday_data, fetch_all_stocks_intraday, fetch_selected_stocks_intraday
    CELERY_AVAILABLE = True
except ImportError:
    CELERY_AVAILABLE = False

router = APIRouter()

@router.get("/stocks/price/{symbol}", response_model=StockPriceResponse)
def live_stock_price(symbol: str):
    try:
        data = get_live_yf_price(symbol.upper())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/intraday/{symbol}")
def intraday_series(symbol: str, background_tasks: BackgroundTasks):
    """Return today's 1m intraday OHLCV for the symbol.
    Does not persist to DB; used for live 1D chart.
    """
    try:
        sym = symbol.upper()
        ticker = yf.Ticker(sym)
        df = ticker.history(period="1d", interval="1m")
        if df is None or df.empty:
            return []

        out = []
        rows_to_save = []
        for idx, row in df.iterrows():
            # idx is pandas Timestamp
            ts = idx.to_pydatetime()
            data_dict = {
                "symbol": sym,
                "date": ts.isoformat(),
                "open": float(row.get("Open", 0.0)),
                "high": float(row.get("High", 0.0)),
                "low": float(row.get("Low", 0.0)),
                "close": float(row.get("Close", 0.0)),
                "volume": float(row.get("Volume", 0.0)),
            }
            out.append(data_dict)

            rows_to_save.append({
                "timestamp": ts,
                "open": float(row.get("Open", 0.0)),
                "high": float(row.get("High", 0.0)),
                "low": float(row.get("Low", 0.0)),
                "close": float(row.get("Close", 0.0)),
                "volume": float(row.get("Volume", 0.0)),
            })

            # DB me save in background

        background_tasks.add_task(_persist_intraday_batch, sym, rows_to_save)
        return out
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch intraday for {symbol}: {e}")


# Celery Tasks ke liye manual trigger endpoints

@router.post("/stocks/celery/fetch-intraday/{symbol}")
def trigger_celery_intraday(symbol: str):
    """
    Manually trigger Celery task to fetch and save intraday data for a symbol
    """
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available. Run celery worker first.")
    
    try:
        result = fetch_intraday_data.delay(symbol.upper())
        return {
            "status": "task_triggered",
            "symbol": symbol.upper(),
            "task_id": result.id,
            "message": "Task queued successfully. Check Celery worker logs for status."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger task: {e}")


@router.post("/stocks/celery/fetch-all-intraday")
def trigger_all_stocks_celery():
    """
    Manually trigger Celery task to fetch intraday data for all stocks in database
    """
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available. Run celery worker first.")
    
    try:
        result = fetch_all_stocks_intraday.delay()
        return {
            "status": "task_triggered",
            "task_id": result.id,
            "message": "Batch task queued. All stocks will be processed."
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger task: {e}")


@router.post("/stocks/celery/fetch-selected-intraday")
def trigger_selected_stocks_celery(symbols: list[str]):
    """
    Manually trigger Celery task for selected stocks
    Body: ["RELIANCE.NS", "TCS.NS", "INFY.NS"]
    """
    if not CELERY_AVAILABLE:
        raise HTTPException(status_code=503, detail="Celery not available. Run celery worker first.")
    
    if not symbols:
        raise HTTPException(status_code=400, detail="Symbols list cannot be empty")
    
    try:
        result = fetch_selected_stocks_intraday.delay(symbols)
        return {
            "status": "task_triggered",
            "total_symbols": len(symbols),
            "task_id": result.id,
            "message": f"Tasks queued for {len(symbols)} stocks"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to trigger task: {e}")
