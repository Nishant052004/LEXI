from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from config.config import settings

# For SQLite, we allow multithreading access
connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False # Set to True if we want SQL statement logs
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency for API endpoints to yield database session and close it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
