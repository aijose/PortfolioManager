# Stock Portfolio Manager - Implementation Plan

## Overview
This document outlines a step-by-step implementation plan for building the Stock Portfolio Manager web application using FastAPI and modern web technologies.

## Development Phases

### Phase 1: Foundation & Core Infrastructure (Week 1-2)

#### 1.1 Project Setup & Environment
**Priority: Critical**

1. **Initialize Project Structure**
   ```
   portfolio_manager/
   ├── main.py
   ├── requirements.txt
   ├── .env.example
   ├── .gitignore
   ├── web_server/
   │   ├── __init__.py
   │   ├── app.py
   │   ├── routes/
   │   │   ├── __init__.py
   │   │   ├── portfolios.py
   │   │   └── api.py
   │   ├── static/
   │   │   ├── css/
   │   │   ├── js/
   │   │   └── images/
   │   └── templates/
   │       ├── base.html
   │       ├── index.html
   │       └── portfolios/
   ├── models/
   │   ├── __init__.py
   │   ├── database.py
   │   ├── portfolio.py
   │   └── holding.py
   ├── controllers/
   │   ├── __init__.py
   │   ├── portfolio_controller.py
   │   └── stock_data_controller.py
   ├── utils/
   │   ├── __init__.py
   │   ├── csv_parser.py
   │   └── validators.py
   ├── data/
   └── tests/
   ```

2. **Setup Dependencies**
   ```python
   # requirements.txt
   fastapi==0.104.1
   uvicorn==0.24.0
   jinja2==3.1.2
   python-multipart==0.0.6
   pandas==2.1.4
   numpy==1.25.2
   sqlalchemy==2.0.23
   yfinance==0.2.18
   plotly==5.17.0
   pytest==7.4.3
   python-dotenv==1.0.0
   ```

3. **Configure Environment**
   - Create `.env` file for configuration
   - Setup logging configuration
   - Initialize Git repository (already done)

#### 1.2 Database Foundation
**Priority: Critical**

1. **SQLAlchemy Models**
   - Portfolio model (id, name, created_date, modified_date)
   - Holding model (portfolio_id, symbol, shares, target_allocation)
   - Database initialization and migrations

2. **Database Operations**
   - CRUD operations for portfolios
   - CRUD operations for holdings
   - Database connection management

#### 1.3 Basic FastAPI Server
**Priority: Critical**

1. **Core FastAPI Application**
   - Basic FastAPI app setup with static files
   - Template rendering with Jinja2
   - Error handling middleware
   - CORS configuration for local development

2. **Basic Routes**
   - Home page route (`/`)
   - Health check endpoint (`/health`)
   - Static file serving

### Phase 2: Portfolio Management Core (Week 2-3)

#### 2.1 Portfolio CRUD Operations
**Priority: High**

1. **Backend API Endpoints**
   - `GET /api/portfolios` - List all portfolios
   - `POST /api/portfolios` - Create new portfolio
   - `GET /api/portfolios/{id}` - Get portfolio details
   - `PUT /api/portfolios/{id}` - Update portfolio
   - `DELETE /api/portfolios/{id}` - Delete portfolio

2. **Frontend Pages**
   - Portfolio list page with create/edit/delete actions
   - Portfolio detail page showing holdings
   - Portfolio creation/editing forms with validation

#### 2.2 CSV Import Functionality
**Priority: High**

1. **CSV Processing Backend**
   - File upload endpoint (`POST /api/portfolios/{id}/import`)
   - CSV validation (Symbol, Shares, Allocation columns)
   - Data validation (symbols, allocation sum to 100%)
   - Error handling and reporting

2. **Frontend CSV Import**
   - Drag-and-drop file upload interface
   - Upload progress indicators
   - Validation error display
   - Success confirmation with imported data preview

#### 2.3 Holdings Management
**Priority: High**

1. **Holdings API**
   - `GET /api/portfolios/{id}/holdings` - List holdings
   - `POST /api/portfolios/{id}/holdings` - Add holding
   - `PUT /api/portfolios/{id}/holdings/{symbol}` - Update holding
   - `DELETE /api/portfolios/{id}/holdings/{symbol}` - Remove holding

