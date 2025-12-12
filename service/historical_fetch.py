import yfinance as yf
from datetime import datetime, timedelta
from db.database import SessionLocal
from model.daily_data import DailyData
from model.stock import Stock
from model.index import IndexStock

def store_history():
    db = SessionLocal()

    # Fetch all symbols from stocks table
    stock_symbols = [s[0] for s in db.query(Stock.symbol).all()]

    # Fetch all unique symbols from indices table
    index_symbols = [s[0] for s in db.query(IndexStock.stock_symbol).distinct().all()]

    # Combine symbols and remove duplicates
    symbols = list(set(stock_symbols + index_symbols))
    print("Total symbols found:", len(symbols))

    for sym in symbols:
        print(f"\nFetching history for {sym}")

        # Check latest date in DB for this symbol
        last_record = (
            db.query(DailyData.date)
            .filter(DailyData.symbol == sym)
            .order_by(DailyData.date.desc())
            .first()
        )

        if last_record:
            start_date = last_record[0] + timedelta(days=1)  # start from next day
        else:
            start_date = datetime(2010, 1, 1).date()  # default start date

        end_date = datetime.now().date()

        if start_date > end_date:
            print("Already up-to-date.")
            continue

        try:
            df = yf.download(sym, start=start_date, end=end_date)
        except Exception as e:
            print(f"Failed to download {sym}: {e}")
            continue

        if df.empty:
            print("No new data available.")
            continue

        # Ensure columns are correct
        df.columns = [col[0] if isinstance(col, tuple) else col for col in df.columns]
        df.reset_index(inplace=True)

        # Insert new rows
        for _, row in df.iterrows():
            date_value = row["Date"].date()
            # Skip if already exists
            exists = (
                db.query(DailyData)
                .filter(DailyData.symbol == sym, DailyData.date == date_value)
                .first()
            )
            if exists:
                continue

            try:
                record = DailyData(
                    symbol=sym,
                    date=date_value,
                    open=float(row["Open"]),
                    high=float(row["High"]),
                    low=float(row["Low"]),
                    close=float(row["Close"]),
                    volume=int(row["Volume"]),
                )
                db.add(record)
            except Exception as e:
                print(f"Error inserting row for {sym} on {date_value}: {e}")
                continue

        db.commit()
        print(f"✔ Saved history for {sym}")

    db.close()
    print("\nAll history updated!")

if __name__ == "__main__":
    store_history()
