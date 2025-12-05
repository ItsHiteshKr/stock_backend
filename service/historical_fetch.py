import yfinance as yf
from datetime import datetime
from db.database import SessionLocal
from model.daily_data import DailyData

# Your symbols
symbols = ["RELIANCE.NS", "TCS.NS", "INFY.NS"]

def store_history():
    db = SessionLocal()

    for sym in symbols:
        print(f"Downloading history for {sym}...")

        df = yf.download(sym, start="2010-01-01", end=datetime.now().date())

        # Flatten multi-index columns from yfinance
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]

        df.reset_index(inplace=True)

        for _, row in df.iterrows():
            try:
                record = DailyData(
                    symbol=sym,
                    date=row["Date"].date(),
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=float(row["Volume"]),
                )
                db.add(record)
            except Exception as e:
                print(f"Error inserting row: {e}")
                continue

        db.commit()
        print(f"Saved {sym} history.\n")

if __name__ == "__main__":
    store_history()
