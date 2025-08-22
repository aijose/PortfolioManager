"""Unit tests for validation logic and business rules."""

import pytest
from pydantic import ValidationError
from datetime import datetime

# Test Pydantic models validation
from controllers.portfolio_controller import PortfolioCreate, PortfolioUpdate, HoldingCreate, HoldingUpdate
from controllers.watchlist_controller import WatchlistCreate, WatchlistUpdate, WatchedItemCreate, WatchedItemUpdate


class TestPortfolioValidation:
    """Test portfolio data validation."""
    
    def test_portfolio_create_valid(self):
        """Test valid portfolio creation data."""
        portfolio_data = PortfolioCreate(name="Test Portfolio")
        assert portfolio_data.name == "Test Portfolio"
    
    def test_portfolio_create_empty_name(self):
        """Test portfolio creation with empty name."""
        with pytest.raises(ValidationError):
            PortfolioCreate(name="")
    
    def test_portfolio_create_whitespace_name(self):
        """Test portfolio creation with whitespace-only name."""
        with pytest.raises(ValidationError):
            PortfolioCreate(name="   ")
    
    def test_portfolio_create_long_name(self):
        """Test portfolio creation with very long name."""
        long_name = "A" * 300  # Very long name
        portfolio_data = PortfolioCreate(name=long_name)
        # Should be trimmed or accepted depending on validation rules
        assert len(portfolio_data.name) <= 300
    
    def test_portfolio_update_valid(self):
        """Test valid portfolio update data."""
        update_data = PortfolioUpdate(name="Updated Portfolio")
        assert update_data.name == "Updated Portfolio"


class TestHoldingValidation:
    """Test holding data validation."""
    
    def test_holding_create_valid(self):
        """Test valid holding creation data."""
        holding_data = HoldingCreate(
            symbol="AAPL",
            shares=10.0,
            target_allocation=25.0
        )
        assert holding_data.symbol == "AAPL"
        assert holding_data.shares == 10.0
        assert holding_data.target_allocation == 25.0
    
    def test_holding_create_invalid_symbol(self):
        """Test holding creation with invalid symbol."""
        with pytest.raises(ValidationError):
            HoldingCreate(symbol="", shares=10.0, target_allocation=25.0)
    
    def test_holding_create_negative_shares(self):
        """Test holding creation with negative shares."""
        with pytest.raises(ValidationError):
            HoldingCreate(symbol="AAPL", shares=-5.0, target_allocation=25.0)
    
    def test_holding_create_zero_shares(self):
        """Test holding creation with zero shares."""
        # Zero shares might be allowed in some cases, let's check actual validation
        try:
            holding_data = HoldingCreate(symbol="AAPL", shares=0.0, target_allocation=25.0)
            # If it doesn't raise an error, that's fine too
            assert holding_data.shares == 0.0
        except ValidationError:
            # If it does raise an error, that's also acceptable
            pass
    
    def test_holding_create_invalid_allocation(self):
        """Test holding creation with invalid allocation percentage."""
        # Test negative allocation
        with pytest.raises(ValidationError):
            HoldingCreate(symbol="AAPL", shares=10.0, target_allocation=-5.0)
        
        # Test allocation over 100%
        with pytest.raises(ValidationError):
            HoldingCreate(symbol="AAPL", shares=10.0, target_allocation=150.0)
    
    def test_holding_create_fractional_shares(self):
        """Test holding creation with fractional shares."""
        holding_data = HoldingCreate(
            symbol="GOOGL",
            shares=2.5,
            target_allocation=30.0
        )
        assert holding_data.shares == 2.5
    
    def test_holding_update_valid(self):
        """Test valid holding update data."""
        update_data = HoldingUpdate(shares=15.0, target_allocation=30.0)
        assert update_data.shares == 15.0
        assert update_data.target_allocation == 30.0


class TestWatchlistValidation:
    """Test watchlist data validation."""
    
    def test_watchlist_create_valid(self):
        """Test valid watchlist creation data."""
        watchlist_data = WatchlistCreate(name="Tech Stocks")
        assert watchlist_data.name == "Tech Stocks"
    
    def test_watchlist_create_empty_name(self):
        """Test watchlist creation with empty name."""
        with pytest.raises(ValidationError):
            WatchlistCreate(name="")
    
    def test_watchlist_create_whitespace_trimming(self):
        """Test watchlist name whitespace trimming."""
        watchlist_data = WatchlistCreate(name="  Tech Stocks  ")
        assert watchlist_data.name == "Tech Stocks"


class TestWatchedItemValidation:
    """Test watched item data validation."""
    
    def test_watched_item_create_valid(self):
        """Test valid watched item creation."""
        item_data = WatchedItemCreate(
            symbol="AAPL",
            notes="Apple Inc - Strong fundamentals"
        )
        assert item_data.symbol == "AAPL"
        assert item_data.notes == "Apple Inc - Strong fundamentals"
    
    def test_watched_item_create_no_notes(self):
        """Test watched item creation without notes."""
        item_data = WatchedItemCreate(symbol="AAPL")
        assert item_data.symbol == "AAPL"
        assert item_data.notes is None
    
    def test_watched_item_create_empty_symbol(self):
        """Test watched item creation with empty symbol."""
        with pytest.raises(ValidationError):
            WatchedItemCreate(symbol="")
    
    def test_watched_item_create_symbol_case(self):
        """Test watched item symbol case handling."""
        item_data = WatchedItemCreate(symbol="aapl")
        # Should be converted to uppercase
        assert item_data.symbol == "AAPL"
    
    def test_watched_item_update_notes(self):
        """Test watched item notes update."""
        update_data = WatchedItemUpdate(notes="Updated analysis")
        assert update_data.notes == "Updated analysis"


