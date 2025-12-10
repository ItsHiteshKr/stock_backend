from pydantic import BaseModel, EmailStr, computed_field
from typing import List, Optional

class WatchlistCreate(BaseModel):
    email: EmailStr
    watchlist_name: str
    symbols: List[str] 

class WatchlistUpdate(BaseModel):
    watchlist_name: Optional[str] = None

class WatchlistResponse(BaseModel):
    id: int
    email: str
    watchlist_name: str
    symbol: List[str] 
    
    @computed_field
    @property
    def symbol_count(self) -> int:
        return len(self.symbol or [])
    
    class Config:
        from_attributes = True
