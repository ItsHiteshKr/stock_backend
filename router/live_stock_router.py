from fastapi import APIRouter, HTTPException
from schema.live_stock_schema import StockPriceResponse
from service.live_stock_service import get_live_nse_price

router = APIRouter()

@router.get("/stocks/price/{symbol}", response_model=StockPriceResponse)
def live_stock_price(symbol: str):
    """
    Get live price of NSE symbol safely.
    """
    try:
        data = get_live_nse_price(symbol.upper())
        return data
    except Exception as e:
        # Return clear error to the API user
        raise HTTPException(status_code=500, detail=f"Error fetching {symbol}: {str(e)}")
