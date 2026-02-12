"""
AI Pattern Matcher Schema
=========================
Request/response models for AI-powered pattern matching.
Uses same data structures as comparison API for chart compatibility.
"""

from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List


class PatternMatchRequest(BaseModel):
    """
    Request - stock symbol aur period_days
    AI automatically finds best matching historical period
    """
    stock_symbol: str = Field(..., description="Stock name like TCS, RELIANCE")
    exchange: str = Field(default="NSE", description="Exchange - NSE or BSE")
    period_days: int = Field(default=30, description="Kitne din ka pattern match karna hai")
    
    class Config:
        json_schema_extra = {
            "example": {
                "stock_symbol": "TCS",
                "exchange": "NSE",
                "period_days": 30
            }
        }


class PeriodDataPoint(BaseModel):
    """Single data point - same as comparison API"""
    day: int
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    change_pct: Optional[float] = None


class PeriodSummary(BaseModel):
    """Period summary statistics"""
    label: str
    start_date: date
    end_date: date
    total_days: int
    start_price: float
    end_price: float
    period_return_pct: float
    avg_price: float
    min_price: float
    max_price: float


class PeriodData(BaseModel):
    """Complete period data with summary and data points"""
    label: str
    summary: PeriodSummary
    data: List[PeriodDataPoint]


class PatternMatchResponse(BaseModel):
    """
    Response - includes full comparison data for charts
    Same structure as comparison API so frontend can render same charts
    """
    success: bool = True
    stock_symbol: str
    exchange: str
    
    # Match info
    match_percentage: float = Field(description="Kitna percentage match hua (0-100)")
    correlation: float = Field(description="Pearson correlation (-1 to 1)")
    
    # Full period data for charts
    current_period: PeriodData
    matched_period: PeriodData
    
    # AI insights
    message: str = Field(description="Simple explanation")
    insights: List[str] = Field(default_factory=list, description="AI analysis insights")
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "stock_symbol": "TCS",
                "exchange": "NSE",
                "match_percentage": 85.5,
                "correlation": 0.87,
                "current_period": {"label": "Jan 11 - Feb 10, 2026", "summary": {}, "data": []},
                "matched_period": {"label": "Mar 01 - Mar 31, 2024", "summary": {}, "data": []},
                "message": "Strong pattern match found!",
                "insights": ["High correlation in price movements"]
            }
        }