2. **Holdings Interface**
   - Holdings table with edit-in-place functionality
   - Add new holding form
   - Delete holdings with confirmation

### Phase 3: Stock Data Integration (Week 3-4)

#### 3.1 Stock Price API Integration
**Priority: High**

1. **Stock Data Service**
   - yfinance integration for real-time prices
   - Batch price fetching for multiple symbols
   - Price caching mechanism (5-minute cache)
   - Error handling for invalid symbols/API failures

2. **Price Update Endpoints**
   - `GET /api/stocks/{symbol}/price` - Get single stock price
   - `POST /api/portfolios/{id}/refresh-prices` - Update all portfolio prices
   - `GET /api/portfolios/{id}/current-value` - Get current portfolio value

#### 3.2 Portfolio Valuation
**Priority: High**

1. **Valuation Logic**
   - Calculate current portfolio value
   - Compute current allocation percentages
   - Calculate gains/losses per holding
   - Portfolio summary statistics

2. **Real-time Updates**
   - Auto-refresh prices every 5 minutes (configurable)
   - WebSocket updates for real-time data (optional)
   - Loading indicators during price updates

### Phase 4: Rebalancing Engine (Week 4-5)

#### 4.1 Rebalancing Analysis
**Priority: High**

1. **Rebalancing Logic**
   - Compare current vs target allocations
   - Calculate required buy/sell transactions
   - Account for transaction costs (configurable)
   - Generate optimization recommendations

2. **Rebalancing API**
   - `GET /api/portfolios/{id}/rebalancing-analysis` - Analyze rebalancing needs
   - `POST /api/portfolios/{id}/generate-transactions` - Generate transaction list
   - `POST /api/portfolios/{id}/execute-rebalancing` - Apply rebalancing (update holdings)

#### 4.2 Rebalancing Interface
**Priority: High**

1. **Analysis Dashboard**
   - Current vs target allocation comparison
   - Visual pie charts showing allocation differences
   - Rebalancing recommendations table
   - Transaction cost estimates

2. **Transaction Execution**
   - Review and approve transactions interface
   - Execute rebalancing with confirmation
   - Transaction history logging

### Phase 5: User Interface Enhancement (Week 5-6)

#### 5.1 Dashboard Development
**Priority: Medium**

1. **Main Dashboard**
   - Portfolio selector dropdown
   - Key metrics cards (total value, P&L, allocation drift)
   - Holdings table with real-time values
   - Recent activity feed

2. **Interactive Charts**
   - Plotly.js integration for interactive charts
   - Current vs target allocation pie charts
   - Portfolio value over time (if historical data available)
   - Individual stock performance charts

#### 5.2 Responsive Design
**Priority: Medium**

1. **CSS Framework Integration**
   - Bootstrap or Tailwind CSS for responsive design
   - Mobile-friendly navigation
   - Touch-friendly controls for tablets

2. **User Experience Improvements**
   - Loading spinners and progress indicators
   - Toast notifications for actions
   - Keyboard shortcuts for power users
   - Auto-save functionality

### Phase 5.5: Market News Integration (Week 5.5-6) - **COMPLETED**

#### 5.5.1 News Controller Development
**Priority: High** (Completed)

1. **Multi-Source News Controller**
   - Polygon.io API integration with rate limiting
   - Yahoo Finance fallback news source
   - Mock data source for testing scenarios
   - Intelligent source switching on failures

2. **News Data Management**
   - NewsArticle data class for consistent structure
   - 4-hour caching system for news articles
   - Database storage of cached news data
   - Automatic cache expiration handling

#### 5.5.2 Watchlist News Integration
**Priority: High** (Completed)

1. **API Endpoints**
   - `GET /api/watchlists/{id}/items/{symbol}/news` - Cached/fresh news
   - `POST /api/watchlists/{id}/items/{symbol}/refresh-news` - Force refresh
   - News validation and error handling

2. **Frontend Integration**
   - Expandable news sections in watchlist detail view
   - "Expand All News" toggle for bulk operations
   - Individual news toggle buttons per stock
   - Loading indicators and error states

### Phase 6: Advanced Features (Week 6-7)

#### 6.1 Export Functionality
**Priority: Medium**

