from sqlalchemy import Column, Integer, String, ForeignKey
from db.database import Base

class IndexStock(Base):
    __tablename__ = "index_stocks"
    id = Column(Integer, primary_key=True, index=True)
    index_name = Column(String(50), index=True)  # e.g., NIFTY50, BANKNIFTY
    stock_symbol = Column(String(20))  # foreign key to Stock.symbol ideally
