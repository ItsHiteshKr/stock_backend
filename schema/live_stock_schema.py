from pydantic import BaseModel
from typing import Optional


class StockPriceResponse(BaseModel):
    symbol: str
    price: float
    open: Optional[float] = None
    high: Optional[float] = None
    low: Optional[float] = None
    volume: Optional[int] = None
    previousClose: Optional[float] = None
    timestamp: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    marketCap: Optional[float] = None
    exchange: Optional[str] = None
