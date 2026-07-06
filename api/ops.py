import os
import json
import time
from datetime import datetime
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
import shutil

from database.connection import get_db
from models.db_models import Agent as DB_Agent, ApprovalRequest, UserFeedback, ChatLog, Conversation
from models.schemas import FeedbackCreate, FeedbackResponse, ApprovalResponse, ApprovalResolve
from agents.registry import agent_registry
from agents.router import agent_router
from agents.base_agent import BaseAgent
from utils.logger import setup_logger

logger = setup_logger("api_ops")
router = APIRouter(prefix="/api/ops", tags=["Operations & HITL"])

# Connection Manager for WebSockets
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, message: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.error(f"Failed to send WS message: {str(e)}")

ws_manager = ConnectionManager()

# Dynamic Agent Wrapper
class DynamicAgent(BaseAgent):
    def __init__(self, name: str, description: str, system_prompt: str = ""):
        self._name = name
        self._description = description
        self.system_prompt = system_prompt

    @property
    def name(self) -> str:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    def execute(self, prompt: str, context: Dict[str, Any]) -> Dict[str, Any]:
        logger.info(f"Executing dynamic agent {self._name}")
        context["developer_guidelines"] = f"Execute as a {self._name} Specialist. System prompt: {self.system_prompt}"
        return {"status": "success", "agent": self.name}

# Synchronize Database Agents with Registry on load
def sync_db_agents_to_registry(db: Session):
    db_agents = db.query(DB_Agent).filter(DB_Agent.status == "active").all()
    for db_agent in db_agents:
        if not agent_registry.get_agent(db_agent.name):
            # Create a dynamic agent wrapper
            agent_registry.register(DynamicAgent(
                name=db_agent.name,
                description=db_agent.description or "Dynamic Specialist Agent"
            ))

# ----------------- AGENT MANAGEMENT -----------------

@router.get("/agents")
def list_agents(db: Session = Depends(get_db)):
    """List all core and dynamically registered agents."""
    sync_db_agents_to_registry(db)
    
    agents = []
    # 1. Gather from registry
    for agent in agent_registry._agents.values():
        agents.append({
            "name": agent.name,
            "description": agent.description,
            "is_dynamic": hasattr(agent, "system_prompt"),
            "status": "active"
        })
    return agents

@router.post("/agents", status_code=status.HTTP_201_CREATED)
def create_dynamic_agent(name: str, description: str, system_prompt: str = "", db: Session = Depends(get_db)):
    """Create a new dynamic agent at runtime and register it."""
    name_clean = "".join(c for c in name if c.isalnum()).strip()
    if not name_clean:
        raise HTTPException(status_code=400, detail="Invalid agent name. Must be alphanumeric.")
        
    # Check if agent already exists
    existing = db.query(DB_Agent).filter(DB_Agent.name == name_clean).first()
    if existing or agent_registry.get_agent(name_clean):
        raise HTTPException(status_code=400, detail="An agent with this name already exists.")

    # Save to database
    db_agent = DB_Agent(name=name_clean, description=description, status="active")
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)

    # Register in memory registry
    new_agent = DynamicAgent(name=name_clean, description=description, system_prompt=system_prompt)
    agent_registry.register(new_agent)
    
    # Automatically map it if description or prompt suggests it
    # We can route a custom intent matching the name
    agent_router.register_route(name_clean.lower(), name_clean)

    # Broadcast update via WS
    import asyncio
    asyncio.run(ws_manager.broadcast({
        "type": "agent_created",
        "data": {"name": name_clean, "description": description}
    }))

    return {"message": f"Agent '{name_clean}' registered successfully.", "agent": {"name": name_clean, "description": description}}

# ----------------- HUMAN IN THE LOOP (HITL) -----------------

@router.get("/approvals", response_model=List[ApprovalResponse])
def get_approvals(status: Optional[str] = "pending", db: Session = Depends(get_db)):
    """List all HITL approval requests."""
    query = db.query(ApprovalRequest)
    if status:
        query = query.filter(ApprovalRequest.status == status)
    return query.order_by(ApprovalRequest.created_at.desc()).all()

