from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import shutil

from database.connection import get_db
from models.db_models import User
from models.schemas import UserCreate, Token, UserResponse
from services.auth_service import get_password_hash, verify_password, create_access_token
from config.config import settings
from utils.logger import setup_logger

logger = setup_logger("api_auth")
router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user profile with hashed passwords."""
    existing_user = db.query(User).filter(User.username == user_in.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered."
        )
    
    hashed_pwd = get_password_hash(user_in.password)
    new_user = User(
        username=user_in.username,
        hashed_password=hashed_pwd,
        role=user_in.role or "user"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    logger.info(f"Successfully registered user: {new_user.username}")
    return new_user

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """Traditional password login returning a JWT Access Token."""
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # If the user was pre-seeded without a password, register this password as their password
    if not user.hashed_password:
        user.hashed_password = get_password_hash(form_data.password)
        db.commit()
        db.refresh(user)
    elif not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(subject=user.username)
    logger.info(f"User {user.username} logged in successfully.")
    return {"access_token": access_token, "token_type": "bearer"}


