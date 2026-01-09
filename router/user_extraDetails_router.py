from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from db.database import get_db
from schema.user_extraDetails_schema import UserExtraDetailsResponse
from service.user_extraDetails_service import UserExtraDetailsService

router = APIRouter(
    prefix="/user-details",
    tags=["User Extra Details"]
)

@router.get("/{user_id}", response_model=UserExtraDetailsResponse)
def get_user_extra_details_by_user_id(user_id: int, db: Session = Depends(get_db)):
    """Get User extra details by user ID"""
    return UserExtraDetailsService.get_user_data_by_user_id(user_id, db)


@router.post("/{user_id}/profile-pic", response_model=UserExtraDetailsResponse)
async def upload_profile_pic(
    user_id: int, 
    file: UploadFile = File(..., description="Profile picture (max 1MB, jpg/png/gif/webp)"),
    db: Session = Depends(get_db)
):
    """Upload profile picture for a user (max 1MB)"""
    return await UserExtraDetailsService.upload_profile_pic(user_id, file, db)


@router.delete("/{user_id}/profile-pic")
def delete_profile_pic(user_id: int, db: Session = Depends(get_db)):
    """Delete profile picture for a user"""
    return UserExtraDetailsService.delete_profile_pic(user_id, db)


# ==================== RECENT SEARCHES ROUTES ====================

@router.post("/{user_id}/recent-search")
def add_recent_search(
    user_id: int, 
    search_term: str,
    search_type: str = "stock",  # stock, index, sector, etc.
    db: Session = Depends(get_db)
):
    """
    Add a recent search for a user.
    - search_term: What user searched (e.g., "RELIANCE", "NIFTY 50")
    - search_type: Type of search (stock, index, sector)
    """
    return UserExtraDetailsService.add_recent_search(user_id, search_term, search_type, db)


@router.get("/{user_id}/recent-searches")
def get_recent_searches(user_id: int, db: Session = Depends(get_db)):
    """Get all recent searches for a user (max 10)"""
    return {"recent_searches": UserExtraDetailsService.get_recent_searches(user_id, db)}


@router.delete("/{user_id}/recent-searches")
def clear_recent_searches(user_id: int, db: Session = Depends(get_db)):
    """Clear all recent searches for a user"""
    return UserExtraDetailsService.clear_recent_searches(user_id, db)


@router.delete("/{user_id}/recent-search/{search_term}")
def remove_single_search(user_id: int, search_term: str, db: Session = Depends(get_db)):
    """Remove a specific search from recent searches"""
    return UserExtraDetailsService.remove_single_search(user_id, search_term, db)