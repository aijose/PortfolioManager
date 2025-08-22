"""Unit tests for RebalancingController."""

import pytest
from controllers.rebalancing_controller import RebalancingController
from controllers.portfolio_controller import PortfolioController, PortfolioCreate, HoldingCreate
from models.portfolio import Portfolio, Holding


@pytest.fixture
def setup_test_portfolio(client, test_db):
    """Set up a test portfolio with holdings for rebalancing tests."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = PortfolioController(db)
        
        # Create portfolio
        portfolio_data = PortfolioCreate(name="Rebalancing Test Portfolio")
        portfolio = controller.create_portfolio(portfolio_data)
        
        # Add holdings with different allocations
        holdings = [
            HoldingCreate(symbol="AAPL", shares=10, target_allocation=40.0),  # Should be 40%
            HoldingCreate(symbol="GOOGL", shares=5, target_allocation=30.0),  # Should be 30% 
            HoldingCreate(symbol="MSFT", shares=8, target_allocation=20.0),   # Should be 20%
            HoldingCreate(symbol="TSLA", shares=2, target_allocation=10.0)    # Should be 10%
        ]
        
        for holding_data in holdings:
            controller.add_holding(portfolio.id, holding_data)
        
        # Mock current prices for calculations
        # AAPL: $150, GOOGL: $2500, MSFT: $300, TSLA: $800
        mock_prices = {
            "AAPL": 150.0,
            "GOOGL": 2500.0,
            "MSFT": 300.0,
            "TSLA": 800.0
        }
        
        # Update holding prices in database
        for holding in controller.get_portfolio_holdings(portfolio.id):
            if holding.symbol in mock_prices:
                holding.last_price = mock_prices[holding.symbol]
        db.commit()
        
        yield portfolio, mock_prices
        
    finally:
        db.close()


def test_rebalancing_controller_initialization():
    """Test RebalancingController initialization with different parameters."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        # Test default initialization
        controller1 = RebalancingController(db)
        assert controller1.tolerance_threshold == 2.0
        assert controller1.transaction_cost_rate == 0.005
        
        # Test custom initialization
        controller2 = RebalancingController(db, tolerance_threshold=2.0, transaction_cost_rate=0.005)
        assert controller2.tolerance_threshold == 2.0
        assert controller2.transaction_cost_rate == 0.005
        
    finally:
        db.close()


def test_analyze_portfolio_rebalancing_balanced(setup_test_portfolio):
    """Test rebalancing analysis for a well-balanced portfolio."""
    portfolio, mock_prices = setup_test_portfolio
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        # Manually set holdings to be perfectly balanced
        controller = PortfolioController(db)
        holdings = controller.get_portfolio_holdings(portfolio.id)
        
        # Calculate total value: (10*150) + (5*2500) + (8*300) + (2*800) = 1500 + 12500 + 2400 + 1600 = 18000
        total_value = 18000.0
        
        # Set shares to match target allocations exactly
        # 40% of 18000 = 7200 -> AAPL needs 48 shares (48*150=7200)
        # 30% of 18000 = 5400 -> GOOGL needs 2.16 shares (2.16*2500=5400)  
        # 20% of 18000 = 3600 -> MSFT needs 12 shares (12*300=3600)
        # 10% of 18000 = 1800 -> TSLA needs 2.25 shares (2.25*800=1800)
        
        updates = [
            ("AAPL", 48, 150.0),
            ("GOOGL", 2.16, 2500.0),
            ("MSFT", 12, 300.0), 
            ("TSLA", 2.25, 800.0)
        ]
        
        for symbol, shares, price in updates:
            for holding in holdings:
                if holding.symbol == symbol:
                    holding.shares = shares
                    holding.last_price = price
        db.commit()
        
        rebalancing_controller = RebalancingController(db, tolerance_threshold=5.0)
        analysis = rebalancing_controller.analyze_portfolio_rebalancing(portfolio.id)
        
        assert analysis.is_balanced is True
        assert len(analysis.transactions) == 0
        assert analysis.total_transaction_cost == 0.0
        assert analysis.total_value > 0
        
    finally:
        db.close()


