# Portfolio Manager User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [Portfolio Management](#portfolio-management)
3. [Watchlist Management](#watchlist-management)
4. [Market News Features](#market-news-features)
5. [Stock Price Management](#stock-price-management)
6. [Data Import and Export](#data-import-and-export)
7. [Tips and Best Practices](#tips-and-best-practices)

## Getting Started

### First Time Setup

1. **Install and Start the Application**
   ```bash
   uv sync
   uv run uvicorn web_server.app:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Access the Web Interface**
   - Open your browser and navigate to `http://localhost:8000`
   - You'll see the main dashboard with navigation options

3. **Understanding the Interface**
   - **Navigation Bar**: Access portfolios, watchlists, and settings
   - **Dashboard**: Overview of your portfolios and recent activity
   - **Responsive Design**: Works on desktop, tablet, and mobile devices

### Key Concepts

- **Portfolio**: A collection of stock holdings with target allocations
- **Watchlist**: A list of stocks you want to monitor (without holdings)
- **Target Allocation**: The percentage of your portfolio you want each stock to represent
- **Current Allocation**: The actual percentage based on current market values

## Portfolio Management

### Creating Your First Portfolio

1. **Navigate to Portfolios**
   - Click "Portfolios" in the navigation bar
   - Click "Create New Portfolio"

2. **Enter Portfolio Details**
   - **Name**: Choose a descriptive name (e.g., "Retirement Fund", "Growth Portfolio")
   - **Description**: Optional description of the portfolio's purpose

3. **Add Holdings**
   - Click "Add Holding" to manually add stocks
   - Or use "Import CSV" for bulk uploads

### Adding Holdings Manually

1. **Stock Symbol**: Enter the ticker symbol (e.g., AAPL, MSFT, GOOGL)
2. **Shares**: Number of shares you currently own
3. **Target Allocation**: Desired percentage of total portfolio value
4. **Validation**: The system validates symbols and ensures allocations sum to 100%

### Portfolio Analytics

**Current Value Calculation**
- Real-time calculation based on current stock prices
- Automatic updates every 5 minutes (cached)
- Manual refresh available

**Allocation Analysis**
- Current vs. Target allocation comparison
- Visual pie charts showing allocation breakdown
- Drift analysis showing how far from target

**Performance Metrics**
- Total portfolio value
- Gains/losses (absolute and percentage)
- Individual stock performance
- Portfolio composition breakdown

### Portfolio Operations

**Editing Portfolios**
- Rename portfolios
- Update descriptions
- Modify holdings and allocations

**Deleting Portfolios**
- Permanent deletion with confirmation
- Removes all associated holdings and history

**Duplicating Portfolios**
- Create copies for testing different allocations
- Useful for scenario planning

## Watchlist Management

### Creating Watchlists

1. **Purpose**: Monitor stocks without owning them
2. **Use Cases**:
   - Research potential investments
   - Track competitor stocks
   - Monitor market sectors
   - Follow news and trends

### Adding Stocks to Watchlists

**Individual Addition**
1. Navigate to your watchlist
2. Click "Add Stock"
3. Enter ticker symbol
4. Add optional notes

**Bulk Addition**
1. Use "Bulk Add" feature
2. Enter multiple symbols separated by commas
3. System validates and adds valid symbols
4. Reports any errors or invalid symbols

### Watchlist Features

**Real-time Price Updates**
- Current stock prices with refresh timestamps
- Percentage changes from previous close
- Color-coded gains (green) and losses (red)

**Notes and Organization**
- Add personal notes for each stock
- Reorder stocks by drag-and-drop
- Filter and search functionality

**Export and Sharing**
- Export watchlist data to CSV
- Share watchlist configurations

## Market News Features

### Viewing Stock News

**In Watchlists**
1. Navigate to any watchlist
2. Find the stock you're interested in
3. Click "Show News" to expand news section
4. Use "Expand All News" for bulk viewing

**News Sources**
- **Primary**: Polygon.io (requires API key)
- **Fallback**: Yahoo Finance
- **Testing**: Mock data when APIs unavailable

### News Management

**Caching System**
- News cached for 4 hours for performance
- Automatic refresh when cache expires
- Manual refresh with "Refresh News" button

**News Display**
- Article titles with publication dates
- Source attribution
- Direct links to full articles
- Article summaries when available

**Bulk Operations**
- "Expand All News" - Show news for all stocks
- "Collapse All News" - Hide all news sections
- Individual toggles for each stock

### News Configuration

**API Setup** (Optional)
- Set `POLYGON_API_KEY` environment variable for enhanced news
- Without API key, system falls back to Yahoo Finance and mock data
- No configuration required for basic functionality

## Stock Price Management

### Automatic Updates

**Price Caching**
- Prices cached for 5 minutes
- Reduces API calls and improves performance
- Cache status displayed in interface

**Scheduled Refreshes**
- Automatic background updates
- Configurable refresh intervals
- Error handling and retry logic

### Manual Updates

**Individual Stock Refresh**
- Click refresh icon next to any stock
- Immediate price update
- Loading indicators during fetch

**Bulk Price Updates**
- "Refresh All Prices" for entire portfolio/watchlist
- Concurrent fetching for improved speed
- Progress indicators and error reporting

### Price Data Sources

**Primary Source**: Yahoo Finance API
- Free and reliable
- Real-time during market hours
- Historical data available

**Error Handling**
- Graceful fallback for API failures
- Clear error messages
- Retry mechanisms

## Data Import and Export

### CSV Import Format

**Required Columns**
```csv
Symbol,Shares,Allocation
AAPL,100,30.0
GOOGL,50,25.0
MSFT,75,20.0
TSLA,25,15.0
NVDA,30,10.0
```

**Validation Rules**
- Symbols: 2-5 character ticker symbols
- Shares: Non-negative numbers (0+ allowed)
- Allocation: Positive percentages that sum to 100%
- No duplicate symbols allowed

### Import Process

1. **Prepare CSV File**
   - Use required column headers
   - Ensure data follows validation rules
   - Save as .csv format

2. **Upload File**
   - Navigate to portfolio
   - Click "Import CSV"
   - Select file using drag-and-drop or file picker

3. **Review Import**
   - System validates all data
   - Shows preview of what will be imported
   - Reports any errors or warnings

4. **Confirm Import**
   - Review changes
   - Click "Confirm Import"
   - System adds/updates holdings

### Export Options

**Portfolio Export**
- Export current portfolio state to CSV
- Includes current prices and allocations
- Suitable for backup or analysis

**Transaction History**
- Export rebalancing transactions
- Historical portfolio changes
- Performance tracking data

## Tips and Best Practices

### Portfolio Management

**Allocation Strategy**
- Keep target allocations realistic and achievable
- Consider transaction costs when setting targets
- Review and adjust allocations periodically

**Diversification**
- Spread risk across different sectors
- Consider market cap diversification
- Monitor correlation between holdings

**Rebalancing**
- Set tolerance bands (e.g., ±5%) for rebalancing triggers
- Consider tax implications of selling
- Account for transaction costs

### Watchlist Organization

**Categorization**
- Create themed watchlists (e.g., "Tech Stocks", "Dividend Growth")
- Use descriptive names for easy identification
- Add notes to remember why you're watching each stock

**Regular Review**
- Check watchlists weekly
- Remove stocks no longer of interest
- Add new stocks based on research

### News and Research

**Information Sources**
- Use multiple news sources for balanced perspective
- Cross-reference news with other research
- Focus on fundamental analysis over short-term news

**News Management**
- Check news regularly but avoid overreacting
- Use news to inform long-term decisions
- Consider the source credibility

### Performance Tracking

**Regular Monitoring**
- Review portfolio performance monthly
- Track against benchmarks (S&P 500, etc.)
- Document investment decisions and outcomes

**Record Keeping**
- Export data regularly for backup
- Maintain transaction records
- Document investment thesis for each holding

### Security and Privacy

**Data Protection**
- All data stored locally on your machine
- No sensitive information sent to external servers
- Regular backups recommended

**API Keys**
- Store API keys securely
- Use environment variables, not hard-coded values
- Rotate keys periodically if supported

---

## Need Help?

- **Troubleshooting**: See [troubleshooting.md](troubleshooting.md)
- **API Reference**: See [api-reference.md](api-reference.md)
- **Developer Guide**: See [developer-guide.md](developer-guide.md)
- **FAQ**: See [faq.md](faq.md)