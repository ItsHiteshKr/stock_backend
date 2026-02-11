from sqlalchemy import Column, Integer, Float, Date, BigInteger, ForeignKey, String, UniqueConstraint
from db.database import Base

class DailyData(Base):
    __tablename__ = "daily_data"

    id = Column(Integer, primary_key=True)
    stock_id = Column(Integer, ForeignKey("stocks.id"), index=True)
    symbol = Column(String(20), index=True) 
    date = Column(Date, index=True)

    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adj_close = Column(Float)
    volume = Column(BigInteger)

    timeframe = Column(String(10), default="1D")

    __table_args__ = (
        UniqueConstraint("stock_id", "date", "timeframe"),
    )
