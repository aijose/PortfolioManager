"""Portfolio business logic and CRUD operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from models.portfolio import Portfolio, Holding
from pydantic import BaseModel, validator


class PortfolioCreate(BaseModel):
    """Schema for creating a new portfolio."""
    name: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Portfolio name cannot be empty')
        return v.strip()


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio."""
    name: str
    
    @validator('name')
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Portfolio name cannot be empty')
        return v.strip()


class HoldingCreate(BaseModel):
    """Schema for creating a new holding."""
    symbol: str
    shares: float
    target_allocation: float
    
    @validator('symbol')
    def symbol_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Symbol cannot be empty')
        return v.strip().upper()
    
    @validator('shares')
    def shares_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Shares must be non-negative')
        return v
    
    @validator('target_allocation')
    def allocation_must_be_valid(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Target allocation must be between 0.01 and 100')
        return v


class PortfolioController:
    """Controller for portfolio operations."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_portfolios(self) -> List[Portfolio]:
        """Get all portfolios."""
        return self.db.query(Portfolio).order_by(Portfolio.name).all()
    
    def get_portfolio(self, portfolio_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio by ID."""
        return self.db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
    
    def get_portfolio_by_name(self, name: str) -> Optional[Portfolio]:
        """Get a portfolio by name."""
        return self.db.query(Portfolio).filter(Portfolio.name == name).first()
    
    def create_portfolio(self, portfolio: PortfolioCreate) -> Portfolio:
        """Create a new portfolio."""
        # Check if portfolio with same name already exists
        existing = self.get_portfolio_by_name(portfolio.name)
        if existing:
            raise ValueError(f"Portfolio with name '{portfolio.name}' already exists")
        
        db_portfolio = Portfolio(name=portfolio.name)
        self.db.add(db_portfolio)
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio
    
    def update_portfolio(self, portfolio_id: int, portfolio: PortfolioUpdate) -> Optional[Portfolio]:
        """Update an existing portfolio."""
        db_portfolio = self.get_portfolio(portfolio_id)
        if not db_portfolio:
            return None
        
        # Check if new name conflicts with existing portfolio (excluding current one)
        existing = self.db.query(Portfolio).filter(
            Portfolio.name == portfolio.name,
            Portfolio.id != portfolio_id
        ).first()
        if existing:
            raise ValueError(f"Portfolio with name '{portfolio.name}' already exists")
        
        db_portfolio.name = portfolio.name
        self.db.commit()
        self.db.refresh(db_portfolio)
        return db_portfolio
    
    def delete_portfolio(self, portfolio_id: int) -> bool:
        """Delete a portfolio and all its holdings."""
        db_portfolio = self.get_portfolio(portfolio_id)
        if not db_portfolio:
            return False
        
        self.db.delete(db_portfolio)
        self.db.commit()
        return True
    
    def add_holding(self, portfolio_id: int, holding: HoldingCreate) -> Optional[Holding]:
        """Add a holding to a portfolio."""
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            return None
        
        # Check if holding with same symbol already exists in this portfolio
        existing = self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.symbol == holding.symbol
        ).first()
        if existing:
            raise ValueError(f"Holding for {holding.symbol} already exists in this portfolio")
        
        db_holding = Holding(
            portfolio_id=portfolio_id,
            symbol=holding.symbol,
            shares=holding.shares,
            target_allocation=holding.target_allocation
        )
        self.db.add(db_holding)
        self.db.commit()
        self.db.refresh(db_holding)
        return db_holding
    
    def get_portfolio_holdings(self, portfolio_id: int) -> List[Holding]:
        """Get all holdings for a portfolio."""
        return self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id
        ).order_by(Holding.symbol).all()
    
    def calculate_portfolio_summary(self, portfolio_id: int) -> dict:
        """Calculate portfolio summary statistics."""
        holdings = self.get_portfolio_holdings(portfolio_id)
        
        total_value = sum(h.current_value for h in holdings if h.last_price)
        total_target_allocation = sum(h.target_allocation for h in holdings)
        
        return {
            "total_holdings": len(holdings),
            "total_value": total_value,
            "total_target_allocation": total_target_allocation,
            "is_allocation_valid": abs(total_target_allocation - 100.0) < 0.01,
            "holdings_with_prices": len([h for h in holdings if h.last_price])
        }