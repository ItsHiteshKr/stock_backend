from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List

from model.watchlist_model import Watchlist
from schema.watchlist_schema import WatchlistCreate, WatchlistUpdate

class WatchlistService:
    
    @staticmethod
    def create_watchlist(watchlist_data: WatchlistCreate, db: Session):
        """Create a new watchlist"""
        try:
            existing = db.query(Watchlist).filter(
                Watchlist.email == watchlist_data.email,
                Watchlist.watchlist_name == watchlist_data.watchlist_name
            ).first()
            
            if existing:
                raise HTTPException(status_code=400, detail="Watchlist with this name already exists")
            
            new_watchlist = Watchlist(
                email=watchlist_data.email,
                watchlist_name=watchlist_data.watchlist_name,
                symbol=watchlist_data.symbols  
            )
            
            db.add(new_watchlist)
            db.commit()
            db.refresh(new_watchlist)
            
            return new_watchlist
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating watchlist: {str(e)}")
    
    @staticmethod
    def get_user_watchlists(email: str, db: Session):
        """Get all watchlists for a user"""
        try:
            watchlists = db.query(Watchlist).filter(Watchlist.email == email).all()
            return watchlists
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching watchlists: {str(e)}")
    
    @staticmethod
    def get_watchlist_by_id(watchlist_id: int, db: Session):
        """Get specific watchlist by ID"""
        try:
            watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
            if not watchlist:
                raise HTTPException(status_code=404, detail="Watchlist not found")
            return watchlist
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching watchlist: {str(e)}")
    
    @staticmethod
    def update_watchlist(watchlist_id: int, watchlist_data: WatchlistUpdate, db: Session):
        """Update watchlist details"""
        try:
            watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
            if not watchlist:
                raise HTTPException(status_code=404, detail="Watchlist not found")
            
            if watchlist_data.watchlist_name is not None:
                watchlist.watchlist_name = watchlist_data.watchlist_name
            
            if watchlist_data.symbols is not None:
                watchlist.symbol = watchlist_data.symbols  # Update JSON array
            
            db.commit()
            db.refresh(watchlist)
            return watchlist
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating watchlist: {str(e)}")
    
    @staticmethod
    def delete_watchlist(watchlist_id: int, db: Session):
        """Delete a watchlist"""
        try:
            watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
            if not watchlist:
                raise HTTPException(status_code=404, detail="Watchlist not found")
            
            db.delete(watchlist)
            db.commit()
            return {"message": "Watchlist deleted successfully"}
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting watchlist: {str(e)}")
    

    @staticmethod
    def add_symbol_to_watchlist(watchlist_id: int, symbol: str, db: Session):
        """Add a symbol to existing watchlist"""
        try:
            
            watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
            if not watchlist:
                raise HTTPException(status_code=404, detail="Watchlist not found")
            
            # Get current symbols (JSON array)
            current_symbols = watchlist.symbol if watchlist.symbol else []
            
            # Ensure it's a list
            if not isinstance(current_symbols, list):
                current_symbols = []
            
            # Check if symbol already exists
            if symbol in current_symbols:
                raise HTTPException(status_code=400, detail="Symbol already exists in watchlist")
            
            # Add new symbol
            current_symbols.append(symbol)
            
            # Force SQLAlchemy to recognize the change
            watchlist.symbol = None
            db.flush()
            watchlist.symbol = current_symbols
            
            db.commit()
            
            db.refresh(watchlist)
            
            return watchlist
        except HTTPException:
            raise
        except Exception as e:
            import traceback
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error adding symbol: {str(e)}")
    
    @staticmethod
    def remove_symbol_from_watchlist(watchlist_id: int, symbol: str, db: Session):
        """Remove a symbol from watchlist"""
        try:
            watchlist = db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
            if not watchlist:
                raise HTTPException(status_code=404, detail="Watchlist not found")
            
            # Get current symbols
            current_symbols = watchlist.symbol or []
            
            # Check if symbol exists
            if symbol not in current_symbols:
                raise HTTPException(status_code=404, detail="Symbol not found in watchlist")
            
            # Remove symbol
            current_symbols.remove(symbol)
            watchlist.symbol = current_symbols
            
            db.commit()
            db.refresh(watchlist)
            return watchlist
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error removing symbol: {str(e)}")
    
    
