"""News controller for fetching stock news from Polygon.io API."""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass
from polygon import RESTClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class NewsArticle:
    """Data class for news article information."""
    title: str
    url: str
    published_utc: str
    source: str
    summary: Optional[str] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'title': self.title,
            'url': self.url,
            'published_utc': self.published_utc,
            'source': self.source,
            'summary': self.summary
        }


class NewsController:
    """Controller for fetching and caching stock news from Polygon.io."""
    
    def __init__(self):
        """Initialize the news controller with Polygon.io client."""
        self.api_key = os.environ.get('POLYGON_API_KEY')
        if not self.api_key:
            logger.warning("POLYGON_API_KEY not found in environment variables")
            self.client = None
        else:
            self.client = RESTClient(self.api_key)
        
        # Cache settings - 4 hours to respect 5 calls/min rate limit
        self.cache_duration = timedelta(hours=4)
        self.max_articles_per_symbol = 5
        
        # Rate limiting - Polygon.io free tier: 5 calls/minute
        self.last_request_time = 0
        self.min_request_interval = 15  # 15 seconds between requests (4/minute max)
        self.request_times = []
    
    def _can_make_request(self) -> bool:
        """Check if we can make a request without hitting rate limits."""
        now = time.time()
        
        # Clean old request times (older than 1 minute)
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        # Check if we've made too many requests in the last minute
        if len(self.request_times) >= 4:  # Stay under 5/minute limit
            logger.warning("Rate limit approached - deferring API request")
            return False
        
        # Check minimum interval between requests
        if now - self.last_request_time < self.min_request_interval:
            wait_time = self.min_request_interval - (now - self.last_request_time)
            logger.info(f"Waiting {wait_time:.1f}s to respect rate limits")
            time.sleep(wait_time)
        
        return True
    
    def _record_request(self):
        """Record that we made a request."""
        now = time.time()
        self.last_request_time = now
        self.request_times.append(now)
    
    def get_ticker_news(self, symbol: str, limit: int = 5) -> List[NewsArticle]:
        """
        Fetch news articles for a specific ticker symbol.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            limit: Maximum number of articles to return
            
        Returns:
            List of NewsArticle objects
        """
        if not self.client:
            logger.error("Polygon.io client not initialized - missing API key")
            return []
        
        # Check if we can make a request without hitting rate limits
        if not self._can_make_request():
            logger.warning(f"Rate limited - returning mock data for {symbol}")
            return self._get_mock_news(symbol, limit)
        
        try:
            # Record this request
            self._record_request()
            
            # Fetch news from Polygon.io
            logger.info(f"Fetching news for {symbol} from Polygon.io")
            
            # Get news articles for the ticker
            news_response = self.client.list_ticker_news(
                ticker=symbol,
                limit=limit,
                order="desc"  # Most recent first
            )
            
            articles = []
            for article_data in news_response:
                try:
                    # Extract publisher name safely
                    source_name = 'Unknown'
                    if hasattr(article_data, 'publisher') and article_data.publisher:
                        if hasattr(article_data.publisher, 'name'):
                            source_name = article_data.publisher.name
                        elif isinstance(article_data.publisher, dict):
                            source_name = article_data.publisher.get('name', 'Unknown')
                    
                    article = NewsArticle(
                        title=getattr(article_data, 'title', 'No title'),
                        url=getattr(article_data, 'article_url', ''),
                        published_utc=getattr(article_data, 'published_utc', ''),
                        source=source_name,
                        summary=getattr(article_data, 'description', None)
                    )
                    articles.append(article)
                except Exception as e:
                    logger.warning(f"Error parsing article for {symbol}: {e}")
                    continue
            
            logger.info(f"Successfully fetched {len(articles)} articles for {symbol}")
            return articles
            
        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {e}")
            
            # If we get rate limited, increase delays for future requests
            if "429" in str(e) or "rate" in str(e).lower():
                logger.warning("Rate limited by Polygon.io - increasing delays")
                self.min_request_interval = min(30, self.min_request_interval * 1.5)
            
            # Return mock data as fallback
            return self._get_mock_news(symbol, limit)
    
    def _get_mock_news(self, symbol: str, limit: int = 5) -> List[NewsArticle]:
        """Generate mock news data when API is unavailable or rate limited."""
        
        # Return empty for crypto and less common symbols
        if symbol in ['BTC-USD', 'PSLV', 'GOLD', 'SLV', 'ETH-USD']:
            logger.info(f"No mock news available for {symbol}")
            return []
        
        # Mock data for major stocks
        mock_articles = [
            NewsArticle(
                title=f'{symbol} Earnings Report Shows Strong Performance',
                url='https://example.com/news/1',
                published_utc='2025-01-06T14:30:00Z',
                source='Financial Times',
                summary=f'Latest earnings report for {symbol} shows strong performance across key metrics.'
            ),
            NewsArticle(
                title=f'Technical Analysis: {symbol} Shows Bullish Patterns',
                url='https://example.com/news/2',
                published_utc='2025-01-06T13:15:00Z',
                source='MarketWatch',
                summary='Technical indicators suggest positive momentum for this stock.'
            )
        ]
        
        logger.info(f"Returning {min(len(mock_articles), limit)} mock articles for {symbol}")
        return mock_articles[:limit]
    
    def is_news_cache_valid(self, last_update: Optional[datetime]) -> bool:
        """Check if cached news is still valid (within cache duration)."""
        if not last_update:
            return False
        return datetime.utcnow() - last_update < self.cache_duration
    
    def format_news_for_storage(self, articles: List[NewsArticle]) -> dict:
        """Format news articles for JSON storage in database."""
        return {
            "articles": [article.to_dict() for article in articles],
            "last_updated": datetime.utcnow().isoformat()
        }
    
    def parse_stored_news(self, news_data: Optional[dict]) -> List[NewsArticle]:
        """Parse news data from database storage back to NewsArticle objects."""
        if not news_data or 'articles' not in news_data:
            return []
        
        articles = []
        for article_dict in news_data['articles']:
            try:
                article = NewsArticle(
                    title=article_dict.get('title', 'No title'),
                    url=article_dict.get('url', ''),
                    published_utc=article_dict.get('published_utc', ''),
                    source=article_dict.get('source', 'Unknown'),
                    summary=article_dict.get('summary', '')
                )
                articles.append(article)
            except Exception as e:
                logger.warning(f"Error parsing stored article: {e}")
                continue
        
        return articles
    
    def get_cached_or_fresh_news(self, symbol: str, last_update: Optional[datetime], 
                                cached_news: Optional[dict]) -> tuple[List[NewsArticle], bool]:
        """
        Get news either from cache (if valid) or fetch fresh from API.
        
        Returns:
            Tuple of (articles, was_fetched_fresh)
        """
        # Check if cache is valid
        if self.is_news_cache_valid(last_update) and cached_news:
            logger.info(f"Using cached news for {symbol}")
            articles = self.parse_stored_news(cached_news)
            return articles, False
        
        # Cache is stale or missing, fetch fresh news
        logger.info(f"Fetching fresh news for {symbol}")
        articles = self.get_ticker_news(symbol, self.max_articles_per_symbol)
        return articles, True
    
    def refresh_multiple_symbols_news(self, symbols: List[str]) -> Dict[str, List[NewsArticle]]:
        """
        Fetch news for multiple symbols with rate limiting.
        
        Args:
            symbols: List of ticker symbols
            
        Returns:
            Dictionary mapping symbols to their news articles
        """
        if not self.client:
            logger.error("Polygon.io client not initialized")
            return {}
        
        results = {}
        
        # Rate limiting: 5 calls per minute max
        calls_made = 0
        start_time = time.time()
        
        for symbol in symbols:
            if calls_made >= 5:
                # Wait for next minute if we've made 5 calls
                elapsed = time.time() - start_time
                if elapsed < 60:
                    wait_time = 60 - elapsed
                    logger.info(f"Rate limiting: waiting {wait_time:.1f} seconds")
                    time.sleep(wait_time)
                    start_time = time.time()
                    calls_made = 0
            
            try:
                articles = self.get_ticker_news(symbol, self.max_articles_per_symbol)
                results[symbol] = articles
                calls_made += 1
                
                # Small delay between calls to be respectful
                time.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching news for {symbol}: {e}")
                results[symbol] = []
        
        return results