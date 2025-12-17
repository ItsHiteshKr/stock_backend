# service/daily_updater.py
import yfinance as yf
from sqlalchemy.exc import IntegrityError
from db.database import SessionLocal
from model.daily_data import DailyData
from model.stock import Stock
from datetime import date
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def fetch_and_insert_symbol(db, stock):
    df = yf.download(stock.symbol, period="1d", progress=False, auto_adjust=False)
    if df.empty:
        logging.warning(f"No data for {stock.symbol}")
        return

    row = DailyData(
        stock_id=stock.id,
        symbol=stock.symbol,
        date=date.today(),
        open=float(df['Open'].iloc[0]),
        high=float(df['High'].iloc[0]),
        low=float(df['Low'].iloc[0]),
        close=float(df['Close'].iloc[0]),
        adj_close=float(df['Adj Close'].iloc[0]) if 'Adj Close' in df.columns else float(df['Close'].iloc[0]),
        volume=int(df['Volume'].iloc[0])
    )

    try:
        db.add(row)
        db.commit()
        logging.info(f"Inserted {stock.symbol} for {row.date}")
    except IntegrityError:
        db.rollback()
        logging.info(f"{stock.symbol} for {row.date} already exists. Skipping.")

def update_daily():
    db = SessionLocal()
    try:
        stocks = db.query(Stock).all()
        if not stocks:
            logging.warning("No stocks found in DB!")
            return
        for stock in stocks:
            fetch_and_insert_symbol(db, stock)
    finally:
        db.close()

if __name__ == "__main__":
    update_daily()
