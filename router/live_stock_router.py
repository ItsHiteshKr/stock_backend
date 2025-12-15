from fastapi import APIRouter, HTTPException
from schema.live_stock_schema import StockPriceResponse
from service.live_stock_service import get_live_yf_price  # updated
import yfinance as yf
from datetime import datetime

router = APIRouter()

@router.get("/stocks/price/{symbol}", response_model=StockPriceResponse)
def live_stock_price(symbol: str):
    try:
        data = get_live_yf_price(symbol.upper())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks/intraday/{symbol}")
def intraday_series(symbol: str):
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
        for idx, row in df.iterrows():
            # idx is pandas Timestamp
            ts = idx.to_pydatetime()
            out.append({
                "symbol": sym,
                "date": ts.isoformat(),
                "open": float(row.get("Open", 0.0)),
                "high": float(row.get("High", 0.0)),
                "low": float(row.get("Low", 0.0)),
                "close": float(row.get("Close", 0.0)),
                "volume": float(row.get("Volume", 0.0)),
            })

        return out
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch intraday for {symbol}: {e}")
