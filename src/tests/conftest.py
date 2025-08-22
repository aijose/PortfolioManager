"""Test configuration and fixtures."""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web_server.app import app
from models.database import get_db, Base
from models.portfolio import Portfolio, Holding, Watchlist, WatchedItem  # Import all models


# Test database setup - use a file-based test database for more reliable testing
TEST_DATABASE_PATH = ":memory:"
SQLALCHEMY_DATABASE_URL = f"sqlite:///{TEST_DATABASE_PATH}"
test_engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


# Override the dependency at module level
app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def test_db():
    """Create clean test database for each test."""
    # Create tables fresh for each test
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    yield
    # Clean up after test
    Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)