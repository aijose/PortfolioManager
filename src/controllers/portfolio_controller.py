"""Portfolio business logic and CRUD operations."""

from typing import List, Optional
from sqlalchemy.orm import Session
from models.portfolio import Portfolio, Holding
from pydantic import BaseModel, field_validator
from controllers.stock_data_controller import StockDataController


class PortfolioCreate(BaseModel):
    """Schema for creating a new portfolio."""
    name: str
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Portfolio name cannot be empty')
        return v.strip()


class PortfolioUpdate(BaseModel):
    """Schema for updating a portfolio."""
    name: str
    
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Portfolio name cannot be empty')
        return v.strip()


class HoldingCreate(BaseModel):
    """Schema for creating a new holding."""
    symbol: str
    shares: float
    target_allocation: float
    
    @field_validator('symbol')
    @classmethod
    def symbol_must_be_valid(cls, v):
        if not v or not v.strip():
            raise ValueError('Symbol cannot be empty')
        return v.strip().upper()
    
    @field_validator('shares')
    @classmethod
    def shares_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Shares must be non-negative')
        return v
    
    @field_validator('target_allocation')
    @classmethod
    def allocation_must_be_valid(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Target allocation must be between 0.01 and 100')
        return v


class HoldingUpdate(BaseModel):
    """Schema for updating a holding."""
    shares: float
    target_allocation: float
    
    @field_validator('shares')
    @classmethod
    def shares_must_be_positive(cls, v):
        if v < 0:
            raise ValueError('Shares must be non-negative')
        return v
    
    @field_validator('target_allocation')
    @classmethod
    def allocation_must_be_valid(cls, v):
        if v <= 0 or v > 100:
            raise ValueError('Target allocation must be between 0.01 and 100')
        return v


class PortfolioController:
    """Controller for portfolio operations."""
    
    def __init__(self, db: Session):
        self.db = db
        self.stock_data_controller = StockDataController()
    
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
    
    def update_holding(self, portfolio_id: int, symbol: str, holding: HoldingUpdate) -> Optional[Holding]:
        """Update an existing holding."""
        db_holding = self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.symbol == symbol
        ).first()
        
        if not db_holding:
            return None
        
        db_holding.shares = holding.shares
        db_holding.target_allocation = holding.target_allocation
        self.db.commit()
        self.db.refresh(db_holding)
        return db_holding
    
    def delete_holding(self, portfolio_id: int, symbol: str) -> bool:
        """Delete a holding from a portfolio."""
        db_holding = self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.symbol == symbol
        ).first()
        
        if not db_holding:
            return False
        
        self.db.delete(db_holding)
        self.db.commit()
        return True
    
    def import_holdings_from_csv(self, portfolio_id: int, holdings_data: List) -> dict:
        """
        Import holdings from CSV data, replacing existing holdings.
        
        Args:
            portfolio_id: ID of the portfolio
            holdings_data: List of CSVHoldingData objects
            
        Returns:
            Dictionary with import results
        """
        portfolio = self.get_portfolio(portfolio_id)
        if not portfolio:
            raise ValueError("Portfolio not found")
        
        # Clear existing holdings
        self.db.query(Holding).filter(Holding.portfolio_id == portfolio_id).delete()
        
        # Add new holdings
        imported_count = 0
        errors = []
        
        for holding_data in holdings_data:
            try:
                db_holding = Holding(
                    portfolio_id=portfolio_id,
                    symbol=holding_data.symbol,
                    shares=holding_data.shares,
                    target_allocation=holding_data.allocation
                )
                self.db.add(db_holding)
                imported_count += 1
            except Exception as e:
                errors.append(f"Failed to import {holding_data.symbol}: {str(e)}")
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            raise ValueError(f"Failed to save holdings: {str(e)}")
        
        return {
            "imported_count": imported_count,
            "errors": errors,
            "success": len(errors) == 0
        }
    
    def refresh_portfolio_prices(self, portfolio_id: int) -> dict:
        """
        Refresh stock prices for all holdings in a portfolio.
        
        Returns:
            Dictionary with update results and statistics
        """
        holdings = self.get_portfolio_holdings(portfolio_id)
        if not holdings:
            return {
                "success": True,
                "updated_count": 0,
                "failed_count": 0,
                "total_count": 0,
                "errors": [],
                "message": "No holdings to update"
            }
        
        # Get symbols to update
        symbols = [h.symbol for h in holdings]
        
        # Fetch prices
        price_results = self.stock_data_controller.refresh_portfolio_prices(symbols)
        
        # Update database with new prices
        updated_count = 0
        failed_symbols = []
        
        for holding in holdings:
            price_data = price_results.get(holding.symbol)
            if price_data:
                holding.last_price = price_data.price
                updated_count += 1
            else:
                failed_symbols.append(holding.symbol)
        
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
            "total_count": len(holdings),
            "failed_symbols": failed_symbols,
            "message": f"Updated {updated_count}/{len(holdings)} prices"
        }
    
    def update_single_holding_price(self, portfolio_id: int, symbol: str) -> dict:
        """Update price for a single holding."""
        holding = self.db.query(Holding).filter(
            Holding.portfolio_id == portfolio_id,
            Holding.symbol == symbol
        ).first()
        
        if not holding:
            return {"success": False, "error": "Holding not found"}
        
        price_data = self.stock_data_controller.get_stock_price(symbol, use_cache=False)
        
        if price_data:
            holding.last_price = price_data.price
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
    
    def get_portfolio_valuation(self, portfolio_id: int) -> dict:
        """Get detailed portfolio valuation and performance metrics."""
        holdings = self.get_portfolio_holdings(portfolio_id)
        
        if not holdings:
            return {
                "total_value": 0.0,
                "total_cost_basis": 0.0,
                "total_gain_loss": 0.0,
                "total_gain_loss_percent": 0.0,
                "holdings_breakdown": [],
                "allocation_analysis": {},
                "last_updated": None
            }
        
        total_value = 0.0
        holdings_breakdown = []
        holdings_with_prices = 0
        
        for holding in holdings:
            if holding.last_price:
                current_value = holding.current_value
                total_value += current_value
                holdings_with_prices += 1
                
                holdings_breakdown.append({
                    "symbol": holding.symbol,
                    "shares": holding.shares,
                    "current_price": holding.last_price,
                    "current_value": current_value,
                    "target_allocation": holding.target_allocation,
                    "current_allocation": 0.0  # Will be calculated after total_value
                })
            else:
                holdings_breakdown.append({
                    "symbol": holding.symbol,
                    "shares": holding.shares,
                    "current_price": None,
                    "current_value": 0.0,
                    "target_allocation": holding.target_allocation,
                    "current_allocation": 0.0
                })
        
        # Calculate current allocation percentages
        if total_value > 0:
            for holding_data in holdings_breakdown:
                if holding_data["current_value"] > 0:
                    holding_data["current_allocation"] = (holding_data["current_value"] / total_value) * 100
        
        # Allocation analysis
        total_target_allocation = sum(h.target_allocation for h in holdings)
        allocation_drift = []
        
        for holding_data in holdings_breakdown:
            target = holding_data["target_allocation"]
            current = holding_data["current_allocation"]
            drift = current - target
            
            if abs(drift) > 1.0:  # Only show significant drifts
                allocation_drift.append({
                    "symbol": holding_data["symbol"],
                    "target": target,
                    "current": current,
                    "drift": drift
                })
        
        return {
            "total_value": total_value,
            "holdings_breakdown": holdings_breakdown,
            "allocation_analysis": {
                "total_target_allocation": total_target_allocation,
                "is_allocation_valid": abs(total_target_allocation - 100.0) < 0.01,
                "significant_drifts": allocation_drift
            },
            "holdings_with_prices": holdings_with_prices,
            "total_holdings": len(holdings),
            "price_coverage": holdings_with_prices / len(holdings) * 100 if holdings else 0
        }
    
    def validate_portfolio_symbols(self, portfolio_id: int) -> dict:
        """Validate all stock symbols in a portfolio."""
        holdings = self.get_portfolio_holdings(portfolio_id)
        
        if not holdings:
            return {"valid_symbols": [], "invalid_symbols": [], "all_valid": True}
        
        symbols = [h.symbol for h in holdings]
        validation_results = self.stock_data_controller.validate_symbols(symbols)
        
        valid_symbols = [symbol for symbol, is_valid in validation_results.items() if is_valid]
        invalid_symbols = [symbol for symbol, is_valid in validation_results.items() if not is_valid]
        
        return {
            "valid_symbols": valid_symbols,
            "invalid_symbols": invalid_symbols,
            "all_valid": len(invalid_symbols) == 0,
            "validation_results": validation_results
        }
    
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