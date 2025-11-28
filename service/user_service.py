from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy.orm import Session

from model.user_model import UserTable
from schema.user_schema import UserUpdate, UserResponse



class UserService:

    @staticmethod
    def get_user_data_by_user_id(user_id: int, db: Session) -> UserTable:
        """Get User data for a specific user ID"""

        db_user = db.query(UserTable).filter(UserTable.id == user_id).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user
    
   


    @staticmethod
    def update_user_data(user_id: int, user: UserUpdate, db: Session) -> UserTable:
        """Update User data for a specific user ID"""

        db_user = db.query(UserTable).filter(UserTable.id == user_id).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.full_name = user.full_name
        db_user.mobile_number = user.mobile_number
        
        db.commit()
        db.refresh(db_user)
        return db_user


    @staticmethod
    def Active_deactivate_user(user_id: int, active_status: int, db: Session) -> UserTable:
        """Activate/Deactivate User account for a specific user ID"""

        db_user = db.query(UserTable).filter(UserTable.id == user_id).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.active = active_status
        
        db.commit()
        db.refresh(db_user)
        return db_user


    @staticmethod
    def delete_user_data_by_user_id(user_id: int, db: Session) -> dict:
        """Delete User data for a specific user ID"""
        db_user = db.query(UserTable).filter(UserTable.id == user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    
    @staticmethod
    def delete_user_data_by_email(email: EmailStr, db: Session) -> dict:
        """Delete User data for a specific user ID"""
        db_user = db.query(UserTable).filter(UserTable.email == email).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(db_user)
        db.commit()
        return {"message": "User deleted successfully"}
    
    @staticmethod
    def get_all_users(skip: int, limit: int, db: Session) -> list[UserResponse]:
        """Get all User data with pagination"""
        return db.query(UserTable).offset(skip).limit(limit).all()