"""Watchlist-related API routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from models.database import get_db
from controllers.watchlist_controller import (
    WatchlistController, 
    WatchedItemCreate, 
    WatchedItemUpdate,
    WatchlistCreate,
    WatchlistUpdate
)
from controllers.news_controller import NewsController
from models.portfolio import WatchedItem

router = APIRouter(prefix="/api/watchlists", tags=["watchlists"])


@router.get("/", response_model=List[dict])
async def list_watchlists(db: Session = Depends(get_db)):
    """Get all watchlists."""
    controller = WatchlistController(db)
    watchlists = controller.get_watchlists()
    
    return [
        {
            "id": w.id,
            "name": w.name,
            "created_date": w.created_date.isoformat(),
            "modified_date": w.modified_date.isoformat(),
            "items_count": len(w.watched_items)
        }
        for w in watchlists
    ]


@router.get("/{watchlist_id}", response_model=dict)
async def get_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    """Get a specific watchlist."""
    controller = WatchlistController(db)
    watchlist = controller.get_watchlist(watchlist_id)
    
    if not watchlist:
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    summary = controller.get_watchlist_summary(watchlist_id)
    
    return {
        "id": watchlist.id,
        "name": watchlist.name,
        "created_date": watchlist.created_date.isoformat(),
        "modified_date": watchlist.modified_date.isoformat(),
        "summary": summary
    }


@router.post("/", response_model=dict)
async def create_watchlist(watchlist: WatchlistCreate, db: Session = Depends(get_db)):
    """Create a new watchlist."""
    controller = WatchlistController(db)
    
    try:
        new_watchlist = controller.create_watchlist(watchlist)
        return {
            "id": new_watchlist.id,
            "name": new_watchlist.name,
            "created_date": new_watchlist.created_date.isoformat(),
            "message": "Watchlist created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{watchlist_id}", response_model=dict)
async def update_watchlist(
    watchlist_id: int, 
    watchlist: WatchlistUpdate, 
    db: Session = Depends(get_db)
):
    """Update a watchlist."""
    controller = WatchlistController(db)
    
    try:
        updated_watchlist = controller.update_watchlist(watchlist_id, watchlist)
        if not updated_watchlist:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        return {
            "id": updated_watchlist.id,
            "name": updated_watchlist.name,
            "modified_date": updated_watchlist.modified_date.isoformat(),
            "message": "Watchlist updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{watchlist_id}")
async def delete_watchlist(watchlist_id: int, db: Session = Depends(get_db)):
    """Delete a watchlist."""
    controller = WatchlistController(db)
    
    if not controller.delete_watchlist(watchlist_id):
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    return {"message": "Watchlist deleted successfully"}


# Watched Items endpoints
@router.get("/{watchlist_id}/items", response_model=List[dict])
async def get_watched_items(watchlist_id: int, db: Session = Depends(get_db)):
    """Get all watched items for a watchlist."""
    controller = WatchlistController(db)
    
    if not controller.get_watchlist(watchlist_id):
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    items = controller.get_watchlist_items_with_details(watchlist_id)
    return items


@router.post("/{watchlist_id}/items", response_model=dict)
async def create_watched_item(
    watchlist_id: int, 
    watched_item: WatchedItemCreate, 
    db: Session = Depends(get_db)
):
    """Add a watched item to a watchlist."""
    controller = WatchlistController(db)
    
    try:
        new_watched_item = controller.add_watched_item(watchlist_id, watched_item)
        if not new_watched_item:
            raise HTTPException(status_code=404, detail="Watchlist not found")
        
        return {
            "symbol": new_watched_item.symbol,
            "notes": new_watched_item.notes,
            "added_date": new_watched_item.added_date.isoformat(),
            "message": "Stock added to watchlist successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{watchlist_id}/items/{symbol}", response_model=dict)
async def update_watched_item(
    watchlist_id: int, 
    symbol: str, 
    watched_item: WatchedItemUpdate, 
    db: Session = Depends(get_db)
):
    """Update a watched item."""
    controller = WatchlistController(db)
    
    try:
        updated_watched_item = controller.update_watched_item(watchlist_id, symbol, watched_item)
        if not updated_watched_item:
            raise HTTPException(status_code=404, detail="Watched item not found")
        
        return {
            "symbol": updated_watched_item.symbol,
            "notes": updated_watched_item.notes,
            "message": "Watched item updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{watchlist_id}/items/{symbol}")
async def delete_watched_item(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Delete a watched item."""
    controller = WatchlistController(db)
    
    if not controller.delete_watched_item(watchlist_id, symbol):
        raise HTTPException(status_code=404, detail="Watched item not found")
    
    return {"message": "Stock removed from watchlist successfully"}


