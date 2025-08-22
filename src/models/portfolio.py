"""Portfolio, Holding, Watchlist, and WatchedItem database models."""

from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from models.database import Base


def utc_now():
    """Helper function to get timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class Portfolio(Base):
    """Portfolio model representing a collection of stock holdings."""
    
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    created_date = Column(DateTime, default=utc_now, nullable=False)
    modified_date = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationship to holdings
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}')>"


class Holding(Base):
    """Holding model representing a stock position or cash within a portfolio."""
    
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(10), nullable=False, index=True)
    shares = Column(Float, nullable=False, default=0.0)  # For $CASH, this represents dollar amount
    target_allocation = Column(Float, nullable=False)  # Percentage (0-100)
    last_price = Column(Float, nullable=True)  # Last fetched price
    
    # Relationship to portfolio
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    def __repr__(self):
        if self.symbol == '$CASH':
            return f"<Holding(symbol='$CASH', amount=${self.shares:.2f}, allocation={self.target_allocation}%)>"
        return f"<Holding(symbol='{self.symbol}', shares={self.shares}, allocation={self.target_allocation}%)>"
    
    @property
    def current_value(self):
        """Calculate current value of the holding."""
        if self.symbol == '$CASH':
            # For cash, shares represents the dollar amount directly
            return self.shares
        
        if self.last_price is None:
            return 0.0
        return self.shares * self.last_price
    
    @property
    def current_allocation_percent(self):
        """Calculate current allocation percentage within the portfolio."""
        if not self.portfolio:
            return 0.0
        
        total_value = sum(h.current_value for h in self.portfolio.holdings if h.last_price)
        if total_value == 0:
            return 0.0
        
        return (self.current_value / total_value) * 100


class Watchlist(Base):
    """Watchlist model representing a collection of stocks being tracked."""
    
    __tablename__ = "watchlists"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    created_date = Column(DateTime, default=utc_now, nullable=False)
    modified_date = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
    
    # Relationship to watched items
    watched_items = relationship("WatchedItem", back_populates="watchlist", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Watchlist(id={self.id}, name='{self.name}')>"


class WatchedItem(Base):
    """WatchedItem model representing a stock being tracked in a watchlist."""
    
    __tablename__ = "watched_items"
    
    id = Column(Integer, primary_key=True, index=True)
    watchlist_id = Column(Integer, ForeignKey("watchlists.id"), nullable=False)
    symbol = Column(String(10), nullable=False, index=True)
    notes = Column(String(500), nullable=True)  # Optional notes about why tracking this stock
    last_price = Column(Float, nullable=True)  # Last fetched price
    added_date = Column(DateTime, default=utc_now, nullable=False)
    news_data = Column(JSON, nullable=True)  # Cached news articles from Polygon.io
    last_news_update = Column(DateTime, nullable=True)  # Last time news was fetched
    order_index = Column(Integer, nullable=False, default=0)  # Order position in watchlist
    
    # Relationship to watchlist
    watchlist = relationship("Watchlist", back_populates="watched_items")
    
    def __repr__(self):
        return f"<WatchedItem(symbol='{self.symbol}', price=${self.last_price or 0:.2f})>"
    
    @property
    def current_value(self):
        """Get current price for display purposes."""
        return self.last_price or 0.0