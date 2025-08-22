#!/usr/bin/env python3
"""Debug script to examine yfinance content structure."""

import sys
sys.path.append('.')

try:
    import yfinance as yf
    import json
    from datetime import datetime
    
    # Test with SOFI
    symbol = 'SOFI'
    print(f"🔍 DETAILED CONTENT ANALYSIS FOR {symbol}")
    print("="*60)
    
    ticker = yf.Ticker(symbol)
    news_data = ticker.news
    
    if news_data and len(news_data) > 0:
        first_item = news_data[0]
        print(f"📰 Full first item structure:")
        print(json.dumps(first_item, indent=2, default=str))
        
        if 'content' in first_item:
            content = first_item['content']
            print(f"\n📋 CONTENT KEYS: {list(content.keys())}")
            
            # Test extraction
            print(f"\n🎯 EXTRACTING DATA:")
            title = content.get('title', 'No title')
            print(f"Title: {title}")
            
            # Check for URL variations
            url_keys = ['canonicalUrl', 'url', 'link']
            for key in url_keys:
                if key in content:
                    print(f"{key}: {content[key]}")
            
            # Check for timestamp variations  
            time_keys = ['pubDate', 'providerPublishTime', 'publishedDate', 'timestamp']
            for key in time_keys:
                if key in content:
                    print(f"{key}: {content[key]} (type: {type(content[key])})")
            
            # Check for source/publisher
            publisher_keys = ['provider', 'publisher', 'source']
            for key in publisher_keys:
                if key in content:
                    print(f"{key}: {content[key]} (type: {type(content[key])})")
            
            # Check for summary
            summary_keys = ['summary', 'description', 'excerpt']
            for key in summary_keys:
                if key in content:
                    print(f"{key}: {str(content[key])[:100]}...")
                    
    else:
        print("❌ No news data available")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()