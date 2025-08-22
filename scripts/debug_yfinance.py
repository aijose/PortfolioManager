#!/usr/bin/env python3
"""Debug script to test yfinance news extraction."""

import sys
sys.path.append('.')

try:
    import yfinance as yf
    import json
    from datetime import datetime
    
    # Test symbols
    symbols = ['SOFI', 'AAPL', 'MSFT']
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"🔍 DEBUGGING {symbol}")
        print(f"{'='*60}")
        
        try:
            ticker = yf.Ticker(symbol)
            print(f"✅ Created ticker object for {symbol}")
            
            # Get news data
            news_data = ticker.news
            print(f"📰 News data type: {type(news_data)}")
            print(f"📰 News data length: {len(news_data) if news_data else 0}")
            
            if news_data:
                print(f"📰 First item type: {type(news_data[0])}")
                print(f"📰 First item keys: {list(news_data[0].keys()) if isinstance(news_data[0], dict) else 'Not a dict'}")
                
                # Print first item structure
                print(f"\n🔎 FIRST NEWS ITEM STRUCTURE:")
                first_item = news_data[0]
                if isinstance(first_item, dict):
                    for key, value in first_item.items():
                        print(f"  {key}: {type(value)} = {str(value)[:100]}...")
                else:
                    print(f"  {first_item}")
                
                print(f"\n📋 PROCESSING TEST:")
                # Test our parsing logic
                for i, item in enumerate(news_data[:2]):
                    print(f"\n  Article {i+1}:")
                    if isinstance(item, dict):
                        title = item.get('title', 'NO TITLE KEY')
                        link = item.get('link', 'NO LINK KEY')
                        publisher = item.get('publisher', 'NO PUBLISHER KEY')
                        pub_time = item.get('providerPublishTime', 'NO TIME KEY')
                        
                        print(f"    Title: {title}")
                        print(f"    Link: {link}")
                        print(f"    Publisher: {publisher}")
                        print(f"    Pub Time: {pub_time}")
                        
                        if pub_time and isinstance(pub_time, (int, float)):
                            formatted_time = datetime.fromtimestamp(pub_time).isoformat() + 'Z'
                            print(f"    Formatted Time: {formatted_time}")
                    else:
                        print(f"    Not a dict: {type(item)}")
            else:
                print(f"❌ No news data returned for {symbol}")
                
        except Exception as e:
            print(f"❌ Error with {symbol}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\n{'='*60}")
    print("🎯 Debug complete!")
    
except ImportError:
    print("❌ yfinance not available")
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    import traceback
    traceback.print_exc()