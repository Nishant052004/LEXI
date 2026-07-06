import time
from typing import Generator, Dict, List
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from database.connection import get_db
from services.auth_service import verify_token
from models.db_models import User
from config.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# In-memory sliding window rate limiter
rate_limit_records: Dict[str, List[float]] = {}

def check_rate_limit(request: Request):
    """Custom rate limiter that tracks requests per IP address."""
    client_ip = request.client.host if request.client else "unknown"
    now = time.time()
    
    # Filter timestamps older than 60 seconds
    if client_ip not in rate_limit_records:
        rate_limit_records[client_ip] = []
        
    rate_limit_records[client_ip] = [t for t in rate_limit_records[client_ip] if now - t < 60]
    
    if len(rate_limit_records[client_ip]) >= settings.RATE_LIMIT_PER_MIN:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Rate limit exceeded. Please wait and try again."
        )
    
    rate_limit_records[client_ip].append(now)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """Dependency to retrieve the currently logged in user via JWT OAuth2."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    username = verify_token(token)
    if username is None:
        raise credentials_exception
        
    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

def require_role(required_role: str):
    """Role-Based Access Control (RBAC) dependency builder."""
    def dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != required_role and current_user.role != "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this user role."
            )
        return current_user
    return dependency