def test_analyze_portfolio_rebalancing_needs_rebalancing(setup_test_portfolio):
    """Test rebalancing analysis for portfolio that needs rebalancing."""
    portfolio, mock_prices = setup_test_portfolio
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        rebalancing_controller = RebalancingController(db, tolerance_threshold=2.0)
        analysis = rebalancing_controller.analyze_portfolio_rebalancing(portfolio.id)
        
        # With the current holdings, the portfolio is likely not perfectly balanced
        # Total value: (10*150) + (5*2500) + (8*300) + (2*800) = 18000
        # Current allocations will differ from target allocations
        
        assert analysis.total_value > 0
        assert len(analysis.allocation_drifts) == 4  # One for each holding
        
        # Check that drift calculations are present
        for drift in analysis.allocation_drifts:
            assert hasattr(drift, 'symbol')
            assert hasattr(drift, 'current_allocation')
            assert hasattr(drift, 'target_allocation')
            assert hasattr(drift, 'drift')
            
    finally:
        db.close()


def test_analyze_portfolio_empty(client, test_db):
    """Test rebalancing analysis for empty portfolio."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = PortfolioController(db)
        portfolio = controller.create_portfolio(PortfolioCreate(name="Empty Portfolio"))
        
        rebalancing_controller = RebalancingController(db)
        
        with pytest.raises(ValueError, match="has no holdings"):
            rebalancing_controller.analyze_portfolio_rebalancing(portfolio.id)
            
    finally:
        db.close()


def test_analyze_nonexistent_portfolio(client, test_db):
    """Test rebalancing analysis for non-existent portfolio."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        rebalancing_controller = RebalancingController(db)
        
        with pytest.raises(ValueError, match="not found"):
            rebalancing_controller.analyze_portfolio_rebalancing(999)
            
    finally:
        db.close()


def test_calculate_allocation_drift():
    """Test allocation drift calculation logic."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        rebalancing_controller = RebalancingController(db)
        
        # Test perfect allocation (no drift)
        drift1 = rebalancing_controller._calculate_allocation_drift(40.0, 40.0)
        assert drift1 == 0.0
        
        # Test positive drift (overweight)
        drift2 = rebalancing_controller._calculate_allocation_drift(45.0, 40.0) 
        assert drift2 == 5.0
        
        # Test negative drift (underweight)
        drift3 = rebalancing_controller._calculate_allocation_drift(35.0, 40.0)
        assert drift3 == -5.0
        
    finally:
        db.close()


def test_calculate_transaction_cost():
    """Test transaction cost calculation."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        rebalancing_controller = RebalancingController(db, transaction_cost_rate=0.01)  # 1%
        
        # Test buy transaction
        cost1 = rebalancing_controller._calculate_transaction_cost(1000.0)  # $1000 trade
        assert cost1 == 10.0  # 1% of $1000
        
        # Test sell transaction (should be same cost)
        cost2 = rebalancing_controller._calculate_transaction_cost(-1000.0)  # $1000 sell
        assert cost2 == 10.0  # 1% of $1000 (absolute value)
        
    finally:
        db.close()


