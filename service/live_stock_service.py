import re
import yfinance as yf
from datetime import datetime


def _clean_name(name: str | None) -> str | None:
    if not name:
        return None
    # Remove trailing Limited/Ltd variants and extra punctuation/spaces
    cleaned = re.sub(r"\s+(LIMITED|Limited|limited|LTD|Ltd)\.?$", "", name).strip()
    cleaned = re.sub(r",+$", "", cleaned).strip()
    return cleaned or name


def get_live_yf_price(symbol: str):
    try:
        stock = yf.Ticker(symbol)

        # Fetch 2-day history to get previousClose and today's OHLCV
        data = stock.history(period="2d", interval="1d")
        
        if data.empty or len(data) < 1:
            raise Exception(f"No data available for {symbol}")
        
        # Current day (latest row)
        current = data.iloc[-1]
        price = float(current['Close'])
        high = float(current['High'])
        low = float(current['Low'])
        open_price = float(current['Open'])
        volume = int(current['Volume']) if current['Volume'] > 0 else 0
        
        # Previous close (if we have 2 days)
        previousClose = float(data.iloc[-2]['Close']) if len(data) >= 2 else price

        # Metadata (name/sector/market cap). This can fail on some tickers, so keep it guarded.
        try:
            info = stock.info or {}
        except Exception:
            info = {}

        raw_name = info.get("shortName") or info.get("longName")
        name = _clean_name(raw_name)
        sector = info.get("sector")
        industry = info.get("industry")
        market_cap = info.get("marketCap")
        exchange = info.get("exchange") or info.get("fullExchangeName")

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        return {
            "symbol": symbol,
            "price": price,
            "open": open_price,
            "high": high,
            "low": low,
            "volume": volume,
            "previousClose": previousClose,
            "timestamp": timestamp,
            "name": name,
            "sector": sector,
            "industry": industry,
            "marketCap": market_cap,
            "exchange": exchange,
        }
    except Exception as e:
        raise Exception(f"Failed to fetch {symbol} price: {e}")
