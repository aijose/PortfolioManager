"""FastAPI application for Portfolio Manager."""

from fastapi import FastAPI, Request, Depends, HTTPException, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
from typing import List

from models.database import get_db, create_tables
from models.portfolio import Portfolio
from controllers.portfolio_controller import PortfolioController, PortfolioCreate

# Create FastAPI app
app = FastAPI(
    title="Portfolio Manager",
    description="A web-based stock portfolio management and rebalancing application",
    version="0.1.0"
)

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