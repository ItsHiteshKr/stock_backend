from pydantic import BaseModel, Field, validator
from typing import Optional


class PatternMatchRequest(BaseModel):
    """Request schema for pattern matching"""
    symbol: str = Field(..., description="Stock symbol", example="TCS.NS", min_length=1, max_length=20)
    years_back: int = Field(default=5, description="Years of historical data", ge=1, le=10)
    window_size: int = Field(default=10, description="Pattern window in days", ge=3, le=100)
    use_cache: bool = Field(default=True, description="Use cached data")
    
    @validator('symbol')
    def validate_symbol(cls, v):
        return v.strip().upper()
    
    class Config:
        schema_extra = {
            "example": {
                "symbol": "TCS.NS",
                "years_back": 5,
                "window_size": 10,
                "use_cache": True
            }
        }


class PatternMatchResponse(BaseModel):
    """Response schema for pattern matching"""
    success: bool = Field(..., description="Request success status")
    message: str = Field(..., description="Response message")
    data: Optional[dict] = Field(None, description="Pattern match data (null on failure)")
    
    class Config:
        schema_extra = {
            "example": {
                "success": True,
                "message": "Pattern match found (Score: 82.45%)",
                "data": {
                    "symbol": "TCS.NS",
                    "current_pattern": {
                        "trend": "UP",
                        "change_percent": 4.29
                    },
                    "best_match": {
                        "score": 82.45,
                        "confidence": "Very Good",
                        "trend": "UP"
                    }
                }
            }
        }