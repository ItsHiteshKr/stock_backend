from fastapi import APIRouter, Depends
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import List
from db.batabase import get_db
from schema.user_schema import UserResponse, UserUpdate
from service.user_service import UserService

router = APIRouter(
    prefix="/user"
)

@router.put("/{user_id}", response_model=UserResponse)
def update_user_data(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    """Update User data entry"""
    return UserService.update_user_data(user_id, user, db)


@router.get("/{user_id}", response_model=UserResponse)
def get_user_data_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """Get User data entry by user ID"""
    return UserService.get_user_data_by_user_id(user_id, db)

@router.put("/{user_id}/activate")
def activate_user(user_id: int, db: Session = Depends(get_db)):
    """Activate User account by user ID"""
    return UserService.Active_deactivate_user(user_id, 1, db)


@router.put("/{user_id}/deactivate")
def deactivate_user(user_id: int, db: Session = Depends(get_db)):
    """Deactivate User account by user ID"""
    return UserService.Active_deactivate_user(user_id, 0, db)

@router.put("/{email}/activate")
def activate_user(email: EmailStr, db: Session = Depends(get_db)):
    """Activate User account by email"""
    return UserService.Active_deactivate_user(email, 1, db)

@router.put("/{email}/deactivate")
def deactivate_user(email: EmailStr, db: Session = Depends(get_db)):
    """Deactivate User account by email"""
    return UserService.Active_deactivate_user(email, 0, db)

@router.delete("/{user_id}")
def delete_user_data_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """Delete User data entry by user ID"""
    return UserService.delete_user_data_by_user_id(user_id, db)

@router.delete("/by-email/{email}")
def delete_user_data_by_email(email: EmailStr, db: Session = Depends(get_db)):
    """Delete User data entry by email"""
    return UserService.delete_user_data_by_email(email, db)

@router.get("/", response_model=List[UserResponse])
def get_all_users_data(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all User data with pagination"""
    return UserService.get_all_users(skip, limit, db)