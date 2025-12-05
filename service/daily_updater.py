# service/daily_updater.py
import yfinance as yf
from sqlalchemy.exc import IntegrityError
from sqlalchemy import text
from db.database import SessionLocal
from model.daily_data import DailyData
from datetime import date
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler()]
)

def get_all_symbols(db):
    """Fetch all unique symbols from the database"""
    result = db.execute(text("SELECT DISTINCT symbol FROM daily_data")).fetchall()
    return [row[0] for row in result]

def get_last_date_for_symbol(db, symbol):
    """Get the latest date we have for a given symbol"""
    result = db.query(DailyData).filter(DailyData.symbol == symbol).order_by(DailyData.date.desc()).first()
    return result.date if result else None

def fetch_and_insert_symbol(db, symbol, start_date=None):
    """Fetch latest stock data for a symbol and insert into DB"""
    df = yf.download(symbol, period="1d", progress=False, auto_adjust=False)
    if df.empty:
        logging.warning(f"No data found for {symbol}")
        return
    
    # Prepare data for insertion
    row = DailyData(
        symbol=symbol,
        date=date.today(),
        open=float(df['Open'].iloc[0]),
        high=float(df['High'].iloc[0]),
        low=float(df['Low'].iloc[0]),
        close=float(df['Close'].iloc[0]),
        volume=int(df['Volume'].iloc[0])
    )

    try:
        db.add(row)
        db.commit()
        logging.info(f"Inserted data for {symbol} on {row.date}")
    except IntegrityError:
        db.rollback()
        logging.info(f"Data for {symbol} on {row.date} already exists. Skipping.")

def update_daily():
    db = SessionLocal()
    try:
        symbols = get_all_symbols(db)
        if not symbols:
            logging.warning("No symbols found in DB. Please add some first.")
            return

        for symbol in symbols:
            fetch_and_insert_symbol(db, symbol)

    finally:
        db.close()

if __name__ == "__main__":
    update_daily()
