#!/usr/bin/env python3
"""Test script for news API integration without server."""

import sys
import json
from datetime import datetime

# Add current directory to Python path  
sys.path.append('.')

try:
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    print("🧪 Testing News API Integration")
    print("=" * 50)
    
    # Test database setup
    from models.database import get_db
    from models.portfolio import WatchedItem, Watchlist
    
    db = next(get_db())
    try:
        # Find a watched item to test with
        watched_item = db.query(WatchedItem).first()
        if not watched_item:
            print("❌ No watched items found. Please add a stock to a watchlist first.")
            exit(1)
            
        print(f"🎯 Testing with symbol: {watched_item.symbol}")
        print(f"   Watchlist ID: {watched_item.watchlist_id}")
        
        # Test the news route logic directly
        from controllers.news_controller import NewsController
        from web_server.routes.watchlists import get_item_news
        
        news_controller = NewsController()
        print(f"\n📰 NewsController Status:")
        print(f"   Client initialized: {news_controller.client is not None}")
        print(f"   Cache duration: {news_controller.cache_duration}")
        print(f"   Max articles: {news_controller.max_articles_per_symbol}")
        
        # Test cache logic
        print(f"\n⏰ Cache Test:")
        is_valid = news_controller.is_news_cache_valid(watched_item.last_news_update)
        print(f"   Current cache valid: {is_valid}")
        print(f"   Last update: {watched_item.last_news_update}")
        print(f"   News data exists: {watched_item.news_data is not None}")
        
        # Test news data formatting
        print(f"\n🔧 Testing Data Formatting:")
        
        # Create mock articles for testing
        from controllers.news_controller import NewsArticle
        mock_articles = [
            NewsArticle(
                title="Apple Reports Strong Q4 Earnings",
                url="https://example.com/news/1",
                published_utc="2025-01-06T14:30:00Z",
                source="Reuters",
                summary="Apple posted better-than-expected quarterly results..."
            ),
            NewsArticle(
                title="AAPL Stock Analysis",
                url="https://example.com/news/2", 
                published_utc="2025-01-06T13:15:00Z",
                source="MarketWatch",
                summary="Technical analysis shows bullish patterns..."
            )
        ]
        
        # Test formatting
        formatted_data = news_controller.format_news_for_storage(mock_articles)
        print(f"   Formatted data keys: {list(formatted_data.keys())}")
        print(f"   Articles count: {len(formatted_data['articles'])}")
        print(f"   First article title: {formatted_data['articles'][0]['title']}")
        
        # Test parsing back
        parsed_articles = news_controller.parse_stored_news(formatted_data)
        print(f"   Parsed back: {len(parsed_articles)} articles")
        
        # Update the database with mock data for testing
        watched_item.news_data = formatted_data
        watched_item.last_news_update = datetime.utcnow()
        db.commit()
        print(f"   ✅ Updated database with mock news data")
        
        print(f"\n📊 Final Database State:")
        print(f"   Symbol: {watched_item.symbol}")
        print(f"   Has news data: {watched_item.news_data is not None}")
        print(f"   Last update: {watched_item.last_news_update}")
        if watched_item.news_data:
            print(f"   Cached articles: {len(watched_item.news_data['articles'])}")
        
    finally:
        db.close()
        
    print(f"\n✅ All tests completed successfully!")
    print(f"\n🔗 Next Steps:")
    print(f"   1. Start the server: uv run uvicorn web_server.app:app --reload")
    print(f"   2. Visit: http://localhost:8000/watchlists")
    print(f"   3. Click the 'News' button next to {watched_item.symbol}")
    print(f"   4. The first click will show cached data (since we just added mock data)")
    print(f"   5. Real API calls will happen when cache expires (4 hours)")

except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()