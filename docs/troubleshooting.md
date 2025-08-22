# Troubleshooting Guide

## Table of Contents

1. [Common Issues](#common-issues)
2. [Installation Problems](#installation-problems)
3. [Database Issues](#database-issues)
4. [API and Network Problems](#api-and-network-problems)
5. [Price Data Issues](#price-data-issues)
6. [News Integration Problems](#news-integration-problems)
7. [CSV Import Issues](#csv-import-issues)
8. [Performance Problems](#performance-problems)
9. [Browser and UI Issues](#browser-and-ui-issues)
10. [Getting Help](#getting-help)

## Common Issues

### Application Won't Start

**Symptoms:**
- Error when running `uvicorn` command
- Import errors
- Permission denied errors

**Solutions:**

1. **Check Python Version**
   ```bash
   python --version  # Should be 3.9+
   ```

2. **Verify Dependencies**
   ```bash
   uv sync
   # or
   pip install -r requirements.txt
   ```

3. **Check Permissions**
   ```bash
   # Ensure data directory is writable
   mkdir -p data
   chmod 755 data
   ```

4. **Port Already in Use**
   ```bash
   # Use different port
   uv run uvicorn web_server.app:app --port 8001
   
   # Or kill existing process
   lsof -ti:8000 | xargs kill -9
   ```

### Can't Access Web Interface

**Symptoms:**
- Browser shows "This site can't be reached"
- Connection refused errors

**Solutions:**

1. **Check Server is Running**
   ```bash
   # Look for "Uvicorn running on http://..." message
   ```

2. **Verify URL**
   - Correct URL: `http://localhost:8000`
   - Not `https://` (unless configured)

3. **Check Firewall**
   ```bash
   # Allow port 8000
   sudo ufw allow 8000
   ```

4. **Try Different Port**
   ```bash
   uv run uvicorn web_server.app:app --port 8001
   ```

## Installation Problems

### uv Command Not Found

**Solution:**
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using pip
pip install uv
```

### Dependency Conflicts

**Symptoms:**
- Package version conflicts
- Import errors after installation

**Solutions:**

1. **Clean Installation**
   ```bash
   # Remove existing virtual environment
   rm -rf .venv
   
   # Fresh install
   uv sync
   ```

2. **Manual Dependency Installation**
   ```bash
   # Install core dependencies individually
   uv add fastapi uvicorn sqlalchemy pandas yfinance
   ```

3. **Use Virtual Environment**
   ```bash
   python -m venv portfolio_env
   source portfolio_env/bin/activate  # Linux/Mac
   # portfolio_env\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

### Build Errors

**Symptoms:**
- Compilation errors during installation
- Missing system dependencies

**Solutions:**

1. **Install System Dependencies** (Ubuntu/Debian)
   ```bash
   sudo apt update
   sudo apt install build-essential python3-dev
   ```

2. **Install System Dependencies** (macOS)
   ```bash
   xcode-select --install
   brew install python
   ```

3. **Install System Dependencies** (Windows)
   - Install Visual Studio Build Tools
   - Or use pre-compiled wheels: `pip install --only-binary=all -r requirements.txt`

## Database Issues

### Database File Permissions

**Symptoms:**
- "Permission denied" when accessing database
- Database locked errors

**Solutions:**

1. **Fix Permissions**
   ```bash
   chmod 664 data/portfolio_manager.db
   chmod 755 data/
   ```

2. **Check Disk Space**
   ```bash
   df -h .  # Check available space
   ```

3. **Move Database Location**
   ```bash
   export DATABASE_URL=sqlite:///tmp/portfolio_manager.db
   ```

### Database Corruption

**Symptoms:**
- "Database is locked" errors
- Data not saving/loading correctly
- SQLite errors in logs

**Solutions:**

1. **Check Database Integrity**
   ```bash
   sqlite3 data/portfolio_manager.db "PRAGMA integrity_check;"
   ```

2. **Backup and Recreate**
   ```bash
   # Backup existing data
   cp data/portfolio_manager.db data/portfolio_manager.db.backup
   
   # Remove corrupted database (will recreate on startup)
   rm data/portfolio_manager.db
   ```

3. **Repair Database**
   ```bash
   sqlite3 data/portfolio_manager.db ".backup data/portfolio_manager_repaired.db"
   mv data/portfolio_manager_repaired.db data/portfolio_manager.db
   ```

### Migration Errors

**Symptoms:**
- Database schema errors
- Missing tables/columns

**Solutions:**

1. **Fresh Database**
   ```bash
   # Backup data first
   cp data/portfolio_manager.db data/backup_$(date +%Y%m%d).db
   
   # Remove database to recreate schema
   rm data/portfolio_manager.db
   ```

2. **Manual Schema Update**
   ```sql
   -- Connect to database
   sqlite3 data/portfolio_manager.db
   
   -- Check existing tables
   .tables
   
   -- Manually add missing columns (example)
   ALTER TABLE portfolios ADD COLUMN new_column TEXT;
   ```

## API and Network Problems

### External API Failures

**Symptoms:**
- Stock prices not updating
- "API request failed" errors
- Timeout errors

**Solutions:**

1. **Check Internet Connection**
   ```bash
   ping google.com
   curl -I https://finance.yahoo.com
   ```

2. **Verify API Endpoints**
   ```bash
   # Test Yahoo Finance directly
   curl "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
   ```

3. **Check Rate Limits**
   - Wait a few minutes and try again
   - Yahoo Finance has rate limits

4. **Use Different Data Source**
   ```bash
   # Set environment variable to use backup source
   export STOCK_DATA_SOURCE=backup
   ```

### SSL/TLS Errors

**Symptoms:**
- Certificate verification errors
- SSL handshake failures

**Solutions:**

1. **Update Certificates**
   ```bash
   # Update system certificates
   sudo apt update && sudo apt install ca-certificates  # Ubuntu
   brew install ca-certificates  # macOS
   ```

2. **Bypass SSL (Not Recommended for Production)**
   ```python
   # In development only
   import ssl
   ssl._create_default_https_context = ssl._create_unverified_context
   ```

### Proxy Issues

**Symptoms:**
- Connection timeouts in corporate environments
- Proxy authentication errors

**Solutions:**

1. **Configure Proxy**
   ```bash
   export HTTP_PROXY=http://proxy.company.com:8080
   export HTTPS_PROXY=http://proxy.company.com:8080
   ```

2. **Authenticated Proxy**
   ```bash
   export HTTP_PROXY=http://username:password@proxy.company.com:8080
   ```

## Price Data Issues

### Prices Not Updating

**Symptoms:**
- Old prices showing
- "Last updated" timestamp is old
- Refresh button not working

**Solutions:**

1. **Manual Refresh**
   - Click individual refresh buttons
   - Use "Refresh All Prices" button

2. **Check API Status**
   ```bash
   # Test individual stock
   curl "https://query1.finance.yahoo.com/v8/finance/chart/AAPL"
   ```

3. **Clear Cache**
   ```bash
   # Restart application to clear cache
   # Or wait for 5-minute cache expiration
   ```

4. **Check Symbol Validity**
   - Ensure stock symbols are correct
   - Some symbols may be delisted

### Invalid Stock Symbols

**Symptoms:**
- "Symbol not found" errors
- No price data for certain stocks
- Validation failures

**Solutions:**

1. **Verify Symbol Format**
   - Use standard ticker symbols (AAPL, not Apple)
   - Check exchange-specific formats
   - International stocks may need suffix (.TO for Toronto)

2. **Check Symbol Existence**
   ```bash
   # Test symbol directly
   curl "https://query1.finance.yahoo.com/v8/finance/chart/SYMBOL"
   ```

3. **Update Symbol List**
   - Remove delisted stocks
   - Use current ticker symbols after mergers

### Price Data Accuracy

**Symptoms:**
- Prices seem incorrect
- Large unexpected changes
- Currency conversion issues

**Solutions:**

1. **Cross-Reference Data**
   - Check prices on Yahoo Finance website
   - Compare with other financial sites

2. **Check Market Hours**
   - Prices may be delayed outside market hours
   - Pre-market/after-hours prices may differ

3. **Currency Considerations**
   - International stocks in local currency
   - Check if conversion is needed

## News Integration Problems

### No News Showing

**Symptoms:**
- Empty news sections
- "No news available" messages
- News not loading

**Solutions:**

1. **Check API Configuration**
   ```bash
   # Check if Polygon API key is set
   echo $POLYGON_API_KEY
   ```

2. **Test News Sources**
   ```bash
   # Test endpoint directly
   curl "http://localhost:8000/api/watchlists/1/items/AAPL/test-news"
   ```

3. **Check Fallback Sources**
   - Polygon.io (requires API key)
   - Yahoo Finance (backup)
   - Mock data (last resort)

4. **Clear News Cache**
   - News cached for 4 hours
   - Use "Refresh News" button for immediate update

### Polygon API Issues

**Symptoms:**
- Rate limit errors
- Authentication failures
- No news from primary source

**Solutions:**

1. **Check API Key**
   ```bash
   # Verify API key is valid
   curl -H "Authorization: Bearer $POLYGON_API_KEY" \
        "https://api.polygon.io/v2/reference/news?ticker=AAPL&limit=1"
   ```

2. **Check Rate Limits**
   - Free tier: 5 calls per minute
   - Paid tier: Higher limits
   - Wait for rate limit reset

3. **Upgrade Plan**
   - Consider paid Polygon.io plan for more API calls
   - Or rely on Yahoo Finance fallback

### News Display Issues

**Symptoms:**
- News formatting problems
- Broken links
- Missing information

**Solutions:**

1. **Check Article URLs**
   - Some news sources may have paywalls
   - Links may be temporary

2. **Browser Compatibility**
   - Test in different browsers
   - Check JavaScript console for errors

3. **Content Filtering**
   - Some corporate networks block news sites
   - Check if external links are accessible

## CSV Import Issues

### File Format Errors

**Symptoms:**
- "Invalid CSV format" errors
- Import fails with parsing errors
- Missing column errors

**Solutions:**

1. **Check Required Columns**
   ```csv
   Symbol,Shares,Allocation
   AAPL,100,30.0
   ```

2. **Verify File Encoding**
   - Save as UTF-8
   - Avoid special characters
   - Use standard comma separator

3. **Check Data Types**
   - Shares: Numbers only (integers or decimals)
   - Allocation: Percentages (must sum to 100)
   - Symbol: Valid ticker symbols

### Validation Errors

**Symptoms:**
- "Allocation doesn't sum to 100%" errors
- Invalid symbol errors
- Negative values errors

**Solutions:**

1. **Fix Allocation Totals**
   ```csv
   # Must sum to exactly 100%
   Symbol,Shares,Allocation
   AAPL,100,50.0
   GOOGL,50,50.0
   ```

2. **Validate Symbols**
   - Use correct ticker symbols
   - Remove delisted stocks
   - Check for typos

3. **Check Value Ranges**
   - Shares: 0 or positive
   - Allocation: 0.01 to 99.99

### Import Performance

**Symptoms:**
- Large files taking too long
- Browser timeouts during import
- Memory issues

**Solutions:**

1. **Split Large Files**
   - Import in smaller batches
   - Maximum recommended: 1000 holdings

2. **Optimize CSV**
   - Remove unnecessary columns
   - Clean data before import

3. **Increase Timeouts**
   ```bash
   # Start server with longer timeout
   uv run uvicorn web_server.app:app --timeout-keep-alive 300
   ```

## Performance Problems

### Slow Loading Times

**Symptoms:**
- Pages take long to load
- Price updates are slow
- Unresponsive interface

**Solutions:**

1. **Check System Resources**
   ```bash
   # Monitor CPU and memory usage
   top
   htop  # If available
   ```

2. **Optimize Database**
   ```bash
   # Vacuum database
   sqlite3 data/portfolio_manager.db "VACUUM;"
   ```

3. **Reduce Data Load**
   - Limit number of holdings per portfolio
   - Clear old price cache
   - Archive unused portfolios

### Memory Usage

**Symptoms:**
- High RAM usage
- System becomes sluggish
- Out of memory errors

**Solutions:**

1. **Restart Application**
   ```bash
   # Stop and restart server
   pkill -f uvicorn
   uv run uvicorn web_server.app:app --reload
   ```

2. **Reduce Cache Size**
   - Configure smaller cache limits
   - More frequent cache clearing

3. **System Optimization**
   ```bash
   # Clear system cache (Linux)
   sudo sysctl vm.drop_caches=3
   ```

### Network Delays

**Symptoms:**
- API calls timing out
- Slow price updates
- Network errors

**Solutions:**

1. **Check Network Connection**
   ```bash
   # Test latency
   ping -c 4 finance.yahoo.com
   
   # Test bandwidth
   curl -w "%{time_total}" -o /dev/null -s "https://finance.yahoo.com"
   ```

2. **Configure Timeouts**
   - Increase API timeout values
   - Use retry mechanisms

3. **Use Local Caching**
   - Increase cache duration
   - Implement offline mode

## Browser and UI Issues

### JavaScript Errors

**Symptoms:**
- Buttons not working
- Forms not submitting
- Interactive features broken

**Solutions:**

1. **Check Browser Console**
   - Open Developer Tools (F12)
   - Look for JavaScript errors
   - Note specific error messages

2. **Clear Browser Cache**
   ```
   Ctrl+Shift+R (hard refresh)
   Or clear browser cache manually
   ```

3. **Try Different Browser**
   - Test in Chrome, Firefox, Safari
   - Check if issue is browser-specific

4. **Disable Extensions**
   - Ad blockers may interfere
   - Try incognito/private mode

### Responsive Design Issues

**Symptoms:**
- Layout broken on mobile
- Elements overlapping
- Text too small/large

**Solutions:**

1. **Check Viewport**
   - Zoom level at 100%
   - Test different screen sizes

2. **Update Browser**
   - Use modern browser versions
   - Enable modern CSS features

3. **Clear CSS Cache**
   - Hard refresh (Ctrl+Shift+R)
   - Check if custom CSS is interfering

### Form Submission Problems

**Symptoms:**
- Forms not submitting
- Data not saving
- Validation errors

**Solutions:**

1. **Check Required Fields**
   - All required fields filled
   - Correct data formats

2. **JavaScript Enabled**
   - Ensure JavaScript is enabled
   - Check for script blocking

3. **Network Issues**
   - Check if server is reachable
   - Look for CORS errors in console

## Getting Help

### Log Files

**Enable Detailed Logging:**
```bash
export LOG_LEVEL=DEBUG
uv run uvicorn web_server.app:app --reload
```

**Check Application Logs:**
- Look for error messages in console output
- Check for stack traces
- Note timestamps of issues

### System Information

**Collect System Info:**
```bash
# Python version
python --version

# Operating system
uname -a  # Linux/Mac
systeminfo  # Windows

# Disk space
df -h .

# Memory usage
free -h  # Linux
vm_stat  # Mac
```

### Bug Reports

**Include in Bug Reports:**
1. **Describe the Problem**
   - What you were trying to do
   - What happened instead
   - Steps to reproduce

2. **Environment Information**
   - Operating system
   - Python version
   - Browser (if web issue)

3. **Error Messages**
   - Complete error messages
   - Stack traces if available
   - Screenshots if helpful

4. **Log Output**
   - Relevant log entries
   - Debug output if available

### Community Support

**Getting Help:**
- Check existing GitHub issues
- Search this documentation
- Review API documentation
- Check the developer guide

**Creating Issues:**
- Use issue templates
- Provide complete information
- Include reproduction steps
- Tag appropriately

### Professional Support

For enterprise or commercial use:
- Consider professional support options
- Custom development services
- Extended maintenance agreements
- Priority bug fixes

---

## Frequently Asked Questions

### Can I run this on Windows?
Yes, the application is cross-platform and runs on Windows, macOS, and Linux.

### Do I need an internet connection?
Yes, for stock price data and news. Some features work offline with cached data.

### Is my data secure?
Yes, all data is stored locally on your machine. No sensitive data is transmitted to external servers.

### Can I use this commercially?
Check the license terms. Generally designed for personal and educational use.

### How do I backup my data?
Copy the `data/portfolio_manager.db` file. Also export portfolios to CSV for additional backup.

### Can I import data from other tools?
Yes, via CSV import. You may need to format your data to match the required CSV structure.

---

Still having issues? Check the other documentation files or create an issue on GitHub.