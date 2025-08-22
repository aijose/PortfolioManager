"""Basic tests for Sprint 1 functionality."""

# Test configuration is now in conftest.py


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "portfolio-manager"}


def test_home_redirect(client):
    """Test home page redirects to portfolios."""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # FastAPI uses 307 for redirects
    assert "/portfolios" in response.headers["location"]


def test_portfolios_list_empty(client, test_db):
    """Test portfolios list page when no portfolios exist."""
    response = client.get("/portfolios")
    assert response.status_code == 200
    assert "No Portfolios Yet" in response.text


def test_create_portfolio_form(client, test_db):
    """Test new portfolio form display."""
    response = client.get("/portfolios/new")
    assert response.status_code == 200
    assert "Create New Portfolio" in response.text


def test_create_portfolio_success(client, test_db):
    """Test successful portfolio creation."""
    response = client.post("/portfolios", data={"name": "Test Portfolio"}, follow_redirects=True)
    assert response.status_code == 200
    
    # Should redirect to portfolio detail page
    assert "Test Portfolio" in response.text
    
    # Verify portfolio appears in list
    response = client.get("/portfolios")
    assert response.status_code == 200
    assert "Test Portfolio" in response.text


def test_create_portfolio_empty_name(client, test_db):
    """Test portfolio creation with empty name."""
    response = client.post("/portfolios", data={"name": ""})
    assert response.status_code == 200
    assert "Portfolio name cannot be empty" in response.text


def test_create_duplicate_portfolio(client, test_db):
    """Test creating portfolio with duplicate name."""
    # Create first portfolio
    client.post("/portfolios", data={"name": "Test Portfolio"})
    
    # Try to create duplicate
    response = client.post("/portfolios", data={"name": "Test Portfolio"})
    assert response.status_code == 200
    assert "already exists" in response.text


def test_portfolio_detail_not_found(client, test_db):
    """Test portfolio detail page for non-existent portfolio."""
    response = client.get("/portfolios/999")
    assert response.status_code == 404


def test_api_portfolios_empty(client, test_db):
    """Test API endpoint for portfolios when empty."""
    response = client.get("/api/portfolios")
    assert response.status_code == 200
    assert response.json() == []


if __name__ == "__main__":
    pytest.main([__file__, "-v"])