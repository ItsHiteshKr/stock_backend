# service/update_fundamentals_live.py
import yfinance as yf
from db.database import get_db
from model.stock_model import StockFundamentals
from sqlalchemy.orm import Session
from datetime import datetime
import time

SYMBOLS = [
    "RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "KOTAKBANK.NS", "SBIN.NS", "ITC.NS", "LT.NS"
    # Add more NSE symbols if needed
]

def update_fundamentals_live(db: Session):
    for symbol in SYMBOLS:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info

            # Fetch fundamentals
            pe_ratio = info.get("trailingPE")
            pb_ratio = info.get("priceToBook")
            market_cap = info.get("marketCap")
            sector = info.get("sector")
            industry = info.get("industry")
            name = info.get("shortName")

            # Safe fetching of live price
            live_price = None
            for key in ["regularMarketPrice", "previousClose", "open"]:
                val = info.get(key)
                if val is not None:
                    live_price = val
                    break
            if live_price is None:
                live_price = 0.0

            existing = db.query(StockFundamentals).filter(StockFundamentals.symbol == symbol).first()

            if existing:
                existing.pe_ratio = pe_ratio
                existing.pb_ratio = pb_ratio
                existing.market_cap = market_cap
                existing.sector = sector
                existing.industry = industry
                existing.name = name
                existing.live_price = live_price
                existing.last_updated = datetime.utcnow()
            else:
                new_stock = StockFundamentals(
                    symbol=symbol,
                    name=name,
                    sector=sector,
                    industry=industry,
                    pe_ratio=pe_ratio,
                    pb_ratio=pb_ratio,
                    market_cap=market_cap,
                    live_price=live_price,
                    last_updated=datetime.utcnow()
                )
                db.add(new_stock)

            db.commit()
            print(f"Updated {symbol}: live_price={live_price}")

            # Optional: short sleep to avoid hitting Yahoo servers too fast
            time.sleep(1)

        except Exception as e:
            print(f"Error updating {symbol}: {e}")
            db.rollback()

if __name__ == "__main__":
    db = next(get_db())
    while True:
        update_fundamentals_live(db)
        print("Sleeping 5 minutes before next update...")
        time.sleep(300)  # Update every 5 minutes
