from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# REQUEST SCHEMAS
class TrendAnalysisRequest(BaseModel):
    """Request schema for trend analysis"""
    symbol: str = Field(..., description="Stock symbol (e.g., AAPL, RELIANCE.NS)")
    period: Optional[str] = Field("3mo", description="Time period: 1mo, 3mo, 6mo, 1y")


# RESPONSE SCHEMAS
class TrendDataResponse(BaseModel):
    """Trend analysis data response"""
    trend: str
    signal: str
    strength: float
    current_price: float
    sma_20: Optional[float]
    sma_50: Optional[float]
    price_change_5d: float
    analysis_date: str
    
    class Config:
        from_attributes = True


class TrendAnalysisResponse(BaseModel):
    """Complete trend analysis response"""
    symbol: str
    status: str
    data: TrendDataResponse


class SupportResistanceData(BaseModel):
    """Support and resistance data response"""
    current_price: float
    support_levels: List[float]
    resistance_levels: List[float]
    nearest_support: Optional[float]
    nearest_resistance: Optional[float]
    distance_to_support_percent: Optional[float]
    distance_to_resistance_percent: Optional[float]
    analysis_date: str
    
    class Config:
        from_attributes = True


class SupportResistanceResponse(BaseModel):
    """Complete support/resistance response"""
    symbol: str
    status: str
    data: SupportResistanceData


class CandlestickPatternData(BaseModel):
    """Individual pattern data"""
    pattern: str
    type: str
    confidence: int
    description: str
    date: str
    price: float


class CandlestickPatternsData(BaseModel):
    """Candlestick patterns data response"""
    total_patterns_found: int
    patterns: List[CandlestickPatternData]
    analysis_period: str
    analysis_date: str


class CandlestickPatternsResponse(BaseModel):
    """Complete candlestick patterns response"""
    symbol: str
    status: str
    data: CandlestickPatternsData

# DATABASE SCHEMAS
class TrendAnalysisDB(BaseModel):
    """Schema for saving trend analysis to DB"""
    id: int
    symbol: str
    trend: str
    signal: str
    strength: float
    current_price: float
    sma_20: Optional[float]
    sma_50: Optional[float]
    price_change_5d: float
    analysis_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class SupportResistanceDB(BaseModel):
    """Schema for saving support/resistance to DB"""
    id: int
    symbol: str
    current_price: float
    support_levels: List[float]
    resistance_levels: List[float]
    nearest_support: Optional[float]
    nearest_resistance: Optional[float]
    distance_to_support_percent: Optional[float]
    distance_to_resistance_percent: Optional[float]
    analysis_date: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True

class CandlestickPatternDB(BaseModel):
    """Schema for saving candlestick pattern to DB"""
    id: int
    symbol: str
    pattern: str
    pattern_type: str
    confidence: int
    description: str
    pattern_date: datetime
    price: float
    detected_at: datetime
    
    class Config:
        from_attributes = True