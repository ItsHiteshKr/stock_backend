from fastapi import APIRouter, HTTPException
from schema.live_stock_schema import StockPriceResponse
from service.live_stock_service import get_live_yf_price  # updated

router = APIRouter()

@router.get("/stocks/price/{symbol}", response_model=StockPriceResponse)
def live_stock_price(symbol: str):
    try:
        data = get_live_yf_price(symbol.upper())
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