# Price update endpoints
@router.post("/{watchlist_id}/refresh-prices")
async def refresh_watchlist_prices(watchlist_id: int, db: Session = Depends(get_db)):
    """Refresh prices for all items in a watchlist."""
    controller = WatchlistController(db)
    
    if not controller.get_watchlist(watchlist_id):
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    result = controller.refresh_watchlist_prices(watchlist_id)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to refresh prices"))
    
    return result


@router.post("/{watchlist_id}/items/{symbol}/refresh-price")
async def refresh_single_item_price(
    watchlist_id: int, 
    symbol: str, 
    db: Session = Depends(get_db)
):
    """Refresh price for a single watched item."""
    controller = WatchlistController(db)
    
    result = controller.update_single_item_price(watchlist_id, symbol)
    
    if not result["success"]:
        if "not found" in result["error"]:
            raise HTTPException(status_code=404, detail=result["error"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    
    return result


# Validation endpoints
@router.get("/{watchlist_id}/validate-symbols")
async def validate_watchlist_symbols(watchlist_id: int, db: Session = Depends(get_db)):
    """Validate all stock symbols in a watchlist."""
    controller = WatchlistController(db)
    
    if not controller.get_watchlist(watchlist_id):
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    validation_result = controller.validate_watchlist_symbols(watchlist_id)
    return validation_result


# Bulk operations
@router.post("/{watchlist_id}/bulk-add")
async def bulk_add_items(
    watchlist_id: int,
    symbols: List[str],
    db: Session = Depends(get_db)
):
    """Add multiple symbols to a watchlist at once with automatic price fetching."""
    controller = WatchlistController(db)
    
    if not controller.get_watchlist(watchlist_id):
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    added_count = 0
    errors = []
    
    for symbol in symbols:
        try:
            symbol = symbol.strip().upper()
            if not symbol:
                continue
                
            watched_item = WatchedItemCreate(symbol=symbol)
            result = controller.add_watched_item(watchlist_id, watched_item)
            if result:
                added_count += 1
        except ValueError as e:
            errors.append(f"{symbol}: {str(e)}")
        except Exception as e:
            errors.append(f"{symbol}: Unexpected error - {str(e)}")
    
    # If items were added successfully, refresh prices for the watchlist
    if added_count > 0:
        try:
            controller.refresh_watchlist_prices(watchlist_id)
        except Exception as e:
            # Don't fail the whole operation if price refresh fails
            pass
    
    return {
        "added_count": added_count,
        "total_requested": len(symbols),
        "errors": errors,
        "success": len(errors) == 0,
        "message": f"Added {added_count} out of {len(symbols)} symbols to watchlist with price fetching"
    }


@router.delete("/{watchlist_id}/bulk-remove")
async def bulk_remove_items(
    watchlist_id: int,
    symbols: List[str],
    db: Session = Depends(get_db)
):
    """Remove multiple symbols from a watchlist at once."""
    controller = WatchlistController(db)
    
    if not controller.get_watchlist(watchlist_id):
        raise HTTPException(status_code=404, detail="Watchlist not found")
    
    removed_count = 0
    errors = []
    
    for symbol in symbols:
        try:
            symbol = symbol.strip().upper()
            if not symbol:
                continue
                
            if controller.delete_watched_item(watchlist_id, symbol):
                removed_count += 1
            else:
                errors.append(f"{symbol}: Not found in watchlist")
        except Exception as e:
            errors.append(f"{symbol}: Unexpected error - {str(e)}")
    
    return {
        "removed_count": removed_count,
        "total_requested": len(symbols),
        "errors": errors,
        "success": len(errors) == 0,
        "message": f"Removed {removed_count} out of {len(symbols)} symbols from watchlist"
    }


# News endpoints
@router.get("/{watchlist_id}/items/{symbol}/news")
async def get_item_news(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Get news for a specific watched item."""
    watchlist_controller = WatchlistController(db)
    news_controller = NewsController()
    
    # Find the watched item
    watched_item = db.query(WatchedItem).filter(
        WatchedItem.watchlist_id == watchlist_id,
        WatchedItem.symbol == symbol
    ).first()
    
    if not watched_item:
        raise HTTPException(status_code=404, detail="Watched item not found")
    
    # Get cached or fresh news
    articles, was_fetched = news_controller.get_cached_or_fresh_news(
        symbol, 
        watched_item.last_news_update, 
        watched_item.news_data
    )
    
    # Update cache if we fetched fresh news
    if was_fetched and articles:
        watched_item.news_data = news_controller.format_news_for_storage(articles)
        watched_item.last_news_update = datetime.utcnow()
        db.commit()
    
    return {
        "symbol": symbol,
        "articles": [article.to_dict() for article in articles],
        "cached": not was_fetched,
        "last_updated": watched_item.last_news_update.isoformat() if watched_item.last_news_update else None,
        "count": len(articles)
    }


@router.post("/{watchlist_id}/items/{symbol}/refresh-news")
async def refresh_item_news(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Force refresh news for a specific watched item."""
    watchlist_controller = WatchlistController(db)
    news_controller = NewsController()
    
    # Find the watched item
    watched_item = db.query(WatchedItem).filter(
        WatchedItem.watchlist_id == watchlist_id,
        WatchedItem.symbol == symbol
    ).first()
    
    if not watched_item:
        raise HTTPException(status_code=404, detail="Watched item not found")
    
    # Force fetch fresh news
    articles = news_controller.get_ticker_news(symbol)
    
    # Update cache
    if articles:
        watched_item.news_data = news_controller.format_news_for_storage(articles)
        watched_item.last_news_update = datetime.utcnow()
        db.commit()
        
        return {
            "symbol": symbol,
            "articles": [article.to_dict() for article in articles],
            "updated": True,
            "last_updated": watched_item.last_news_update.isoformat(),
            "count": len(articles),
            "message": f"Refreshed {len(articles)} news articles for {symbol}"
        }
    else:
        return {
            "symbol": symbol,
            "articles": [],
            "updated": False,
            "error": "No news found or API error",
            "count": 0
        }


# Debug endpoint to test connectivity
@router.get("/{watchlist_id}/items/{symbol}/test-news")
async def test_news_endpoint(watchlist_id: int, symbol: str, db: Session = Depends(get_db)):
    """Simple test endpoint to verify connectivity and data."""
    # Find the watched item
    watched_item = db.query(WatchedItem).filter(
        WatchedItem.watchlist_id == watchlist_id,
        WatchedItem.symbol == symbol
    ).first()
    
    if not watched_item:
        return {"error": "Watched item not found", "symbol": symbol, "watchlist_id": watchlist_id}
    
    # Return basic info and mock news
    mock_articles = [
        {
            "title": f"Test News for {symbol}",
            "url": "https://example.com/test",
            "published_utc": "2025-01-06T15:00:00Z",
            "source": "Test Source",
            "summary": "This is a test article to verify the news system is working."
        }
    ]
    
    return {
        "symbol": symbol,
        "watchlist_id": watchlist_id,
        "articles": mock_articles,
        "cached": True,
        "count": len(mock_articles),
        "has_news_data": watched_item.news_data is not None,
        "last_news_update": watched_item.last_news_update.isoformat() if watched_item.last_news_update else None,
        "test": True
    }