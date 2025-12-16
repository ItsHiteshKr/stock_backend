from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from service.trend_service import (
    get_stock_data,
    calculate_trend,
    save_trend_analysis,
    get_trend_history,
    find_support_resistance_levels,
    save_support_resistance,
    detect_candlestick_patterns,
    save_candlestick_patterns,
    get_pattern_history
)
from schema.trend_schema import (
    TrendAnalysisResponse,
    SupportResistanceResponse,
    CandlestickPatternsResponse
)

router = APIRouter(
    prefix="/trend",
    tags=["Trend & Pattern Analysis"]
)


@router.get("/{symbol}", response_model=TrendAnalysisResponse)
async def get_trend(symbol: str, db: Session = Depends(get_db), save_to_db: bool = True):
    """
     trend detection (uptrend, downtrend, sideways)
    
    - **symbol**: Stock symbol (e.g., AAPL, RELIANCE.NS)
    - **save_to_db**: Save analysis to database (default: True)
    """
    df = get_stock_data(symbol.upper(), period="3mo")
    trend_data = calculate_trend(df)
    
    # Save to database if requested
    if save_to_db:
        save_trend_analysis(db, symbol.upper(), trend_data)
    
    return {
        "symbol": symbol.upper(),
        "status": "success",
        "data": trend_data
    }

@router.get("/{symbol}/history")
async def get_trend_analysis_history(symbol: str, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get historical trend analysis for a symbol
    
    - **symbol**: Stock symbol
    - **limit**: Number of records to return (default: 10)
    """
    history = get_trend_history(db, symbol.upper(), limit)
    return {
        "symbol": symbol.upper(),
        "status": "success",
        "total_records": len(history),
        "data": history
    }


@router.get("/support-resistance/{symbol}", response_model=SupportResistanceResponse)
async def get_support_resistance(symbol: str, db: Session = Depends(get_db), save_to_db: bool = True):
    """
    Key support and resistance levels
    
    - **symbol**: Stock symbol
    - **save_to_db**: Save levels to database (default: True)
    """
    df = get_stock_data(symbol.upper(), period="6mo")
    levels_data = find_support_resistance_levels(df)
    
    # Save to database if requested
    if save_to_db:
        save_support_resistance(db, symbol.upper(), levels_data)
    
    return {
        "symbol": symbol.upper(),
        "status": "success",
        "data": levels_data
    }


@router.get("/candlestick/{symbol}", response_model=CandlestickPatternsResponse)
async def get_candlestick_patterns(symbol: str, db: Session = Depends(get_db), save_to_db: bool = True):
    """
    Candlestick patterns (Doji, Hammer, etc.)
    
    - **symbol**: Stock symbol
    - **save_to_db**: Save patterns to database (default: True)
    """
    df = get_stock_data(symbol.upper(), period="1mo")
    patterns_data = detect_candlestick_patterns(df)
    
    # Save to database if requested
    if save_to_db:
        save_candlestick_patterns(db, symbol.upper(), patterns_data)
    
    return {
        "symbol": symbol.upper(),
        "status": "success",
        "data": patterns_data
    }


@router.get("/candlestick/{symbol}/history")
async def get_candlestick_pattern_history(symbol: str, limit: int = 20, db: Session = Depends(get_db)):
    """
    Get historical candlestick patterns for a symbol
    
    - **symbol**: Stock symbol
    - **limit**: Number of patterns to return (default: 20)
    """
    history = get_pattern_history(db, symbol.upper(), limit)
    return {
        "symbol": symbol.upper(),
        "status": "success",
        "total_patterns": len(history),
        "data": history
    }