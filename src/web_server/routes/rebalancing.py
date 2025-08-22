"""Rebalancing API routes."""

from fastapi import APIRouter, Depends, HTTPException, Form
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional

from models.database import get_db
from controllers.rebalancing_controller import RebalancingController, RebalancingTransaction

router = APIRouter(prefix="/api/rebalancing", tags=["rebalancing"])


@router.get("/portfolios/{portfolio_id}/analysis")
async def analyze_portfolio_rebalancing(
    portfolio_id: int,
    tolerance: Optional[float] = None,
    transaction_cost_rate: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Analyze portfolio for rebalancing needs.
    
    Args:
        portfolio_id: Portfolio to analyze
        tolerance: Custom tolerance threshold in percentage points (default: 2.0)
        transaction_cost_rate: Custom transaction cost rate as decimal (default: 0.005)
    """
    try:
        controller = RebalancingController(db, tolerance_threshold=tolerance or 2.0, 
                                         transaction_cost_rate=transaction_cost_rate or 0.005)
        
        analysis = controller.analyze_portfolio_rebalancing(
            portfolio_id, 
            custom_tolerance=tolerance,
            custom_cost_rate=transaction_cost_rate
        )
        
        # Convert to JSON-serializable format
        return {
            "portfolio_id": analysis.portfolio_id,
            "total_value": analysis.total_value,
            "is_balanced": analysis.is_balanced,
            "tolerance_threshold": analysis.tolerance_threshold,
            "analysis_timestamp": analysis.analysis_timestamp.isoformat(),
            "allocation_drifts": [
                {
                    "symbol": drift.symbol,
                    "current_allocation": drift.current_allocation,
                    "target_allocation": drift.target_allocation,
                    "drift": drift.drift,
                    "drift_percentage": drift.drift_percentage,
                    "current_value": drift.current_value,
                    "target_value": drift.target_value,
                    "value_difference": drift.value_difference
                }
                for drift in analysis.allocation_drifts
            ],
            "transactions": [
                {
                    "symbol": tx.symbol,
                    "action": tx.action,
                    "shares": tx.shares,
                    "current_price": tx.current_price,
                    "transaction_value": tx.transaction_value,
                    "transaction_cost": tx.transaction_cost,
                    "reason": tx.reason
                }
                for tx in analysis.transactions
            ],
            "total_transaction_cost": analysis.total_transaction_cost,
            "estimated_final_value": analysis.estimated_final_value
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing rebalancing: {str(e)}")


@router.get("/portfolios/{portfolio_id}/summary")
async def get_rebalancing_summary(portfolio_id: int, db: Session = Depends(get_db)):
    """Get a quick summary of rebalancing needs for a portfolio."""
    controller = RebalancingController(db)
    summary = controller.get_rebalancing_summary(portfolio_id)
    
    if "error" in summary:
        raise HTTPException(status_code=400, detail=summary["error"])
    
    return summary


@router.post("/portfolios/{portfolio_id}/validate")
async def validate_rebalancing_feasibility(portfolio_id: int, db: Session = Depends(get_db)):
    """Validate if rebalancing is feasible for a portfolio."""
    controller = RebalancingController(db)
    validation = controller.validate_rebalancing_feasibility(portfolio_id)
    return validation


@router.post("/portfolios/{portfolio_id}/execute")
async def execute_rebalancing(
    portfolio_id: int,
    dry_run: bool = True,
    tolerance: Optional[float] = None,
    transaction_cost_rate: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """
    Execute rebalancing transactions for a portfolio.
    
    Args:
        portfolio_id: Portfolio to rebalance
        dry_run: If True, don't actually update holdings (default: True for safety)
        tolerance: Custom tolerance threshold
        transaction_cost_rate: Custom transaction cost rate
    """
    try:
        controller = RebalancingController(db, tolerance_threshold=tolerance or 2.0,
                                         transaction_cost_rate=transaction_cost_rate or 0.005)
        
        # First analyze to get transactions
        analysis = controller.analyze_portfolio_rebalancing(
            portfolio_id,
            custom_tolerance=tolerance,
            custom_cost_rate=transaction_cost_rate
        )
        
        if analysis.is_balanced:
            return {
                "success": True,
                "message": "Portfolio is already balanced within tolerance",
                "executed": False,
                "transactions_count": 0,
                "total_cost": 0
            }
        
        # Execute the transactions
        result = controller.execute_rebalancing(portfolio_id, analysis.transactions, dry_run)
        return result
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error executing rebalancing: {str(e)}")


@router.get("/portfolios/{portfolio_id}/transactions")
async def get_rebalancing_transactions(
    portfolio_id: int,
    tolerance: Optional[float] = None,
    transaction_cost_rate: Optional[float] = None,
    db: Session = Depends(get_db)
):
    """Get rebalancing transactions for a portfolio without executing them."""
    try:
        controller = RebalancingController(db, tolerance_threshold=tolerance or 2.0,
                                         transaction_cost_rate=transaction_cost_rate or 0.005)
        
        analysis = controller.analyze_portfolio_rebalancing(
            portfolio_id,
            custom_tolerance=tolerance,
            custom_cost_rate=transaction_cost_rate
        )
        
        return {
            "portfolio_id": portfolio_id,
            "is_balanced": analysis.is_balanced,
            "transactions": [
                {
                    "symbol": tx.symbol,
                    "action": tx.action,
                    "shares": tx.shares,
                    "current_price": tx.current_price,
                    "transaction_value": tx.transaction_value,
                    "transaction_cost": tx.transaction_cost,
                    "reason": tx.reason
                }
                for tx in analysis.transactions
            ],
            "total_transaction_cost": analysis.total_transaction_cost,
            "transaction_count": len(analysis.transactions)
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating transactions: {str(e)}")


@router.get("/portfolios/{portfolio_id}/allocation-chart-data")
async def get_allocation_chart_data(portfolio_id: int, db: Session = Depends(get_db)):
    """Get data for allocation comparison charts."""
    try:
        controller = RebalancingController(db)
        analysis = controller.analyze_portfolio_rebalancing(portfolio_id)
        
        # Prepare data for pie charts
        current_allocations = []
        target_allocations = []
        
        for drift in analysis.allocation_drifts:
            if drift.current_value > 0:  # Only include holdings with value
                current_allocations.append({
                    "symbol": drift.symbol,
                    "allocation": drift.current_allocation,
                    "value": drift.current_value
                })
                target_allocations.append({
                    "symbol": drift.symbol,
                    "allocation": drift.target_allocation,
                    "value": drift.target_value
                })
        
        return {
            "current_allocations": current_allocations,
            "target_allocations": target_allocations,
            "total_value": analysis.total_value,
            "is_balanced": analysis.is_balanced
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart data: {str(e)}")


# Settings endpoints for rebalancing configuration
@router.get("/settings/defaults")
async def get_rebalancing_defaults():
    """Get default rebalancing settings."""
    return {
        "tolerance_threshold": 2.0,
        "transaction_cost_rate": 0.005,
        "minimum_transaction_value": 100.0,
        "minimum_shares_change": 0.1
    }


@router.post("/portfolios/{portfolio_id}/rebalance-preview")
async def preview_rebalancing_impact(
    portfolio_id: int,
    tolerance: float = 2.0,
    transaction_cost_rate: float = 0.005,
    db: Session = Depends(get_db)
):
    """
    Preview the impact of rebalancing with different settings.
    Useful for testing different tolerance and cost scenarios.
    """
    try:
        controller = RebalancingController(db, tolerance_threshold=tolerance,
                                         transaction_cost_rate=transaction_cost_rate)
        
        analysis = controller.analyze_portfolio_rebalancing(portfolio_id)
        
        # Calculate some additional metrics for preview
        total_value_change = sum(abs(drift.value_difference) for drift in analysis.allocation_drifts)
        cost_percentage = (analysis.total_transaction_cost / analysis.total_value * 100) if analysis.total_value > 0 else 0
        
        return {
            "settings": {
                "tolerance_threshold": tolerance,
                "transaction_cost_rate": transaction_cost_rate
            },
            "impact": {
                "is_balanced": analysis.is_balanced,
                "transactions_needed": len(analysis.transactions),
                "total_transaction_cost": analysis.total_transaction_cost,
                "cost_percentage": cost_percentage,
                "total_value_to_trade": total_value_change,
                "estimated_final_value": analysis.estimated_final_value
            },
            "significant_drifts": [
                {
                    "symbol": drift.symbol,
                    "drift": drift.drift,
                    "drift_percentage": drift.drift_percentage
                }
                for drift in analysis.allocation_drifts
                if abs(drift.drift) > tolerance
            ]
        }
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error previewing rebalancing: {str(e)}")