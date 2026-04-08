from model.intraday_model import IntradayData
from model.daily_data import DailyData
from db.database import SessionLocal
import re
import yfinance as yf
from datetime import datetime, timedelta
from utils.cache_utils import stock_cache, get_cache_key, CACHE_TTL
from sqlalchemy import desc


def _clean_name(name: str | None) -> str | None:
    if not name:
        return None
    # Remove trailing Limited/Ltd variants and extra punctuation/spaces
    cleaned = re.sub(r"\s+(LIMITED|Limited|limited|LTD|Ltd)\.?$", "", name).strip()
    cleaned = re.sub(r",+$", "", cleaned).strip()
    return cleaned or name


def _get_price_from_db(symbol: str):
    """
    Fallback: Get latest price from database
    Priority: 1. Today's intraday data (minute-wise)
              2. Latest daily data (day-wise)
    """
    db = SessionLocal()
    try:
        today = datetime.now().date()
        
        # 🔹 PRIORITY 1: Try today's intraday data (most recent)
        latest_intraday = db.query(IntradayData).filter(
            IntradayData.symbol == symbol,
            IntradayData.timestamp >= datetime.combine(today, datetime.min.time())
        ).order_by(desc(IntradayData.timestamp)).first()
        
        if latest_intraday:
            # Get yesterday's close for previousClose
            yesterday = today - timedelta(days=1)
            previous_daily = db.query(DailyData).filter(
                DailyData.symbol == symbol,
                DailyData.date <= yesterday
            ).order_by(desc(DailyData.date)).first()
            
            previousClose = float(previous_daily.close) if previous_daily else float(latest_intraday.close)
            
            # Calculate today's OHLC from all intraday candles
            today_candles = db.query(IntradayData).filter(
                IntradayData.symbol == symbol,
                IntradayData.timestamp >= datetime.combine(today, datetime.min.time())
            ).all()
            
            if today_candles:
                opens = [float(c.open) for c in today_candles]
                highs = [float(c.high) for c in today_candles]
                lows = [float(c.low) for c in today_candles]
                volumes = [int(c.volume) for c in today_candles]
                
                return {
                    "symbol": symbol,
                    "price": float(latest_intraday.close),  # Latest minute's close
                    "open": opens[0] if opens else float(latest_intraday.open),  # First candle's open
                    "high": max(highs) if highs else float(latest_intraday.high),
                    "low": min(lows) if lows else float(latest_intraday.low),
                    "volume": sum(volumes) if volumes else int(latest_intraday.volume),
                    "previousClose": previousClose,
                    "timestamp": latest_intraday.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "name": None,
                    "sector": None,
                    "industry": None,
                    "marketCap": None,
                    "exchange": None,
                    "source": "database_intraday"  # Indicate intraday DB source
                }
        
        # 🔹 PRIORITY 2: Fallback to daily data
        latest_daily = db.query(DailyData).filter(
            DailyData.symbol == symbol
        ).order_by(desc(DailyData.date)).first()
        
        if not latest_daily:
            return None
        
        # Get previous day for previousClose
        previous = db.query(DailyData).filter(
            DailyData.symbol == symbol,
            DailyData.date < latest_daily.date
        ).order_by(desc(DailyData.date)).first()
        
        previousClose = float(previous.close) if previous else float(latest_daily.close)
        
        return {
            "symbol": symbol,
            "price": float(latest_daily.close),
            "open": float(latest_daily.open),
            "high": float(latest_daily.high),
            "low": float(latest_daily.low),
            "volume": int(latest_daily.volume),
            "previousClose": previousClose,
            "timestamp": latest_daily.date.strftime("%Y-%m-%d %H:%M:%S"),
            "name": None,
            "sector": None,
            "industry": None,
            "marketCap": None,
            "exchange": None,
            "source": "database_daily"  # Indicate daily DB source
        }
    except Exception as e:
        print(f"Database fallback failed for {symbol}: {e}")
        return None
    finally:
        db.close()


def get_live_yf_price(symbol: str):
    """
    Get live stock price with caching and rate limit handling
    - First checks cache (2 min TTL)
    - If cache miss, tries Yahoo Finance API
    - If rate limited, falls back to database
    """
    # Check cache first
    cache_key = get_cache_key("live_price", symbol)
    cached_data = stock_cache.get(cache_key)
    
    if cached_data:
        print(f"✅ Cache hit for {symbol}")
        return cached_data
    
    # Cache miss - try Yahoo Finance API
    try:
        stock = yf.Ticker(symbol)

        # Fetch 2-day history to get previousClose and today's OHLCV
        data = stock.history(period="2d", interval="1d")
        
        if data.empty or len(data) < 1:
            # Try database fallback
            db_data = _get_price_from_db(symbol)
            if db_data:
                print(f"⚠️ No YF data, using database for {symbol}")
                stock_cache.set(cache_key, db_data, CACHE_TTL["live_price"])
                return db_data
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

        result = {
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
            "source": "yahoo_finance"
        }
        
        # Cache the result
        stock_cache.set(cache_key, result, CACHE_TTL["live_price"])
        print(f"✅ Fetched and cached {symbol} from Yahoo Finance")
        
        return result
        
    except Exception as e:
        error_msg = str(e).lower()
        
        # Check if it's a rate limit error
        if "rate limit" in error_msg or "too many requests" in error_msg or "429" in error_msg:
            print(f"⚠️ Rate limited for {symbol}, trying database fallback...")
            
            # Try database fallback
            db_data = _get_price_from_db(symbol)
            if db_data:
                # Cache DB data for shorter time (30 seconds) to retry API soon
                stock_cache.set(cache_key, db_data, 30)
                print(f"✅ Using database fallback for {symbol}")
                return db_data
            
            raise Exception(f"Rate limited and no database fallback available for {symbol}")
        
        # For other errors, try database fallback
        db_data = _get_price_from_db(symbol)
        if db_data:
            stock_cache.set(cache_key, db_data, CACHE_TTL["live_price"])
            return db_data
        
        raise Exception(f"Failed to fetch {symbol} price: {e}")
    
def _persist_intraday_batch(sym: str, rows: list[dict]):
    db = SessionLocal()
    try:
        for r in rows:
            exists = db.query(IntradayData.id).filter(
                IntradayData.symbol == sym,
                IntradayData.timestamp == r["timestamp"]
            ).first()
            if exists:
                continue
            db.add(IntradayData(
                symbol=sym,
                timestamp=r["timestamp"],
                open=r["open"],
                high=r["high"],
                low=r["low"],
                close=r["close"],
                volume=r["volume"],
            ))
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()
