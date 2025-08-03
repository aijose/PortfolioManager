"""Stock data controller for fetching real-time stock prices."""

import yfinance as yf
import time
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class StockPrice:
    """Data class for stock price information."""
    symbol: str
    price: float
    currency: str
    market_cap: Optional[float]
    pe_ratio: Optional[float]
    dividend_yield: Optional[float]
    fifty_two_week_high: Optional[float]
    fifty_two_week_low: Optional[float]
    volume: Optional[int]
    avg_volume: Optional[int]
    market_state: str  # 'REGULAR', 'CLOSED', 'PRE', 'POST'
    last_updated: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'symbol': self.symbol,
            'price': self.price,
            'currency': self.currency,
            'market_cap': self.market_cap,
            'pe_ratio': self.pe_ratio,
            'dividend_yield': self.dividend_yield,
            'fifty_two_week_high': self.fifty_two_week_high,
            'fifty_two_week_low': self.fifty_two_week_low,
            'volume': self.volume,
            'avg_volume': self.avg_volume,
            'market_state': self.market_state,
            'last_updated': self.last_updated.isoformat()
        }


class PriceCache:
    """In-memory cache for stock prices with TTL."""
    
    def __init__(self, ttl_minutes: int = 5):
        self.cache: Dict[str, Tuple[StockPrice, datetime]] = {}
        self.ttl = timedelta(minutes=ttl_minutes)
    
    def get(self, symbol: str) -> Optional[StockPrice]:
        """Get cached price if still valid."""
        if symbol in self.cache:
            price, cached_time = self.cache[symbol]
            if datetime.now() - cached_time < self.ttl:
                return price
            else:
                # Remove expired entry
                del self.cache[symbol]
        return None
    
    def set(self, symbol: str, price: StockPrice) -> None:
        """Cache a stock price."""
        self.cache[symbol] = (price, datetime.now())
    
    def clear(self) -> None:
        """Clear all cached prices."""
        self.cache.clear()
    
    def remove(self, symbol: str) -> None:
        """Remove a specific symbol from cache."""
        if symbol in self.cache:
            del self.cache[symbol]
    
    def get_cache_info(self) -> dict:
        """Get information about the cache."""
        now = datetime.now()
        valid_entries = 0
        expired_entries = 0
        
        for symbol, (price, cached_time) in self.cache.items():
            if now - cached_time < self.ttl:
                valid_entries += 1
            else:
                expired_entries += 1
        
        return {
            'total_entries': len(self.cache),
            'valid_entries': valid_entries,
            'expired_entries': expired_entries,
            'ttl_minutes': self.ttl.total_seconds() / 60
        }


