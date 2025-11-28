from pydantic import BaseModel,EmailStr
from datetime import  datetime
from typing import Optional

class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    mobile_number: int
    password: str
    country: Optional[str] = 'IN'

    class Config:
        from_attributes = True

class UserUpdate(BaseModel):
    full_name: str
    mobile_number: int

    class Config:
        from_attributes = True

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    mobile_number: int
    country: Optional[str] = "IN"
    active: int
    created_at: datetime = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class UserDeleteResponse(BaseModel):
    detail: str

    class Config:
        from_attributes = True

