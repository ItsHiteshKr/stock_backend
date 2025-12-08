from pydantic import BaseModel

class MonthlyData(BaseModel):
    year: int
    month: int
    open: float
    high: float
    low: float
    close: float

class YearlyData(BaseModel):
    year: int
    open: float
    high: float
    low: float
    close: float

class RangeData(BaseModel):
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: int