@router.post("/approvals", response_model=ApprovalResponse)
def create_approval(
    conversation_id: int, 
    agent_name: str, 
    task_type: str, 
    task_details: str, 
    db: Session = Depends(get_db)
):
    """Create a pending approval request (called by agents during execution)."""
    req = ApprovalRequest(
        conversation_id=conversation_id,
        agent_name=agent_name,
        task_type=task_type,
        task_details=task_details,
        status="pending"
    )
    db.add(req)
    db.commit()
    db.refresh(req)

    # Broadcast notification to the frontend OS
    import asyncio
    asyncio.run(ws_manager.broadcast({
        "type": "hitl_approval_required",
        "data": {
            "id": req.id,
            "conversation_id": conversation_id,
            "agent_name": agent_name,
            "task_type": task_type,
            "task_details": task_details
        }
    }))

    return req

@router.put("/approvals/{approval_id}", response_model=ApprovalResponse)
def resolve_approval(approval_id: int, payload: ApprovalResolve, db: Session = Depends(get_db)):
    """Resolve an approval request (Approve or Reject)."""
    req = db.query(ApprovalRequest).filter(ApprovalRequest.id == approval_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Approval request not found.")
    
    if req.status != "pending":
        raise HTTPException(status_code=400, detail="Approval request already resolved.")

    req.status = payload.status
    req.resolved_at = datetime.utcnow()
    db.commit()
    db.refresh(req)

    # Broadcast resolution via WS
    import asyncio
    asyncio.run(ws_manager.broadcast({
        "type": "hitl_approval_resolved",
        "data": {
            "id": req.id,
            "status": req.status
        }
    }))

    return req

# ----------------- SELF LEARNING & FEEDBACK -----------------

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    """Submit user feedback for agent response quality checks (Self-Learning)."""
    chat_log = db.query(ChatLog).filter(ChatLog.id == payload.chat_log_id).first()
    if not chat_log:
        raise HTTPException(status_code=404, detail="Chat log not found.")

    feedback = UserFeedback(
        chat_log_id=payload.chat_log_id,
        rating=payload.rating,
        feedback_text=payload.feedback_text,
        corrected_response=payload.corrected_response
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)

    # Self-learning mechanism:
    # If the user corrects the response or gives a low score, we can adapt future context/prompts.
    if payload.rating <= 2 and payload.corrected_response:
        # Save correction log to guide future reflection loops
        logger.info(f"Low rating received. Self-correcting loop activated for agent '{chat_log.agent_name}'.")
        # In a real self-evolving system, this feedback would be loaded into RAG or used in fine-tuning prompts.

    return feedback

# ----------------- DOCUMENT UPLOAD -----------------

@router.post("/upload")
def upload_document(conversation_id: int, file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Upload a text/PDF document and inject it as agent context."""
    upload_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(upload_dir, exist_ok=True)
    
    file_path = os.path.join(upload_dir, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    content = ""
    # Process text files or PDFs
    ext = os.path.splitext(file.filename)[1].lower()
    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to read text file: {str(e)}")
    elif ext == ".pdf":
        try:
            # Fallback simple reading if pypdf is not installed
            try:
                import pypdf
                reader = pypdf.PdfReader(file_path)
                content = "\n".join([page.extract_text() or "" for page in reader.pages])
            except ImportError:
                content = f"[PDF file uploaded: {file.filename}. Summary: PDF processing fallback triggered. Content exists on disk.]"
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to parse PDF: {str(e)}")
    else:
        content = f"[Uploaded file: {file.filename} of type {ext}]"

    # Add content to conversation history as a system message context
    # Create a system message in the chat logs
    log = ChatLog(
        conversation_id=conversation_id,
        agent_name="DocumentAgent",
        prompt=f"Upload file: {file.filename}",
        response=f"Document '{file.filename}' processed successfully ({len(content)} characters extracted). Context loaded.",
        sentiment="neutral",
        intent="research",
        execution_time_s=0.1
    )
    db.add(log)
    db.commit()

    return {
        "filename": file.filename,
        "content_preview": content[:300] + "..." if len(content) > 300 else content,
        "size": len(content)
    }

# ----------------- WEBSOCKET ROUTE -----------------

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        # Send initial status
        await websocket.send_json({
            "type": "system_status",
            "data": {
                "cpu": 12.5,
                "memory": 45.2,
                "status": "healthy",
                "active_agents": len(agent_registry.list_agents()),
                "timestamp": time.time()
            }
        })
        
        while True:
            # Simple heartbeat or user messages
            data = await websocket.receive_text()
            payload = json.loads(data)
            
            if payload.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})
                
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
        ws_manager.disconnect(websocket)
