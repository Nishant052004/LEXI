from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from typing import Dict, Any, List, Optional

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    role: Optional[str] = "user"

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str
    role: str
    preferences: str
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class ChatRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    conversation_id: Optional[int] = None

class ChatResponse(BaseModel):
    response: str
    conversation_id: int
    sentiment: str
    intent: str
    execution_time_s: float

class PreferenceUpdate(BaseModel):
    preferences: Dict[str, Any]

class EntityResponse(BaseModel):
    id: int
    conversation_id: int
    entity_type: str
    entity_value: str
    label: Optional[str]
    extracted_at: datetime

    class Config:
        from_attributes = True

class ConversationResponse(BaseModel):
    id: int
    user_id: int
    title: str
    created_at: datetime

    class Config:
        from_attributes = True

class ChatLogResponse(BaseModel):
    id: int
    conversation_id: int
    agent_name: str
    prompt: str
    response: str
    sentiment: Optional[str]
    intent: Optional[str]
    execution_time_s: float
    logged_at: datetime

    class Config:
        from_attributes = True


class FeedbackCreate(BaseModel):
    chat_log_id: int
    rating: int = Field(..., ge=1, le=5)
    feedback_text: Optional[str] = None
    corrected_response: Optional[str] = None


class FeedbackResponse(BaseModel):
    id: int
    chat_log_id: int
    rating: int
    feedback_text: Optional[str]
    corrected_response: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class ApprovalCreate(BaseModel):
    conversation_id: int
    agent_name: str
    task_type: str
    task_details: str


class ApprovalResponse(BaseModel):
    id: int
    conversation_id: int
    agent_name: str
    task_type: str
    task_details: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApprovalResolve(BaseModel):
    status: str = Field(..., description="approved or rejected")

