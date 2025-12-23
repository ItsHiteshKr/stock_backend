from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from schema.live_stock_schema import StockPriceResponse
from service.live_stock_service import get_live_yf_price
from db.database import get_db, Base, engine
import yfinance as yf
from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger

# Create Intraday model
class IntradayData(Base):
    __tablename__ = "intraday_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    timestamp = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

# Create table if not exists
Base.metadata.create_all(bind=engine)

# router = APIRouter()

# @router.get("/stocks/price/{symbol}", response_model=StockPriceResponse)
# def live_stock_price(symbol: str):
#     try:
#         data = get_live_yf_price(symbol.upper())
#         return data
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))

# @router.get("/stocks/intraday/{symbol}")
# def intraday_series(symbol: str, db: Session = Depends(get_db)):
#     """Fetch today's 1m intraday data and save to DB"""
#     try:
#         sym = symbol.upper()
#         ticker = yf.Ticker(sym)
#         df = ticker.history(period="1d", interval="1m")
        
#         if df is None or df.empty:
#             return []

#         out = []
#         for idx, row in df.iterrows():
#             ts = idx.to_pydatetime()
#             data_point = {
#                 "symbol": sym,
#                 "date": ts.isoformat(),
#                 "open": float(row.get("Open", 0.0)),
#                 "high": float(row.get("High", 0.0)),
#                 "low": float(row.get("Low", 0.0)),
#                 "close": float(row.get("Close", 0.0)),
#                 "volume": float(row.get("Volume", 0.0)),
#             }
            
#             # DB में save करें
#             intraday_record = IntradayData(
#                 symbol=sym,
#                 timestamp=ts,
#                 open=data_point["open"],
#                 high=data_point["high"],
#                 low=data_point["low"],
#                 close=data_point["close"],
#                 volume=data_point["volume"]
#             )
#             db.add(intraday_record)
#             out.append(data_point)
        
#         db.commit()
#         return out
#     except Exception as e:
#         db.rollback()
#         raise HTTPException(status_code=500, detail=f"Failed to fetch intraday: {e}")