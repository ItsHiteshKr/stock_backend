import requests
from datetime import datetime

def get_live_nse_price(symbol: str):
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
    }
    session = requests.Session()
    session.get("https://www.nseindia.com", headers=headers)
    response = session.get(url, headers=headers)
    data = response.json()
    price = data['priceInfo']['lastPrice']
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {"symbol": symbol, "price": price, "timestamp": timestamp}
