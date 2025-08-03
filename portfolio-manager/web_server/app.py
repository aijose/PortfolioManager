"""FastAPI application for Portfolio Manager."""

from fastapi import FastAPI, Request, Depends, HTTPException, Form, UploadFile, File
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from models.database import get_db, create_tables
from models.portfolio import Portfolio, Holding
from controllers.portfolio_controller import (
    PortfolioController, 
    PortfolioCreate, 
    HoldingCreate, 
    HoldingUpdate
)
from utils.csv_parser import CSVPortfolioParser
from utils.validators import validate_file_extension
from controllers.rebalancing_controller import RebalancingController
from web_server.routes.portfolios import router as portfolios_router
from web_server.routes.stock_data import router as stock_data_router
from web_server.routes.rebalancing import router as rebalancing_router

# Create FastAPI app
app = FastAPI(
    title="Portfolio Manager",
    description="A web-based stock portfolio management and rebalancing application",
    version="0.1.0"
)

# Include API routers
app.include_router(portfolios_router)
app.include_router(stock_data_router)
app.include_router(rebalancing_router)

# Mount static files
app.mount("/static", StaticFiles(directory="web_server/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="web_server/templates")

# Create database tables on startup
@app.on_event("startup")
async def startup_event():
    create_tables()


# Home page - redirect to portfolios
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return RedirectResponse(url="/portfolios")


# Portfolio routes
@app.get("/portfolios", response_class=HTMLResponse)
async def list_portfolios(request: Request, db: Session = Depends(get_db)):
    """Display list of all portfolios."""
    controller = PortfolioController(db)
    portfolios = controller.get_portfolios()
    
    # Calculate summary for each portfolio
    portfolio_summaries = []
    for portfolio in portfolios:
        summary = controller.calculate_portfolio_summary(portfolio.id)
        portfolio_summaries.append({
            "portfolio": portfolio,
            "summary": summary
        })
    
    return templates.TemplateResponse("portfolios/list.html", {
        "request": request,
        "portfolio_summaries": portfolio_summaries
    })


@app.get("/portfolios/new", response_class=HTMLResponse)
async def new_portfolio_form(request: Request):
    """Display form to create a new portfolio."""
    return templates.TemplateResponse("portfolios/new.html", {
        "request": request
    })


@app.post("/portfolios", response_class=HTMLResponse)
async def create_portfolio(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new portfolio."""
    controller = PortfolioController(db)
    
    try:
        portfolio_data = PortfolioCreate(name=name)
        portfolio = controller.create_portfolio(portfolio_data)
        return RedirectResponse(url=f"/portfolios/{portfolio.id}", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse("portfolios/new.html", {
            "request": request,
            "error": str(e),
            "name": name
        })


@app.get("/portfolios/{portfolio_id}", response_class=HTMLResponse)
async def view_portfolio(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    """Display portfolio details."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    holdings = controller.get_portfolio_holdings(portfolio_id)
    summary = controller.calculate_portfolio_summary(portfolio_id)
    
    return templates.TemplateResponse("portfolios/detail.html", {
        "request": request,
        "portfolio": portfolio,
        "holdings": holdings,
        "summary": summary
    })


@app.post("/portfolios/{portfolio_id}/delete", response_class=HTMLResponse)
async def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Delete a portfolio."""
    controller = PortfolioController(db)
    success = controller.delete_portfolio(portfolio_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return RedirectResponse(url="/portfolios", status_code=303)


@app.get("/portfolios/{portfolio_id}/import", response_class=HTMLResponse)
async def import_csv_form(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    """Display CSV import form."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    # Generate sample CSV for display
    parser = CSVPortfolioParser()
    sample_csv = parser.generate_sample_csv()
    
    return templates.TemplateResponse("portfolios/import.html", {
        "request": request,
        "portfolio": portfolio,
        "sample_csv": sample_csv
    })


@app.post("/portfolios/{portfolio_id}/import", response_class=HTMLResponse)
async def import_csv_upload(
    request: Request,
    portfolio_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """Handle CSV file upload and import."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    errors = []
    warnings = []
    success = False
    imported_count = 0
    
    try:
        # Validate file type
        if not validate_file_extension(file.filename, ['.csv']):
            errors.append("Only CSV files are allowed")
        else:
            # Read and process file
            content = await file.read()
            content_str = content.decode('utf-8')
            
            parser = CSVPortfolioParser()
            
            # Validate file size
            if not parser.validate_file_size(content_str):
                errors.append("File size exceeds 1MB limit")
            else:
                # Parse CSV
                holdings_data, parse_errors, parse_warnings = parser.parse_csv_content(content_str)
                errors.extend(parse_errors)
                warnings.extend(parse_warnings)
                
                if not errors:
                    # Import data
                    import_result = controller.import_holdings_from_csv(portfolio_id, holdings_data)
                    success = import_result["success"]
                    imported_count = import_result["imported_count"]
                    errors.extend(import_result["errors"])
    
    except UnicodeDecodeError:
        errors.append("File is not a valid CSV file")
    except Exception as e:
        errors.append(f"Failed to process file: {str(e)}")
    
    if success and not errors:
        return RedirectResponse(url=f"/portfolios/{portfolio_id}?imported={imported_count}", status_code=303)
    else:
        # Generate sample CSV for redisplay
        parser = CSVPortfolioParser()
        sample_csv = parser.generate_sample_csv()
        
        return templates.TemplateResponse("portfolios/import.html", {
            "request": request,
            "portfolio": portfolio,
            "sample_csv": sample_csv,
            "errors": errors,
            "warnings": warnings,
            "filename": file.filename
        })


@app.get("/portfolios/{portfolio_id}/holdings/new", response_class=HTMLResponse)
async def new_holding_form(request: Request, portfolio_id: int, db: Session = Depends(get_db)):
    """Display form to add a new holding."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    return templates.TemplateResponse("portfolios/holding_form.html", {
        "request": request,
        "portfolio": portfolio,
        "action": "add"
    })


@app.post("/portfolios/{portfolio_id}/holdings", response_class=HTMLResponse)
async def create_holding_web(
    request: Request,
    portfolio_id: int,
    symbol: str = Form(...),
    shares: float = Form(...),
    target_allocation: float = Form(...),
    db: Session = Depends(get_db)
):
    """Create a new holding via web form."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    try:
        holding_data = HoldingCreate(
            symbol=symbol,
            shares=shares,
            target_allocation=target_allocation
        )
        controller.add_holding(portfolio_id, holding_data)
        return RedirectResponse(url=f"/portfolios/{portfolio_id}?added={symbol}", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse("portfolios/holding_form.html", {
            "request": request,
            "portfolio": portfolio,
            "action": "add",
            "error": str(e),
            "symbol": symbol,
            "shares": shares,
            "target_allocation": target_allocation
        })


@app.get("/portfolios/{portfolio_id}/holdings/{symbol}/edit", response_class=HTMLResponse)
async def edit_holding_form(request: Request, portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    """Display form to edit a holding."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    holdings = controller.get_portfolio_holdings(portfolio_id)
    holding = next((h for h in holdings if h.symbol == symbol), None)
    
    if not holding:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    return templates.TemplateResponse("portfolios/holding_form.html", {
        "request": request,
        "portfolio": portfolio,
        "action": "edit",
        "symbol": holding.symbol,
        "shares": holding.shares,
        "target_allocation": holding.target_allocation
    })


@app.post("/portfolios/{portfolio_id}/holdings/{symbol}/edit", response_class=HTMLResponse)
async def update_holding_web(
    request: Request,
    portfolio_id: int,
    symbol: str,
    shares: float = Form(...),
    target_allocation: float = Form(...),
    db: Session = Depends(get_db)
):
    """Update a holding via web form."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    try:
        holding_data = HoldingUpdate(
            shares=shares,
            target_allocation=target_allocation
        )
        updated_holding = controller.update_holding(portfolio_id, symbol, holding_data)
        
        if not updated_holding:
            raise HTTPException(status_code=404, detail="Holding not found")
        
        return RedirectResponse(url=f"/portfolios/{portfolio_id}?updated={symbol}", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse("portfolios/holding_form.html", {
            "request": request,
            "portfolio": portfolio,
            "action": "edit",
            "error": str(e),
            "symbol": symbol,
            "shares": shares,
            "target_allocation": target_allocation
        })


@app.post("/portfolios/{portfolio_id}/holdings/{symbol}/delete", response_class=HTMLResponse)
async def delete_holding_web(portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    """Delete a holding via web form."""
    controller = PortfolioController(db)
    success = controller.delete_holding(portfolio_id, symbol)
    
    if not success:
        raise HTTPException(status_code=404, detail="Holding not found")
    
    return RedirectResponse(url=f"/portfolios/{portfolio_id}?deleted={symbol}", status_code=303)


@app.post("/portfolios/{portfolio_id}/refresh-prices", response_class=HTMLResponse)
async def refresh_portfolio_prices_web(portfolio_id: int, db: Session = Depends(get_db)):
    """Refresh all portfolio prices via web interface."""
    controller = PortfolioController(db)
    
    portfolio = controller.get_portfolio(portfolio_id)
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    result = controller.refresh_portfolio_prices(portfolio_id)
    
    if result["success"]:
        message = f"refreshed={result['updated_count']}&failed={result['failed_count']}"
        if result["failed_symbols"]:
            failed_symbols = ",".join(result["failed_symbols"])
            message += f"&failed_symbols={failed_symbols}"
    else:
        message = f"error={result.get('error', 'Failed to refresh prices')}"
    
    return RedirectResponse(url=f"/portfolios/{portfolio_id}?{message}", status_code=303)


@app.post("/portfolios/{portfolio_id}/holdings/{symbol}/refresh-price", response_class=HTMLResponse)
async def refresh_single_price_web(portfolio_id: int, symbol: str, db: Session = Depends(get_db)):
    """Refresh single holding price via web interface."""
    controller = PortfolioController(db)
    
    result = controller.update_single_holding_price(portfolio_id, symbol)
    
    if result["success"]:
        message = f"price_updated={symbol}&new_price={result['price']:.2f}"
    else:
        message = f"price_error={result.get('error', 'Failed to update price')}"
    
    return RedirectResponse(url=f"/portfolios/{portfolio_id}?{message}", status_code=303)


@app.get("/portfolios/{portfolio_id}/rebalancing", response_class=HTMLResponse)
async def view_rebalancing_analysis(
    request: Request, 
    portfolio_id: int, 
    tolerance: Optional[float] = 2.0,
    cost_rate: Optional[float] = 0.005,
    db: Session = Depends(get_db)
):
    """Display rebalancing analysis page."""
    controller = PortfolioController(db)
    portfolio = controller.get_portfolio(portfolio_id)
    
    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")
    
    try:
        rebalancing_controller = RebalancingController(
            db, 
            tolerance_threshold=tolerance,
            transaction_cost_rate=cost_rate
        )
        
        analysis = rebalancing_controller.analyze_portfolio_rebalancing(portfolio_id)
        
        # Calculate cost percentage
        cost_percentage = (analysis.total_transaction_cost / analysis.total_value * 100) if analysis.total_value > 0 else 0
        
        return templates.TemplateResponse("portfolios/rebalancing.html", {
            "request": request,
            "portfolio": portfolio,
            "is_balanced": analysis.is_balanced,
            "total_value": analysis.total_value,
            "tolerance_threshold": analysis.tolerance_threshold,
            "transaction_cost_rate": cost_rate,
            "allocation_drifts": analysis.allocation_drifts,
            "transactions": analysis.transactions,
            "transaction_count": len(analysis.transactions),
            "total_transaction_cost": analysis.total_transaction_cost,
            "cost_percentage": cost_percentage,
            "estimated_final_value": analysis.estimated_final_value
        })
        
    except ValueError as e:
        return templates.TemplateResponse("portfolios/rebalancing.html", {
            "request": request,
            "portfolio": portfolio,
            "error": str(e),
            "is_balanced": True,
            "total_value": 0,
            "tolerance_threshold": tolerance,
            "transaction_cost_rate": cost_rate,
            "allocation_drifts": [],
            "transactions": [],
            "transaction_count": 0,
            "total_transaction_cost": 0,
            "cost_percentage": 0,
            "estimated_final_value": 0
        })


# API endpoints for AJAX requests
@app.get("/api/portfolios", response_model=List[dict])
async def api_list_portfolios(db: Session = Depends(get_db)):
    """API endpoint to get all portfolios."""
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


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "portfolio-manager"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)