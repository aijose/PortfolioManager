"""Tests for Sprint 2 functionality: CSV import and holdings management."""

import pytest
import sys
import os
import io

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from web_server.app import app
from models.database import get_db, Base
from models.portfolio import Portfolio, Holding
from utils.csv_parser import CSVPortfolioParser
from controllers.portfolio_controller import PortfolioController, PortfolioCreate, HoldingCreate


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_sprint2.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def sample_portfolio(test_db):
    """Create a sample portfolio for testing."""
    db = TestingSessionLocal()
    try:
        controller = PortfolioController(db)
        portfolio = controller.create_portfolio(PortfolioCreate(name="Test Portfolio"))
        return portfolio
    finally:
        db.close()


def test_csv_parser_valid_data():
    """Test CSV parser with valid data."""
    csv_content = """Symbol,Shares,Allocation
AAPL,100,50.0
MSFT,200,50.0"""
    
    parser = CSVPortfolioParser()
    holdings_data, errors, warnings = parser.parse_csv_content(csv_content)
    
    assert len(holdings_data) == 2
    assert len(errors) == 0
    assert len(warnings) == 0
    
    assert holdings_data[0].symbol == "AAPL"
    assert holdings_data[0].shares == 100
    assert holdings_data[0].allocation == 50.0


def test_csv_parser_invalid_allocation():
    """Test CSV parser with invalid allocation sum."""
    csv_content = """Symbol,Shares,Allocation
AAPL,100,30.0
MSFT,200,50.0"""
    
    parser = CSVPortfolioParser()
    holdings_data, errors, warnings = parser.parse_csv_content(csv_content)
    
    assert len(warnings) == 1
    assert "less than 100%" in warnings[0]


def test_csv_parser_missing_columns():
    """Test CSV parser with missing required columns."""
    csv_content = """Symbol,Shares
AAPL,100
MSFT,200"""
    
    parser = CSVPortfolioParser()
    holdings_data, errors, warnings = parser.parse_csv_content(csv_content)
    
    assert len(errors) > 0
    assert "Missing required columns" in errors[0]


def test_csv_parser_duplicate_symbols():
    """Test CSV parser with duplicate symbols."""
    csv_content = """Symbol,Shares,Allocation
AAPL,100,50.0
AAPL,200,50.0"""
    
    parser = CSVPortfolioParser()
    holdings_data, errors, warnings = parser.parse_csv_content(csv_content)
    
    assert len(errors) > 0
    assert "Duplicate symbol" in str(errors)


def test_holdings_api_create(client, test_db, sample_portfolio):
    """Test creating a holding via API."""
    holding_data = {
        "symbol": "AAPL",
        "shares": 100,
        "target_allocation": 50.0
    }
    
    response = client.post(f"/api/portfolios/{sample_portfolio.id}/holdings", json=holding_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["symbol"] == "AAPL"
    assert data["shares"] == 100
    assert data["target_allocation"] == 50.0


def test_holdings_api_list(client, test_db, sample_portfolio):
    """Test listing holdings via API."""
    # First create a holding
    holding_data = {
        "symbol": "AAPL",
        "shares": 100,
        "target_allocation": 50.0
    }
    client.post(f"/api/portfolios/{sample_portfolio.id}/holdings", json=holding_data)
    
    # Then list holdings
    response = client.get(f"/api/portfolios/{sample_portfolio.id}/holdings")
    assert response.status_code == 200
    
    holdings = response.json()
    assert len(holdings) == 1
    assert holdings[0]["symbol"] == "AAPL"


def test_holdings_api_update(client, test_db, sample_portfolio):
    """Test updating a holding via API."""
    # Create a holding
    holding_data = {
        "symbol": "AAPL",
        "shares": 100,
        "target_allocation": 50.0
    }
    client.post(f"/api/portfolios/{sample_portfolio.id}/holdings", json=holding_data)
    
    # Update the holding
    update_data = {
        "shares": 150,
        "target_allocation": 60.0
    }
    response = client.put(f"/api/portfolios/{sample_portfolio.id}/holdings/AAPL", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["shares"] == 150
    assert data["target_allocation"] == 60.0


def test_holdings_api_delete(client, test_db, sample_portfolio):
    """Test deleting a holding via API."""
    # Create a holding
    holding_data = {
        "symbol": "AAPL",
        "shares": 100,
        "target_allocation": 50.0
    }
    client.post(f"/api/portfolios/{sample_portfolio.id}/holdings", json=holding_data)
    
    # Delete the holding
    response = client.delete(f"/api/portfolios/{sample_portfolio.id}/holdings/AAPL")
    assert response.status_code == 200
    
    # Verify it's gone
    response = client.get(f"/api/portfolios/{sample_portfolio.id}/holdings")
    holdings = response.json()
    assert len(holdings) == 0


def test_csv_import_api_success(client, test_db, sample_portfolio):
    """Test successful CSV import via API."""
    csv_content = """Symbol,Shares,Allocation
AAPL,100,50.0
MSFT,200,50.0"""
    
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post(f"/api/portfolios/{sample_portfolio.id}/import-csv", files=files)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["imported_count"] == 2


def test_csv_import_api_validation_error(client, test_db, sample_portfolio):
    """Test CSV import with validation errors."""
    csv_content = """Symbol,Shares,Allocation
AAPL,100,30.0
MSFT,200,80.0"""  # Total exceeds 100%
    
    files = {"file": ("test.csv", io.BytesIO(csv_content.encode()), "text/csv")}
    response = client.post(f"/api/portfolios/{sample_portfolio.id}/import-csv", files=files)
    
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "exceeds 100%" in str(data["errors"])


def test_csv_import_invalid_file_type(client, test_db, sample_portfolio):
    """Test CSV import with invalid file type."""
    files = {"file": ("test.txt", io.BytesIO(b"not a csv"), "text/plain")}
    response = client.post(f"/api/portfolios/{sample_portfolio.id}/import-csv", files=files)
    
    assert response.status_code == 400


def test_holdings_web_form_display(client, test_db, sample_portfolio):
    """Test holdings form display."""
    response = client.get(f"/portfolios/{sample_portfolio.id}/holdings/new")
    assert response.status_code == 200
    assert "Add New Holding" in response.text


def test_holdings_web_form_create(client, test_db, sample_portfolio):
    """Test creating holding via web form."""
    form_data = {
        "symbol": "AAPL",
        "shares": 100,
        "target_allocation": 50.0
    }
    
    response = client.post(f"/portfolios/{sample_portfolio.id}/holdings", data=form_data, follow_redirects=True)
    assert response.status_code == 200
    assert "AAPL" in response.text


def test_csv_import_web_form_display(client, test_db, sample_portfolio):
    """Test CSV import form display."""
    response = client.get(f"/portfolios/{sample_portfolio.id}/import")
    assert response.status_code == 200
    assert "Import Holdings from CSV" in response.text


def test_sample_csv_generation():
    """Test sample CSV generation."""
    parser = CSVPortfolioParser()
    sample_csv = parser.generate_sample_csv()
    
    assert "Symbol,Shares,Allocation" in sample_csv
    assert "AAPL" in sample_csv
    assert "MSFT" in sample_csv


if __name__ == "__main__":
    pytest.main([__file__, "-v"])