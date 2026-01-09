from sqlalchemy import JSON, Column, Integer, String, DateTime
from sqlalchemy.sql import func
from db.database import Base

class UserExtraTable(Base):
    __tablename__ = "user_extra_details"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, unique=True, nullable=False)
    profile_pic = Column(String(255), nullable=True)  # stores file path
    location = Column(String(100), nullable=True)
    recent_searches = Column(JSON, nullable=True)  # stores list of recent searches
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())