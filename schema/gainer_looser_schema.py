from pydantic import BaseModel

class IndexBase(BaseModel):
    stock_symbol: str
    stock_name: str
    percent_change: float

    class Config:
        orm_mode = True
