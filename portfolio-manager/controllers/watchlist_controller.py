"""Watchlist business logic and CRUD operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from models.portfolio import Watchlist, WatchedItem
from pydantic import BaseModel, validator
from controllers.stock_data_controller import StockDataController


class WatchlistCreate(BaseModel):
    """Schema for creating a new watchlist."""
    name: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Watchlist name cannot be empty')
        return v.strip()


class WatchlistUpdate(BaseModel):
    """Schema for updating a watchlist."""
    name: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Watchlist name cannot be empty')
        return v.strip()


class WatchedItemCreate(BaseModel):
    """Schema for creating a new watched item."""
    symbol: str
    notes: Optional[str] = None
    
    @validator('symbol')
    def symbol_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Symbol cannot be empty')
        return v.strip().upper()
    
    @validator('notes')
    def notes_length_check(cls, v):
        if v and len(v) > 500:
            raise ValueError('Notes cannot exceed 500 characters')
        return v


class WatchedItemUpdate(BaseModel):
    """Schema for updating a watched item."""
    notes: Optional[str] = None
    
    @validator('notes')
    def notes_length_check(cls, v):
        if v and len(v) > 500:
            raise ValueError('Notes cannot exceed 500 characters')
        return v


class WatchlistController:
    """Controller for watchlist operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.stock_data_controller = StockDataController()
    
    def get_watchlists(self) -> List[Watchlist]:
        """Get all watchlists."""
        return self.db.query(Watchlist).order_by(Watchlist.name).all()
    
    def get_watchlist(self, watchlist_id: int) -> Optional[Watchlist]:
        """Get a specific watchlist by ID."""
        return self.db.query(Watchlist).filter(Watchlist.id == watchlist_id).first()
    
    def get_watchlist_by_name(self, name: str) -> Optional[Watchlist]:
        """Get a watchlist by name."""
        return self.db.query(Watchlist).filter(Watchlist.name == name).first()
    
    def create_watchlist(self, watchlist: WatchlistCreate) -> Watchlist:
        """Create a new watchlist."""
        # Check if watchlist with same name already exists
        existing = self.get_watchlist_by_name(watchlist.name)
        if existing:
            raise ValueError(f"Watchlist with name '{watchlist.name}' already exists")
        
        db_watchlist = Watchlist(name=watchlist.name)
        self.db.add(db_watchlist)
        self.db.commit()
        self.db.refresh(db_watchlist)
        return db_watchlist
    
    def update_watchlist(self, watchlist_id: int, watchlist: WatchlistUpdate) -> Optional[Watchlist]:
        """Update an existing watchlist."""
        db_watchlist = self.get_watchlist(watchlist_id)
        if not db_watchlist:
            return None
        
        # Check if new name conflicts with existing watchlist (excluding current one)
        existing = self.db.query(Watchlist).filter(
            Watchlist.name == watchlist.name,
            Watchlist.id != watchlist_id
        ).first()
        if existing:
            raise ValueError(f"Watchlist with name '{watchlist.name}' already exists")
        
        db_watchlist.name = watchlist.name
        self.db.commit()
        self.db.refresh(db_watchlist)
        return db_watchlist
    
    def delete_watchlist(self, watchlist_id: int) -> bool:
        """Delete a watchlist and all its watched items."""
        db_watchlist = self.get_watchlist(watchlist_id)
        if not db_watchlist:
            return False
        
        self.db.delete(db_watchlist)
        self.db.commit()
        return True
    
    def add_watched_item(self, watchlist_id: int, watched_item: WatchedItemCreate) -> Optional[WatchedItem]:
        """Add a watched item to a watchlist and fetch its current price."""
        watchlist = self.get_watchlist(watchlist_id)
        if not watchlist:
            return None
        
        # Check if watched item with same symbol already exists in this watchlist
        existing = self.db.query(WatchedItem).filter(
            WatchedItem.watchlist_id == watchlist_id,
            WatchedItem.symbol == watched_item.symbol
        ).first()
        if existing:
            raise ValueError(f"Stock {watched_item.symbol} is already in this watchlist")
        
        # Try to fetch current price when adding the item
        price_data = self.stock_data_controller.get_stock_price(watched_item.symbol, use_cache=True)
        current_price = price_data.price if price_data else None
        
        # Set order_index to the next available position
        max_order = self.db.query(WatchedItem).filter(
            WatchedItem.watchlist_id == watchlist_id
        ).count()
        
        db_watched_item = WatchedItem(
            watchlist_id=watchlist_id,
            symbol=watched_item.symbol,
            notes=watched_item.notes,
            last_price=current_price,
            order_index=max_order
        )
        self.db.add(db_watched_item)
        self.db.commit()
        self.db.refresh(db_watched_item)
        return db_watched_item
    
    def get_watchlist_items(self, watchlist_id: int) -> List[WatchedItem]:
        """Get all watched items for a watchlist, ordered by order_index."""
        return self.db.query(WatchedItem).filter(
            WatchedItem.watchlist_id == watchlist_id
        ).order_by(WatchedItem.order_index, WatchedItem.symbol).all()
    
    def update_watched_item(self, watchlist_id: int, symbol: str, watched_item: WatchedItemUpdate) -> Optional[WatchedItem]:
        """Update an existing watched item."""
        db_watched_item = self.db.query(WatchedItem).filter(
            WatchedItem.watchlist_id == watchlist_id,
            WatchedItem.symbol == symbol
        ).first()
        
        if not db_watched_item:
            return None
        
        db_watched_item.notes = watched_item.notes
        self.db.commit()
        self.db.refresh(db_watched_item)
        return db_watched_item
    
    def delete_watched_item(self, watchlist_id: int, symbol: str) -> bool:
        """Delete a watched item from a watchlist."""
        db_watched_item = self.db.query(WatchedItem).filter(
            WatchedItem.watchlist_id == watchlist_id,
            WatchedItem.symbol == symbol
        ).first()
        
        if not db_watched_item:
            return False
        
        self.db.delete(db_watched_item)
        self.db.commit()
        return True
    
    def refresh_watchlist_prices(self, watchlist_id: int) -> dict:
        """
        Refresh stock prices for all watched items in a watchlist.
        
        Returns:
            Dictionary with update results and statistics
        """
        watched_items = self.get_watchlist_items(watchlist_id)
        if not watched_items:
            return {
                "success": True,
                "updated_count": 0,
                "failed_count": 0,
                "total_count": 0,
                "errors": [],
                "message": "No items to update"
            }
        
        # Get symbols to update
        symbols = [item.symbol for item in watched_items]
        
        # Fetch prices
        price_results = self.stock_data_controller.refresh_portfolio_prices(symbols)
        
        # Update database with new prices
        updated_count = 0
        failed_symbols = []
        
        for watched_item in watched_items:
            price_data = price_results.get(watched_item.symbol)
            if price_data:
                watched_item.last_price = price_data.price
                updated_count += 1
            else:
                failed_symbols.append(watched_item.symbol)
        
        # Commit changes
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            return {
                "success": False,
                "error": f"Failed to save price updates: {str(e)}"
            }
        
        return {
            "success": True,
            "updated_count": updated_count,
            "failed_count": len(failed_symbols),
            "total_count": len(watched_items),
            "failed_symbols": failed_symbols,
            "message": f"Updated {updated_count}/{len(watched_items)} prices"
        }
    
    def update_single_item_price(self, watchlist_id: int, symbol: str) -> dict:
        """Update price for a single watched item."""
        watched_item = self.db.query(WatchedItem).filter(
            WatchedItem.watchlist_id == watchlist_id,
            WatchedItem.symbol == symbol
        ).first()
        
        if not watched_item:
            return {"success": False, "error": "Watched item not found"}
        
        price_data = self.stock_data_controller.get_stock_price(symbol, use_cache=False)
        
        if price_data:
            watched_item.last_price = price_data.price
            try:
                self.db.commit()
                return {
                    "success": True,
                    "symbol": symbol,
                    "price": price_data.price,
                    "message": f"Updated {symbol} price to ${price_data.price:.2f}"
                }
            except Exception as e:
                self.db.rollback()
                return {"success": False, "error": f"Failed to save price: {str(e)}"}
        else:
            return {"success": False, "error": f"Failed to fetch price for {symbol}"}
    
    def get_watchlist_summary(self, watchlist_id: int) -> dict:
        """Get watchlist summary with statistics."""
        watched_items = self.get_watchlist_items(watchlist_id)
        
        total_items = len(watched_items)
        items_with_prices = len([item for item in watched_items if item.last_price])
        items_with_notes = len([item for item in watched_items if item.notes])
        
        # Calculate some basic statistics
        prices = [item.last_price for item in watched_items if item.last_price]
        avg_price = sum(prices) / len(prices) if prices else 0.0
        
        return {
            "total_items": total_items,
            "items_with_prices": items_with_prices,
            "items_with_notes": items_with_notes,
            "price_coverage": items_with_prices / total_items * 100 if total_items > 0 else 0,
            "average_price": avg_price
        }
    
    def validate_watchlist_symbols(self, watchlist_id: int) -> dict:
        """Validate all stock symbols in a watchlist."""
        watched_items = self.get_watchlist_items(watchlist_id)
        
        if not watched_items:
            return {"valid_symbols": [], "invalid_symbols": [], "all_valid": True}
        
        symbols = [item.symbol for item in watched_items]
        validation_results = self.stock_data_controller.validate_symbols(symbols)
        
        valid_symbols = [symbol for symbol, is_valid in validation_results.items() if is_valid]
        invalid_symbols = [symbol for symbol, is_valid in validation_results.items() if not is_valid]
        
        return {
            "valid_symbols": valid_symbols,
            "invalid_symbols": invalid_symbols,
            "all_valid": len(invalid_symbols) == 0,
            "validation_results": validation_results
        }
    
    def get_watchlist_items_with_details(self, watchlist_id: int) -> List[dict]:
        """Get watched items with detailed information for display."""
        watched_items = self.get_watchlist_items(watchlist_id)
        
        return [
            {
                "symbol": item.symbol,
                "notes": item.notes,
                "last_price": item.last_price,
                "added_date": item.added_date.isoformat(),
                "has_price": item.last_price is not None,
                "has_notes": bool(item.notes)
            }
            for item in watched_items
        ]
    
    def reorder_watchlist_items(self, watchlist_id: int, symbol_order: List[str]) -> bool:
        """
        Reorder watched items in a watchlist based on provided symbol order.
        
        Args:
            watchlist_id: The watchlist ID
            symbol_order: List of symbols in their desired order
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get all watched items for this watchlist
            watched_items = self.get_watchlist_items(watchlist_id)
            item_dict = {item.symbol: item for item in watched_items}
            
            # Validate that all symbols in the order exist in the watchlist
            watchlist_symbols = set(item_dict.keys())
            order_symbols = set(symbol_order)
            
            if watchlist_symbols != order_symbols:
                missing_in_order = watchlist_symbols - order_symbols
                extra_in_order = order_symbols - watchlist_symbols
                error_msg = []
                if missing_in_order:
                    error_msg.append(f"Missing symbols in order: {missing_in_order}")
                if extra_in_order:
                    error_msg.append(f"Extra symbols in order: {extra_in_order}")
                raise ValueError("; ".join(error_msg))
            
            # Update order_index for each item
            for index, symbol in enumerate(symbol_order):
                item_dict[symbol].order_index = index
            
            self.db.commit()
            return True
            
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to reorder items: {str(e)}")