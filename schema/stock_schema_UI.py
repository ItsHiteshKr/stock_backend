from pydantic import BaseModel

class StockBase(BaseModel):
    symbol: str
    name: str

    class Config:
        orm_mode = True


class StockBaseWithSector(BaseModel):
    symbol: str
    name: str
    sector: str

    class Config:
        orm_mode = True

class PopularStockResponse(BaseModel):
    symbol: str
