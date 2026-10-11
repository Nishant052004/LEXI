from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from models.db_models import User, Conversation, ChatLog
from models.schemas import ConversationResponse, ChatLogResponse
from api.dependencies import get_current_user
from utils.logger import setup_logger

logger = setup_logger("api_history")
router = APIRouter(prefix="/api/history", tags=["Conversation History"])

@router.get("/conversations", response_model=List[ConversationResponse])
def get_user_conversations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all conversations initiated by the user."""
    convos = db.query(Conversation).filter(
        Conversation.user_id == current_user.id
    ).order_by(Conversation.created_at.desc()).all()
    return convos

@router.post("/conversations", response_model=ConversationResponse)
def create_user_conversation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Creates a new conversation session for the user."""
    from memory.memory_manager import memory_manager
    convo = memory_manager.get_or_create_conversation(db, user_id=current_user.id, title="New Session")
    return convo

@router.get("/conversations/{convo_id}/logs", response_model=List[ChatLogResponse])
def get_conversation_logs(
    convo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves individual chat logs and execution states for a specific conversation."""
    # Verify ownership of conversation
    convo = db.query(Conversation).filter(
        Conversation.id == convo_id,
        Conversation.user_id == current_user.id
    ).first()
    
    if not convo:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversation not found or access denied."
        )
        
    logs = db.query(ChatLog).filter(
        ChatLog.conversation_id == convo_id
    ).order_by(ChatLog.logged_at.asc()).all()
    return logs
