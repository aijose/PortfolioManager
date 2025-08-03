"""Validation utilities for the Portfolio Manager application."""

import re
from typing import Optional


def validate_stock_symbol(symbol: str) -> bool:
    """
    Validate a stock symbol.
    
    Args:
        symbol: The stock symbol to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol:
        return False
    
    # Remove whitespace and convert to uppercase
    symbol = symbol.strip().upper()
    
    # Check length (1-10 characters)
    if len(symbol) < 1 or len(symbol) > 10:
        return False
    
    # Check that it contains only letters and numbers
    if not re.match(r'^[A-Z0-9]+$', symbol):
        return False
    
    return True


def validate_allocation_sum(allocations: list) -> tuple[bool, float]:
    """
    Validate that allocations sum to approximately 100%.
    
    Args:
        allocations: List of allocation percentages
        
    Returns:
        Tuple of (is_valid, total_sum)
    """
    total = sum(allocations)
    is_valid = abs(total - 100.0) <= 0.01
    return is_valid, total


def validate_shares_amount(shares: float) -> bool:
    """
    Validate shares amount.
    
    Args:
        shares: Number of shares
        
    Returns:
        True if valid, False otherwise
    """
    return shares >= 0


def validate_allocation_percentage(allocation: float) -> bool:
    """
    Validate allocation percentage.
    
    Args:
        allocation: Allocation percentage
        
    Returns:
        True if valid, False otherwise
    """
    return 0 < allocation <= 100


def sanitize_portfolio_name(name: str) -> str:
    """
    Sanitize portfolio name for safe storage.
    
    Args:
        name: Portfolio name to sanitize
        
    Returns:
        Sanitized portfolio name
    """
    if not name:
        return ""
    
    # Remove leading/trailing whitespace
    name = name.strip()
    
    # Limit length
    if len(name) > 100:
        name = name[:100]
    
    return name


def validate_file_extension(filename: str, allowed_extensions: list = None) -> bool:
    """
    Validate file extension.
    
    Args:
        filename: Name of the file
        allowed_extensions: List of allowed extensions (default: ['.csv'])
        
    Returns:
        True if valid, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = ['.csv']
    
    if not filename:
        return False
    
    # Extract extension
    extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
    
    return extension in allowed_extensions


def format_currency(amount: float) -> str:
    """
    Format amount as currency string.
    
    Args:
        amount: Amount to format
        
    Returns:
        Formatted currency string
    """
    return f"${amount:,.2f}"


def format_percentage(percentage: float, decimal_places: int = 1) -> str:
    """
    Format percentage string.
    
    Args:
        percentage: Percentage to format
        decimal_places: Number of decimal places
        
    Returns:
        Formatted percentage string
    """
    return f"{percentage:.{decimal_places}f}%"


def validate_csv_headers(headers: list, required_headers: list) -> tuple[bool, list]:
    """
    Validate CSV headers against required headers (case-insensitive).
    
    Args:
        headers: List of headers from CSV file
        required_headers: List of required headers
        
    Returns:
        Tuple of (is_valid, missing_headers)
    """
    if not headers:
        return False, required_headers
    
    # Convert to lowercase for comparison
    headers_lower = [h.lower().strip() for h in headers]
    required_lower = [h.lower() for h in required_headers]
    
    missing = [req for req in required_headers if req.lower() not in headers_lower]
    
    return len(missing) == 0, missing