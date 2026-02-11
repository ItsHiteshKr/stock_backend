from celery_config import celery_app
from service.live_stock_service import _persist_intraday_batch
from db.database import SessionLocal
from model.stock_model import StockFundamentals
import yfinance as yf
from datetime import datetime
import logging

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@celery_app.task(name="celery_tasks.fetch_intraday_data")
def fetch_intraday_data(symbol: str):
    """
    Single stock ke liye intraday data fetch karke database me save kare
    """
    try:
        sym = symbol.upper()
        logger.info(f"Fetching intraday data for {sym}")
        
        ticker = yf.Ticker(sym)
        df = ticker.history(period="1d", interval="1m")
        
        if df is None or df.empty:
            logger.warning(f"No intraday data found for {sym}")
            return {"status": "no_data", "symbol": sym}

        rows_to_save = []
        for idx, row in df.iterrows():
            ts = idx.to_pydatetime()
            rows_to_save.append({
                "timestamp": ts,
                "open": float(row.get("Open", 0.0)),
                "high": float(row.get("High", 0.0)),
                "low": float(row.get("Low", 0.0)),
                "close": float(row.get("Close", 0.0)),
                "volume": float(row.get("Volume", 0.0)),
            })

        # Database me save kare
        _persist_intraday_batch(sym, rows_to_save)
        
        logger.info(f"Successfully saved {len(rows_to_save)} records for {sym}")
        return {
            "status": "success",
            "symbol": sym,
            "records_saved": len(rows_to_save)
        }
    
    except Exception as e:
        logger.error(f"Error fetching intraday data for {symbol}: {str(e)}")
        return {
            "status": "error",
            "symbol": symbol,
            "error": str(e)
        }


@celery_app.task(name="celery_tasks.fetch_all_stocks_intraday")
def fetch_all_stocks_intraday():
    """
    Database me available sabhi stocks ke liye intraday data fetch kare
    """
    db = SessionLocal()
    try:
        # Database se sabhi stocks fetch kare
        stocks = db.query(StockFundamentals.symbol).all()
        symbols = [stock.symbol for stock in stocks]
        
        logger.info(f"Fetching intraday data for {len(symbols)} stocks")
        
        results = []
        for symbol in symbols:
            # Har stock ke liye task trigger kare
            result = fetch_intraday_data.delay(symbol)
            results.append({
                "symbol": symbol,
                "task_id": result.id
            })
        
        return {
            "status": "triggered",
            "total_stocks": len(symbols),
            "tasks": results
        }
    
    except Exception as e:
        logger.error(f"Error in fetch_all_stocks_intraday: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }
    finally:
        db.close()


@celery_app.task(name="celery_tasks.fetch_selected_stocks_intraday")
def fetch_selected_stocks_intraday(symbols: list[str]):
    """
    Selected stocks ke liye intraday data fetch kare
    
    Args:
        symbols: List of stock symbols
    """
    logger.info(f"Fetching intraday data for selected {len(symbols)} stocks")
    
    results = []
    for symbol in symbols:
        result = fetch_intraday_data.delay(symbol)
        results.append({
            "symbol": symbol,
            "task_id": result.id
        })
    
    return {
        "status": "triggered",
        "total_stocks": len(symbols),
        "tasks": results
    }
