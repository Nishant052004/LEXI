from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.connection import get_db
from models.db_models import User, Conversation, Entity
from models.schemas import EntityResponse
from api.dependencies import get_current_user
from ner.ner_module import ner_extractor
from utils.logger import setup_logger

logger = setup_logger("api_entities")
router = APIRouter(prefix="/api/entities", tags=["Named Entity Extraction"])

@router.get("/conversations/{convo_id}", response_model=List[EntityResponse])
def get_extracted_entities(
    convo_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieves all named entities extracted during a conversation."""
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
        
    entities = db.query(Entity).filter(
        Entity.conversation_id == convo_id
    ).order_by(Entity.extracted_at.desc()).all()
    return entities

@router.post("/custom", status_code=status.HTTP_201_CREATED)
def register_custom_entity(
    label: str,
    literal_text: str,
    current_user: User = Depends(get_current_user)
):
    """
    Registers a new custom entity label dynamically at runtime.
    Emails, phone numbers, and default spaCy labels are matched automatically;
    use this route to match custom literals (e.g. project name 'Antigravity' -> 'PROJECT').
    """
    if current_user.role != "admin" and current_user.role != "user":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized role to register custom entities."
        )
        
    ner_extractor.add_custom_entity_label(label, literal_text)
    
    return {
        "status": "success",
        "message": f"Successfully registered literal text '{literal_text}' to custom label '{label.upper()}'."
    }
