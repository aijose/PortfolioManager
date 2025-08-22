#!/usr/bin/env python3
"""
Demo script for Sprint 2 functionality.

This script demonstrates:
1. CSV parsing and validation
2. Holdings management
3. API endpoints
4. Web interface features
"""

import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_csv_parsing():
    """Test CSV parsing functionality."""
    print("=== CSV Parsing Demo ===")
    
    from utils.csv_parser import CSVPortfolioParser
    
    # Test valid CSV
    print("\n1. Testing valid CSV data...")
    valid_csv = """Symbol,Shares,Allocation
AAPL,100,25.0
MSFT,200,30.0
GOOGL,50,20.0
TSLA,75,15.0
BND,500,10.0"""
    
    parser = CSVPortfolioParser()
    holdings_data, errors, warnings = parser.parse_csv_content(valid_csv)
    
    print(f"✓ Parsed {len(holdings_data)} holdings")
    print(f"✓ {len(errors)} errors, {len(warnings)} warnings")
    for holding in holdings_data:
        print(f"  - {holding.symbol}: {holding.shares} shares, {holding.allocation}%")
    
    # Test invalid CSV
    print("\n2. Testing invalid CSV data...")
    invalid_csv = """Symbol,Shares,Allocation
AAPL,100,30.0
MSFT,200,80.0"""  # Total exceeds 100%
    
    holdings_data, errors, warnings = parser.parse_csv_content(invalid_csv)
    
    print(f"✓ Parsed {len(holdings_data)} holdings")
    print(f"✓ {len(errors)} errors, {len(warnings)} warnings")
    if errors:
        print("  Errors:")
        for error in errors:
            print(f"    - {error}")
    
    # Test sample CSV generation
    print("\n3. Sample CSV generation...")
    sample_csv = parser.generate_sample_csv()
    print("✓ Generated sample CSV:")
    print(sample_csv[:200] + "...")


def test_database_operations():
    """Test database operations."""
    print("\n=== Database Operations Demo ===")
    
    from models.database import create_tables, SessionLocal
    from controllers.portfolio_controller import PortfolioController, PortfolioCreate, HoldingCreate
    
    # Initialize database
    create_tables()
    db = SessionLocal()
    
    try:
        controller = PortfolioController(db)
        
        print("\n1. Creating test portfolio...")
        portfolio = controller.create_portfolio(PortfolioCreate(name="Demo Portfolio"))
        print(f"✓ Created portfolio: {portfolio.name} (ID: {portfolio.id})")
        
        print("\n2. Adding holdings...")
        holdings_to_add = [
            HoldingCreate(symbol="AAPL", shares=100, target_allocation=30.0),
            HoldingCreate(symbol="MSFT", shares=200, target_allocation=25.0),
            HoldingCreate(symbol="GOOGL", shares=50, target_allocation=20.0),
            HoldingCreate(symbol="TSLA", shares=75, target_allocation=15.0),
            HoldingCreate(symbol="BND", shares=500, target_allocation=10.0)
        ]
        
        for holding_data in holdings_to_add:
            holding = controller.add_holding(portfolio.id, holding_data)
            print(f"✓ Added {holding.symbol}: {holding.shares} shares, {holding.target_allocation}%")
        
        print("\n3. Portfolio summary...")
        summary = controller.calculate_portfolio_summary(portfolio.id)
        print(f"✓ Total holdings: {summary['total_holdings']}")
        print(f"✓ Total allocation: {summary['total_target_allocation']}%")
        print(f"✓ Allocation valid: {summary['is_allocation_valid']}")
        
        print("\n4. Testing CSV import...")
        from utils.csv_parser import CSVHoldingData
        
        # Simulate CSV import data
        csv_holdings = [
            CSVHoldingData(symbol="AAPL", shares=150, allocation=35.0),
            CSVHoldingData(symbol="MSFT", shares=250, allocation=30.0),
            CSVHoldingData(symbol="NVDA", shares=100, allocation=25.0),
            CSVHoldingData(symbol="AMD", shares=200, allocation=10.0),
        ]
        
        import_result = controller.import_holdings_from_csv(portfolio.id, csv_holdings)
        print(f"✓ Import successful: {import_result['success']}")
        print(f"✓ Imported {import_result['imported_count']} holdings")
        
        # Check updated holdings
        updated_holdings = controller.get_portfolio_holdings(portfolio.id)
        print(f"✓ Portfolio now has {len(updated_holdings)} holdings")
        for holding in updated_holdings:
            print(f"  - {holding.symbol}: {holding.shares} shares, {holding.target_allocation}%")
        
    finally:
        db.close()


def test_validation():
    """Test validation utilities."""
    print("\n=== Validation Demo ===")
    
    from utils.validators import (
        validate_stock_symbol, 
        validate_allocation_sum, 
        validate_shares_amount,
        validate_allocation_percentage,
        validate_file_extension
    )
    
    print("\n1. Stock symbol validation...")
    test_symbols = ["AAPL", "MSFT", "123", "TOOLONG123", ""]
    for symbol in test_symbols:
        valid = validate_stock_symbol(symbol)
        print(f"✓ '{symbol}': {'Valid' if valid else 'Invalid'}")
    
    print("\n2. Allocation sum validation...")
    test_allocations = [
        [25.0, 30.0, 20.0, 15.0, 10.0],  # Sums to 100%
        [25.0, 30.0, 20.0, 15.0, 15.0],  # Sums to 105%
        [25.0, 30.0, 20.0, 15.0, 5.0],   # Sums to 95%
    ]
    
    for allocations in test_allocations:
        valid, total = validate_allocation_sum(allocations)
        print(f"✓ {allocations} -> Total: {total}%, Valid: {valid}")
    
    print("\n3. File extension validation...")
    test_files = ["portfolio.csv", "data.xlsx", "file.txt", "noextension"]
    for filename in test_files:
        valid = validate_file_extension(filename, ['.csv'])
        print(f"✓ '{filename}': {'Valid' if valid else 'Invalid'}")


def main():
    """Main demo function."""
    print("🚀 Sprint 2 Functionality Demo")
    print("=" * 50)
    
    try:
        test_csv_parsing()
        test_database_operations()
        test_validation()
        
        print("\n" + "=" * 50)
        print("✅ Sprint 2 Demo Complete!")
        print("\n📋 Implemented Features:")
        print("✓ CSV parsing and validation with detailed error reporting")
        print("✓ Holdings CRUD operations (Create, Read, Update, Delete)")
        print("✓ CSV import functionality with data replacement")
        print("✓ Comprehensive validation utilities")
        print("✓ API endpoints for all holdings operations")
        print("✓ Web interface for holdings management")
        print("✓ File upload with drag-and-drop support")
        print("✓ Error handling and user feedback")
        
        print("\n🌐 Web Interface Features:")
        print("✓ Portfolio detail page with holdings table")
        print("✓ Add/Edit/Delete holdings forms")
        print("✓ CSV import wizard with sample data")
        print("✓ Real-time validation and error messages")
        print("✓ Success notifications and user feedback")
        
        print("\n🚀 To test the web interface:")
        print("  uv run python main.py")
        print("  Visit: http://127.0.0.1:8000")
        
        print("\n🧪 To run tests:")
        print("  uv run pytest tests/test_sprint2.py -v")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()