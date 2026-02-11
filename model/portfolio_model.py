from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from db.database import Base


class Portfolio(Base):
    """User's portfolio (like Groww, Zerodha, etc.)"""
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True)
    portfolio_name = Column(String(50), nullable=False)
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationship to holdings
    holdings = relationship("PortfolioHolding", back_populates="portfolio", cascade="all, delete-orphan")

    # Unique constraint: one portfolio name per user
    __table_args__ = (
        UniqueConstraint('user_id', 'portfolio_name', name='uq_user_portfolio'),
        {'mysql_engine': 'InnoDB'}
    )


class PortfolioHolding(Base):
    """Individual stock holdings in a portfolio"""
    __tablename__ = "portfolio_holdings"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id", onupdate="CASCADE", ondelete="CASCADE"), nullable=False, index=True)
    symbol = Column(String(20), nullable=False, index=True)
    stock_name = Column(String(100), nullable=True)
    quantity = Column(Integer, nullable=False, default=0)
    avg_buy_price = Column(Float, nullable=False, default=0.0)
    total_invested = Column(Float, nullable=False, default=0.0)
    sector = Column(String(50), nullable=True)
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=True, onupdate=func.now())

    # Relationship back to portfolio
    portfolio = relationship("Portfolio", back_populates="holdings")

    # Unique constraint: one symbol per portfolio
    __table_args__ = (
        UniqueConstraint('portfolio_id', 'symbol', name='uq_portfolio_symbol'),
        {'mysql_engine': 'InnoDB'}
    )