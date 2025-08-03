"""Portfolio and Holding database models."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from models.database import Base


class Portfolio(Base):
    """Portfolio model representing a collection of stock holdings."""
    
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    created_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    modified_date = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationship to holdings
    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Portfolio(id={self.id}, name='{self.name}')>"


class Holding(Base):
    """Holding model representing a stock position within a portfolio."""
    
    __tablename__ = "holdings"
    
    id = Column(Integer, primary_key=True, index=True)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    symbol = Column(String(10), nullable=False, index=True)
    shares = Column(Float, nullable=False, default=0.0)
    target_allocation = Column(Float, nullable=False)  # Percentage (0-100)
    last_price = Column(Float, nullable=True)  # Last fetched price
    
    # Relationship to portfolio
    portfolio = relationship("Portfolio", back_populates="holdings")
    
    def __repr__(self):
        return f"<Holding(symbol='{self.symbol}', shares={self.shares}, allocation={self.target_allocation}%)>"
    
    @property
    def current_value(self):
        """Calculate current value of the holding."""
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