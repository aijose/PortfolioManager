#!/usr/bin/env python3
"""Test script for news integration using yfinance."""

import os
import sys
from datetime import datetime

# Add current directory to Python path
sys.path.append('.')

try:
    print("🔧 Environment Setup:")
    print("✅ Using yfinance for news - no API key required")
        
    # Test database connection
    print("\n📁 Database Test:")
    from models.database import get_db, create_tables
    from models.portfolio import WatchedItem, Watchlist
    
    create_tables()
    print("✅ Database tables created/verified")
    
    # Test if we have any watchlists
    db = next(get_db())
    try:
        watchlists = db.query(Watchlist).all()
        watched_items = db.query(WatchedItem).all()
        print(f"✅ Found {len(watchlists)} watchlists, {len(watched_items)} watched items")
        
        if watched_items:
            for item in watched_items[:3]:  # Show first 3
                print(f"  - {item.symbol}: news_data={item.news_data is not None}, last_update={item.last_news_update}")
    finally:
        db.close()
    
    # Test NewsController
    print("\n📰 News Controller Test:")
    from controllers.news_controller import NewsController
    
    news_controller = NewsController()
    print("✅ yfinance-based news controller initialized")
    
    # Test with a few symbols
    test_symbols = ['AAPL', 'MSFT', 'GOOGL']
    
    for symbol in test_symbols:
        print(f"\n🔍 Testing {symbol}:")
        try:
            articles = news_controller.get_ticker_news(symbol, limit=2)
            if articles:
                print(f"  ✅ Found {len(articles)} articles:")
                for i, article in enumerate(articles, 1):
                    print(f"    {i}. {article.title[:50]}...")
                    print(f"       Source: {article.source}")
            else:
                print(f"  ⚠️  No articles found for {symbol}")
        except Exception as e:
            print(f"  ❌ Error testing {symbol}: {e}")
    
    print("\n🎯 News integration test complete!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()