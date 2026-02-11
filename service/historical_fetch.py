# service/historical_fetch.py
import yfinance as yf
from datetime import datetime, timedelta
from db.database import SessionLocal
from model.daily_data import DailyData
from model.stock import Stock

def store_history():
    db = SessionLocal()

    # Fetch all stocks
    stocks = db.query(Stock).all()
    print("Total symbols to fetch:", len(stocks))

    for stock in stocks:
        sym = stock.symbol
        print(f"Fetching history for {sym}...")

        # Get latest date for this stock
        last_record = (
            db.query(DailyData.date)
            .filter(DailyData.stock_id == stock.id)
            .order_by(DailyData.date.desc())
            .first()
        )

        if last_record:
            start_date = last_record[0] + timedelta(days=1)
        else:
            start_date = datetime(2010, 1, 1).date()

        end_date = datetime.now().date()

        if start_date > end_date:
            print(f"{sym} already up-to-date.")
            continue

        try:
            df = yf.download(sym, start=start_date, end=end_date)
        except Exception as e:
            print(f"Failed to download {sym}: {e}")
            continue

        if df.empty:
            print(f"No new data for {sym}")
            continue

        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df.reset_index(inplace=True)

        for _, row in df.iterrows():
            date_value = row["Date"].date()

            exists = (
                db.query(DailyData)
                .filter(DailyData.stock_id == stock.id, DailyData.date == date_value)
                .first()
            )
            if exists:
                continue

            try:
                record = DailyData(
                    stock_id=stock.id,
                    symbol=stock.symbol,
                    date=date_value,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    adj_close=float(row["Adj Close"]) if "Adj Close" in row else float(row["Close"]),
                    volume=int(row["Volume"])
                )
                db.add(record)
            except Exception as e:
                print(f"Error inserting {sym} on {date_value}: {e}")
                continue

        db.commit()
        print(f"✔ Saved history for {sym}")

    db.close()
    print("✅ All historical data updated!")

if __name__ == "__main__":
    store_history()
