import requests
from datetime import datetime
from time import sleep

def get_live_nse_price(symbol: str, retries: int = 3, delay: float = 1.0):
    """
    Fetch live NSE price safely with retries.
    """
    url = f"https://www.nseindia.com/api/quote-equity?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.nseindia.com/get-quotes/equity?symbol=" + symbol,
    }

    session = requests.Session()

    # Initial request to get cookies
    try:
        session.get("https://www.nseindia.com", headers=headers, timeout=5)
    except Exception as e:
        raise Exception(f"Initial NSE connection failed: {e}")

    # Retry loop
    for attempt in range(retries):
        try:
            response = session.get(url, headers=headers, timeout=5)
            response.raise_for_status()
            data = response.json()
            price = data['priceInfo']['lastPrice']
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            return {"symbol": symbol, "price": price, "timestamp": timestamp}
        except Exception as e:
            if attempt < retries - 1:
                sleep(delay)  # wait before retrying
                continue
            else:
                raise Exception(f"Failed to fetch {symbol} after {retries} attempts: {e}")
