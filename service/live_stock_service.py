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

        # Price (fast path from history)
        data = stock.history(period="1d", interval="1m")
        price = data['Close'][-1] if not data.empty else 0.0

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
            "timestamp": timestamp,
            "name": name,
            "sector": sector,
            "industry": industry,
            "marketCap": market_cap,
            "exchange": exchange,
        }
    except Exception as e:
        raise Exception(f"Failed to fetch {symbol} price: {e}")
