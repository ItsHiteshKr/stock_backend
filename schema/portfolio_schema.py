from pydantic import BaseModel, EmailStr, computed_field
from typing import List, Optional
from datetime import datetime


# ============ HOLDING SCHEMAS ============
class HoldingItem(BaseModel):
    """Single stock holding data"""
    symbol: str
    stock_name: Optional[str] = None
    quantity: int
    avg_buy_price: float
    sector: Optional[str] = None


class HoldingUpdate(BaseModel):
    """Schema for updating an existing holding"""
    quantity: Optional[int] = None
    avg_buy_price: Optional[float] = None


# ============ PORTFOLIO SCHEMAS ============
class PortfolioCreate(BaseModel):
    """Create portfolio with multiple stocks at once"""
    user_email: EmailStr
    portfolio_name: str
    holdings: List[HoldingItem]  # Multiple stocks


class PortfolioUpdate(BaseModel):
    """Update portfolio metadata"""
    portfolio_name: Optional[str] = None


class AddHoldingToPortfolio(BaseModel):
    """Add single holding to existing portfolio"""
    symbol: str
    stock_name: Optional[str] = None
    quantity: int
    avg_buy_price: float
    sector: Optional[str] = None


# ============ RESPONSE SCHEMAS ============
class HoldingResponse(BaseModel):
    """Response schema for a single holding"""
    id: int
    portfolio_id: int
    symbol: str
    stock_name: Optional[str]
    quantity: int
    avg_buy_price: float
    total_invested: float
    sector: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class PortfolioListResponse(BaseModel):
    """Response for listing user's portfolios"""
    id: int
    portfolio_name: str
    total_holdings: int
    total_invested: float
    created_at: datetime

    class Config:
        from_attributes = True


class PortfolioDetailResponse(BaseModel):
    """Detailed portfolio response with all holdings"""
    id: int
    user_email: EmailStr
    portfolio_name: str
    holdings: List[HoldingResponse]
    created_at: datetime
    updated_at: Optional[datetime]
    
    @computed_field
    @property
    def total_holdings(self) -> int:
        return len(self.holdings)
    
    @computed_field
    @property
    def total_invested(self) -> float:
        return sum(h.total_invested for h in self.holdings)

    class Config:
        from_attributes = True
