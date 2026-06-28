from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from database.connection import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user") # 'admin', 'user'
    preferences = Column(Text, default="{}") # JSON encoded string for user preferences
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    conversations = relationship("Conversation", back_populates="user", cascade="all, delete-orphan")


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, default="New Conversation")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="conversations")
    entities = relationship("Entity", back_populates="conversation", cascade="all, delete-orphan")
    chat_logs = relationship("ChatLog", back_populates="conversation", cascade="all, delete-orphan")


class Entity(Base):
    __tablename__ = "entities"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    entity_type = Column(String, nullable=False)  # PERSON, ORG, GPE, EMAIL, etc.
    entity_value = Column(String, nullable=False)
    label = Column(String, nullable=True) # Custom labels
    extracted_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="entities")


class Agent(Base):
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    status = Column(String, default="active")  # 'active', 'inactive'
    registered_at = Column(DateTime, default=datetime.utcnow)


class ChatLog(Base):
    __tablename__ = "chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    prompt = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    sentiment = Column(String, nullable=True)
    intent = Column(String, nullable=True)
    execution_time_s = Column(Float, default=0.0)
    logged_at = Column(DateTime, default=datetime.utcnow)

    conversation = relationship("Conversation", back_populates="chat_logs")


class CustomEntityMapping(Base):
    __tablename__ = "custom_entity_mappings"

    id = Column(Integer, primary_key=True, index=True)
    label = Column(String, nullable=False)
    literal_text = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class ApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    agent_name = Column(String, nullable=False)
    task_type = Column(String, nullable=False) # e.g. "shell_command", "file_edit", "email"
    task_details = Column(Text, nullable=False) # JSON details or command string
    status = Column(String, default="pending") # "pending", "approved", "rejected"
    created_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(Integer, primary_key=True, index=True)
    chat_log_id = Column(Integer, ForeignKey("chat_logs.id"), nullable=False)
    rating = Column(Integer, nullable=False) # 1 to 5
    feedback_text = Column(Text, nullable=True)
    corrected_response = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


