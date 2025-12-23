from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON
from sqlalchemy.sql import func
from db.database import Base

class TrendAnalysis(Base):
    """Store trend analysis results"""
    __tablename__ = "trend_analysis"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    trend = Column(String(20), nullable=False)  # uptrend, downtrend, sideways
    signal = Column(String(10), nullable=False)  # buy, sell, hold
    strength = Column(Float)
    current_price = Column(Float)
    sma_20 = Column(Float)
    sma_50 = Column(Float)
    price_change_5d = Column(Float)
    analysis_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())


class SupportResistance(Base):
    """Store support and resistance levels"""
    __tablename__ = "support_resistance"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    current_price = Column(Float)
    support_levels = Column(JSON)  # Array of support prices
    resistance_levels = Column(JSON)  # Array of resistance prices
    nearest_support = Column(Float)
    nearest_resistance = Column(Float)
    distance_to_support_percent = Column(Float)
    distance_to_resistance_percent = Column(Float)
    analysis_date = Column(DateTime, default=func.now())
    created_at = Column(DateTime, default=func.now())


class CandlestickPattern(Base):
    """Store detected candlestick patterns"""
    __tablename__ = "candlestick_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True, nullable=False)
    pattern = Column(String(50), nullable=False)  # Doji, Hammer, etc.
    pattern_type = Column(String(20))  # bullish, bearish, neutral
    confidence = Column(Integer)  # 0-100
    description = Column(Text)
    pattern_date = Column(DateTime)
    price = Column(Float)
    detected_at = Column(DateTime, default=func.now())