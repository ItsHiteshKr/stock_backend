from sqlalchemy.orm import Session
from db.database import SessionLocal
from model.stock import Stock
from model.index import Index, IndexStock

# -------------------------------
# MAJOR INDEXES
# -------------------------------
INDEXES = [
    {"name": "NIFTY 50", "exchange": "NSE", "category": "BROAD"},
    {"name": "NIFTY NEXT 50", "exchange": "NSE", "category": "BROAD"},
    {"name": "BANKNIFTY", "exchange": "NSE", "category": "SECTOR"},
    {"name": "NIFTY IT", "exchange": "NSE", "category": "SECTOR"},
    {"name": "NIFTY FMCG", "exchange": "NSE", "category": "SECTOR"},
    {"name": "NIFTY AUTO", "exchange": "NSE", "category": "SECTOR"},
    {"name": "NIFTY PHARMA", "exchange": "NSE", "category": "SECTOR"},
    {"name": "SENSEX", "exchange": "NSE", "category": "BROAD"},
]

# -------------------------------
# STOCKS PER INDEX
# -------------------------------
NIFTY50 = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
    {"symbol": "INFY.NS", "name": "Infosys"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
    {"symbol": "SBIN.NS", "name": "State Bank of India"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel"},
    {"symbol": "ITC.NS", "name": "ITC Ltd"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki"},
    {"symbol": "TITAN.NS", "name": "Titan Company"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid"},
    {"symbol": "WIPRO.NS", "name": "Wipro"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy’s Labs"},
    {"symbol": "COALINDIA.NS", "name": "Coal India"},
    {"symbol": "BRITANNIA.NS", "name": "Britannia Industries"},
    {"symbol": "CIPLA.NS", "name": "Cipla Ltd"},
    {"symbol": "BPCL.NS", "name": "Bharat Petroleum"},
    {"symbol": "ASIANPAINT.NS", "name": "Asian Paints"},
    {"symbol": "BAJAJ-AUTO.NS", "name": "Bajaj Auto"},
    {"symbol": "BAJAJFINSV.NS", "name": "Bajaj Finserv"},
    {"symbol": "ADANIPORTS.NS", "name": "Adani Ports"},
    {"symbol": "TECHM.NS", "name": "Tech Mahindra"},
    {"symbol": "NTPC.NS", "name": "NTPC Ltd"},
    {"symbol": "TATASTEEL.NS", "name": "Tata Steel"},
    {"symbol": "UPL.NS", "name": "UPL Ltd"},
    {"symbol": "INDUSINDBK.NS", "name": "IndusInd Bank"},
    {"symbol": "HDFCLIFE.NS", "name": "HDFC Life"},
    {"symbol": "JSWSTEEL.NS", "name": "JSW Steel"},
    {"symbol": "M&M.NS", "name": "Mahindra & Mahindra"},
    {"symbol": "IOC.NS", "name": "Indian Oil"},
    {"symbol": "ONGC.NS", "name": "ONGC"},
    {"symbol": "HEROMOTOCO.NS", "name": "Hero MotoCorp"},
    {"symbol": "GAIL.NS", "name": "GAIL India"},
    {"symbol": "SBILIFE.NS", "name": "SBI Life Insurance"},
    {"symbol": "DIVISLAB.NS", "name": "Divi’s Laboratories"},
    {"symbol": "TATAMOTORS.NS", "name": "Tata Motors"},
    {"symbol": "BEL.NS", "name": "Bharat Electronics"},
    {"symbol": "BHARATFORG.NS", "name": "Bharat Forge"},
    {"symbol": "PEL.NS", "name": "Piramal Enterprises"},
    {"symbol": "ADANIENT.NS", "name": "Adani Enterprises"},
]

BANKNIFTY = [
    "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "SBIN.NS", "INDUSINDBK.NS",
    "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "FEDERALBNK.NS",
    "IDFCFIRSTB.NS", "RBLBANK.NS"
]

NIFTY_IT = [
    "TCS.NS", "INFY.NS", "HCLTECH.NS", "TECHM.NS",
    "WIPRO.NS", "LTIM.NS", "MPHASIS.NS", "COFORGE.NS",
    "INFOBEAN.NS"
]

NIFTY_AUTO = [
    "MARUTI.NS", "BAJAJ-AUTO.NS", "M&M.NS",
    "HEROMOTOCO.NS", "TATAMOTORS.NS", "EICHERMOT.NS"
]

NIFTY_FMCG = [
    "HINDUNILVR.NS", "ITC.NS", "BRITANNIA.NS",
    "NESTLEIND.NS", "DABUR.NS", "TATACONSUM.NS"
]

NIFTY_PHARMA = [
    "SUNPHARMA.NS", "CIPLA.NS", "DIVISLAB.NS",
    "DRREDDY.NS", "GLAND.NS", "AUROPHARMA.NS"
]

SENSEX = [s.replace(".BO", ".NS") for s in[
    "RELIANCE.BO", "HDFCBANK.BO", "TCS.BO", "INFY.BO",
    "HINDUNILVR.BO", "ICICIBANK.BO", "ITC.BO", "BAJFINANCE.BO",
    "AXISBANK.BO", "LT.BO", "SBIN.BO", "SUNPHARMA.BO",
    "MARUTI.BO", "TATASTEEL.BO", "BHARTIARTL.BO", "ULTRACEMCO.BO",
    "ONGC.BO", "NTPC.BO", "TITAN.BO", "TECHM.BO", "BRITANNIA.BO",
    "COALINDIA.BO", "BPCL.BO", "DIVISLAB.BO", "ADANIPORTS.BO",
    "HCLTECH.BO", "BAJAJ-AUTO.BO", "BAJAJFINSV.BO", "M&M.BO"
]]

# -------------------------------
# HELPER FUNCTIONS
# -------------------------------
def add_stocks(db: Session, stock_list, exchange="NSE"):
    for s in stock_list:
        if isinstance(s, dict):
            symbol = s["symbol"]
            name = s["name"]
        else:
            symbol = s
            name = s
        # Ensure symbol ends with .NS
        if not symbol.endswith(".NS"):
            symbol = symbol.split('.')[0] + ".NS"
        if not db.query(Stock).filter(Stock.symbol == symbol).first():
            db.add(Stock(symbol=symbol, name=name, exchange=exchange))
    db.commit()


def populate_index(db: Session, index_name, symbols):
    index_obj = db.query(Index).filter(Index.name == index_name).first()
    if not index_obj:
        print(f"Index {index_name} not found!")
        return
    for sym in symbols:
        stock = db.query(Stock).filter(Stock.symbol == sym).first()
        if stock:
            if not db.query(IndexStock).filter(
                IndexStock.index_id == index_obj.id,
                IndexStock.stock_id == stock.id
            ).first():
                db.add(IndexStock(index_id=index_obj.id, stock_id=stock.id))
    db.commit()


def main():
    db = SessionLocal()

    # Add indexes
    for idx in INDEXES:
        if not db.query(Index).filter_by(name=idx["name"]).first():
            db.add(Index(**idx))
    db.commit()

    # Add stocks
    add_stocks(db, NIFTY50)
    add_stocks(db, BANKNIFTY)
    add_stocks(db, NIFTY_IT)
    add_stocks(db, NIFTY_AUTO)
    add_stocks(db, NIFTY_FMCG)
    add_stocks(db, NIFTY_PHARMA)
    add_stocks(db, SENSEX)

    # Map indexes
    populate_index(db, "NIFTY 50", [s["symbol"] for s in NIFTY50])
    populate_index(db, "BANKNIFTY", BANKNIFTY)
    populate_index(db, "NIFTY IT", NIFTY_IT)
    populate_index(db, "NIFTY AUTO", NIFTY_AUTO)
    populate_index(db, "NIFTY FMCG", NIFTY_FMCG)
    populate_index(db, "NIFTY PHARMA", NIFTY_PHARMA)
    populate_index(db, "SENSEX", SENSEX)

    print("✅ Stocks and indexes populated successfully!")


if __name__ == "__main__":
    main()
