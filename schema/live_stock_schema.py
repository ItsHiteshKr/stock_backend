from pydantic import BaseModel
from typing import Optional


class StockPriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: str
    name: Optional[str] = None
    sector: Optional[str] = None
    industry: Optional[str] = None
    marketCap: Optional[float] = None
    exchange: Optional[str] = None
