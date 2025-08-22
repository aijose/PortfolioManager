"""Unit tests for WatchlistController."""

import pytest
from datetime import datetime
from controllers.watchlist_controller import (
    WatchlistController,
    WatchlistCreate,
    WatchlistUpdate,
    WatchedItemCreate,
    WatchedItemUpdate
)
from models.portfolio import Watchlist, WatchedItem


def test_create_watchlist_success(client, test_db):
    """Test successful watchlist creation."""
    from tests.conftest import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist_data = WatchlistCreate(name="Tech Stocks")
        
        watchlist = controller.create_watchlist(watchlist_data)
        
        assert watchlist is not None
        assert watchlist.name == "Tech Stocks"
        assert watchlist.id is not None
        assert isinstance(watchlist.created_date, datetime)
        assert isinstance(watchlist.modified_date, datetime)
    finally:
        db.close()


def test_create_watchlist_duplicate_name(client, test_db):
    """Test creating watchlist with duplicate name raises error."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist_data = WatchlistCreate(name="Tech Stocks")
        
        # Create first watchlist
        controller.create_watchlist(watchlist_data)
        
        # Try to create duplicate
        with pytest.raises(ValueError, match="already exists"):
            controller.create_watchlist(watchlist_data)
    finally:
        db.close()


def test_create_watchlist_empty_name(client, test_db):
    """Test creating watchlist with empty name raises error."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        
        with pytest.raises(ValueError, match="cannot be empty"):
            WatchlistCreate(name="")
    finally:
        db.close()


def test_get_watchlists_empty(client, test_db):
    """Test getting watchlists when none exist."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlists = controller.get_watchlists()
        
        assert watchlists == []
    finally:
        db.close()


def test_get_watchlists_with_data(client, test_db):
    """Test getting watchlists when data exists."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        
        # Create test watchlists
        watchlist1 = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        watchlist2 = controller.create_watchlist(WatchlistCreate(name="Blue Chips"))
        
        watchlists = controller.get_watchlists()
        
        assert len(watchlists) == 2
        # Should be ordered by name
        assert watchlists[0].name == "Blue Chips"
        assert watchlists[1].name == "Tech Stocks"
    finally:
        db.close()


def test_get_watchlist_by_id(client, test_db):
    """Test getting specific watchlist by ID."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        created_watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        retrieved_watchlist = controller.get_watchlist(created_watchlist.id)
        
        assert retrieved_watchlist is not None
        assert retrieved_watchlist.name == "Tech Stocks"
        assert retrieved_watchlist.id == created_watchlist.id
    finally:
        db.close()


def test_get_nonexistent_watchlist(client, test_db):
    """Test getting non-existent watchlist returns None."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.get_watchlist(999)
        
        assert watchlist is None
    finally:
        db.close()


def test_update_watchlist(client, test_db):
    """Test updating watchlist name."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        original_modified = watchlist.modified_date
        
        # Small delay to ensure modified date changes
        import time
        time.sleep(0.1)
        
        update_data = WatchlistUpdate(name="Technology Stocks")
        updated_watchlist = controller.update_watchlist(watchlist.id, update_data)
        
        assert updated_watchlist is not None
        assert updated_watchlist.name == "Technology Stocks"
        assert updated_watchlist.modified_date > original_modified
    finally:
        db.close()


def test_delete_watchlist(client, test_db):
    """Test deleting a watchlist."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        result = controller.delete_watchlist(watchlist.id)
        assert result is True
        
        # Verify it's deleted
        deleted_watchlist = controller.get_watchlist(watchlist.id)
        assert deleted_watchlist is None
    finally:
        db.close()


def test_delete_nonexistent_watchlist(client, test_db):
    """Test deleting non-existent watchlist returns False."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        result = controller.delete_watchlist(999)
        
        assert result is False
    finally:
        db.close()


def test_add_watched_item(client, test_db):
    """Test adding watched item to watchlist."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        item_data = WatchedItemCreate(symbol="AAPL", notes="Apple Inc - Strong fundamentals")
        watched_item = controller.add_watched_item(watchlist.id, item_data)
        
        assert watched_item is not None
        assert watched_item.symbol == "AAPL"
        assert watched_item.notes == "Apple Inc - Strong fundamentals"
        assert watched_item.watchlist_id == watchlist.id
    finally:
        db.close()


def test_add_duplicate_watched_item(client, test_db):
    """Test adding duplicate watched item raises error."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        item_data = WatchedItemCreate(symbol="AAPL")
        controller.add_watched_item(watchlist.id, item_data)
        
        # Try to add duplicate
        with pytest.raises(ValueError, match="already in this watchlist"):
            controller.add_watched_item(watchlist.id, item_data)
    finally:
        db.close()


def test_get_watchlist_items(client, test_db):
    """Test getting watched items for a watchlist."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        # Add multiple items
        controller.add_watched_item(watchlist.id, WatchedItemCreate(symbol="AAPL"))
        controller.add_watched_item(watchlist.id, WatchedItemCreate(symbol="GOOGL"))
        controller.add_watched_item(watchlist.id, WatchedItemCreate(symbol="MSFT"))
        
        items = controller.get_watchlist_items(watchlist.id)
        
        assert len(items) == 3
        symbols = [item.symbol for item in items]
        assert "AAPL" in symbols
        assert "GOOGL" in symbols
        assert "MSFT" in symbols
    finally:
        db.close()


def test_update_watched_item(client, test_db):
    """Test updating watched item notes."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        item = controller.add_watched_item(watchlist.id, WatchedItemCreate(symbol="AAPL", notes="Original notes"))
        
        update_data = WatchedItemUpdate(notes="Updated notes about Apple")
        updated_item = controller.update_watched_item(watchlist.id, "AAPL", update_data)
        
        assert updated_item is not None
        assert updated_item.notes == "Updated notes about Apple"
    finally:
        db.close()


def test_delete_watched_item(client, test_db):
    """Test deleting watched item from watchlist."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        controller.add_watched_item(watchlist.id, WatchedItemCreate(symbol="AAPL"))
        
        result = controller.delete_watched_item(watchlist.id, "AAPL")
        assert result is True
        
        # Verify it's deleted
        items = controller.get_watchlist_items(watchlist.id)
        assert len(items) == 0
    finally:
        db.close()


def test_get_watchlist_summary(client, test_db):
    """Test getting watchlist summary statistics."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = WatchlistController(db)
        watchlist = controller.create_watchlist(WatchlistCreate(name="Tech Stocks"))
        
        # Add items
        controller.add_watched_item(watchlist.id, WatchedItemCreate(symbol="AAPL"))
        controller.add_watched_item(watchlist.id, WatchedItemCreate(symbol="GOOGL"))
        
        summary = controller.get_watchlist_summary(watchlist.id)
        
        assert summary["total_items"] == 2
        assert "items_with_prices" in summary
        assert "price_coverage" in summary
        assert summary["items_with_prices"] >= 0  # Prices might be fetched from real APIs
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])