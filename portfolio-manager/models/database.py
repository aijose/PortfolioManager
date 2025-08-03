"""Database configuration and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./data/portfolio_manager.db")

# Create database engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for SQL logging during development
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()


def get_db():
    """Get database session dependency for FastAPI."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Create all database tables."""
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    Base.metadata.create_all(bind=engine)


def drop_tables():
    """Drop all database tables (for testing/development)."""
    Base.metadata.drop_all(bind=engine)