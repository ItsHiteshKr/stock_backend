from pydantic import BaseModel

class IndexBase(BaseModel):
    stock_symbol: str

    class Config:
        orm_mode = True


class IndexListResponse(BaseModel):
    index: str

    class Config:
        from_attributes = True

class PopularIndexResponse(BaseModel):
    index: str
    count: int

    class Config:
        from_attributes = True