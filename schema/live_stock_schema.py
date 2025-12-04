from pydantic import BaseModel

class StockPriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: str
