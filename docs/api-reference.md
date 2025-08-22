# API Reference

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Response Format](#response-format)
4. [Error Handling](#error-handling)
5. [Portfolio Endpoints](#portfolio-endpoints)
6. [Holdings Endpoints](#holdings-endpoints)
7. [Stock Data Endpoints](#stock-data-endpoints)
8. [Watchlist Endpoints](#watchlist-endpoints)
9. [News Endpoints](#news-endpoints)
10. [Utility Endpoints](#utility-endpoints)

## Overview

The Portfolio Manager API is a RESTful API built with FastAPI that provides endpoints for managing stock portfolios, watchlists, and retrieving market data.

**Base URL**: `http://localhost:8000`

**Interactive Documentation**: `http://localhost:8000/docs` (Swagger UI)

**Alternative Documentation**: `http://localhost:8000/redoc` (ReDoc)

## Authentication

Currently, the API does not require authentication as it's designed for single-user local use. All endpoints are publicly accessible.

## Response Format

All API responses follow a consistent JSON format:

### Success Response
```json
{
  "data": { /* response data */ },
  "message": "Success message",
  "timestamp": "2025-01-06T12:00:00Z"
}
```

### Error Response
```json
{
  "detail": "Error description",
  "status_code": 400,
  "timestamp": "2025-01-06T12:00:00Z"
}
```

## Error Handling

### HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid request data |
| 404 | Not Found - Resource not found |
| 422 | Unprocessable Entity - Validation error |
| 500 | Internal Server Error - Server error |

### Common Error Responses

**Validation Error (422)**
```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Not Found Error (404)**
```json
{
  "detail": "Portfolio not found"
}
```

## Portfolio Endpoints

### List Portfolios

**GET** `/portfolios`

Returns a list of all portfolios.

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "Growth Portfolio",
    "created_date": "2025-01-01T10:00:00Z",
    "modified_date": "2025-01-06T12:00:00Z",
    "holdings_count": 5,
    "total_value": 50000.00
  }
]
```

### Get Portfolio Details

**GET** `/portfolios/{portfolio_id}`

Returns detailed information about a specific portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Response Example:**
```json
{
  "id": 1,
  "name": "Growth Portfolio",
  "created_date": "2025-01-01T10:00:00Z",
  "modified_date": "2025-01-06T12:00:00Z",
  "summary": {
    "total_value": 50000.00,
    "total_gain_loss": 5000.00,
    "total_gain_loss_percent": 11.11,
    "holdings_count": 5,
    "last_updated": "2025-01-06T12:00:00Z"
  }
}
```

### Create Portfolio

**POST** `/portfolios`

Creates a new portfolio.

**Request Body:**
```json
{
  "name": "New Portfolio"
}
```

**Response Example:**
```json
{
  "id": 2,
  "name": "New Portfolio",
  "created_date": "2025-01-06T12:00:00Z",
  "message": "Portfolio created successfully"
}
```

### Update Portfolio

**PUT** `/portfolios/{portfolio_id}`

Updates an existing portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Request Body:**
```json
{
  "name": "Updated Portfolio Name"
}
```

### Delete Portfolio

**DELETE** `/portfolios/{portfolio_id}`

Deletes a portfolio and all its holdings.

**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Response:**
```json
{
  "message": "Portfolio deleted successfully"
}
```

## Holdings Endpoints

### List Holdings

**GET** `/api/portfolios/{portfolio_id}/holdings`

Returns all holdings for a specific portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Response Example:**
```json
[
  {
    "symbol": "AAPL",
    "shares": 100,
    "target_allocation": 30.0,
    "current_price": 150.00,
    "current_value": 15000.00,
    "current_allocation": 30.0,
    "gain_loss": 2000.00,
    "gain_loss_percent": 15.38,
    "last_updated": "2025-01-06T12:00:00Z"
  }
]
```

### Add Holding

**POST** `/api/portfolios/{portfolio_id}/holdings`

Adds a new holding to a portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Request Body:**
```json
{
  "symbol": "AAPL",
  "shares": 100,
  "target_allocation": 30.0
}
```

**Response Example:**
```json
{
  "symbol": "AAPL",
  "shares": 100,
  "target_allocation": 30.0,
  "message": "Holding added successfully"
}
```

### Update Holding

**PUT** `/api/portfolios/{portfolio_id}/holdings/{symbol}`

Updates an existing holding.

**Parameters:**
- `portfolio_id` (path): Portfolio ID
- `symbol` (path): Stock symbol

**Request Body:**
```json
{
  "shares": 120,
  "target_allocation": 35.0
}
```

### Delete Holding

**DELETE** `/api/portfolios/{portfolio_id}/holdings/{symbol}`

Removes a holding from a portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio ID
- `symbol` (path): Stock symbol

### Import Holdings from CSV

**POST** `/api/portfolios/{portfolio_id}/import-csv`

Imports holdings from a CSV file.

**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Request Body:** (multipart/form-data)
- `file`: CSV file with columns: Symbol, Shares, Allocation

**Response Example:**
```json
{
  "imported_count": 5,
  "errors": [],
  "message": "Successfully imported 5 holdings"
}
```

### Refresh Portfolio Prices

**POST** `/api/portfolios/{portfolio_id}/refresh-prices`

Updates stock prices for all holdings in a portfolio.

**Parameters:**
- `portfolio_id` (path): Portfolio ID

**Response Example:**
```json
{
  "success": true,
  "updated_count": 5,
  "failed_count": 0,
  "message": "Updated prices for 5 stocks"
}
```

## Stock Data Endpoints

### Get Stock Price

**GET** `/api/stocks/{symbol}/price`

Returns current price for a specific stock.

**Parameters:**
- `symbol` (path): Stock ticker symbol

**Response Example:**
```json
{
  "symbol": "AAPL",
  "price": 150.00,
  "currency": "USD",
  "last_updated": "2025-01-06T12:00:00Z",
  "market_state": "REGULAR"
}
```

### Get Multiple Stock Prices

**POST** `/api/stocks/prices`

Returns current prices for multiple stocks.

**Request Body:**
```json
{
  "symbols": ["AAPL", "GOOGL", "MSFT"]
}
```

**Response Example:**
```json
{
  "prices": {
    "AAPL": {
      "price": 150.00,
      "currency": "USD",
      "last_updated": "2025-01-06T12:00:00Z"
    },
    "GOOGL": {
      "price": 2800.00,
      "currency": "USD",
      "last_updated": "2025-01-06T12:00:00Z"
    }
  },
  "success_count": 2,
  "failed_count": 0
}
```

### Validate Stock Symbols

**POST** `/api/stocks/validate`

Validates whether stock symbols are valid.

**Request Body:**
```json
{
  "symbols": ["AAPL", "INVALID", "GOOGL"]
}
```

**Response Example:**
```json
{
  "valid": ["AAPL", "GOOGL"],
  "invalid": ["INVALID"],
  "validation_results": {
    "AAPL": true,
    "INVALID": false,
    "GOOGL": true
  }
}
```

### Market Summary

**GET** `/api/stocks/market-summary`

Returns summary of major market indices.

**Response Example:**
```json
{
  "indices": {
    "^GSPC": {
      "name": "S&P 500",
      "price": 4700.00,
      "change": 25.00,
      "change_percent": 0.53
    },
    "^DJI": {
      "name": "Dow Jones Industrial Average",
      "price": 36000.00,
      "change": 150.00,
      "change_percent": 0.42
    }
  },
  "last_updated": "2025-01-06T12:00:00Z"
}
```

## Watchlist Endpoints

### List Watchlists

**GET** `/api/watchlists`

Returns all watchlists.

**Response Example:**
```json
[
  {
    "id": 1,
    "name": "Tech Stocks",
    "created_date": "2025-01-01T10:00:00Z",
    "modified_date": "2025-01-06T12:00:00Z",
    "items_count": 10
  }
]
```

### Get Watchlist Details

**GET** `/api/watchlists/{watchlist_id}`

Returns detailed watchlist information.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Response Example:**
```json
{
  "id": 1,
  "name": "Tech Stocks",
  "created_date": "2025-01-01T10:00:00Z",
  "modified_date": "2025-01-06T12:00:00Z",
  "summary": {
    "items_count": 10,
    "avg_change_percent": 2.5,
    "last_updated": "2025-01-06T12:00:00Z"
  }
}
```

### Create Watchlist

**POST** `/api/watchlists`

Creates a new watchlist.

**Request Body:**
```json
{
  "name": "New Watchlist"
}
```

### Update Watchlist

**PUT** `/api/watchlists/{watchlist_id}`

Updates watchlist information.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Request Body:**
```json
{
  "name": "Updated Watchlist Name"
}
```

### Delete Watchlist

**DELETE** `/api/watchlists/{watchlist_id}`

Deletes a watchlist and all watched items.

### List Watched Items

**GET** `/api/watchlists/{watchlist_id}/items`

Returns all items in a watchlist.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Response Example:**
```json
[
  {
    "symbol": "AAPL",
    "notes": "Apple Inc. - monitoring for entry point",
    "added_date": "2025-01-01T10:00:00Z",
    "current_price": 150.00,
    "change_percent": 2.5,
    "last_updated": "2025-01-06T12:00:00Z"
  }
]
```

### Add Watched Item

**POST** `/api/watchlists/{watchlist_id}/items`

Adds a stock to a watchlist.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Request Body:**
```json
{
  "symbol": "AAPL",
  "notes": "Monitoring for entry point"
}
```

### Update Watched Item

**PUT** `/api/watchlists/{watchlist_id}/items/{symbol}`

Updates watched item information.

**Parameters:**
- `watchlist_id` (path): Watchlist ID
- `symbol` (path): Stock symbol

**Request Body:**
```json
{
  "notes": "Updated notes"
}
```

### Delete Watched Item

**DELETE** `/api/watchlists/{watchlist_id}/items/{symbol}`

Removes a stock from watchlist.

### Bulk Add Items

**POST** `/api/watchlists/{watchlist_id}/bulk-add`

Adds multiple stocks to a watchlist.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Request Body:**
```json
["AAPL", "GOOGL", "MSFT", "TSLA"]
```

**Response Example:**
```json
{
  "added_count": 4,
  "total_requested": 4,
  "errors": [],
  "success": true,
  "message": "Added 4 out of 4 symbols to watchlist"
}
```

### Bulk Remove Items

**DELETE** `/api/watchlists/{watchlist_id}/bulk-remove`

Removes multiple stocks from a watchlist.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Request Body:**
```json
["AAPL", "GOOGL"]
```

### Refresh Watchlist Prices

**POST** `/api/watchlists/{watchlist_id}/refresh-prices`

Updates prices for all stocks in a watchlist.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Response Example:**
```json
{
  "success": true,
  "updated_count": 10,
  "failed_count": 0,
  "message": "Updated prices for 10 stocks"
}
```

### Refresh Single Item Price

**POST** `/api/watchlists/{watchlist_id}/items/{symbol}/refresh-price`

Updates price for a specific watched item.

**Parameters:**
- `watchlist_id` (path): Watchlist ID
- `symbol` (path): Stock symbol

### Validate Watchlist Symbols

**GET** `/api/watchlists/{watchlist_id}/validate-symbols`

Validates all symbols in a watchlist.

**Parameters:**
- `watchlist_id` (path): Watchlist ID

**Response Example:**
```json
{
  "valid_symbols": ["AAPL", "GOOGL"],
  "invalid_symbols": [],
  "total_count": 2,
  "valid_count": 2,
  "invalid_count": 0
}
```

## News Endpoints

### Get Item News

**GET** `/api/watchlists/{watchlist_id}/items/{symbol}/news`

Returns news articles for a specific watched item.

**Parameters:**
- `watchlist_id` (path): Watchlist ID
- `symbol` (path): Stock symbol

**Response Example:**
```json
{
  "symbol": "AAPL",
  "articles": [
    {
      "title": "Apple Reports Strong Q4 Earnings",
      "url": "https://example.com/news/apple-earnings",
      "published_utc": "2025-01-06T10:00:00Z",
      "source": "Financial Times",
      "summary": "Apple Inc. reported stronger than expected quarterly earnings..."
    }
  ],
  "cached": true,
  "last_updated": "2025-01-06T08:00:00Z",
  "count": 5
}
```

### Refresh Item News

**POST** `/api/watchlists/{watchlist_id}/items/{symbol}/refresh-news`

Forces refresh of news for a specific item.

**Parameters:**
- `watchlist_id` (path): Watchlist ID
- `symbol` (path): Stock symbol

**Response Example:**
```json
{
  "symbol": "AAPL",
  "articles": [ /* news articles */ ],
  "updated": true,
  "last_updated": "2025-01-06T12:00:00Z",
  "count": 5,
  "message": "Refreshed 5 news articles for AAPL"
}
```

### Test News Endpoint

**GET** `/api/watchlists/{watchlist_id}/items/{symbol}/test-news`

Tests news connectivity for a specific item.

**Parameters:**
- `watchlist_id` (path): Watchlist ID
- `symbol` (path): Stock symbol

**Response Example:**
```json
{
  "symbol": "AAPL",
  "watchlist_id": 1,
  "articles": [ /* test articles */ ],
  "cached": true,
  "count": 1,
  "has_news_data": true,
  "last_news_update": "2025-01-06T08:00:00Z",
  "test": true
}
```

## Utility Endpoints

### Health Check

**GET** `/health`

Returns application health status.

**Response Example:**
```json
{
  "status": "healthy",
  "timestamp": "2025-01-06T12:00:00Z",
  "version": "1.0.0",
  "database": "connected"
}
```

### Application Info

**GET** `/info`

Returns application information.

**Response Example:**
```json
{
  "name": "Portfolio Manager",
  "version": "1.0.0",
  "environment": "development",
  "database_url": "sqlite:///data/portfolio_manager.db",
  "features": {
    "news_integration": true,
    "price_caching": true,
    "csv_import": true
  }
}
```

## Rate Limiting

Some endpoints have rate limiting to protect external APIs:

- **Stock Price Endpoints**: 10 requests per minute per IP
- **News Endpoints**: 5 requests per minute per symbol
- **Bulk Operations**: 2 requests per minute per operation

Rate limit headers are included in responses:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1641470400
```

## SDKs and Libraries

### Python SDK Example

```python
import requests

class PortfolioManagerClient:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
    
    def get_portfolios(self):
        response = requests.get(f"{self.base_url}/portfolios")
        response.raise_for_status()
        return response.json()
    
    def create_portfolio(self, name):
        response = requests.post(
            f"{self.base_url}/portfolios",
            json={"name": name}
        )
        response.raise_for_status()
        return response.json()

# Usage
client = PortfolioManagerClient()
portfolios = client.get_portfolios()
```

### JavaScript/Node.js Example

```javascript
class PortfolioManagerAPI {
    constructor(baseURL = 'http://localhost:8000') {
        this.baseURL = baseURL;
    }
    
    async getPortfolios() {
        const response = await fetch(`${this.baseURL}/portfolios`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }
    
    async createPortfolio(name) {
        const response = await fetch(`${this.baseURL}/portfolios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name })
        });
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    }
}

// Usage
const api = new PortfolioManagerAPI();
const portfolios = await api.getPortfolios();
```

---

For more information, see:
- [User Guide](user-guide.md)
- [Developer Guide](developer-guide.md)
- [Troubleshooting](troubleshooting.md)