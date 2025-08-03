"""Portfolio-related API routes."""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List

from models.database import get_db
from controllers.portfolio_controller import (
    PortfolioController, 
    HoldingCreate, 
    HoldingUpdate,
    PortfolioCreate,
    PortfolioUpdate
)
from utils.csv_parser import CSVPortfolioParser
from utils.validators import validate_file_extension

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])


@router.get("/", response_model=List[dict])
async def list_portfolios(db: Session = Depends(get_db)):
    """Get all portfolios."""
    controller = PortfolioController(db)
    portfolios = controller.get_portfolios()
    
    return [
        {
            "id": p.id,
            "name": p.name,
            "created_date": p.created_date.isoformat(),
            "modified_date": p.modified_date.isoformat(),
            "holdings_count": len(p.holdings)
        }
        for p in portfolios
    ]


@router.get("/{portfolio_id}", response_model=dict)
async def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Get a specific portfolio."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    summary = controller.calculate_portfolio_summary(portfolio_id)
    
    return {
        "id": portfolio.id,
        "name": portfolio.name,
        "created_date": portfolio.created_date.isoformat(),
        "modified_date": portfolio.modified_date.isoformat(),
        "summary": summary
    }


@router.post("/", response_model=dict)
async def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    """Create a new portfolio."""
    controller = PortfolioController(db)
    
    try:
        new_portfolio = controller.create_portfolio(portfolio)
        return {
            "id": new_portfolio.id,
            "name": new_portfolio.name,
            "created_date": new_portfolio.created_date.isoformat(),
            "message": "Portfolio created successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{portfolio_id}", response_model=dict)
async def update_portfolio(
    portfolio_id: int, 
    portfolio: PortfolioUpdate, 
    db: Session = Depends(get_db)
):
    """Update a portfolio."""
    controller = PortfolioController(db)
    
    try:
        updated_portfolio = controller.update_portfolio(portfolio_id, portfolio)
        if not updated_portfolio:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return {
            "id": updated_portfolio.id,
            "name": updated_portfolio.name,
            "modified_date": updated_portfolio.modified_date.isoformat(),
            "message": "Portfolio updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{portfolio_id}")
async def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Delete a portfolio."""
    controller = PortfolioController(db)
    
    if not controller.delete_portfolio(portfolio_id):
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return {"message": "Portfolio deleted successfully"}


# Holdings endpoints
@router.get("/{portfolio_id}/holdings", response_model=List[dict])
async def get_holdings(portfolio_id: int, db: Session = Depends(get_db)):
    """Get all holdings for a portfolio."""
    controller = PortfolioController(db)
    
    if not controller.get_portfolio(portfolio_id):
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    holdings = controller.get_portfolio_holdings(portfolio_id)
    
    return [
        {
            "symbol": h.symbol,
            "shares": h.shares,
            "target_allocation": h.target_allocation,
            "last_price": h.last_price,
            "current_value": h.current_value,
            "current_allocation_percent": h.current_allocation_percent
        }
        for h in holdings
    ]


@router.post("/{portfolio_id}/holdings", response_model=dict)
async def create_holding(
    portfolio_id: int, 
    holding: HoldingCreate, 
    db: Session = Depends(get_db)
):
    """Add a holding to a portfolio."""
    controller = PortfolioController(db)
    
    try:
        new_holding = controller.add_holding(portfolio_id, holding)
        if not new_holding:
            raise HTTPException(status_code=404, detail="Portfolio not found")
        
        return {
            "symbol": new_holding.symbol,
            "shares": new_holding.shares,
            "target_allocation": new_holding.target_allocation,
            "message": "Holding added successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{portfolio_id}/holdings/{symbol}", response_model=dict)
async def update_holding(
    portfolio_id: int, 
    symbol: str, 
    holding: HoldingUpdate, 
    db: Session = Depends(get_db)
):
    """Update a holding."""
    controller = PortfolioController(db)
    
    try:
        updated_holding = controller.update_holding(portfolio_id, symbol, holding)
        if not updated_holding:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        return {
            "symbol": updated_holding.symbol,
            "shares": updated_holding.shares,
            "target_allocation": updated_holding.target_allocation,
            "message": "Holding updated successfully"
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{portfolio_id}/holdings/{symbol}")
async def delete_holding(portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    """Delete a holding."""
    controller = PortfolioController(db)
    
    if not controller.delete_holding(portfolio_id, symbol):
        raise HTTPException(status_code=404, detail="Holding not found")
    
    return {"message": "Holding deleted successfully"}


# CSV Import endpoints
@router.post("/{portfolio_id}/import-csv")
async def import_csv(
    portfolio_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Import holdings from CSV file."""
    controller = PortfolioController(db)
    
    # Validate portfolio exists
    if not controller.get_portfolio(portfolio_id):
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Validate file type
    if not validate_file_extension(file.filename, ['.csv']):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read file content
        content = await file.read()
        content_str = content.decode('utf-8')
        
        # Parse and validate CSV
        parser = CSVPortfolioParser()
        
        # Check file size
        if not parser.validate_file_size(content_str):
            raise HTTPException(status_code=400, detail="File too large")
        
        holdings_data, errors, warnings = parser.parse_csv_content(content_str)
        
        if errors:
            return JSONResponse(
                status_code=400,
                content={
                    "success": False,
                    "errors": errors,
                    "warnings": warnings,
                    "message": "CSV validation failed"
                }
            )
        
        # Import data
        import_result = controller.import_holdings_from_csv(portfolio_id, holdings_data)
        
        return {
            "success": import_result["success"],
            "imported_count": import_result["imported_count"],
            "errors": import_result["errors"],
            "warnings": warnings,
            "message": f"Successfully imported {import_result['imported_count']} holdings"
        }
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File is not a valid CSV file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process file: {str(e)}")


@router.get("/{portfolio_id}/sample-csv")
async def get_sample_csv(portfolio_id: int, db: Session = Depends(get_db)):
    """Get a sample CSV file for download."""
    controller = PortfolioController(db)
    
    if not controller.get_portfolio(portfolio_id):
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    parser = CSVPortfolioParser()
    sample_content = parser.generate_sample_csv()
    
    return JSONResponse(
        content={"csv_content": sample_content},
        headers={"Content-Type": "application/json"}
    )