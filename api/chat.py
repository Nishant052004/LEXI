from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import time

from database.connection import get_db
from models.db_models import User, ChatLog
from models.schemas import ChatRequest, ChatResponse
from api.dependencies import get_current_user, check_rate_limit
from coordinator import decide_agent
from utils.logger import setup_logger

logger = setup_logger("api_chat")
router = APIRouter(prefix="/api/chat", tags=["Chat"])

@router.post("", response_model=ChatResponse, dependencies=[Depends(check_rate_limit)])
def chat(
    payload: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submits a prompt to the Multi-Agent Chatbot.
    Requires JWT authentication and obeys rate limits.
    """
    logger.info(f"API chat request from user '{current_user.username}': {payload.prompt}")
    
    start_time = time.perf_counter()
    
    # Run agent orchestration
    # (decide_agent stores conversation records and messages internally)
    messages = []
    
    try:
        response_text = decide_agent(messages, payload.prompt)
        exec_time = time.perf_counter() - start_time
        
        # Query the database for the log we just generated to return detailed analysis
        latest_log = db.query(ChatLog).filter(
            ChatLog.prompt == payload.prompt
        ).order_by(ChatLog.logged_at.desc()).first()
        
        convo_id = latest_log.conversation_id if latest_log else 1
        sentiment = latest_log.sentiment if latest_log else "neutral"
        intent = latest_log.intent if latest_log else "general"
        
        return ChatResponse(
            response=response_text,
            conversation_id=convo_id,
            sentiment=sentiment,
            intent=intent,
            execution_time_s=exec_time
        )
        
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Orchestration failure: {str(e)}"
        )
