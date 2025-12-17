from sqlalchemy.orm import Session
from model.trend_model import TrendAnalysis, SupportResistance, CandlestickPattern
from typing import Dict, List
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from fastapi import HTTPException

# ============================================
# DATA FETCHING
# ============================================

def get_stock_data(symbol: str, period: str = "3mo") -> pd.DataFrame:
    """
    Fetch stock data from Yahoo Finance
    
    Args:
        symbol: Stock symbol
        period: Time period (1mo, 3mo, 6mo, 1y)
    
    Returns:
        DataFrame with OHLCV data
    """
    try:
        stock = yf.Ticker(symbol)
        df = stock.history(period=period)
        
        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No data found for symbol: {symbol}"
            )
        return df
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Error fetching data for {symbol}: {str(e)}"
        )


# ============================================
# TREND ANALYSIS
# ============================================

def calculate_trend(df: pd.DataFrame) -> Dict:
    """Calculate trend analysis"""
    
    df['SMA_20'] = df['Close'].rolling(window=20).mean()
    df['SMA_50'] = df['Close'].rolling(window=50).mean()
    
    current_price = df['Close'].iloc[-1]
    sma_20 = df['SMA_20'].iloc[-1]
    sma_50 = df['SMA_50'].iloc[-1]
    prev_price = df['Close'].iloc[-5] if len(df) >= 5 else df['Close'].iloc[0]
    
    if pd.isna(sma_20) or pd.isna(sma_50):
        trend = "insufficient_data"
        strength = 0
        signal = "hold"
    elif current_price > sma_20 > sma_50:
        trend = "uptrend"
        strength = min(((current_price - sma_50) / sma_50) * 100, 100)
        signal = "buy"
    elif current_price < sma_20 < sma_50:
        trend = "downtrend"
        strength = min(((sma_50 - current_price) / sma_50) * 100, 100)
        signal = "sell"
    else:
        trend = "sideways"
        strength = 50
        signal = "hold"
    
    price_change = ((current_price - prev_price) / prev_price) * 100
    
    return {
        "trend": trend,
        "signal": signal,
        "strength": round(abs(strength), 2),
        "current_price": round(current_price, 2),
        "sma_20": round(sma_20, 2) if not pd.isna(sma_20) else None,
        "sma_50": round(sma_50, 2) if not pd.isna(sma_50) else None,
        "price_change_5d": round(price_change, 2),
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_trend_analysis(db: Session, symbol: str, trend_data: Dict):
    """Save trend analysis to database"""
    try:
        trend_record = TrendAnalysis(
            symbol=symbol,
            trend=trend_data["trend"],
            signal=trend_data["signal"],
            strength=trend_data["strength"],
            current_price=trend_data["current_price"],
            sma_20=trend_data["sma_20"],
            sma_50=trend_data["sma_50"],
            price_change_5d=trend_data["price_change_5d"]
        )
        db.add(trend_record)
        db.commit()
        db.refresh(trend_record)
        return trend_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_trend_history(db: Session, symbol: str, limit: int = 10):
    """Get historical trend analysis for a symbol"""
    return db.query(TrendAnalysis)\
        .filter(TrendAnalysis.symbol == symbol)\
        .order_by(TrendAnalysis.created_at.desc())\
        .limit(limit)\
        .all()


# ============================================
# SUPPORT & RESISTANCE
# ============================================

def find_support_resistance_levels(df: pd.DataFrame) -> Dict:
    """Identify support and resistance levels"""
    
    window = 10
    support_levels = []
    resistance_levels = []
    
    for i in range(window, len(df) - window):
        if df['Low'].iloc[i] == df['Low'].iloc[i-window:i+window+1].min():
            support_levels.append(df['Low'].iloc[i])
    
    for i in range(window, len(df) - window):
        if df['High'].iloc[i] == df['High'].iloc[i-window:i+window+1].max():
            resistance_levels.append(df['High'].iloc[i])
    
    support_levels = sorted(list(set([round(x, 2) for x in support_levels[-5:]])))
    resistance_levels = sorted(list(set([round(x, 2) for x in resistance_levels[-5:]])))
    
    current_price = df['Close'].iloc[-1]
    nearest_support = max([x for x in support_levels if x < current_price], default=None)
    nearest_resistance = min([x for x in resistance_levels if x > current_price], default=None)
    
    return {
        "current_price": round(current_price, 2),
        "support_levels": support_levels,
        "resistance_levels": resistance_levels,
        "nearest_support": nearest_support,
        "nearest_resistance": nearest_resistance,
        "distance_to_support_percent": round(((current_price - nearest_support) / current_price * 100), 2) if nearest_support else None,
        "distance_to_resistance_percent": round(((nearest_resistance - current_price) / current_price * 100), 2) if nearest_resistance else None,
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_support_resistance(db: Session, symbol: str, levels_data: Dict):
    """Save support/resistance levels to database"""
    try:
        sr_record = SupportResistance(
            symbol=symbol,
            current_price=levels_data["current_price"],
            support_levels=levels_data["support_levels"],
            resistance_levels=levels_data["resistance_levels"],
            nearest_support=levels_data["nearest_support"],
            nearest_resistance=levels_data["nearest_resistance"],
            distance_to_support_percent=levels_data["distance_to_support_percent"],
            distance_to_resistance_percent=levels_data["distance_to_resistance_percent"]
        )
        db.add(sr_record)
        db.commit()
        db.refresh(sr_record)
        return sr_record
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


# CANDLESTICK PATTERNS
def detect_candlestick_patterns(df: pd.DataFrame) -> Dict:
    """Detect candlestick patterns"""
    
    patterns_detected = []
    
    for i in range(max(0, len(df) - 5), len(df)):
        candle = df.iloc[i]
        
        open_price = candle['Open']
        close_price = candle['Close']
        high = candle['High']
        low = candle['Low']
        
        body = abs(close_price - open_price)
        total_range = high - low
        upper_shadow = high - max(open_price, close_price)
        lower_shadow = min(open_price, close_price) - low
        
        candle_date = df.index[i].strftime('%Y-%m-%d')
        
        if total_range == 0:
            continue
        
        if body < total_range * 0.1:
            patterns_detected.append({
                "pattern": "Doji",
                "type": "neutral",
                "confidence": 75,
                "description": "Market indecision",
                "date": candle_date,
                "price": round(close_price, 2)
            })
        
        elif lower_shadow > body * 2 and upper_shadow < body * 0.5 and close_price > open_price:
            patterns_detected.append({
                "pattern": "Hammer",
                "type": "bullish",
                "confidence": 80,
                "description": "Bullish reversal signal",
                "date": candle_date,
                "price": round(close_price, 2)
            })
        
        elif lower_shadow > body * 2 and upper_shadow < body * 0.5 and close_price < open_price:
            patterns_detected.append({
                "pattern": "Hanging Man",
                "type": "bearish",
                "confidence": 75,
                "description": "Potential bearish reversal",
                "date": candle_date,
                "price": round(close_price, 2)
            })
        
        elif upper_shadow > body * 2 and lower_shadow < body * 0.5:
            patterns_detected.append({
                "pattern": "Shooting Star",
                "type": "bearish",
                "confidence": 80,
                "description": "Strong bearish signal",
                "date": candle_date,
                "price": round(close_price, 2)
            })
        
        if i > 0:
            prev_candle = df.iloc[i-1]
            prev_body = abs(prev_candle['Close'] - prev_candle['Open'])
            
            if (prev_candle['Close'] < prev_candle['Open'] and
                close_price > open_price and
                body > prev_body * 1.5):
                patterns_detected.append({
                    "pattern": "Bullish Engulfing",
                    "type": "bullish",
                    "confidence": 85,
                    "description": "Strong bullish reversal",
                    "date": candle_date,
                    "price": round(close_price, 2)
                })
    
    return {
        "total_patterns_found": len(patterns_detected),
        "patterns": patterns_detected,
        "analysis_period": "Last 5 trading days",
        "analysis_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }


def save_candlestick_patterns(db: Session, symbol: str, patterns_data: Dict):
    """Save detected patterns to database"""
    try:
        saved_patterns = []
        for pattern in patterns_data["patterns"]:
            pattern_record = CandlestickPattern(
                symbol=symbol,
                pattern=pattern["pattern"],
                pattern_type=pattern["type"],
                confidence=pattern["confidence"],
                description=pattern["description"],
                pattern_date=datetime.strptime(pattern["date"], "%Y-%m-%d"),
                price=pattern["price"]
            )
            db.add(pattern_record)
            saved_patterns.append(pattern_record)
        
        db.commit()
        return saved_patterns
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def get_pattern_history(db: Session, symbol: str, limit: int = 20):
    """Get historical patterns for a symbol"""
    return db.query(CandlestickPattern)\
        .filter(CandlestickPattern.symbol == symbol)\
        .order_by(CandlestickPattern.detected_at.desc())\
        .limit(limit)\
        .all()