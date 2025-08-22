"""Portfolio rebalancing controller for analyzing and executing rebalancing transactions."""

from typing import List, Dict, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from dataclasses import dataclass
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from models.portfolio import Portfolio, Holding
from controllers.portfolio_controller import PortfolioController
from controllers.stock_data_controller import StockDataController

logger = logging.getLogger(__name__)


@dataclass
class RebalancingTransaction:
    """Represents a single buy/sell transaction for rebalancing."""
    symbol: str
    action: str  # 'BUY' or 'SELL'
    shares: float
    current_price: float
    transaction_value: float
    transaction_cost: float
    reason: str


@dataclass
class AllocationDrift:
    """Represents the allocation drift for a single holding."""
    symbol: str
    current_allocation: float
    target_allocation: float
    drift: float
    drift_percentage: float
    current_value: float
    target_value: float
    value_difference: float


@dataclass
class RebalancingAnalysis:
    """Complete rebalancing analysis for a portfolio."""
    portfolio_id: int
    total_value: float
    is_balanced: bool
    tolerance_threshold: float
    allocation_drifts: List[AllocationDrift]
    transactions: List[RebalancingTransaction]
    total_transaction_cost: float
    estimated_final_value: float
    analysis_timestamp: datetime


class RebalancingController:
    """Controller for portfolio rebalancing operations."""
    
    def __init__(self, db: Session, tolerance_threshold: float = 2.0, transaction_cost_rate: float = 0.005):
        """
        Initialize rebalancing controller.
        
        Args:
            db: Database session
            tolerance_threshold: Allocation drift threshold in percentage points (default: 2%)
            transaction_cost_rate: Transaction cost as percentage of trade value (default: 0.5%)
        """
        self.db = db
        self.tolerance_threshold = tolerance_threshold
        self.transaction_cost_rate = transaction_cost_rate
        self.portfolio_controller = PortfolioController(db)
        self.stock_data_controller = StockDataController()
    
    def analyze_portfolio_rebalancing(self, portfolio_id: int, 
                                    custom_tolerance: Optional[float] = None,
                                    custom_cost_rate: Optional[float] = None) -> RebalancingAnalysis:
        """
        Analyze portfolio for rebalancing needs and generate transaction recommendations.
        
        Args:
            portfolio_id: ID of the portfolio to analyze
            custom_tolerance: Custom tolerance threshold (overrides default)
            custom_cost_rate: Custom transaction cost rate (overrides default)
            
        Returns:
            RebalancingAnalysis object with complete analysis
        """
        tolerance = custom_tolerance if custom_tolerance is not None else self.tolerance_threshold
        cost_rate = custom_cost_rate if custom_cost_rate is not None else self.transaction_cost_rate
        
        # Get portfolio and holdings
        portfolio = self.portfolio_controller.get_portfolio(portfolio_id)
        if not portfolio:
            raise ValueError(f"Portfolio {portfolio_id} not found")
        
        holdings = self.portfolio_controller.get_portfolio_holdings(portfolio_id)
        if not holdings:
            raise ValueError(f"Portfolio {portfolio_id} has no holdings")
        
        # Calculate current portfolio value
        total_value = sum(h.current_value for h in holdings if h.last_price)
        
        if total_value <= 0:
            raise ValueError("Portfolio has no current market value. Please refresh stock prices first.")
        
        # Analyze allocation drifts
        allocation_drifts = self._calculate_allocation_drifts(holdings, total_value)
        
        # Determine if rebalancing is needed
        significant_drifts = [d for d in allocation_drifts if abs(d.drift) > tolerance]
        is_balanced = len(significant_drifts) == 0
        
        # Generate transactions if rebalancing is needed
        transactions = []
        total_transaction_cost = 0.0
        estimated_final_value = total_value
        
        if not is_balanced:
            transactions, total_transaction_cost = self._generate_rebalancing_transactions(
                holdings, total_value, allocation_drifts, cost_rate
            )
            estimated_final_value = total_value - total_transaction_cost
        
        return RebalancingAnalysis(
            portfolio_id=portfolio_id,
            total_value=total_value,
            is_balanced=is_balanced,
            tolerance_threshold=tolerance,
            allocation_drifts=allocation_drifts,
            transactions=transactions,
            total_transaction_cost=total_transaction_cost,
            estimated_final_value=estimated_final_value,
            analysis_timestamp=datetime.now()
        )
    
    def _calculate_allocation_drifts(self, holdings: List[Holding], total_value: float) -> List[AllocationDrift]:
        """Calculate allocation drift for each holding."""
        drifts = []
        
        for holding in holdings:
            current_value = holding.current_value if holding.last_price else 0.0
            current_allocation = (current_value / total_value * 100) if total_value > 0 else 0.0
            target_allocation = holding.target_allocation
            
            drift = current_allocation - target_allocation
            drift_percentage = (drift / target_allocation * 100) if target_allocation > 0 else 0.0
            
            target_value = total_value * (target_allocation / 100)
            value_difference = current_value - target_value
            
            drifts.append(AllocationDrift(
                symbol=holding.symbol,
                current_allocation=current_allocation,
                target_allocation=target_allocation,
                drift=drift,
                drift_percentage=drift_percentage,
                current_value=current_value,
                target_value=target_value,
                value_difference=value_difference
            ))
        
        return drifts
    
    def _generate_rebalancing_transactions(self, holdings: List[Holding], total_value: float,
                                         allocation_drifts: List[AllocationDrift], 
                                         cost_rate: float) -> Tuple[List[RebalancingTransaction], float]:
        """Generate buy/sell transactions to achieve target allocation."""
        transactions = []
        total_cost = 0.0
        
        # Create a map for quick lookup
        drift_map = {d.symbol: d for d in allocation_drifts}
        
        for holding in holdings:
            if not holding.last_price:
                logger.warning(f"Skipping {holding.symbol} - no current price available")
                continue
            
            drift = drift_map[holding.symbol]
            
            # Skip if drift is within tolerance
            if abs(drift.drift) <= self.tolerance_threshold:
                continue
            
            # Calculate required shares change
            target_value = drift.target_value
            current_value = drift.current_value
            value_difference = target_value - current_value
            
            # Calculate shares to buy/sell
            shares_change = value_difference / holding.last_price
            action = "BUY" if shares_change > 0 else "SELL"
            shares_change = abs(shares_change)
            
            # Skip very small transactions (less than 0.1 shares)
            if shares_change < 0.1:
                continue
            
            transaction_value = shares_change * holding.last_price
            transaction_cost = transaction_value * cost_rate
            total_cost += transaction_cost
            
            # Determine reason for transaction
            if drift.drift > 0:
                reason = f"Overweight by {drift.drift:.1f}% ({drift.drift_percentage:.1f}% relative)"
            else:
                reason = f"Underweight by {abs(drift.drift):.1f}% ({abs(drift.drift_percentage):.1f}% relative)"
            
            transactions.append(RebalancingTransaction(
                symbol=holding.symbol,
                action=action,
                shares=shares_change,
                current_price=holding.last_price,
                transaction_value=transaction_value,
                transaction_cost=transaction_cost,
                reason=reason
            ))
        
        return transactions, total_cost
    
    def get_rebalancing_summary(self, portfolio_id: int) -> Dict:
        """Get a quick summary of rebalancing needs for a portfolio."""
        try:
            analysis = self.analyze_portfolio_rebalancing(portfolio_id)
            
            significant_drifts = [d for d in analysis.allocation_drifts if abs(d.drift) > self.tolerance_threshold]
            
            return {
                "needs_rebalancing": not analysis.is_balanced,
                "total_value": analysis.total_value,
                "tolerance_threshold": analysis.tolerance_threshold,
                "significant_drifts_count": len(significant_drifts),
                "max_drift": max([abs(d.drift) for d in analysis.allocation_drifts]) if analysis.allocation_drifts else 0,
                "transaction_count": len(analysis.transactions),
                "estimated_transaction_cost": analysis.total_transaction_cost,
                "cost_percentage": (analysis.total_transaction_cost / analysis.total_value * 100) if analysis.total_value > 0 else 0
            }
        except Exception as e:
            logger.error(f"Error calculating rebalancing summary for portfolio {portfolio_id}: {e}")
            return {
                "error": str(e),
                "needs_rebalancing": False,
                "total_value": 0
            }
    
    def execute_rebalancing(self, portfolio_id: int, transactions: List[RebalancingTransaction],
                          dry_run: bool = True) -> Dict:
        """
        Execute rebalancing transactions by updating portfolio holdings.
        
        Args:
            portfolio_id: Portfolio to rebalance
            transactions: List of transactions to execute
            dry_run: If True, don't actually update holdings (default: True for safety)
            
        Returns:
            Execution results
        """
        if dry_run:
            return {
                "success": True,
                "message": "Dry run completed successfully",
                "transactions_count": len(transactions),
                "total_cost": sum(t.transaction_cost for t in transactions),
                "executed": False
            }
        
        try:
            holdings = self.portfolio_controller.get_portfolio_holdings(portfolio_id)
            holdings_map = {h.symbol: h for h in holdings}
            
            executed_transactions = []
            total_cost = 0.0
            
            for transaction in transactions:
                holding = holdings_map.get(transaction.symbol)
                if not holding:
                    logger.warning(f"Holding {transaction.symbol} not found, skipping transaction")
                    continue
                
                # Calculate new shares amount
                if transaction.action == "BUY":
                    new_shares = holding.shares + transaction.shares
                else:  # SELL
                    new_shares = holding.shares - transaction.shares
                
                # Ensure we don't go negative
                if new_shares < 0:
                    logger.warning(f"Transaction would result in negative shares for {transaction.symbol}, adjusting")
                    new_shares = 0
                
                # Update holding
                holding.shares = new_shares
                executed_transactions.append(transaction)
                total_cost += transaction.transaction_cost
            
            # Commit changes
            self.db.commit()
            
            # Log the rebalancing execution
            self._log_rebalancing_execution(portfolio_id, executed_transactions, total_cost)
            
            return {
                "success": True,
                "message": f"Successfully executed {len(executed_transactions)} transactions",
                "transactions_count": len(executed_transactions),
                "total_cost": total_cost,
                "executed": True
            }
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error executing rebalancing for portfolio {portfolio_id}: {e}")
            return {
                "success": False,
                "error": str(e),
                "executed": False
            }
    
    def _log_rebalancing_execution(self, portfolio_id: int, transactions: List[RebalancingTransaction], total_cost: float):
        """Log rebalancing execution for audit trail."""
        # For now, just log to application logs
        # In a production system, this would go to a dedicated rebalancing_history table
        logger.info(f"Rebalancing executed for portfolio {portfolio_id}:")
        logger.info(f"  - Total transactions: {len(transactions)}")
        logger.info(f"  - Total cost: ${total_cost:.2f}")
        for tx in transactions:
            logger.info(f"  - {tx.action} {tx.shares:.2f} shares of {tx.symbol} at ${tx.current_price:.2f}")
    
    def validate_rebalancing_feasibility(self, portfolio_id: int) -> Dict:
        """
        Validate if rebalancing is feasible for a portfolio.
        
        Returns validation results with any issues found.
        """
        issues = []
        warnings = []
        
        # Check if portfolio exists
        portfolio = self.portfolio_controller.get_portfolio(portfolio_id)
        if not portfolio:
            issues.append("Portfolio not found")
            return {"feasible": False, "issues": issues, "warnings": warnings}
        
        # Check if portfolio has holdings
        holdings = self.portfolio_controller.get_portfolio_holdings(portfolio_id)
        if not holdings:
            issues.append("Portfolio has no holdings")
            return {"feasible": False, "issues": issues, "warnings": warnings}
        
        # Check if all holdings have current prices
        holdings_without_prices = [h.symbol for h in holdings if not h.last_price]
        if holdings_without_prices:
            issues.append(f"Missing current prices for: {', '.join(holdings_without_prices)}")
        
        # Check if target allocations sum to approximately 100%
        total_target_allocation = sum(h.target_allocation for h in holdings)
        if abs(total_target_allocation - 100.0) > 0.1:
            issues.append(f"Target allocations sum to {total_target_allocation:.1f}% instead of 100%")
        
        # Check for zero target allocations
        zero_targets = [h.symbol for h in holdings if h.target_allocation <= 0]
        if zero_targets:
            warnings.append(f"Holdings with zero target allocation: {', '.join(zero_targets)}")
        
        # Check portfolio value
        total_value = sum(h.current_value for h in holdings if h.last_price)
        if total_value <= 0:
            issues.append("Portfolio has no current market value")
        elif total_value < 1000:  # Arbitrary minimum for meaningful rebalancing
            warnings.append(f"Portfolio value (${total_value:.2f}) may be too small for cost-effective rebalancing")
        
        is_feasible = len(issues) == 0
        
        return {
            "feasible": is_feasible,
            "issues": issues,
            "warnings": warnings,
            "total_value": total_value,
            "holdings_count": len(holdings),
            "holdings_with_prices": len([h for h in holdings if h.last_price])
        }
    
    def _calculate_allocation_drift(self, current_allocation: float, target_allocation: float) -> float:
        """Calculate simple allocation drift (current - target)."""
        return current_allocation - target_allocation
    
    def _calculate_transaction_cost(self, trade_value: float) -> float:
        """Calculate transaction cost for a trade value."""
        return abs(trade_value) * self.transaction_cost_rate