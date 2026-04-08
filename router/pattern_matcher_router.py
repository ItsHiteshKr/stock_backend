"""
AI Pattern Matcher API
======================
Find historical periods with similar patterns using AI correlation.

Endpoints:
  GET  /pattern/match/{stock}   - AI finds best matching period (with chart data)
  GET  /pattern/stocks          - List available stocks from database
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session

from db.database import get_db
from schema.pattern_matcher_schema import PatternMatchRequest, PatternMatchResponse
from service.pattern_matcher_service import find_best_match, get_available_stocks


router = APIRouter(prefix="/pattern", tags=["Pattern Matcher"])


@router.get(
    "/match/{stock_symbol}",
    response_model=PatternMatchResponse,
    summary="AI Pattern Match - Find Best Historical Period"
)
async def find_matching_period(
    stock_symbol: str,
    exchange: str = Query(default="NSE", description="Exchange - NSE or BSE"),
    period_days: int = Query(default=30, ge=7, le=365, description="Period in days"),
    db: Session = Depends(get_db)
):
    """
    AI-powered pattern matching using real historical data.
    
    **How it works:**
    1. Fetches current period price data
    2. Scans through up to 5 years of history
    3. Uses Pearson correlation to find the most similar price pattern
    4. Returns full chart data for both periods
    
    **Input:**
    - stock_symbol: Stock name (TCS, RELIANCE, INFY, etc.)
    - exchange: NSE or BSE
    - period_days: Number of days (default 30)
    
    **Output:**
    - Match percentage and correlation score
    - Full price data for both periods (for chart rendering)
    - AI-generated insights
    
    **Example:**
    ```
    GET /pattern/match/TCS?exchange=NSE&period_days=30
    ```
    """
    try:
        request = PatternMatchRequest(
            stock_symbol=stock_symbol,
            exchange=exchange,
            period_days=period_days
        )
        result = find_best_match(db, request)
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stocks", summary="List Available Stocks")
async def list_stocks(db: Session = Depends(get_db)):
    """
    Get list of available stocks from database for pattern matching.
    """
    stocks = get_available_stocks(db)
    return {
        "success": True,
        "total_stocks": len(stocks),
        "stocks": stocks
    }