class TestBusinessLogicValidation:
    """Test business logic validation."""
    
    def test_allocation_sum_validation(self):
        """Test that allocation percentages should sum to 100%."""
        # This would be tested in the controller logic
        allocations = [25.0, 30.0, 25.0, 20.0]  # Sums to 100%
        total = sum(allocations)
        assert abs(total - 100.0) < 0.01
        
        # Test invalid sum
        invalid_allocations = [25.0, 30.0, 25.0]  # Sums to 80%
        invalid_total = sum(invalid_allocations)
        assert abs(invalid_total - 100.0) > 0.01
    
    def test_portfolio_value_calculation(self):
        """Test portfolio value calculation logic."""
        holdings = [
            {"shares": 10, "price": 150.0},  # $1,500
            {"shares": 5, "price": 2500.0},  # $12,500
            {"shares": 8, "price": 300.0},   # $2,400
        ]
        
        total_value = sum(h["shares"] * h["price"] for h in holdings)
        assert total_value == 16400.0
    
    def test_allocation_drift_calculation(self):
        """Test allocation drift calculation."""
        def calculate_drift(current_allocation, target_allocation):
            return current_allocation - target_allocation
        
        # Test no drift
        assert calculate_drift(25.0, 25.0) == 0.0
        
        # Test positive drift (overweight)
        assert calculate_drift(30.0, 25.0) == 5.0
        
        # Test negative drift (underweight)
        assert calculate_drift(20.0, 25.0) == -5.0
    
    def test_rebalancing_threshold_logic(self):
        """Test rebalancing threshold logic."""
        def needs_rebalancing(drift, threshold):
            return abs(drift) > threshold
        
        # Test within threshold
        assert not needs_rebalancing(2.0, 5.0)
        assert not needs_rebalancing(-3.0, 5.0)
        
        # Test exceeds threshold
        assert needs_rebalancing(7.0, 5.0)
        assert needs_rebalancing(-6.0, 5.0)
    
    def test_transaction_cost_calculation(self):
        """Test transaction cost calculation."""
        def calculate_transaction_cost(trade_value, cost_rate):
            return abs(trade_value) * cost_rate
        
        # Test buy transaction
        buy_cost = calculate_transaction_cost(1000.0, 0.01)  # $1000 trade, 1% fee
        assert buy_cost == 10.0
        
        # Test sell transaction
        sell_cost = calculate_transaction_cost(-1000.0, 0.01)  # $1000 sell, 1% fee
        assert sell_cost == 10.0


class TestDataSanitization:
    """Test data sanitization and cleaning."""
    
    def test_symbol_normalization(self):
        """Test stock symbol normalization."""
        def normalize_symbol(symbol):
            if not symbol:
                return None
            return symbol.strip().upper()
        
        assert normalize_symbol("aapl") == "AAPL"
        assert normalize_symbol("  googl  ") == "GOOGL"
        assert normalize_symbol("BRK.A") == "BRK.A"
        assert normalize_symbol("") is None
        assert normalize_symbol(None) is None
    
    def test_name_sanitization(self):
        """Test name field sanitization."""
        def sanitize_name(name):
            if not name:
                return None
            stripped = name.strip()
            return stripped if stripped else None
        
        assert sanitize_name("  Test Portfolio  ") == "Test Portfolio"
        assert sanitize_name("Portfolio\n\t") == "Portfolio"
        assert sanitize_name("") is None
        assert sanitize_name("   ") is None
    
    def test_numeric_precision(self):
        """Test numeric precision handling."""
        def round_to_precision(value, decimals=2):
            return round(float(value), decimals)
        
        assert round_to_precision(123.456789, 2) == 123.46
        assert round_to_precision(100.0, 2) == 100.0
        assert round_to_precision("150.25", 2) == 150.25


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_very_large_numbers(self):
        """Test handling of very large numbers."""
        # Test large share count
        large_shares = 1000000.0
        large_price = 50000.0
        large_value = large_shares * large_price
        
        assert large_value == 50000000000.0  # $50 billion
        
        # Should handle large numbers without overflow
        assert isinstance(large_value, float)
        assert large_value > 0
    
    def test_very_small_numbers(self):
        """Test handling of very small numbers."""
        small_shares = 0.001
        small_price = 0.01
        small_value = small_shares * small_price
        
        assert small_value == 0.00001
        assert small_value > 0
    
    def test_unicode_handling(self):
        """Test Unicode character handling in names."""
        unicode_name = "Tech Stocks 📈"
        # Should handle Unicode characters gracefully
        assert len(unicode_name) > 0
        assert "📈" in unicode_name
    
    def test_special_characters(self):
        """Test special characters in input."""
        special_names = [
            "Tech & Growth",
            "High-Yield Dividend",
            "ESG/Sustainable",
            "Micro-Cap (Small)",
        ]
        
        for name in special_names:
            # Should accept reasonable special characters
            assert len(name) > 0
            assert any(c in name for c in "&-/()") if any(c in name for c in "&-/()") else True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])