# Portfolio Manager - Comprehensive Test Plan

## Test Plan Overview

This document outlines a comprehensive testing strategy for the Portfolio Manager application, covering unit tests, integration tests, API tests, and manual testing scenarios.

## Testing Scope

### Components to Test
1. **Models & Database** (`src/models/`)
   - Portfolio model CRUD operations
   - Holdings model operations
   - Watchlist and WatchedItem models
   - Database relationships and constraints

2. **Controllers** (`src/controllers/`)
   - Portfolio Controller
   - Stock Data Controller
   - News Controller
   - Watchlist Controller
   - Rebalancing Controller

3. **Utilities** (`src/utils/`)
   - CSV Parser functionality
   - Validation functions

4. **API Endpoints** (`src/web_server/routes/`)
   - Portfolio management endpoints
   - Stock data endpoints
   - Watchlist endpoints
   - News endpoints
   - Rebalancing endpoints

5. **Web Application** (`src/web_server/`)
   - FastAPI application startup
   - Template rendering
   - Static file serving
   - Error handling

## Test Categories

### 1. Unit Tests
- Test individual functions and methods in isolation
- Mock external dependencies (APIs, database)
- Validate business logic correctness
- Test edge cases and error conditions

### 2. Integration Tests
- Test component interactions
- Database integration tests
- External API integration tests
- End-to-end workflow tests

### 3. API Tests
- Test all REST endpoints
- Validate request/response formats
- Test authentication and authorization
- Test error responses and status codes

### 4. Performance Tests
- Load testing for concurrent requests
- Database query performance
- Memory usage monitoring
- Response time validation

### 5. Manual Tests
- User interface testing
- Cross-browser compatibility
- Mobile responsiveness
- User workflow validation

## Test Environment Setup

### Prerequisites
- Python 3.9+
- pytest framework
- FastAPI TestClient
- SQLAlchemy test database
- Mock external APIs

### Test Database
- Use separate test database
- Clean state for each test
- Seed data for integration tests

## Detailed Test Cases

### Models Testing

#### Portfolio Model Tests
- ✅ Create portfolio with valid data
- ✅ Portfolio name uniqueness validation
- ✅ Portfolio deletion cascades to holdings
- ✅ Portfolio modification timestamps
- ❌ Invalid portfolio data handling

#### Holdings Model Tests
- ✅ Create holding with valid data
- ✅ Holding allocation validation (0-100%)
- ✅ Symbol format validation
- ✅ Shares non-negative validation
- ❌ Duplicate symbols in same portfolio
- ❌ Allocation sum validation (must equal 100%)

#### Watchlist Model Tests
- ✅ Create watchlist with valid data
- ✅ Add/remove watched items
- ✅ News data storage and retrieval
- ✅ Price data caching
- ❌ Invalid symbol handling

### Controllers Testing

#### Portfolio Controller Tests
- ✅ CRUD operations for portfolios
- ✅ Holdings management
- ✅ CSV import/export functionality
- ✅ Portfolio validation logic
- ❌ Error handling for invalid data
- ❌ Database connection failures

#### Stock Data Controller Tests
- ✅ Single stock price retrieval
- ✅ Batch price retrieval
- ✅ Price caching mechanism
- ✅ Symbol validation
- ❌ API failure handling
- ❌ Rate limiting compliance
- ❌ Invalid symbol responses

#### News Controller Tests
- ✅ Multi-source news fetching
- ✅ News caching system
- ✅ Fallback mechanism testing
- ✅ Rate limiting compliance
- ❌ API key validation
- ❌ Malformed API responses
- ❌ Network timeout handling

#### Watchlist Controller Tests
- ✅ Watchlist CRUD operations
- ✅ Watched item management
- ✅ Bulk operations
- ✅ Price refresh functionality
- ❌ Invalid data handling
- ❌ Concurrent modification issues

### API Endpoint Testing

#### Portfolio Endpoints
- GET /portfolios - List all portfolios
- POST /portfolios - Create portfolio
- GET /portfolios/{id} - Get portfolio details
- PUT /portfolios/{id} - Update portfolio
- DELETE /portfolios/{id} - Delete portfolio

#### Holdings Endpoints
- GET /api/portfolios/{id}/holdings - List holdings
- POST /api/portfolios/{id}/holdings - Add holding
- PUT /api/portfolios/{id}/holdings/{symbol} - Update holding
- DELETE /api/portfolios/{id}/holdings/{symbol} - Delete holding
- POST /api/portfolios/{id}/import-csv - Import CSV
- POST /api/portfolios/{id}/refresh-prices - Refresh prices

#### Stock Data Endpoints
- GET /api/stocks/{symbol}/price - Get stock price
- POST /api/stocks/prices - Get multiple prices
- POST /api/stocks/validate - Validate symbols

#### Watchlist Endpoints
- GET /api/watchlists - List watchlists
- POST /api/watchlists - Create watchlist
- GET /api/watchlists/{id} - Get watchlist
- PUT /api/watchlists/{id} - Update watchlist
- DELETE /api/watchlists/{id} - Delete watchlist
- POST /api/watchlists/{id}/items - Add watched item
- DELETE /api/watchlists/{id}/items/{symbol} - Remove item

#### News Endpoints
- GET /api/watchlists/{id}/items/{symbol}/news - Get news
- POST /api/watchlists/{id}/items/{symbol}/refresh-news - Refresh news

