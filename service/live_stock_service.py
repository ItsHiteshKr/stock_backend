import yfinance as yf
from datetime import datetime

def get_live_yf_price(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        data = stock.history(period="1d", interval="1m")
        if not data.empty:
            price = data['Close'][-1]
        else:
            price = 0.0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {"symbol": symbol, "price": price, "timestamp": timestamp}
    except Exception as e:
        raise Exception(f"Failed to fetch {symbol} price: {e}")
