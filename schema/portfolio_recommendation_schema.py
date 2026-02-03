from pydantic import BaseModel, Field
from typing import Dict, List, Optional

class PortfolioRecommendationRequest(BaseModel):
    portfolio: Dict[str, int]
    months: int = 12
    years_of_data: int = Field(default=5, ge=1, le=15, description="Years of historical data to use (1-15 years)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "portfolio": {
                    "RELIANCE.NS": 15,
                    "TCS.NS": 10,
                    "AAPL": 5,
                    "TSLA": 3
                },
                "months": 12,
                "years_of_data": 10
            }
        }

class StockRecommendation(BaseModel):
    ticker: str
    company_name: str
    shares: int
    current_price: float
    projected_price: float
    current_value: float
    projected_value: float
    change_percent: float
    signal: int
    action: str
    confidence_lower: float
    confidence_upper: float
    volatility: float
    rsi: float
    macd: float
    technical_score: int

class PortfolioSummary(BaseModel):
    current_value: float
    projected_value: float
    expected_return: float
    projection_months: int
    total_stocks: int
    valid_stocks: int
    invalid_stocks: int
    years_of_data_used: int

class SignalDistribution(BaseModel):
    buy: int
    sell: int
    hold: int

class InvalidTicker(BaseModel):
    ticker: str
    error: str

class PortfolioRecommendationResponse(BaseModel):
    stocks: List[StockRecommendation]
    portfolio_summary: PortfolioSummary
    signal_distribution: SignalDistribution
    invalid_tickers: List[InvalidTicker]