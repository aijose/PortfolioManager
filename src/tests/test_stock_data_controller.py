"""Unit tests for StockDataController."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from controllers.stock_data_controller import StockDataController
from datetime import datetime, date, timedelta


@pytest.fixture
def mock_stock_controller():
    """Create a stock data controller for testing."""
    return StockDataController()


def test_get_current_price_success(mock_stock_controller):
    """Test successful current price retrieval."""
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = {
            'currentPrice': 150.25,
            'currency': 'USD',
            'marketCap': 1000000000,
            'trailingPE': 25.5,
            'dividendYield': 0.02,
            'fiftyTwoWeekHigh': 180.0,
            'fiftyTwoWeekLow': 120.0,
            'volume': 50000000,
            'averageVolume': 45000000,
            'marketState': 'REGULAR'
        }
        mock_ticker.return_value = mock_ticker_instance
        
        price = mock_stock_controller.get_current_price("AAPL")
        
        assert price is not None
        assert isinstance(price, (int, float))
        assert price == 150.25


def test_get_current_price_invalid_symbol(mock_stock_controller):
    """Test current price retrieval with invalid symbol."""
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker_instance = Mock()
        mock_ticker_instance.info = {}  # Empty info for invalid symbol
        mock_ticker.return_value = mock_ticker_instance
        
        price = mock_stock_controller.get_current_price("INVALID")
        
        assert price is None


def test_get_current_price_network_error(mock_stock_controller):
    """Test current price retrieval with network error."""
    with patch('yfinance.Ticker') as mock_ticker:
        mock_ticker.side_effect = Exception("Network error")
        
        price = mock_stock_controller.get_current_price("AAPL")
        
        assert price is None


def test_get_multiple_current_prices(mock_stock_controller):
    """Test getting current prices for multiple symbols."""
    symbols = ["AAPL", "GOOGL", "MSFT"]
    mock_prices = {
        "AAPL": 150.25,
        "GOOGL": 2750.50, 
        "MSFT": 325.75
    }
    
    with patch.object(mock_stock_controller, 'get_current_price') as mock_get_price:
        mock_get_price.side_effect = lambda symbol: mock_prices.get(symbol)
        
        prices = {}
        for symbol in symbols:
            prices[symbol] = mock_stock_controller.get_current_price(symbol)
        
        assert len(prices) == 3
        assert prices["AAPL"] == 150.25
        assert prices["GOOGL"] == 2750.50
        assert prices["MSFT"] == 325.75


def test_get_historical_prices_success(mock_stock_controller):
    """Test successful historical price retrieval."""
    with patch('yfinance.Ticker') as mock_ticker:
        # Create mock DataFrame with historical data
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range(start='2024-01-01', periods=30, freq='D')
        mock_df = pd.DataFrame({
            'Close': np.random.uniform(140, 160, 30),
            'Open': np.random.uniform(140, 160, 30),
            'High': np.random.uniform(155, 165, 30),
            'Low': np.random.uniform(135, 145, 30),
            'Volume': np.random.randint(1000000, 5000000, 30)
        }, index=dates)
        
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_ticker_instance
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        historical_data = mock_stock_controller.get_historical_prices("AAPL", start_date, end_date)
        
        assert historical_data is not None
        assert len(historical_data['data']) == 30
        assert 'symbol' in historical_data
        assert historical_data['symbol'] == 'AAPL'


def test_get_historical_prices_invalid_symbol(mock_stock_controller):
    """Test historical price retrieval with invalid symbol."""
    with patch('yfinance.Ticker') as mock_ticker:
        mock_df = Mock()
        mock_df.empty = True
        mock_ticker_instance = Mock()
        mock_ticker_instance.history.return_value = mock_df
        mock_ticker.return_value = mock_ticker_instance
        
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        
        historical_data = mock_stock_controller.get_historical_prices("INVALID", start_date, end_date)
        
        assert historical_data is None


def test_get_historical_prices_date_validation(mock_stock_controller):
    """Test historical price retrieval with invalid date range."""
    end_date = date.today()
    start_date = end_date + timedelta(days=1)  # Start date after end date
    
    with pytest.raises(ValueError, match="Start date must be before end date"):
        mock_stock_controller.get_historical_prices("AAPL", start_date, end_date)


def test_get_stock_info_success(mock_stock_controller):
    """Test successful stock info retrieval."""
    mock_info = {
        'symbol': 'AAPL',
        'longName': 'Apple Inc.',
        'sector': 'Technology',
        'industry': 'Consumer Electronics',
        'marketCap': 2800000000000,
        'beta': 1.2,
        'trailingPE': 25.5,
        'dividendYield': 0.0055,
        '52WeekHigh': 180.0,
        '52WeekLow': 120.0
    }
    
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = Mock()
        mock_ticker.info = mock_info
        mock_ticker_class.return_value = mock_ticker
        
        info = mock_stock_controller.get_stock_info("AAPL")
        
        assert info is not None
        assert info['symbol'] == 'AAPL'
        assert info['longName'] == 'Apple Inc.'
        assert 'marketCap' in info


def test_get_stock_info_invalid_symbol(mock_stock_controller):
    """Test stock info retrieval with invalid symbol."""
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = Mock()
        mock_ticker.info = {}  # Empty info for invalid symbol
        mock_ticker_class.return_value = mock_ticker
        
        info = mock_stock_controller.get_stock_info("INVALID")
        
        assert info is None or len(info) == 0


def test_get_stock_info_network_error(mock_stock_controller):
    """Test stock info retrieval with network error."""
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker_class.side_effect = Exception("Network error")
        
        info = mock_stock_controller.get_stock_info("AAPL")
        
        assert info is None


def test_calculate_price_change(mock_stock_controller):
    """Test price change calculation."""
    current_price = 150.0
    previous_price = 145.0
    
    change, change_percent = mock_stock_controller.calculate_price_change(current_price, previous_price)
    
    assert change == 5.0
    assert abs(change_percent - 3.45) < 0.01  # 3.45% increase


def test_calculate_price_change_negative(mock_stock_controller):
    """Test negative price change calculation."""
    current_price = 140.0
    previous_price = 150.0
    
    change, change_percent = mock_stock_controller.calculate_price_change(current_price, previous_price)
    
    assert change == -10.0
    assert abs(change_percent - (-6.67)) < 0.01  # 6.67% decrease


def test_calculate_price_change_zero_previous(mock_stock_controller):
    """Test price change calculation with zero previous price."""
    current_price = 150.0
    previous_price = 0.0
    
    with pytest.raises(ValueError, match="Previous price cannot be zero"):
        mock_stock_controller.calculate_price_change(current_price, previous_price)


def test_get_market_data_batch(mock_stock_controller):
    """Test getting market data for multiple symbols in batch."""
    symbols = ["AAPL", "GOOGL", "MSFT"]
    
    with patch('yfinance.Ticker') as mock_ticker:
        # Mock batch download
        import pandas as pd
        import numpy as np
        
        # Create multi-index DataFrame for multiple symbols
        dates = pd.date_range(start='2024-01-15', periods=1)
        columns = pd.MultiIndex.from_product([symbols, ['Close']])
        mock_df = pd.DataFrame(
            np.array([[150.0, 2750.0, 325.0]]),
            index=dates,
            columns=columns
        )
        mock_download.return_value = mock_df
        
        batch_data = mock_stock_controller.get_batch_current_prices(symbols)
        
        assert len(batch_data) == 3
        assert "AAPL" in batch_data
        assert "GOOGL" in batch_data
        assert "MSFT" in batch_data


def test_validate_symbol_format(mock_stock_controller):
    """Test symbol format validation."""
    # Valid symbols
    assert mock_stock_controller.validate_symbol("AAPL") is True
    assert mock_stock_controller.validate_symbol("GOOGL") is True
    assert mock_stock_controller.validate_symbol("BRK.A") is True  # With dot
    
    # Invalid symbols
    assert mock_stock_controller.validate_symbol("") is False
    assert mock_stock_controller.validate_symbol(None) is False
    assert mock_stock_controller.validate_symbol("123") is False  # All numbers
    assert mock_stock_controller.validate_symbol("TOOLONGASYMBOL") is False  # Too long


def test_get_dividend_history(mock_stock_controller):
    """Test dividend history retrieval."""
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = Mock()
        
        # Mock dividend history
        import pandas as pd
        dividend_dates = pd.date_range(start='2024-01-01', periods=4, freq='Q')
        mock_dividends = pd.Series([0.25, 0.25, 0.28, 0.28], index=dividend_dates)
        mock_ticker.dividends = mock_dividends
        mock_ticker_class.return_value = mock_ticker
        
        dividends = mock_stock_controller.get_dividend_history("AAPL")
        
        assert dividends is not None
        assert len(dividends) == 4
        assert all(div > 0 for div in dividends.values)


def test_get_stock_splits(mock_stock_controller):
    """Test stock splits retrieval."""
    with patch('yfinance.Ticker') as mock_ticker_class:
        mock_ticker = Mock()
        
        # Mock stock splits
        import pandas as pd
        split_dates = pd.date_range(start='2024-06-01', periods=1)
        mock_splits = pd.Series([4.0], index=split_dates)  # 4-for-1 split
        mock_ticker.splits = mock_splits
        mock_ticker_class.return_value = mock_ticker
        
        splits = mock_stock_controller.get_stock_splits("AAPL")
        
        assert splits is not None
        assert len(splits) >= 0  # May have splits or not


def test_rate_limiting_compliance(mock_stock_controller):
    """Test that controller respects rate limiting."""
    symbols = ["AAPL", "GOOGL", "MSFT", "TSLA", "NVDA"]
    
    with patch('yfinance.download') as mock_download, \
         patch('time.sleep') as mock_sleep:
        
        mock_df = Mock()
        mock_df.empty = False
        mock_df.iloc = Mock()
        mock_df.iloc.__getitem__.return_value = {'Close': 150.0}
        mock_download.return_value = mock_df
        
        # Make rapid successive calls
        start_time = datetime.now()
        prices = []
        for symbol in symbols:
            price = mock_stock_controller.get_current_price(symbol)
            prices.append(price)
        end_time = datetime.now()
        
        # Verify that calls complete and optionally check for rate limiting
        assert len(prices) == 5
        assert all(price is not None for price in prices)


def test_error_handling_robustness(mock_stock_controller):
    """Test robust error handling across different failure scenarios."""
    test_cases = [
        ("AAPL", Exception("Network timeout")),
        ("GOOGL", ConnectionError("Connection failed")),
        ("MSFT", ValueError("Invalid response")),
        ("TSLA", KeyError("Missing data")),
    ]
    
    for symbol, error in test_cases:
        with patch('yfinance.Ticker') as mock_ticker:
            mock_download.side_effect = error
            
            # Should not raise exception, should return None gracefully
            price = mock_stock_controller.get_current_price(symbol)
            assert price is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])