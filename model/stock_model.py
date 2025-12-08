from sqlalchemy import Column, Integer, String, Float, DateTime, Text
from sqlalchemy.orm import relationship
from db.database import Base
from datetime import datetime

class StockFundamentals(Base):
    __tablename__ = "stock_fundamentals"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), unique=True, index=True)
    name = Column(String(100))
    sector = Column(String(50))
    industry = Column(String(50))
    market_cap = Column(Float)
    pe_ratio = Column(Float)
    pb_ratio = Column(Float)
    eps = Column(Float)
    dividend_yield = Column(Float)
    last_updated = Column(DateTime, default=datetime.utcnow)
    live_price = Column(Float, default=0.0)



class CustomScreener(Base):
    __tablename__ = "custom_screeners"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)
    description = Column(Text, nullable=True)
    filters = Column(Text)  # JSON string with filter criteria
    created_at = Column(DateTime, default=datetime.utcnow)
