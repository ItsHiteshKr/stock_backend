
from db.database import get_db, Base
from sqlalchemy import Column, Integer, String, Float, DateTime, BigInteger, UniqueConstraint

# Create Intraday model
class IntradayData(Base):
    __tablename__ = "intraday_data"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), index=True)
    timestamp = Column(DateTime, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(BigInteger)

    __table_args__ = (UniqueConstraint("symbol", "timestamp"),)
