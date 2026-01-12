from sqlalchemy import Column, Integer, String, Float, JSON, DateTime
from db.database import Base
from datetime import datetime

class PortfolioRecommendation(Base):
    __tablename__ = "portfolio_recommendations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_email = Column(String(255), index=True, nullable=True)
    portfolio_data = Column(JSON, nullable=False)
    projection_months = Column(Integer, default=12)
    analysis_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<PortfolioRecommendation(id={self.id}, user_email={self.user_email})>"