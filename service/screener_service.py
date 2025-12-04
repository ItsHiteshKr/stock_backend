# service/screener_service.py
from db.database import get_db
from model.stock_model import StockFundamentals
from schema.stock_schema import ScreenerFilter, ScreenerAdvanced

# Fetch stocks with live price already updated
def filter_stocks(db, min_price, max_price, min_pe, max_pe):
    stocks = db.query(StockFundamentals).filter(
        StockFundamentals.live_price >= min_price,
        StockFundamentals.live_price <= max_price,
        StockFundamentals.pe_ratio >= min_pe,
        StockFundamentals.pe_ratio <= max_pe
    ).all()
    return [s.__dict__ for s in stocks]

def advanced_filter(db, filter: ScreenerAdvanced):
    stocks = db.query(StockFundamentals).filter(
        StockFundamentals.pe_ratio >= filter.min_pe,
        StockFundamentals.pe_ratio <= filter.max_pe,
        StockFundamentals.pb_ratio >= filter.min_pb,
        StockFundamentals.pb_ratio <= filter.max_pb,
        StockFundamentals.market_cap >= filter.min_mcap,
        StockFundamentals.market_cap <= filter.max_mcap
    ).all()
    return [s.__dict__ for s in stocks]

def filter_by_sector(db, sector):
    stocks = db.query(StockFundamentals).filter(StockFundamentals.sector == sector).all()
    return [s.__dict__ for s in stocks]

def save_screener(db, filter: ScreenerFilter):
    # Optional: save to a CustomScreener table if needed
    pass

def list_screeners(db):
    # Optional: return saved screeners
    return []
