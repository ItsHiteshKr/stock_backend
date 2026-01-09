import os
import uuid
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from model.user_extraDetails_model import UserExtraTable
from schema.user_extraDetails_schema import UserExtraDetailsCreate, MAX_FILE_SIZE, ALLOWED_EXTENSIONS

# Upload directory for profile pics
UPLOAD_DIR = "static/uploads/profile_pics"


class UserExtraDetailsService:

    @staticmethod
    def get_user_data_by_user_id(user_id: int, db: Session) -> UserExtraTable:
        """Get User data for a specific user ID"""
        db_user = db.query(UserExtraTable).filter(UserExtraTable.user_id == user_id).first()

        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        return db_user

    @staticmethod
    async def upload_profile_pic(user_id: int, file: UploadFile, db: Session) -> UserExtraTable:
        """Upload profile pic for a user (max 1MB)"""
        
        # Check file extension
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=400, 
                detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
        
        # Read file content
        content = await file.read()
        
        # Check file size (max 1MB)
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400, 
                detail=f"File size exceeds 1MB limit. Your file: {len(content) / (1024*1024):.2f}MB"
            )
        
        # Create upload directory if not exists
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        
        # Generate unique filename
        unique_filename = f"{user_id}_{uuid.uuid4().hex}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Get or create user extra details
        db_user = db.query(UserExtraTable).filter(UserExtraTable.user_id == user_id).first()
        
        # Delete old profile pic if exists
        if db_user and db_user.profile_pic:
            old_file_path = db_user.profile_pic
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
        
        # Save new file
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update or create database record
        if db_user:
            db_user.profile_pic = file_path
        else:
            db_user = UserExtraTable(user_id=user_id, profile_pic=file_path)
            db.add(db_user)
        
        db.commit()
        db.refresh(db_user)
        
        return db_user

    @staticmethod
    def delete_profile_pic(user_id: int, db: Session) -> dict:
        """Delete profile pic for a user"""
        db_user = db.query(UserExtraTable).filter(UserExtraTable.user_id == user_id).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        if db_user.profile_pic and os.path.exists(db_user.profile_pic):
            os.remove(db_user.profile_pic)
        
        db_user.profile_pic = None
        db.commit()
        
        return {"message": "Profile pic deleted successfully"}

    # ==================== RECENT SEARCHES ====================
    
    MAX_RECENT_SEARCHES = 10  # Maximum recent searches to store

    @staticmethod
    def add_recent_search(user_id: int, search_term: str, search_type: str, db: Session) -> dict:
        """
        Add a recent search for a user
        search_type can be: 'stock', 'index', 'sector', etc.
        """
        from datetime import datetime
        
        db_user = db.query(UserExtraTable).filter(UserExtraTable.user_id == user_id).first()
        
        if not db_user:
            # Create new record if user doesn't exist
            db_user = UserExtraTable(user_id=user_id, recent_searches=[])
            db.add(db_user)
        
        # Get current searches or initialize empty list
        current_searches = db_user.recent_searches or []
        
        # Create new search entry
        new_search = {
            "term": search_term,
            "type": search_type,
            "timestamp": datetime.now().isoformat()
        }
        
        # Remove duplicate if same search term exists
        current_searches = [s for s in current_searches if s.get("term") != search_term]
        
        # Add new search at the beginning
        current_searches.insert(0, new_search)
        
        # Keep only last MAX_RECENT_SEARCHES
        current_searches = current_searches[:UserExtraDetailsService.MAX_RECENT_SEARCHES]
        
        # Update database
        db_user.recent_searches = current_searches
        db.commit()
        db.refresh(db_user)
        
        return {"message": "Search added", "recent_searches": current_searches}

    @staticmethod
    def get_recent_searches(user_id: int, db: Session) -> list:
        """Get recent searches for a user"""
        db_user = db.query(UserExtraTable).filter(UserExtraTable.user_id == user_id).first()
        
        if not db_user:
            return []
        
        return db_user.recent_searches or []

    @staticmethod
    def clear_recent_searches(user_id: int, db: Session) -> dict:
        """Clear all recent searches for a user"""
        db_user = db.query(UserExtraTable).filter(UserExtraTable.user_id == user_id).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db_user.recent_searches = []
        db.commit()
        
        return {"message": "Recent searches cleared"}

    @staticmethod
    def remove_single_search(user_id: int, search_term: str, db: Session) -> dict:
        """Remove a specific search from recent searches"""
        db_user = db.query(UserExtraTable).filter(UserExtraTable.user_id == user_id).first()
        
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        current_searches = db_user.recent_searches or []
        
        # Filter out the search term to remove
        updated_searches = [s for s in current_searches if s.get("term") != search_term]
        
        if len(updated_searches) == len(current_searches):
            raise HTTPException(status_code=404, detail="Search term not found")
        
        db_user.recent_searches = updated_searches
        db.commit()
        
        return {"message": "Search removed", "recent_searches": updated_searches}
    