### Utility Function Testing

#### CSV Parser Tests
- ✅ Valid CSV parsing
- ✅ Header validation
- ✅ Data type conversion
- ❌ Malformed CSV handling
- ❌ Missing columns
- ❌ Invalid data types
- ❌ Large file handling

#### Validator Tests
- ✅ Stock symbol validation
- ✅ Allocation percentage validation
- ✅ Share count validation
- ❌ Edge case handling
- ❌ Invalid input types

### Integration Testing

#### Database Integration
- ✅ CRUD operations across models
- ✅ Transaction handling
- ✅ Constraint enforcement
- ✅ Cascade operations
- ❌ Connection pool exhaustion
- ❌ Deadlock scenarios

#### External API Integration
- ✅ Yahoo Finance API integration
- ✅ Polygon.io API integration
- ✅ Error response handling
- ❌ API rate limiting
- ❌ Authentication failures
- ❌ Network timeouts

#### End-to-End Workflows
- ✅ Portfolio creation to rebalancing
- ✅ CSV import to price updates
- ✅ Watchlist creation to news viewing
- ❌ Error recovery scenarios

## Manual Testing Scenarios

### User Interface Testing
1. **Portfolio Management**
   - Create, edit, delete portfolios
   - Add, modify, remove holdings
   - Import CSV files
   - View portfolio analytics

2. **Watchlist Management**
   - Create, edit, delete watchlists
   - Add, remove watched items
   - View news for stocks
   - Refresh prices

3. **Navigation and UX**
   - Menu navigation
   - Form validation
   - Error message display
   - Loading indicators

### Cross-Browser Testing
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

### Mobile Responsiveness
- Mobile portrait/landscape
- Tablet portrait/landscape
- Desktop various resolutions

## Performance Testing

### Load Testing
- Concurrent user simulation
- API endpoint stress testing
- Database query performance
- Memory leak detection

### Response Time Testing
- Page load times (<3 seconds)
- API response times (<2 seconds)
- Large CSV import times
- Price refresh operations

## Security Testing

### Input Validation
- SQL injection prevention
- XSS prevention
- File upload security
- Parameter tampering

### Data Protection
- Local data storage security
- API key protection
- Session management

## Test Execution Plan

### Phase 1: Unit Tests
1. Set up testing framework
2. Implement model tests
3. Implement controller tests
4. Implement utility tests

### Phase 2: Integration Tests
1. Database integration tests
2. API integration tests
3. End-to-end workflow tests

### Phase 3: API Tests
1. Endpoint functionality tests
2. Error handling tests
3. Performance tests

### Phase 4: Manual Tests
1. UI/UX testing
2. Cross-browser testing
3. Mobile responsiveness testing

### Phase 5: Bug Fixes
1. Document found issues
2. Prioritize fixes
3. Implement fixes
4. Regression testing

## Success Criteria

### Code Coverage
- Unit tests: >90% coverage
- Integration tests: >80% coverage
- Critical paths: 100% coverage

### Performance Benchmarks
- API response time: <2 seconds
- Page load time: <3 seconds
- CSV import (1000 rows): <30 seconds
- Price refresh (50 stocks): <30 seconds

### Bug Criteria
- Zero critical bugs
- Zero high-priority bugs
- <5 medium-priority bugs
- Documentation for known limitations

## Risk Assessment

### High Risk Areas
1. External API dependencies
2. Database transaction handling
3. CSV import validation
4. Price caching mechanism
5. News source fallback logic

### Mitigation Strategies
1. Comprehensive mocking for external APIs
2. Transaction rollback testing
3. Malformed data injection testing
4. Cache invalidation testing
5. Fallback mechanism validation

## Test Data

### Sample Portfolios
- Small portfolio (5 stocks)
- Medium portfolio (20 stocks)
- Large portfolio (100+ stocks)
- Edge case portfolio (1 stock, 100% allocation)

### Sample Stocks
- Valid symbols: AAPL, GOOGL, MSFT, TSLA
- Invalid symbols: INVALID, BADSTOCK
- Special symbols: BTC-USD, ^GSPC

### Sample CSV Files
- Valid format files
- Invalid format files
- Large files (1000+ rows)
- Edge case files (empty, single row)

## Bug Tracking

### Issue Categories
- Critical: Application crash, data loss
- High: Feature broken, security issue
- Medium: Usability issue, performance problem
- Low: Cosmetic issue, enhancement

### Bug Report Format
```
Bug ID: [Unique identifier]
Title: [Brief description]
Severity: [Critical/High/Medium/Low]
Priority: [P1/P2/P3/P4]
Component: [Models/Controllers/API/UI]
Description: [Detailed description]
Steps to Reproduce: [Step-by-step instructions]
Expected Result: [What should happen]
Actual Result: [What actually happens]
Environment: [Browser, OS, Python version]
Screenshots: [If applicable]
```

## Test Automation

### Continuous Integration
- Automated test execution on commit
- Code coverage reporting
- Performance regression detection
- Security vulnerability scanning

### Test Frameworks and Tools
- pytest for unit and integration tests
- FastAPI TestClient for API tests
- SQLAlchemy test fixtures
- Mock library for external dependencies
- Coverage.py for code coverage
- pytest-asyncio for async tests

---

**Test Plan Version**: 1.0  
**Created**: January 6, 2025  
**Status**: In Progress