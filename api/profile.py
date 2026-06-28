from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.db_models import User
from models.schemas import UserResponse, PreferenceUpdate
from api.dependencies import get_current_user
from memory.memory_manager import memory_manager
from utils.logger import setup_logger

logger = setup_logger("api_profile")
router = APIRouter(prefix="/api/profile", tags=["User Profile"])

@router.get("", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """Fetches user profile details."""
    return current_user

@router.get("/preferences")
def get_preferences(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Fetches user configuration settings."""
    prefs = memory_manager.get_user_preferences(db, current_user.id)
    return prefs

@router.put("/preferences")
def update_preferences(
    payload: PreferenceUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Updates user configuration settings."""
    success = memory_manager.update_user_preferences(db, current_user.id, payload.preferences)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found."
        )
    return {"status": "success", "message": "Preferences updated successfully."}
