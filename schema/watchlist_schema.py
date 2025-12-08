from pydantic import BaseModel, EmailStr
from typing import List, Optional

class WatchlistCreate(BaseModel):
    email: EmailStr
    watchlist_name: str
    symbols: List[str] 

class WatchlistUpdate(BaseModel):
    watchlist_name: Optional[str] = None
    symbols: Optional[List[str]] = None

class WatchlistResponse(BaseModel):
    id: int
    email: str
    watchlist_name: str
    symbol: List[str] 
    
    class Config:
        from_attributes = True
