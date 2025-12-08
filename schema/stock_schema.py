# schema/nifty_schema.py
from pydantic import BaseModel

class ScreenerFilter(BaseModel):
    min_price: float
    max_price: float
    min_pe: float
    max_pe: float

class ScreenerAdvanced(BaseModel):
    min_pe: float
    max_pe: float
    min_pb: float
    max_pb: float
    min_mcap: float
    max_mcap: float
