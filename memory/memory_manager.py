import json
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy import func
from sqlalchemy.orm import Session
from models.db_models import User, Conversation, Entity, ChatLog
from utils.logger import setup_logger

logger = setup_logger("memory_manager")

class MemoryManager:
    def __init__(self):
        pass

    def get_or_create_user(self, db: Session, username: str, hashed_password: str = None, role: str = "user") -> User:
        """Retrieves user by username, or creates if not existing."""
        user = db.query(User).filter(User.username == username).first()
        if not user:
            user = User(
                username=username,
                hashed_password=hashed_password or "",
                role=role,
                preferences=json.dumps({"theme": "dark", "temperature": 0.7, "greeting_enabled": True})
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Created new user profile for: {username}")
        return user

    def update_user_preferences(self, db: Session, user_id: int, preferences: Dict[str, Any]) -> bool:
        """Saves/updates user preferences dictionary."""
        user = db.query(User).filter(User.id == user_id).first()
        if user:
            current_prefs = json.loads(user.preferences or "{}")
            current_prefs.update(preferences)
            user.preferences = json.dumps(current_prefs)
            db.commit()
            logger.info(f"Updated user preferences for user ID {user_id}")
            return True
        return False

    def get_user_preferences(self, db: Session, user_id: int) -> Dict[str, Any]:
        """Retrieves user preferences dict."""
        user = db.query(User).filter(User.id == user_id).first()
        if user and user.preferences:
            return json.loads(user.preferences)
        return {"theme": "dark", "temperature": 0.7, "greeting_enabled": True}

    def get_or_create_conversation(self, db: Session, user_id: int, conversation_id: Optional[int] = None) -> Conversation:
        """Retrieves a conversation or creates a new one for the user."""
        if conversation_id:
            convo = db.query(Conversation).filter(Conversation.id == conversation_id, Conversation.user_id == user_id).first()
            if convo:
                return convo
        
        convo = Conversation(user_id=user_id, title=f"Chat {datetime.utcnow().strftime('%Y-%m-%d %H:%M')}")
        db.add(convo)
        db.commit()
        db.refresh(convo)
        logger.info(f"Created new conversation ID {convo.id} for user ID {user_id}")
        return convo

    def get_conversation_history(self, db: Session, conversation_id: int, limit: int = 20) -> List[Dict[str, Any]]:
        """Retrieves the recent messages/logs in a conversation."""
        logs = db.query(ChatLog).filter(ChatLog.conversation_id == conversation_id).order_by(ChatLog.logged_at.asc()).limit(limit).all()
        history = []
        for log in logs:
            history.append({"role": "user", "content": log.prompt})
            history.append({"role": "assistant", "content": log.response})
        return history

    def log_interaction(self, db: Session, conversation_id: int, agent_name: str, prompt: str, response: str, sentiment: str, intent: str, execution_time: float) -> ChatLog:
        """Logs a chat interaction into the database."""
        log = ChatLog(
            conversation_id=conversation_id,
            agent_name=agent_name,
            prompt=prompt,
            response=response,
            sentiment=sentiment,
            intent=intent,
            execution_time_s=execution_time
        )
        db.add(log)
        db.commit()
        db.refresh(log)
        logger.info(f"Logged interaction for convo ID {conversation_id} handled by agent {agent_name}")
        return log

    def save_entities(self, db: Session, conversation_id: int, entities: List[Dict[str, Any]]):
        """Saves extracted named entities associated with a conversation."""
        for ent in entities:
            # Check if this entity value is already saved in this conversation to avoid duplicates
            exists = db.query(Entity).filter(
                Entity.conversation_id == conversation_id,
                Entity.entity_type == ent["label"],
                Entity.entity_value == ent["text"]
            ).first()
            
            if not exists:
                db_ent = Entity(
                    conversation_id=conversation_id,
                    entity_type=ent["label"],
                    entity_value=ent["text"],
                    label=ent.get("custom_label")
                )
                db.add(db_ent)
        db.commit()
        logger.info(f"Saved {len(entities)} named entities for conversation ID {conversation_id}")

    def get_frequently_asked_topics(self, db: Session, conversation_id: int, limit: int = 5) -> List[tuple]:
        """Analyzes chat logs to extract frequently occurring keyword categories or intents."""
        results = db.query(
            ChatLog.intent, 
            func.count(ChatLog.id).label('qty')
        ).filter(
            ChatLog.conversation_id == conversation_id,
            ChatLog.intent != 'greeting',
            ChatLog.intent != 'general'
        ).group_by(ChatLog.intent).order_by(func.count(ChatLog.id).desc()).limit(limit).all()
        return results

memory_manager = MemoryManager()
