from sqlalchemy import Column, Integer, String, Boolean
from db.database import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(100))


    exchange = Column(String(10), default="NSE")
    is_active = Column(Boolean, default=True)
