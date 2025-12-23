from sqlalchemy import Column, Integer, String, Float, ForeignKey
from db.database import Base

class Index(Base):
    __tablename__ = "indexes"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, index=True)
    exchange = Column(String(10))
    category = Column(String(20))


class IndexStock(Base):
    __tablename__ = "index_stocks"

    id = Column(Integer, primary_key=True)
    index_id = Column(Integer, ForeignKey("indexes.id"), index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    
