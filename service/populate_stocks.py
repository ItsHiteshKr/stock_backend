from db.database import SessionLocal
from model.stock import Stock
from model.index import IndexStock

nifty50 = [
    {"symbol": "RELIANCE.NS", "name": "Reliance Industries"},
    {"symbol": "HDFCBANK.NS", "name": "HDFC Bank"},
    {"symbol": "TCS.NS", "name": "Tata Consultancy Services"},
    {"symbol": "BHARTIARTL.NS", "name": "Bharti Airtel"},
    {"symbol": "ICICIBANK.NS", "name": "ICICI Bank"},
    {"symbol": "SBIN.NS", "name": "State Bank of India"},
    {"symbol": "INFY.NS", "name": "Infosys"},
    {"symbol": "BAJFINANCE.NS", "name": "Bajaj Finance"},
    {"symbol": "HINDUNILVR.NS", "name": "Hindustan Unilever"},
    {"symbol": "ITC.NS", "name": "ITC Ltd"},
    {"symbol": "LT.NS", "name": "Larsen & Toubro"},
    {"symbol": "KOTAKBANK.NS", "name": "Kotak Mahindra Bank"},
    {"symbol": "SUNPHARMA.NS", "name": "Sun Pharma"},
    {"symbol": "HCLTECH.NS", "name": "HCL Technologies"},
    {"symbol": "AXISBANK.NS", "name": "Axis Bank"},
    {"symbol": "ULTRACEMCO.NS", "name": "UltraTech Cement"},
    {"symbol": "MARUTI.NS", "name": "Maruti Suzuki"},
    {"symbol": "TITAN.NS", "name": "Titan Company"},
    {"symbol": "POWERGRID.NS", "name": "Power Grid Corporation"},
    {"symbol": "WIPRO.NS", "name": "Wipro"},
    {"symbol": "DRREDDY.NS", "name": "Dr. Reddy’s Laboratories"},
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

banknifty = [
    "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS",
    "AXISBANK.NS", "SBIN.NS", "INDUSINDBK.NS",
    "BANKBARODA.NS", "PNB.NS", "CANBK.NS", "FEDERALBNK.NS"
]

sensex = [
    "RELIANCE.NS", "HDFCBANK.NS", "TCS.NS", "INFY.NS",
    "HINDUNILVR.NS", "ICICIBANK.NS", "ITC.NS", "BAJFINANCE.NS",
    "AXISBANK.NS", "LT.NS", "SBIN.NS", "SUNPHARMA.NS",
    "MARUTI.NS", "TATASTEEL.NS", "BHARTIARTL.NS", "ULTRACEMCO.NS",
    "ONGC.NS", "NTPC.NS", "TITAN.NS", "TECHM.NS", "BRITANNIA.NS",
    "COALINDIA.NS", "BPCL.NS", "DIVISLAB.NS", "ADANIPORTS.NS",
    "HCLTECH.NS", "BAJAJ-AUTO.NS", "BAJAJFINSV.NS", "M&M.NS"
]

db = SessionLocal()

for s in nifty50:
    if not db.query(Stock).filter(Stock.symbol==s["symbol"]).first():
        db.add(Stock(**s))
db.commit()

def populate_index(index_name, symbols):
    for sym in symbols:
        if not db.query(IndexStock).filter(
            IndexStock.index_name==index_name,
            IndexStock.stock_symbol==sym
        ).first():
            db.add(IndexStock(index_name=index_name, stock_symbol=sym))
    db.commit()

populate_index("NIFTY50",[s["symbol"] for s in nifty50])
populate_index("BANKNIFTY",banknifty)
populate_index("SENSEX",sensex)

print("Stocks & indices populated!")
