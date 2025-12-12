from pydantic import BaseModel

class IndexBase(BaseModel):
    index_name: str
    stock_symbol: str

    class Config:
        orm_mode = True


class IndexListResponse(BaseModel):
    index: str


class PopularIndexResponse(BaseModel):
    index: str
    count: int