def test_rebalancing_with_invalid_allocations(client, test_db):
    """Test rebalancing with invalid target allocations."""
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        controller = PortfolioController(db)
        portfolio = controller.create_portfolio(PortfolioCreate(name="Invalid Allocation Portfolio"))
        
        # Add holdings with allocations that don't sum to 100%
        holdings = [
            HoldingCreate(symbol="AAPL", shares=10, target_allocation=50.0),
            HoldingCreate(symbol="GOOGL", shares=5, target_allocation=30.0)  # Only 80% total
        ]
        
        for holding_data in holdings:
            controller.add_holding(portfolio.id, holding_data)
        
        # Set prices so we can test allocation validation
        for holding in controller.get_portfolio_holdings(portfolio.id):
            holding.last_price = 100.0  # Set some price
        db.commit()
        
        rebalancing_controller = RebalancingController(db)
        
        # Should complete successfully, but analysis should show issues
        analysis = rebalancing_controller.analyze_portfolio_rebalancing(portfolio.id)
        
        # Analysis should complete, but portfolio won't be balanced due to invalid allocations
        assert analysis is not None
        assert not analysis.is_balanced  # Should not be balanced with invalid allocations
            
    finally:
        db.close()


def test_rebalancing_with_zero_prices(setup_test_portfolio):
    """Test rebalancing with holdings that have zero/null prices."""
    portfolio, mock_prices = setup_test_portfolio
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        # Set one holding to have zero price
        controller = PortfolioController(db)
        holdings = controller.get_portfolio_holdings(portfolio.id)
        
        for holding in holdings:
            if holding.symbol == "AAPL":
                holding.last_price = None
        db.commit()
        
        rebalancing_controller = RebalancingController(db)
        
        # Should complete successfully, skipping holdings without prices
        analysis = rebalancing_controller.analyze_portfolio_rebalancing(portfolio.id)
        
        # Should include all holdings in drift analysis (including ones with no price)
        assert len(analysis.allocation_drifts) == 4  # All holdings
        
        # AAPL should have 0 current allocation due to no price
        aapl_drift = next(d for d in analysis.allocation_drifts if d.symbol == "AAPL")
        assert aapl_drift.current_allocation == 0.0
            
    finally:
        db.close()


def test_rebalancing_analysis_structure(setup_test_portfolio):
    """Test that rebalancing analysis returns proper data structure."""
    portfolio, mock_prices = setup_test_portfolio
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        rebalancing_controller = RebalancingController(db)
        analysis = rebalancing_controller.analyze_portfolio_rebalancing(portfolio.id)
        
        # Check that analysis object has all required attributes
        required_attrs = [
            'is_balanced', 'total_value', 'tolerance_threshold',
            'allocation_drifts', 'transactions', 'total_transaction_cost',
            'estimated_final_value'
        ]
        
        for attr in required_attrs:
            assert hasattr(analysis, attr), f"Analysis missing attribute: {attr}"
        
        # Check types
        assert isinstance(analysis.is_balanced, bool)
        assert isinstance(analysis.total_value, (int, float))
        assert isinstance(analysis.tolerance_threshold, (int, float))
        assert isinstance(analysis.allocation_drifts, list)
        assert isinstance(analysis.transactions, list)
        assert isinstance(analysis.total_transaction_cost, (int, float))
        assert isinstance(analysis.estimated_final_value, (int, float))
        
    finally:
        db.close()


def test_high_tolerance_vs_low_tolerance(setup_test_portfolio):
    """Test difference between high and low tolerance thresholds."""
    portfolio, mock_prices = setup_test_portfolio
    from models.database import TestingSessionLocal
    db = TestingSessionLocal()
    
    try:
        # High tolerance - should be more likely to be "balanced"
        high_tolerance_controller = RebalancingController(db, tolerance_threshold=10.0)
        high_analysis = high_tolerance_controller.analyze_portfolio_rebalancing(portfolio.id)
        
        # Low tolerance - should be more likely to need rebalancing
        low_tolerance_controller = RebalancingController(db, tolerance_threshold=1.0)  
        low_analysis = low_tolerance_controller.analyze_portfolio_rebalancing(portfolio.id)
        
        # With same portfolio, high tolerance should have fewer/no transactions
        assert len(high_analysis.transactions) <= len(low_analysis.transactions)
        assert high_analysis.total_transaction_cost <= low_analysis.total_transaction_cost
        
    finally:
        db.close()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])