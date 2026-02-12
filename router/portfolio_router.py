from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
from typing import List
import csv
import io

from db.database import get_db
from schema.portfolio_schema import (
    PortfolioCreate,
    PortfolioUpdate,
    AddHoldingToPortfolio,
    HoldingUpdate, 
    HoldingResponse, 
    PortfolioListResponse,
    PortfolioDetailResponse,
    HoldingItem
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
        "user_email": "user@example.com",
        "portfolio_name": "Groww",
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


@router.get("/list/{user_email}", response_model=List[PortfolioListResponse])
def get_user_portfolios(user_email: str, db: Session = Depends(get_db)):
    """Get list of all portfolios for a user with summary"""
    return PortfolioService.get_user_portfolios(user_email, db)

@router.get("/{portfolio_id}", response_model=PortfolioDetailResponse)
def get_portfolio(portfolio_id: int, db: Session = Depends(get_db)):
    """Get portfolio with all holdings"""
    return PortfolioService.get_portfolio_by_id(portfolio_id, db)


@router.put("/{portfolio_id}", response_model=PortfolioDetailResponse)
def update_portfolio_name(portfolio_id: int, portfolio: PortfolioUpdate, db: Session = Depends(get_db)):
    """
    Update portfolio name only
    Example:
    {
        "portfolio_name": "My Groww Portfolio"
    }
    """
    return PortfolioService.update_portfolio(portfolio_id, portfolio, db)


@router.delete("/delete/{portfolio_id}")
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
        "sector": "IT"
    }
    """
    return PortfolioService.add_holding_to_portfolio(portfolio_id, holding, db)


@router.put("/{portfolio_id}/holdings", response_model=PortfolioDetailResponse)
def add_multiple_holdings(portfolio_id: int, holdings: List[HoldingItem], db: Session = Depends(get_db)):
    """
    Add multiple new holdings to an existing portfolio
    Example:
    [
        {
            "symbol": "INFY",
            "stock_name": "Infosys Ltd",
            "quantity": 15,
            "avg_buy_price": 1450.00,
            "sector": "IT"
        },
        {
            "symbol": "WIPRO",
            "stock_name": "Wipro Ltd",
            "quantity": 20,
            "avg_buy_price": 450.00,
            "sector": "IT"
        }
    ]
    """
    return PortfolioService.add_multiple_holdings(portfolio_id, holdings, db)


@router.put("/holding/{holding_id}", response_model=HoldingResponse)
def update_holding(holding_id: int, holding: HoldingUpdate, db: Session = Depends(get_db)):
    """
    Update an existing holding
    Example:
    {
        "quantity": 25,
        "avg_buy_price": 1500.00
    }
    """
    return PortfolioService.update_holding(holding_id, holding, db)


@router.delete("/holding/delete/{holding_id}")
def delete_holding(holding_id: int, db: Session = Depends(get_db)):
    """Delete a specific stock from portfolio"""
    return PortfolioService.delete_holding(holding_id, db)


# ============ CSV UPLOAD ENDPOINT ============

@router.post("/upload-csv/{portfolio_id}")
async def upload_holdings_csv(
    portfolio_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload CSV file to add multiple holdings to a portfolio.
    
    CSV Format (with header row):
    symbol,stock_name,quantity,avg_buy_price,sector
    
    Required columns: symbol, stock_name, quantity, avg_buy_price
    Optional columns: sector
    
    Example CSV content:
    symbol,stock_name,quantity,avg_buy_price,sector
    RELIANCE,Reliance Industries,10,2500.50,Energy
    TCS,Tata Consultancy Services,5,3800.00,IT
    HDFCBANK,HDFC Bank,20,1650.00,Banking
    """
    # Validate file type
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read file content
        contents = await file.read()
        decoded = contents.decode('utf-8')
        
        # Parse CSV
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        # Validate required columns
        required_columns = {'symbol', 'stock_name', 'quantity', 'avg_buy_price'}
        if csv_reader.fieldnames is None:
            raise HTTPException(status_code=400, detail="CSV file is empty or has no headers")
        
        csv_columns = set(col.strip().lower() for col in csv_reader.fieldnames)
        missing_columns = required_columns - csv_columns
        
        if missing_columns:
            raise HTTPException(
                status_code=400, 
                detail=f"Missing required columns: {', '.join(missing_columns)}"
            )
        
        # Parse holdings from CSV
        holdings = []
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 (header is row 1)
            # Normalize keys to lowercase
            row = {k.strip().lower(): v.strip() if v else '' for k, v in row.items()}
            
            # Validate required fields
            if not row.get('symbol'):
                errors.append(f"Row {row_num}: 'symbol' is required")
                continue
            if not row.get('stock_name'):
                errors.append(f"Row {row_num}: 'stock_name' is required")
                continue
            if not row.get('quantity'):
                errors.append(f"Row {row_num}: 'quantity' is required")
                continue
            if not row.get('avg_buy_price'):
                errors.append(f"Row {row_num}: 'avg_buy_price' is required")
                continue
            
            try:
                quantity = int(row['quantity'])
                if quantity <= 0:
                    errors.append(f"Row {row_num}: 'quantity' must be positive")
                    continue
            except ValueError:
                errors.append(f"Row {row_num}: 'quantity' must be a valid integer")
                continue
            
            try:
                avg_buy_price = float(row['avg_buy_price'])
                if avg_buy_price <= 0:
                    errors.append(f"Row {row_num}: 'avg_buy_price' must be positive")
                    continue
            except ValueError:
                errors.append(f"Row {row_num}: 'avg_buy_price' must be a valid number")
                continue
            
            holdings.append({
                'symbol': row['symbol'].upper(),
                'stock_name': row['stock_name'],
                'quantity': quantity,
                'avg_buy_price': avg_buy_price,
                'sector': row.get('sector') or None
            })
        
        if not holdings:
            raise HTTPException(
                status_code=400, 
                detail=f"No valid holdings found in CSV. Errors: {errors}"
            )
        
        # Add holdings to portfolio
        result = PortfolioService.add_holdings_from_csv(portfolio_id, holdings, db)
        
        return {
            "message": f"Successfully added {result['added']} holdings to portfolio",
            "added": result['added'],
            "skipped": result['skipped'],
            "skipped_symbols": result['skipped_symbols'],
            "csv_parse_errors": errors
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")