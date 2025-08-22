"""Multi-source news controller for fetching stock news with intelligent fallback."""

import os
import time
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from dataclasses import dataclass

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
    """Multi-source news controller with intelligent fallback between APIs."""
    
    def __init__(self):
        """Initialize the multi-source news controller."""
        # Initialize all news sources
        self._init_sources()
        
        # Cache settings
        self.cache_duration = timedelta(hours=4)
        self.max_articles_per_symbol = 5
    
    def _init_sources(self):
        """Initialize all available news sources."""
        self.sources = []
        
        # 1. Polygon.io (primary source)
        self._init_polygon_source()
        
        # 2. Yahoo Finance (first fallback)
        self._init_yahoo_source()
        
        # 3. Mock data (last resort)
        self._init_mock_source()
        
        logger.info(f"Initialized {len(self.sources)} news sources")
    
    def _init_polygon_source(self):
        """Initialize Polygon.io source."""
        api_key = os.environ.get('POLYGON_API_KEY')
        if api_key:
            try:
                from polygon import RESTClient
                client = RESTClient(api_key)
                
                # Polygon source with rate limiting
                source = {
                    'name': 'Polygon.io',
                    'client': client,
                    'last_request_time': 0,
                    'min_interval': 15,
                    'request_times': [],
                    'active': True
                }
                self.sources.append(source)
                logger.info("✅ Polygon.io source initialized")
            except ImportError:
                logger.warning("❌ Polygon.io client not available (import error)")
        else:
            logger.warning("❌ Polygon.io source not available (no API key)")
    
    def _init_yahoo_source(self):
        """Initialize Yahoo Finance source."""
        try:
            import yfinance as yf
            source = {
                'name': 'Yahoo Finance',
                'yf': yf,
                'last_request_time': 0,
                'min_interval': 2,
                'active': True
            }
            self.sources.append(source)
            logger.info("✅ Yahoo Finance source initialized")
        except ImportError:
            logger.warning("❌ Yahoo Finance source not available (yfinance not installed)")
    
    def _init_mock_source(self):
        """Initialize mock data source."""
        source = {
            'name': 'Mock Data',
            'active': True
        }
        self.sources.append(source)
        logger.info("✅ Mock data source initialized")
    
    def get_ticker_news(self, symbol: str, limit: int = 5) -> List[NewsArticle]:
        """
        Fetch news articles from multiple sources with intelligent fallback.
        
        Args:
            symbol: Stock ticker symbol (e.g., 'AAPL')
            limit: Maximum number of articles to return
            
        Returns:
            List of NewsArticle objects from the first successful source
        """
        logger.info(f"Getting news for {symbol} from {len(self.sources)} potential sources")
        
        for source in self.sources:
            if not source.get('active', True):
                continue
                
            try:
                articles = self._get_news_from_source(source, symbol, limit)
                
                if articles:
                    logger.info(f"✅ Got {len(articles)} articles from {source['name']}")
                    return articles
                else:
                    logger.info(f"⚠️  No articles from {source['name']}, trying next source")
                    
            except Exception as e:
                logger.error(f"❌ {source['name']} failed: {e}")
                continue
        
        logger.warning(f"❌ All news sources failed for {symbol}")
        return []
    
    def _get_news_from_source(self, source: dict, symbol: str, limit: int) -> List[NewsArticle]:
        """Get news from a specific source."""
        source_name = source['name']
        
        if source_name == 'Polygon.io':
            return self._get_polygon_news(source, symbol, limit)
        elif source_name == 'Yahoo Finance':
            return self._get_yahoo_news(source, symbol, limit)
        elif source_name == 'Mock Data':
            return self._get_mock_news(symbol, limit)
        else:
            logger.warning(f"Unknown source: {source_name}")
            return []
    
    def _get_polygon_news(self, source: dict, symbol: str, limit: int) -> List[NewsArticle]:
        """Get news from Polygon.io with rate limiting."""
        client = source['client']
        
        # Rate limiting check
        now = time.time()
        source['request_times'] = [t for t in source.get('request_times', []) if now - t < 60]
        
        if len(source['request_times']) >= 4:
            logger.warning(f"[Polygon.io] Rate limit approached - skipping")
            return []
        
        if now - source.get('last_request_time', 0) < source['min_interval']:
            wait_time = source['min_interval'] - (now - source['last_request_time'])
            logger.info(f"[Polygon.io] Waiting {wait_time:.1f}s for rate limiting")
            time.sleep(wait_time)
        
        try:
            # Record request
            source['last_request_time'] = now
            source['request_times'] = source.get('request_times', []) + [now]
            
            logger.info(f"[Polygon.io] Fetching news for {symbol}")
            
            news_response = client.list_ticker_news(
                ticker=symbol,
                limit=limit,
                order="desc"
            )
            
            articles = []
            for article_data in news_response:
                try:
                    source_name = 'Unknown'
                    if hasattr(article_data, 'publisher') and article_data.publisher:
                        if hasattr(article_data.publisher, 'name'):
                            source_name = article_data.publisher.name
                    
                    article = NewsArticle(
                        title=getattr(article_data, 'title', 'No title'),
                        url=getattr(article_data, 'article_url', ''),
                        published_utc=getattr(article_data, 'published_utc', ''),
                        source=source_name,
                        summary=getattr(article_data, 'description', '')[:200] if hasattr(article_data, 'description') else None
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error(f"[Polygon.io] Error processing article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            if "429" in str(e) or "rate" in str(e).lower():
                logger.warning(f"[Polygon.io] Rate limited - increasing delays")
                source['min_interval'] = min(30, source['min_interval'] * 1.5)
            
            logger.error(f"[Polygon.io] Error: {e}")
            return []
    
    def _get_yahoo_news(self, source: dict, symbol: str, limit: int) -> List[NewsArticle]:
        """Get news from Yahoo Finance."""
        yf = source['yf']
        
        # Basic rate limiting
        now = time.time()
        if now - source.get('last_request_time', 0) < source['min_interval']:
            wait_time = source['min_interval'] - (now - source['last_request_time'])
            time.sleep(wait_time)
        
        try:
            source['last_request_time'] = now
            logger.info(f"[Yahoo Finance] Fetching news for {symbol}")
            
            ticker = yf.Ticker(symbol)
            news_data = ticker.news
            
            articles = []
            for item in news_data[:limit]:
                try:
                    content = item.get('content', {})
                    
                    pub_date = content.get('pubDate', '')
                    if not pub_date:
                        pub_date = datetime.utcnow().isoformat() + 'Z'
                    
                    provider = content.get('provider', {})
                    source_name = provider.get('displayName', 'Yahoo Finance')
                    
                    canonical_url = content.get('canonicalUrl', {})
                    url = canonical_url.get('url', '') if canonical_url else ''
                    
                    article = NewsArticle(
                        title=content.get('title', 'No title'),
                        url=url,
                        published_utc=pub_date,
                        source=source_name,
                        summary=content.get('summary', '')[:200] if content.get('summary') else None
                    )
                    articles.append(article)
                except Exception as e:
                    logger.error(f"[Yahoo Finance] Error processing article: {e}")
                    continue
            
            return articles
            
        except Exception as e:
            logger.error(f"[Yahoo Finance] Error: {e}")
            return []
    
    def _get_mock_news(self, symbol: str, limit: int = 5) -> List[NewsArticle]:
        """Generate mock news data when APIs are unavailable."""
        
        # Return empty for crypto and uncommon symbols  
        if symbol in ['BTC-USD', 'PSLV', 'GOLD', 'SLV', 'ETH-USD']:
            logger.info(f"[Mock Data] No mock news for {symbol}")
            return []
        
        mock_articles = [
            NewsArticle(
                title=f'{symbol} Earnings Report Shows Strong Performance',
                url='https://example.com/news/1',
                published_utc='2025-01-06T14:30:00Z',
                source='Financial Times (Mock)',
                summary=f'Latest earnings report for {symbol} shows strong performance across key metrics.'
            ),
            NewsArticle(
                title=f'Technical Analysis: {symbol} Shows Bullish Patterns',
                url='https://example.com/news/2',
                published_utc='2025-01-06T13:15:00Z',
                source='MarketWatch (Mock)',
                summary='Technical indicators suggest positive momentum for this stock.'
            )
        ]
        
        logger.info(f"[Mock Data] Generated {min(len(mock_articles), limit)} mock articles for {symbol}")
        return mock_articles[:limit]
    
    # Keep existing cache methods for compatibility
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
                    summary=article_dict.get('summary')
                )
                articles.append(article)
            except Exception as e:
                logger.error(f"Error parsing stored article: {e}")
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
        results = {}
        
        for symbol in symbols:
            try:
                articles = self.get_ticker_news(symbol, self.max_articles_per_symbol)
                results[symbol] = articles
                
                # Small delay between symbols to be respectful
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"Error fetching news for {symbol}: {e}")
                results[symbol] = []
        
        return results


# Test the multi-source controller
if __name__ == "__main__":
    print("🧪 TESTING MULTI-SOURCE NEWS CONTROLLER")
    print("=" * 50)
    
    controller = NewsController()
    
    # Test with different symbols
    test_symbols = ['AAPL', 'MSFT', 'BTC-USD', 'PSLV']
    
    for symbol in test_symbols:
        print(f"\n📰 Testing {symbol}...")
        articles = controller.get_ticker_news(symbol, limit=3)
        
        if articles:
            print(f"✅ Got {len(articles)} articles:")
            for i, article in enumerate(articles, 1):
                print(f"   {i}. {article.title[:60]}... (Source: {article.source})")
        else:
            print(f"❌ No articles found for {symbol}")
    
    print("\n🎯 Multi-source controller test complete!")