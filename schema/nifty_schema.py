from pydantic import BaseModel
from datetime import date
from typing import Optional

class NiftyDataCreate(BaseModel):
    date: date
    open: float
    high: float
    low: float
    close: float
    shares_traded: int
    turnover_in_crores: Optional[float] = None

    class Config:
        from_attributes = True

class NiftyDataResponse(BaseModel):
    id: int
    date: date
    open: float
    high: float
    low: float
    close: float
    shares_traded: int
    turnover_in_crores: Optional[float] = None

    class Config:
        from_attributes = True

class NiftyDataUpdate(BaseModel):
    id: int
    date: date
    open: float
    high: float
    low: float
    close: float
    shares_traded: int
    turnover_in_crores: Optional[float] = None

    class Config:
        from_attributes = True

# Alias for backward compatibility
NiftyData = NiftyDataResponse
