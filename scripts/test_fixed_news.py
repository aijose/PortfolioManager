#!/usr/bin/env python3
"""Test the fixed yfinance news controller."""

import sys
sys.path.append('.')

try:
    from controllers.news_controller import NewsController
    
    controller = NewsController()
    
    # Test symbols including SOFI
    test_symbols = ['SOFI', 'AAPL', 'MSFT', 'GOOGL']
    
    for symbol in test_symbols:
        print(f"\n{'='*60}")
        print(f"📰 TESTING {symbol}")
        print(f"{'='*60}")
        
        try:
            articles = controller.get_ticker_news(symbol, limit=3)
            
            if articles:
                print(f"✅ Got {len(articles)} articles:")
                for i, article in enumerate(articles, 1):
                    print(f"\n  📄 Article {i}:")
                    print(f"    Title: {article.title}")
                    print(f"    Source: {article.source}")
                    print(f"    URL: {article.url}")
                    print(f"    Published: {article.published_utc}")
                    if article.summary:
                        print(f"    Summary: {article.summary[:100]}...")
                    else:
                        print(f"    Summary: None")
            else:
                print(f"❌ No articles found for {symbol}")
                
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🎯 News extraction test complete!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()