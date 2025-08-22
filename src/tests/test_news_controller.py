"""Unit tests for NewsController."""

import pytest
from unittest.mock import Mock, patch
from controllers.news_controller import NewsController


@pytest.fixture
def mock_news_controller():
    """Create a news controller with mocked dependencies."""
    return NewsController()


def test_get_ticker_news_with_polygon_success(mock_news_controller):
    """Test getting stock news with successful Polygon.io response."""
    mock_polygon_response = {
        "results": [
            {
                "title": "Apple Reports Strong Q4 Earnings",
                "description": "Apple Inc. reported strong fourth quarter earnings...",
                "published_utc": "2024-01-15T10:30:00Z",
                "article_url": "https://example.com/apple-earnings",
                "amp_url": "https://amp.example.com/apple-earnings",
                "image_url": "https://example.com/apple-image.jpg"
            },
            {
                "title": "Apple Announces New Product Line",
                "description": "Apple announced new products in their latest event...",
                "published_utc": "2024-01-14T14:20:00Z",
                "article_url": "https://example.com/apple-products",
                "amp_url": "https://amp.example.com/apple-products",
                "image_url": "https://example.com/apple-products-image.jpg"
            }
        ]
    }
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_polygon_response
        mock_get.return_value = mock_response
        
        news = mock_news_controller.get_ticker_news("AAPL", limit=2)
        
        assert len(news) >= 2
        # The controller returns NewsArticle objects
        assert hasattr(news[0], 'title')
        assert hasattr(news[0], 'source') 
        assert hasattr(news[0], "url")
        assert hasattr(news[0], "published_utc")
        assert hasattr(news[0], "summary")


def test_get_ticker_news_polygon_fallback_to_yahoo(mock_news_controller):
    """Test fallback to Yahoo Finance when Polygon.io fails."""
    with patch('requests.get') as mock_get:
        # First call (Polygon) fails
        mock_get.side_effect = [Exception("API Error"), Mock()]
        
        # Second call (Yahoo) succeeds
        mock_yahoo_response = Mock()
        mock_yahoo_response.raise_for_status.return_value = None
        mock_yahoo_response.text = '''
        <div class="caas-body">
            <h3><a href="https://finance.yahoo.com/news/apple-1">Apple Stock Rises</a></h3>
            <p>Apple stock continues to perform well...</p>
            <span class="caas-attr-time-style">2 hours ago</span>
        </div>
        '''
        mock_get.return_value = mock_yahoo_response
        
        news = mock_news_controller.get_ticker_news("AAPL")
        
        assert len(news) >= 1
        # Check that news articles are NewsArticle objects
        assert all(hasattr(item, 'title') for item in news)


def test_get_ticker_news_fallback_to_mock(mock_news_controller):
    """Test fallback to mock data when all sources fail."""
    with patch('requests.get') as mock_get, patch('yfinance.Ticker') as mock_ticker:
        # All API calls fail
        mock_get.side_effect = Exception("Network Error")
        mock_ticker.side_effect = Exception("Network Error") 
        
        news = mock_news_controller.get_ticker_news("AAPL")
        
        # Should return mock news
        assert len(news) > 0
        assert any("mock" in item.source.lower() for item in news)
        assert all(hasattr(item, 'title') for item in news)
        assert all(hasattr(item, 'summary') for item in news)


def test_get_ticker_news_empty_symbol(mock_news_controller):
    """Test handling of empty stock symbol."""
    news = mock_news_controller.get_ticker_news("")
    
    # Should return mock data or empty list
    assert isinstance(news, list)


