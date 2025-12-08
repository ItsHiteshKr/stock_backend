from sqlalchemy import extract, func, and_
from model.daily_data import DailyData
from datetime import datetime

# ---------------------------------------------------------
# 1. MONTHLY ANALYSIS (Open / Close / High / Low)
# ---------------------------------------------------------
def get_monthly_summary(db, symbol):
    grouped = (
        db.query(
            extract('year', DailyData.date).label("year"),
            extract('month', DailyData.date).label("month"),
            func.min(DailyData.low).label("low"),
            func.max(DailyData.high).label("high"),
            func.min(DailyData.date).label("start_date"),
            func.max(DailyData.date).label("end_date")
        )
        .filter(DailyData.symbol == symbol)
        .group_by(extract('year', DailyData.date), extract('month', DailyData.date))
        .order_by("year", "month")
        .all()
    )

    result = []

    for row in grouped:
        # OPEN = price on first trading day of month
        open_price = db.query(DailyData.open).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.start_date
        ).scalar()

        # CLOSE = price on last trading day of month
        close_price = db.query(DailyData.close).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.end_date
        ).scalar()

        result.append({
            "year": int(row.year),
            "month": int(row.month),
            "open": float(open_price) if open_price else None,
            "close": float(close_price) if close_price else None,
            "high": float(row.high),
            "low": float(row.low),
        })

    return result


# ---------------------------------------------------------
# 2. YEARLY ANALYSIS (Open / Close / High / Low)
# ---------------------------------------------------------
def get_yearly_summary(db, symbol):
    grouped = (
        db.query(
            extract('year', DailyData.date).label("year"),
            func.min(DailyData.low).label("low"),
            func.max(DailyData.high).label("high"),
            func.min(DailyData.date).label("start_date"),
            func.max(DailyData.date).label("end_date"),
        )
        .filter(DailyData.symbol == symbol)
        .group_by(extract('year', DailyData.date))
        .order_by("year")
        .all()
    )

    result = []

    for row in grouped:
        open_price = db.query(DailyData.open).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.start_date
        ).scalar()

        close_price = db.query(DailyData.close).filter(
            DailyData.symbol == symbol,
            DailyData.date == row.end_date
        ).scalar()

        result.append({
            "year": int(row.year),
            "open": float(open_price) if open_price else None,
            "close": float(close_price) if close_price else None,
            "high": float(row.high),
            "low": float(row.low)
        })

    return result


# ---------------------------------------------------------
# 3. CUSTOM DATE RANGE ANALYSIS
# ---------------------------------------------------------
def get_period_summary(db, symbol, start_date, end_date):
    data = (
        db.query(
            func.min(DailyData.low).label("low"),
            func.max(DailyData.high).label("high"),
            func.min(DailyData.date).label("start_date"),
            func.max(DailyData.date).label("end_date")
        )
        .filter(
            DailyData.symbol == symbol,
            DailyData.date >= start_date,
            DailyData.date <= end_date
        )
        .first()
    )

    if not data.start_date:
        return None  # No trading data

    open_price = db.query(DailyData.open).filter(
        DailyData.symbol == symbol,
        DailyData.date == data.start_date
    ).scalar()

    close_price = db.query(DailyData.close).filter(
        DailyData.symbol == symbol,
        DailyData.date == data.end_date
    ).scalar()

    return {
        "start_date": str(data.start_date),
        "end_date": str(data.end_date),
        "open": float(open_price) if open_price else None,
        "close": float(close_price) if close_price else None,
        "high": float(data.high),
        "low": float(data.low)
    }

from datetime import datetime

def parse_date(date_str: str):
    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Invalid date format: {date_str}. Allowed formats: YYYY-MM-DD, DD-MM-YYYY, DD/MM/YYYY")
