from pydantic import BaseModel
from datetime import datetime
from typing import Optional

# Max file size: 1MB
MAX_FILE_SIZE = 1 * 1024 * 1024  # 1MB in bytes
ALLOWED_EXTENSIONS = [".jpg", ".jpeg", ".png", ".gif", ".webp"]

class UserExtraDetailsCreate(BaseModel):
    user_id: int
    location: Optional[str] = None
    recent_searches: Optional[dict] = None

    class Config:
        from_attributes = True

class UserExtraDetailsResponse(BaseModel):
    id: int
    user_id: int
    profile_pic: Optional[str] = None
    location: Optional[str] = None
    recent_searches: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserExtraDetailsUpdate(BaseModel):
    profile_pic: Optional[str] = None
    location: Optional[str] = None
    recent_searches: Optional[dict] = None