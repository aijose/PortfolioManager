#!/usr/bin/env python3
"""Check SOFI data in the database."""

import sys
sys.path.append('.')

from models.database import get_db
from models.portfolio import WatchedItem, Watchlist
from datetime import datetime

try:
    db = next(get_db())
    
    # Find SOFI in watchlists
    sofi_items = db.query(WatchedItem).filter(WatchedItem.symbol == 'SOFI').all()
    
    print(f"🔍 Found {len(sofi_items)} SOFI entries in database:")
    
    for item in sofi_items:
        print(f"\n📊 SOFI in Watchlist {item.watchlist_id}:")
        print(f"   Symbol: {item.symbol}")
        print(f"   Last Price: {item.last_price}")
        print(f"   Has News Data: {item.news_data is not None}")
        if item.news_data:
            print(f"   News Articles Count: {len(item.news_data.get('articles', []))}")
        print(f"   Last News Update: {item.last_news_update}")
        print(f"   Added Date: {item.added_date}")
        
        # Show sample news data if available
        if item.news_data and 'articles' in item.news_data:
            articles = item.news_data['articles'][:2]  # First 2 articles
            for i, article in enumerate(articles, 1):
                print(f"   Article {i}: {article.get('title', 'No title')[:50]}...")
    
    if not sofi_items:
        print("❌ No SOFI entries found in database")
        print("   You might need to add SOFI to a watchlist first")
    
    db.close()

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()