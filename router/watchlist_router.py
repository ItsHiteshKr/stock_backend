from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from pydantic import EmailStr

from db.database import get_db
from schema.watchlist_schema import WatchlistCreate, WatchlistUpdate, WatchlistListsResponse,WatchlistDetailsResponse
from service.watchlist_service import WatchlistService

router = APIRouter(
    prefix="/watchlist"
)

@router.post("/", response_model=WatchlistDetailsResponse)
def create_watchlist(watchlist: WatchlistCreate, db: Session = Depends(get_db)):
    """
    Create a new watchlist with symbols
    Example:
    {
        "email": "user@example.com",
        "watchlist_name": "My Tech Stocks",
        "symbols": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "WIPRO.NS", "HDFCBANK.NS"]
    }
    """
    return WatchlistService.create_watchlist(watchlist, db)

@router.get("/list/{email}", response_model=List[WatchlistListsResponse])
def get_user_all_watchlists_list(email: EmailStr, db: Session = Depends(get_db)):
    """Get all watchlists for a specific user"""
    return WatchlistService.get_user_all_watchlists_list(email, db)

@router.get("/detail/{email}", response_model=List[WatchlistDetailsResponse])
def get_user_all_watchlists_detail(email: EmailStr, db: Session = Depends(get_db)):
    """Get all watchlists for a specific user"""
    return WatchlistService.get_user_all_watchlists_detail(email, db)

@router.get("/{watchlist_id}", response_model=WatchlistDetailsResponse)
def get_watchlist(watchlist_id: int, db: Session = Depends(get_db)):        
    """Get a specific watchlist by ID"""
    return WatchlistService.get_watchlist_by_id(watchlist_id, db)

@router.put("/{watchlist_id}", response_model=WatchlistDetailsResponse)
def update_watchlist(watchlist_id: int, watchlist: WatchlistUpdate, db: Session = Depends(get_db)):
    """
    Update watchlist name or symbols
    Example:
    {
        "watchlist_name": "Updated Name",
        "symbols": ["RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
    }
    """
    return WatchlistService.update_watchlist(watchlist_id, watchlist, db)

@router.delete("/{watchlist_id}")
def delete_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    """Delete a watchlist"""
    return WatchlistService.delete_watchlist(watchlist_id, db)


@router.post("/{watchlist_id}/add-symbol/{symbol}", response_model=WatchlistDetailsResponse)
def add_symbol(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Add a single symbol to watchlist"""
    return WatchlistService.add_symbol_to_watchlist(watchlist_id, symbol, db)

@router.delete("/{watchlist_id}/remove-symbol/{symbol}", response_model=WatchlistDetailsResponse)
def remove_symbol(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Remove a symbol from watchlist"""
    return WatchlistService.remove_symbol_from_watchlist(watchlist_id, symbol, db)


