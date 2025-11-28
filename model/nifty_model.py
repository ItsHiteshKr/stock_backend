from sqlalchemy import Column, Integer, Float, Date
from db.batabase import Base

class NiftyTable(Base):
    __tablename__ = "nifty_data"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    date = Column(Date, nullable=False, unique=True, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    shares_traded = Column(Integer, nullable=True)
    turnover_in_crores = Column(Float, nullable=True)

