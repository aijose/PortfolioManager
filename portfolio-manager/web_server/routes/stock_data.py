"""Stock data API routes."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from models.database import get_db
from controllers.stock_data_controller import StockDataController
from controllers.portfolio_controller import PortfolioController

router = APIRouter(prefix="/api/stocks", tags=["stock-data"])


@router.get("/{symbol}/price")
async def get_stock_price(symbol: str, use_cache: bool = True):
    """Get current price for a single stock symbol."""
    controller = StockDataController()
    
    price_data = controller.get_stock_price(symbol, use_cache=use_cache)
    
    if not price_data:
        raise HTTPException(status_code=404, detail=f"Price data not found for symbol: {symbol}")
    
    return price_data.to_dict()


@router.post("/prices")
async def get_multiple_stock_prices(symbols: List[str], use_cache: bool = True):
    """Get current prices for multiple stock symbols."""
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
    
    if len(symbols) > 50:
        raise HTTPException(status_code=400, detail="Maximum 50 symbols allowed per request")
    
    controller = StockDataController()
    price_results = controller.get_multiple_stock_prices(symbols, use_cache=use_cache)
    
    # Convert to JSON-serializable format
    response_data = {}
    for symbol, price_data in price_results.items():
        if price_data:
            response_data[symbol] = price_data.to_dict()
        else:
            response_data[symbol] = None
    
    return response_data


@router.post("/validate")
async def validate_symbols(symbols: List[str]):
    """Validate that stock symbols exist and can be fetched."""
    if not symbols:
        raise HTTPException(status_code=400, detail="No symbols provided")
    
    controller = StockDataController()
    validation_results = controller.validate_symbols(symbols)
    
    return {
        "validation_results": validation_results,
        "valid_symbols": [s for s, valid in validation_results.items() if valid],
        "invalid_symbols": [s for s, valid in validation_results.items() if not valid]
    }


@router.get("/market-summary")
async def get_market_summary():
    """Get general market summary information."""
    controller = StockDataController()
    return controller.get_market_summary()


@router.delete("/cache")
async def clear_price_cache():
    """Clear the price cache."""
    controller = StockDataController()
    controller.clear_cache()
    
    return {"message": "Price cache cleared successfully"}


@router.get("/cache/stats")
async def get_cache_stats():
    """Get cache statistics."""
    controller = StockDataController()
    return controller.get_cache_stats()


# Portfolio-specific price update routes
@router.post("/portfolios/{portfolio_id}/refresh-prices")
async def refresh_portfolio_prices(portfolio_id: int, db: Session = Depends(get_db)):
    """Refresh prices for all holdings in a portfolio."""
    controller = PortfolioController(db)
    
    # Check if portfolio exists
    portfolio = controller.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Refresh prices
    result = controller.refresh_portfolio_prices(portfolio_id)
    
    if not result["success"]:
        raise HTTPException(status_code=500, detail=result.get("error", "Failed to refresh prices"))
    
    return result


@router.post("/portfolios/{portfolio_id}/holdings/{symbol}/refresh-price")
async def refresh_single_holding_price(portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    """Refresh price for a single holding."""
    controller = PortfolioController(db)
    
    result = controller.update_single_holding_price(portfolio_id, symbol)
    
    if not result["success"]:
        if "not found" in result.get("error", "").lower():
            raise HTTPException(status_code=404, detail=result["error"])
        else:
            raise HTTPException(status_code=500, detail=result["error"])
    
    return result


@router.get("/portfolios/{portfolio_id}/valuation")
async def get_portfolio_valuation(portfolio_id: int, db: Session = Depends(get_db)):
    """Get detailed portfolio valuation and performance metrics."""
    controller = PortfolioController(db)
    
    # Check if portfolio exists
    portfolio = controller.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return controller.get_portfolio_valuation(portfolio_id)


@router.get("/portfolios/{portfolio_id}/validate-symbols")
async def validate_portfolio_symbols(portfolio_id: int, db: Session = Depends(get_db)):
    """Validate all stock symbols in a portfolio."""
    controller = PortfolioController(db)
    
    # Check if portfolio exists
    portfolio = controller.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return controller.validate_portfolio_symbols(portfolio_id)