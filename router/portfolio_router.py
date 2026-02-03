from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from db.database import get_db
from schema.portfolio_schema import (
    PortfolioCreate,
    PortfolioUpdate,
    AddHoldingToPortfolio,
    HoldingUpdate, 
    HoldingResponse, 
    PortfolioListResponse,
    PortfolioDetailResponse
)
from service.portfolio_service import PortfolioService

router = APIRouter(
    prefix="/portfolio"
)


# ============ PORTFOLIO ENDPOINTS ============

@router.post("/", response_model=PortfolioDetailResponse)
def create_portfolio(portfolio: PortfolioCreate, db: Session = Depends(get_db)):
    """
    Create a new portfolio with multiple stocks at once
    Example:
    {
        "user_id": 1,
        "portfolio_name": "Groww",
        "description": "My Groww investments",
        "holdings": [
            {
                "symbol": "RELIANCE",
                "stock_name": "Reliance Industries",
                "quantity": 10,
                "avg_buy_price": 2500.50,
                "sector": "Energy"
            },
            {
                "symbol": "TCS",
                "stock_name": "Tata Consultancy Services",
                "quantity": 5,
                "avg_buy_price": 3800.00,
                "sector": "IT"
            },
            {
                "symbol": "HDFCBANK",
                "stock_name": "HDFC Bank",
                "quantity": 20,
                "avg_buy_price": 1650.00,
                "sector": "Banking"
            }
        ]
    }
    """
    return PortfolioService.create_portfolio(portfolio, db)


@router.get("/list/{user_id}", response_model=List[PortfolioListResponse])
def get_user_portfolios(user_id: int, db: Session = Depends(get_db)):
    """Get list of all portfolios for a user with summary"""
    return PortfolioService.get_user_portfolios(user_id, db)


@router.get("/{portfolio_id}", response_model=PortfolioDetailResponse)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Get portfolio with all holdings"""
    return PortfolioService.get_portfolio_by_id(portfolio_id, db)


@router.put("/{portfolio_id}", response_model=PortfolioDetailResponse)
def update_portfolio(portfolio_id: int, portfolio: PortfolioUpdate, db: Session = Depends(get_db)):
    """
    Update portfolio name or description
    Example:
    {
        "portfolio_name": "My Groww Portfolio",
        "description": "Long term investments"
    }
    """
    return PortfolioService.update_portfolio(portfolio_id, portfolio, db)


@router.delete("/{portfolio_id}")
def delete_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Delete entire portfolio with all its holdings"""
    return PortfolioService.delete_portfolio(portfolio_id, db)


# ============ HOLDING ENDPOINTS ============

@router.post("/{portfolio_id}/holding", response_model=HoldingResponse)
def add_holding(portfolio_id: int, holding: AddHoldingToPortfolio, db: Session = Depends(get_db)):
    """
    Add a single stock to existing portfolio
    Example:
    {
        "symbol": "INFY",
        "stock_name": "Infosys Ltd",
        "quantity": 15,
        "avg_buy_price": 1450.00,
        "sector": "IT",
        "notes": "Added on dip"
    }
    """
    return PortfolioService.add_holding_to_portfolio(portfolio_id, holding, db)


@router.put("/holding/{holding_id}", response_model=HoldingResponse)
def update_holding(holding_id: int, holding: HoldingUpdate, db: Session = Depends(get_db)):
    """
    Update an existing holding
    Example:
    {
        "quantity": 25,
        "avg_buy_price": 1500.00,
        "notes": "Averaged up"
    }
    """
    return PortfolioService.update_holding(holding_id, holding, db)


@router.delete("/holding/{holding_id}")
def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    """Delete a specific stock from portfolio"""
    return PortfolioService.delete_holding(holding_id, db)