from sqlalchemy import Column, Integer, String, JSON
from db.database import Base

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(100), index=True)
    watchlist_name = Column(String(100), index=True)
    symbol = Column(JSON)