# Developer Guide

## Table of Contents

1. [Development Environment Setup](#development-environment-setup)
2. [Project Architecture](#project-architecture)
3. [Code Structure](#code-structure)
4. [Development Workflow](#development-workflow)
5. [Testing](#testing)
6. [API Development](#api-development)
7. [Frontend Development](#frontend-development)
8. [Database Management](#database-management)
9. [Contributing Guidelines](#contributing-guidelines)
10. [Deployment](#deployment)

## Development Environment Setup

### Prerequisites

- **Python 3.9+**: Required for modern async/await features
- **uv**: Modern Python package manager (recommended)
- **Git**: Version control
- **Node.js** (optional): For advanced frontend tooling

### Initial Setup

1. **Clone the Repository**
   ```bash
   git clone <repository-url>
   cd PortfolioManager
   ```

2. **Install Dependencies**
   ```bash
   # Using uv (recommended)
   uv sync
   
   # Or using pip
   pip install -r requirements.txt
   ```

3. **Environment Variables**
   ```bash
   # Create .env file
   cp .env.example .env
   
   # Edit .env with your configuration
   POLYGON_API_KEY=your_polygon_key_here  # Optional
   DATABASE_URL=sqlite:///data/portfolio_manager.db
   LOG_LEVEL=INFO
   ```

4. **Initialize Database**
   ```bash
   # Database auto-initializes on first run
   uv run uvicorn web_server.app:app --reload
   ```

### Development Tools

**Code Quality**
```bash
# Install development tools
uv add --dev black ruff pytest pytest-asyncio

# Format code
uv run black .

# Lint code  
uv run ruff check .

# Type checking (if using mypy)
uv run mypy src/
```

**IDE Setup**
- **VS Code**: Recommended with Python extension
- **PyCharm**: Professional or Community edition
- **Vim/Neovim**: With appropriate Python plugins

## Project Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   External      │
│   (HTML/JS/CSS) │◄──►│   (FastAPI)     │◄──►│   APIs          │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Database      │
                       │   (SQLite)      │
                       └─────────────────┘
```

### Design Patterns

**MVC Pattern**
- **Models**: SQLAlchemy ORM models (`src/models/`)
- **Views**: Jinja2 templates (`src/web_server/templates/`)
- **Controllers**: Business logic (`src/controllers/`)

**Repository Pattern**
- Data access abstraction
- Database operations encapsulated in controllers
- Easy testing and mocking

**Service Layer**
- Business logic separation
- Reusable components
- Clean API interfaces

## Code Structure

### Directory Layout

```
PortfolioManager/
├── src/                          # Source code
│   ├── controllers/              # Business logic
│   │   ├── __init__.py
│   │   ├── portfolio_controller.py    # Portfolio CRUD operations
│   │   ├── stock_data_controller.py   # Stock price/data management
│   │   ├── watchlist_controller.py    # Watchlist management
│   │   └── news_controller.py         # Multi-source news integration
│   ├── models/                   # Database models
│   │   ├── __init__.py
│   │   ├── database.py          # Database connection/setup
│   │   └── portfolio.py         # SQLAlchemy models
│   ├── utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── csv_parser.py        # CSV import/export
│   │   └── validators.py        # Data validation
│   └── web_server/              # Web application
│       ├── app.py               # FastAPI application
│       ├── routes/              # API endpoints
│       │   ├── __init__.py
│       │   ├── portfolios.py
│       │   ├── stocks.py
│       │   └── watchlists.py
│       ├── static/              # CSS, JS, images
│       │   ├── css/
│       │   ├── js/
│       │   └── images/
│       └── templates/           # HTML templates
│           ├── base.html
│           ├── index.html
│           ├── portfolios/
│           └── watchlists/
├── data/                        # Database files
├── docs/                        # Documentation
├── scripts/                     # Utility scripts
├── tests/                       # Test suite
├── pyproject.toml              # Project configuration
└── requirements.txt            # Dependencies
```

### Key Components

**FastAPI Application** (`src/web_server/app.py`)
- Main application entry point
- Middleware configuration
- Route registration
- CORS setup for development

**Database Models** (`src/models/portfolio.py`)
- SQLAlchemy ORM models
- Relationships and constraints
- Data validation

**Controllers** (`src/controllers/`)
- Business logic implementation
- Data validation and processing
- External API integration

## Development Workflow

### Git Workflow

1. **Feature Development**
   ```bash
   # Create feature branch
   git checkout -b feature/new-feature-name
   
   # Make changes and commit
   git add .
   git commit -m "Add new feature: description"
   
   # Push and create PR
   git push origin feature/new-feature-name
   ```

2. **Commit Message Format**
   ```
   type(scope): brief description
   
   Longer description if needed
   
   🤖 Generated with [Claude Code](https://claude.ai/code)
   
   Co-Authored-By: Claude <noreply@anthropic.com>
   ```

### Code Review Process

**Before Submitting PR**
- Run all tests: `uv run pytest`
- Format code: `uv run black .`
- Lint code: `uv run ruff check .`
- Update documentation if needed

**PR Requirements**
- Clear description of changes
- Tests for new functionality
- Documentation updates
- Screenshots for UI changes

### Development Server

**Standard Development**
```bash
# Start development server
uv run uvicorn web_server.app:app --reload --host 0.0.0.0 --port 8000

# With debugging
uv run uvicorn web_server.app:app --reload --log-level debug
```

**Advanced Development**
```bash
# Custom configuration
export LOG_LEVEL=DEBUG
export DATABASE_URL=sqlite:///data/dev.db
uv run uvicorn web_server.app:app --reload
```

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py                 # Test configuration
├── test_controllers/           # Controller tests
│   ├── test_portfolio_controller.py
│   ├── test_stock_data_controller.py
│   └── test_news_controller.py
├── test_models/               # Model tests
│   └── test_portfolio.py
├── test_utils/                # Utility tests
│   ├── test_csv_parser.py
│   └── test_validators.py
└── test_web_server/           # API tests
    ├── test_app.py
    └── test_routes/
        ├── test_portfolios.py
        └── test_watchlists.py
```

### Running Tests

**All Tests**
```bash
uv run pytest
```

**Specific Test Files**
```bash
uv run pytest tests/test_controllers/test_portfolio_controller.py
```

**With Coverage**
```bash
uv run pytest --cov=src --cov-report=html
```

**Test Categories**
```bash
# Unit tests only
uv run pytest -m "not integration"

# Integration tests only  
uv run pytest -m integration

# Fast tests only
uv run pytest -m "not slow"
```

### Writing Tests

**Test Example**
```python
import pytest
from fastapi.testclient import TestClient
from src.web_server.app import app
from src.models.database import get_db

client = TestClient(app)

def test_create_portfolio():
    """Test portfolio creation."""
    response = client.post(
        "/api/portfolios",
        json={"name": "Test Portfolio"}
    )
    assert response.status_code == 201
    assert response.json()["name"] == "Test Portfolio"

@pytest.mark.asyncio
async def test_stock_price_fetch():
    """Test stock price fetching."""
    from src.controllers.stock_data_controller import StockDataController
    
    controller = StockDataController()
    price = await controller.get_stock_price("AAPL")
    assert price > 0
```

### Test Data Management

**Fixtures** (`tests/conftest.py`)
```python
@pytest.fixture
def test_db():
    """Create test database."""
    # Setup test database
    yield db
    # Cleanup

@pytest.fixture
def sample_portfolio():
    """Create sample portfolio for testing."""
    return {
        "name": "Test Portfolio",
        "holdings": [
            {"symbol": "AAPL", "shares": 100, "allocation": 50.0},
            {"symbol": "GOOGL", "shares": 50, "allocation": 50.0}
        ]
    }
```

## API Development

### FastAPI Best Practices

**Route Definition**
```python
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])

class PortfolioCreate(BaseModel):
    name: str
    description: Optional[str] = None

@router.post("/", response_model=Portfolio)
async def create_portfolio(
    portfolio: PortfolioCreate,
    db: Session = Depends(get_db)
):
    """Create a new portfolio."""
    # Implementation
    pass
```

**Error Handling**
```python
from fastapi import HTTPException

def get_portfolio_or_404(portfolio_id: int, db: Session):
    portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    return portfolio
```

**Response Models**
```python
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class PortfolioResponse(BaseModel):
    id: int
    name: str
    created_date: datetime
    holdings: List[HoldingResponse]
    
    class Config:
        from_attributes = True
```

### API Documentation

**OpenAPI/Swagger**
- Automatic documentation at `/docs`
- Interactive API testing
- Schema generation

**Route Documentation**
```python
@router.get("/portfolios/{portfolio_id}", 
           summary="Get portfolio by ID",
           description="Retrieve detailed information about a specific portfolio",
           response_description="Portfolio with all holdings and current values")
async def get_portfolio(portfolio_id: int):
    """
    Get a specific portfolio by ID.
    
    - **portfolio_id**: The ID of the portfolio to retrieve
    
    Returns the portfolio with current holdings and market values.
    """
    pass
```

## Frontend Development

### Template Structure

**Base Template** (`templates/base.html`)
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}Portfolio Manager{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', path='/css/style.css') }}">
</head>
<body>
    <nav class="navbar navbar-expand-lg navbar-dark bg-primary">
        <!-- Navigation content -->
    </nav>
    
    <main class="container mt-4">
        {% block content %}{% endblock %}
    </main>
    
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    <script src="{{ url_for('static', path='/js/app.js') }}"></script>
    {% block scripts %}{% endblock %}
</body>
</html>
```

### JavaScript Best Practices

**API Calls**
```javascript
// Utility function for API calls
async function apiCall(url, options = {}) {
    const response = await fetch(url, {
        headers: {
            'Content-Type': 'application/json',
            ...options.headers
        },
        ...options
    });
    
    if (!response.ok) {
        throw new Error(`API call failed: ${response.statusText}`);
    }
    
    return response.json();
}

// Usage
async function refreshPrices(portfolioId) {
    try {
        const result = await apiCall(`/api/portfolios/${portfolioId}/refresh-prices`, {
            method: 'POST'
        });
        // Handle success
    } catch (error) {
        console.error('Error refreshing prices:', error);
        // Handle error
    }
}
```

**Progressive Enhancement**
- Core functionality works without JavaScript
- JavaScript enhances user experience
- Graceful degradation for unsupported features

### CSS Organization

**Structure**
```css
/* Base styles */
:root {
    --primary-color: #007bff;
    --secondary-color: #6c757d;
    --success-color: #28a745;
    --danger-color: #dc3545;
}

/* Layout */
.container { /* ... */ }
.sidebar { /* ... */ }

/* Components */
.card-portfolio { /* ... */ }
.table-holdings { /* ... */ }

/* Utilities */
.text-gradient { /* ... */ }
.shadow-custom { /* ... */ }
```

## Database Management

### Model Development

**Creating Models**
```python
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), unique=True, index=True)
    created_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
```

**Migrations**
```python
# For schema changes, create migration scripts
def upgrade_database():
    """Apply database schema changes."""
    # Implementation depends on chosen migration tool
    pass
```

### Database Operations

**CRUD Operations**
```python
class PortfolioController:
    def __init__(self, db: Session):
        self.db = db
    
    def create_portfolio(self, portfolio_data: PortfolioCreate) -> Portfolio:
        """Create new portfolio."""
        db_portfolio = Portfolio(**portfolio_data.dict())
        self.db.add(db_portfolio)
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get portfolio by ID."""
        return self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
```

## Contributing Guidelines

### Code Standards

**Python Style**
- Follow PEP 8
- Use Black for formatting
- Maximum line length: 88 characters
- Use type hints where appropriate

**Naming Conventions**
- Classes: `PascalCase`
- Functions/variables: `snake_case`
- Constants: `UPPER_CASE`
- Private methods: `_leading_underscore`

**Documentation**
- Docstrings for all public functions/classes
- Google-style docstrings
- Inline comments for complex logic

### Pull Request Process

1. **Fork and Branch**
   - Fork the repository
   - Create feature branch from `main`
   - Use descriptive branch names

2. **Development**
   - Write tests for new functionality
   - Update documentation
   - Follow code standards

3. **Testing**
   - Ensure all tests pass
   - Add integration tests for new features
   - Test UI changes in multiple browsers

4. **Documentation**
   - Update relevant documentation
   - Add docstrings to new functions
   - Update API documentation if needed

5. **Submit PR**
   - Clear title and description
   - Reference related issues
   - Include screenshots for UI changes

### Issue Guidelines

**Bug Reports**
- Clear description of the issue
- Steps to reproduce
- Expected vs actual behavior
- Environment information

**Feature Requests**
- Clear description of the feature
- Use cases and benefits
- Mockups or examples if applicable

## Deployment

### Production Setup

**Environment Configuration**
```bash
# Production environment variables
export ENVIRONMENT=production
export DATABASE_URL=sqlite:///data/portfolio_manager.db
export POLYGON_API_KEY=your_production_key
export LOG_LEVEL=INFO
```

**Production Server**
```bash
# Using Gunicorn
gunicorn web_server.app:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker (if Dockerfile exists)
docker build -t PortfolioManager .
docker run -p 8000:8000 PortfolioManager
```

### Security Considerations

**Data Protection**
- All data stored locally
- No sensitive data transmission
- Secure API key storage

**Input Validation**
- Validate all user inputs
- Sanitize data before database storage
- Use parameterized queries

**Access Control**
- Single-user application by design
- Local network access only
- No authentication system needed

### Monitoring

**Logging**
```python
import logging

logger = logging.getLogger(__name__)

def process_portfolio(portfolio_id):
    logger.info(f"Processing portfolio {portfolio_id}")
    try:
        # Process portfolio
        logger.info(f"Successfully processed portfolio {portfolio_id}")
    except Exception as e:
        logger.error(f"Error processing portfolio {portfolio_id}: {e}")
        raise
```

**Health Checks**
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }
```

---

For more specific information, see:
- [API Reference](api-reference.md)
- [User Guide](user-guide.md)
- [Troubleshooting](troubleshooting.md)