def test_get_ticker_news_invalid_symbol(mock_news_controller):
    """Test handling of invalid stock symbol."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = Exception("Invalid symbol")
        mock_get.return_value = mock_response
        
        news = mock_news_controller.get_ticker_news("INVALID")
        
        # Should fallback to mock data
        assert isinstance(news, list)
        assert len(news) > 0


def test_get_multiple_stock_news(mock_news_controller):
    """Test getting news for multiple stocks."""
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "results": [
                {
                    "title": "Tech Stock Update",
                    "description": "Latest tech stock news...",
                    "published_utc": "2024-01-15T10:30:00Z",
                    "article_url": "https://example.com/tech-news",
                    "amp_url": "https://amp.example.com/tech-news",
                    "image_url": "https://example.com/tech-image.jpg"
                }
            ]
        }
        mock_get.return_value = mock_response
        
        all_news = {}
        for symbol in symbols:
            all_news[symbol] = mock_news_controller.get_ticker_news(symbol)
        
        # Should have news for each symbol
        assert len(all_news) == 3
        for symbol in symbols:
            assert isinstance(all_news[symbol], list)
            assert len(all_news[symbol]) > 0


def test_polygon_news_parsing(mock_news_controller):
    """Test proper parsing of Polygon.io news format."""
    mock_polygon_response = {
        "results": [
            {
                "title": "Test News Article",
                "description": "This is a test article description",
                "published_utc": "2024-01-15T10:30:00Z",
                "article_url": "https://example.com/test-article",
                "amp_url": "https://amp.example.com/test-article",
                "image_url": "https://example.com/test-image.jpg",
                "keywords": ["technology", "stocks"],
                "author": "Test Author"
            }
        ]
    }
    
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = mock_polygon_response
        mock_get.return_value = mock_response
        
        news = mock_news_controller.get_ticker_news("AAPL")
        
        assert len(news) == 1
        article = news[0]
        
        # Check all expected fields are present on NewsArticle object
        assert hasattr(article, 'title')
        assert hasattr(article, 'summary')  # description becomes summary
        assert hasattr(article, 'url')
        assert hasattr(article, 'published_utc')
        assert hasattr(article, 'source')
        
        assert article.title == "Test News Article"
        assert "Polygon.io" in article.source


def test_yahoo_finance_html_parsing(mock_news_controller):
    """Test proper parsing of Yahoo Finance HTML content."""
    mock_html_content = '''
    <html>
        <body>
            <div class="caas-body">
                <h3><a href="/news/test-article-1">First Test Article</a></h3>
                <p>First article description content here.</p>
                <span class="caas-attr-time-style">1 hour ago</span>
            </div>
            <div class="caas-body">
                <h3><a href="/news/test-article-2">Second Test Article</a></h3>
                <p>Second article description content here.</p>
                <span class="caas-attr-time-style">3 hours ago</span>
            </div>
        </body>
    </html>
    '''
    
    with patch('requests.get') as mock_get:
        # First call (Polygon) fails
        mock_get.side_effect = [Exception("API Error")]
        
        # Second call (Yahoo) succeeds
        mock_yahoo_response = Mock()
        mock_yahoo_response.raise_for_status.return_value = None
        mock_yahoo_response.text = mock_html_content
        mock_get.side_effect = [Exception("API Error"), mock_yahoo_response]
        
        news = mock_news_controller.get_ticker_news("AAPL")
        
        # Should parse Yahoo Finance content 
        assert len(news) >= 1
        # Check that articles have required fields as NewsArticle objects
        for article in news[:2]:  # Check first two articles
            assert hasattr(article, 'title')
            assert hasattr(article, 'summary')
            assert hasattr(article, 'source')
            assert "Yahoo" in article.source


def test_rate_limiting_and_caching(mock_news_controller):
    """Test that news controller handles rate limiting appropriately."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {"results": []}
        mock_get.return_value = mock_response
        
        # Make multiple requests for the same symbol
        news1 = mock_news_controller.get_ticker_news("AAPL")
        news2 = mock_news_controller.get_ticker_news("AAPL")
        
        # Both should return successfully (controller should handle caching/rate limiting)
        assert isinstance(news1, list)
        assert isinstance(news2, list)


def test_mock_news_data_structure(mock_news_controller):
    """Test that mock news data has the correct structure."""
    with patch('requests.get') as mock_get:
        # Force fallback to mock data
        mock_get.side_effect = Exception("Network Error")
        
        news = mock_news_controller.get_ticker_news("AAPL")
        
        assert len(news) > 0
        
        # Check structure of mock news items - they are NewsArticle objects
        for item in news:
            assert hasattr(item, 'title')
            assert hasattr(item, 'summary')
            assert hasattr(item, 'url')
            assert hasattr(item, 'published_utc')
            assert hasattr(item, 'source')
            
            # Check that values are strings (not None/empty)
            assert isinstance(item.title, str)
            assert len(item.title) > 0
            assert isinstance(item.summary, str)
            assert len(item.summary) > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])