1. **Data Export**
   - `GET /api/portfolios/{id}/export/csv` - Export portfolio to CSV
   - `GET /api/portfolios/{id}/export/transactions` - Export rebalancing transactions
   - PDF report generation (basic)

2. **Backup & Restore**
   - Full portfolio data backup
   - Import/restore from backup files
   - Automated daily backups

#### 6.2 Configuration & Settings
**Priority: Low**

1. **Application Settings**
   - Price refresh intervals
   - Transaction cost settings
   - Default allocation tolerances
   - Theme preferences

2. **Portfolio Settings**
   - Portfolio-specific settings
   - Custom categories/sectors
   - Rebalancing preferences

### Phase 7: Testing & Polish (Week 7-8)

#### 7.1 Comprehensive Testing
**Priority: High**

1. **Backend Testing**
   - Unit tests for all models and controllers
   - API endpoint testing
   - Database operation testing
   - Mock external API calls for testing

2. **Frontend Testing**
   - JavaScript unit tests
   - Integration tests for user workflows
   - Cross-browser compatibility testing

#### 7.2 Documentation & Deployment
**Priority: Medium**

1. **Documentation**
   - User manual/guide
   - API documentation
   - Developer setup guide
   - Troubleshooting guide

2. **Deployment Preparation**
   - Production configuration
   - Security hardening
   - Performance optimization
   - Error monitoring setup

## Implementation Priority Order

### Sprint 1 (Week 1): Foundation
1. Project structure setup
2. Database models and basic CRUD
3. Basic FastAPI server with templates
4. Simple portfolio list/create interface

### Sprint 2 (Week 2): Core Functionality
1. CSV import with validation
2. Holdings management
3. Basic portfolio detail pages
4. Error handling and validation

### Sprint 3 (Week 3): Stock Data
1. yfinance integration
2. Real-time price updates
3. Portfolio valuation calculations
4. Price refresh interface

### Sprint 4 (Week 4): Rebalancing
1. Rebalancing analysis logic
2. Transaction generation
3. Rebalancing interface
4. Transaction execution

### Sprint 5 (Week 5): UI Polish & News Integration
1. Dashboard enhancement
2. Interactive charts
3. Responsive design
4. User experience improvements
5. **Market news integration (COMPLETED)**

### Sprint 6 (Week 6): Advanced Features
1. Export functionality
2. Settings and configuration
3. Backup/restore features
4. Performance optimization

### Sprint 7 (Week 7): Testing & Documentation
1. Comprehensive testing
2. Bug fixes and polish
3. Documentation
4. Final deployment preparation

## Technical Considerations

### Performance Targets
- Server startup: < 10 seconds
- Page load time: < 3 seconds
- API response time: < 2 seconds
- Price refresh for 50 stocks: < 30 seconds

### Security Considerations
- Input validation for all user data
- SQL injection prevention (SQLAlchemy ORM)
- File upload security (CSV validation)
- Rate limiting for API endpoints

### Error Handling Strategy
- Graceful degradation for API failures
- User-friendly error messages
- Comprehensive logging
- Fallback mechanisms for stock data

### Testing Strategy
- Unit tests for business logic (80% coverage target)
- Integration tests for API endpoints
- End-to-end tests for critical user workflows
- Performance testing for large portfolios

## Success Metrics

### MVP Success Criteria
- [ ] Launch local web server successfully
- [ ] Import CSV with Symbol, Shares, Allocation columns
- [ ] Create and manage multiple named portfolios
- [ ] Display current vs target allocation
- [ ] Generate rebalancing recommendations
- [ ] Update stock prices from yfinance API

### Performance Benchmarks
- [ ] Handle 10 portfolios with 50 stocks each
- [ ] Sub-3-second page loads
- [ ] 99% uptime for local server
- [ ] Successful CSV import for 1000+ holdings

### User Experience Goals
- [ ] Intuitive navigation requiring minimal learning
- [ ] Mobile-friendly responsive design
- [ ] Clear error messages and guidance
- [ ] Fast, real-time updates

---

**Document Version**: 1.0  
**Created**: August 3, 2025  
**Last Updated**: August 3, 2025  
**Prepared By**: Claude  
**Status**: Planning Phase