class StockDataController:
    """Controller for managing stock data operations."""
    
    def __init__(self, cache_ttl_minutes: int = 5, max_workers: int = 10):
        self.cache = PriceCache(cache_ttl_minutes)
        self.max_workers = max_workers
    
    def get_stock_price(self, symbol: str, use_cache: bool = True) -> Optional[StockPrice]:
        """
        Get current stock price for a single symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'AAPL')
            use_cache: Whether to use cached data if available
            
        Returns:
            StockPrice object or None if failed
        """
        symbol = symbol.upper().strip()
        
        # Check cache first
        if use_cache:
            cached_price = self.cache.get(symbol)
            if cached_price:
                logger.debug(f"Cache hit for {symbol}")
                return cached_price
        
        try:
            # Fetch from yfinance
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Check if we got valid data and extract price
            current_price = None
            
            # Try multiple price fields in order of preference
            price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose', 'open']
            for field in price_fields:
                if info and info.get(field) is not None:
                    current_price = info.get(field)
                    break
            
            # If no price found in info, try fast_info as fallback
            if current_price is None:
                try:
                    fast_info = ticker.fast_info
                    current_price = fast_info.get('last_price')
                except Exception as e:
                    logger.debug(f"Failed to get fast_info for {symbol}: {e}")
            
            # If still no price, try recent history
            if current_price is None:
                try:
                    hist = ticker.history(period="1d")
                    if not hist.empty and 'Close' in hist.columns:
                        current_price = hist['Close'].iloc[-1]
                        logger.info(f"Using historical close price for {symbol}")
                except Exception as e:
                    logger.debug(f"Failed to get history for {symbol}: {e}")
            
            # If we still don't have a price, give up
            if current_price is None:
                logger.warning(f"No price data available for {symbol}")
                return None
            
            # Determine market state
            market_state = self._determine_market_state(info)
            
            # Create StockPrice object
            stock_price = StockPrice(
                symbol=symbol,
                price=float(current_price),
                currency=info.get('currency', 'USD'),
                market_cap=info.get('marketCap'),
                pe_ratio=info.get('trailingPE'),
                dividend_yield=info.get('dividendYield'),
                fifty_two_week_high=info.get('fiftyTwoWeekHigh'),
                fifty_two_week_low=info.get('fiftyTwoWeekLow'),
                volume=info.get('volume'),
                avg_volume=info.get('averageVolume'),
                market_state=market_state,
                last_updated=datetime.now()
            )
            
            # Cache the result
            if use_cache:
                self.cache.set(symbol, stock_price)
            
            logger.info(f"Fetched price for {symbol}: ${current_price:.2f}")
            return stock_price
            
        except Exception as e:
            logger.error(f"Failed to fetch price for {symbol}: {e}")
            return None
    
    def get_multiple_stock_prices(self, symbols: List[str], use_cache: bool = True) -> Dict[str, Optional[StockPrice]]:
        """
        Get current stock prices for multiple symbols in parallel.
        
        Args:
            symbols: List of stock symbols
            use_cache: Whether to use cached data if available
            
        Returns:
            Dictionary mapping symbols to StockPrice objects
        """
        symbols = [s.upper().strip() for s in symbols]
        results = {symbol: None for symbol in symbols}
        
        # Check cache for all symbols first
        symbols_to_fetch = []
        if use_cache:
            for symbol in symbols:
                cached_price = self.cache.get(symbol)
                if cached_price:
                    results[symbol] = cached_price
                else:
                    symbols_to_fetch.append(symbol)
        else:
            symbols_to_fetch = symbols
        
        # Fetch uncached symbols in parallel
        if symbols_to_fetch:
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                # Submit all fetch tasks
                future_to_symbol = {
                    executor.submit(self.get_stock_price, symbol, False): symbol 
                    for symbol in symbols_to_fetch
                }
                
                # Collect results as they complete
                for future in as_completed(future_to_symbol):
                    symbol = future_to_symbol[future]
                    try:
                        price = future.result()
                        results[symbol] = price
                        
                        # Cache successful results
                        if price and use_cache:
                            self.cache.set(symbol, price)
                            
                    except Exception as e:
                        logger.error(f"Failed to fetch price for {symbol}: {e}")
                        results[symbol] = None
        
        return results
    
    def refresh_portfolio_prices(self, portfolio_holdings: List[str]) -> Dict[str, Optional[StockPrice]]:
        """
        Refresh prices for all holdings in a portfolio.
        
        Args:
            portfolio_holdings: List of stock symbols in the portfolio
            
        Returns:
            Dictionary mapping symbols to updated StockPrice objects
        """
        logger.info(f"Refreshing prices for {len(portfolio_holdings)} holdings")
        
        # Force refresh by not using cache
        results = self.get_multiple_stock_prices(portfolio_holdings, use_cache=False)
        
        successful_updates = len([r for r in results.values() if r is not None])
        logger.info(f"Successfully updated {successful_updates}/{len(portfolio_holdings)} prices")
        
        return results
    
    def validate_symbols(self, symbols: List[str]) -> Dict[str, bool]:
        """
        Validate that stock symbols exist and can be fetched.
        
        Args:
            symbols: List of stock symbols to validate
            
        Returns:
            Dictionary mapping symbols to boolean validity
        """
        results = {}
        
        for symbol in symbols:
            symbol = symbol.upper().strip()
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # A valid symbol should have basic info and at least one price field
                price_fields = ['currentPrice', 'regularMarketPrice', 'previousClose', 'open']
                has_price = any(info.get(field) is not None for field in price_fields) if info else False
                is_valid = bool(info and has_price)
                results[symbol] = is_valid
                
            except Exception as e:
                logger.warning(f"Symbol validation failed for {symbol}: {e}")
                results[symbol] = False
        
        return results
    
    def get_market_summary(self) -> dict:
        """Get general market summary information."""
        try:
            # Get major indices
            indices = {
                '^GSPC': 'S&P 500',
                '^DJI': 'Dow Jones',
                '^IXIC': 'NASDAQ',
                '^VIX': 'VIX'
            }
            
            index_data = {}
            for symbol, name in indices.items():
                price_data = self.get_stock_price(symbol)
                if price_data:
                    index_data[name] = {
                        'symbol': symbol,
                        'price': price_data.price,
                        'last_updated': price_data.last_updated.isoformat()
                    }
            
            return {
                'indices': index_data,
                'cache_info': self.cache.get_cache_info(),
                'last_updated': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get market summary: {e}")
            return {'error': str(e)}
    
    def _determine_market_state(self, info: dict) -> str:
        """Determine the current market state based on info data."""
        try:
            # Check if market is open
            market_state = info.get('marketState', 'UNKNOWN')
            if market_state in ['REGULAR', 'CLOSED', 'PRE', 'POST']:
                return market_state
            
            # Fallback: check regular market hours
            now = datetime.now()
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            if market_open <= now <= market_close:
                return 'REGULAR'
            elif now < market_open:
                return 'PRE'
            else:
                return 'POST'
                
        except Exception:
            return 'UNKNOWN'
    
    def clear_cache(self) -> None:
        """Clear all cached prices."""
        self.cache.clear()
        logger.info("Price cache cleared")
    
    def get_cache_stats(self) -> dict:
        """Get cache statistics."""
        return self.cache.get_cache_info()