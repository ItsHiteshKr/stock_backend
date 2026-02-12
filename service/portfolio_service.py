from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from typing import List

from model.portfolio_model import Portfolio, PortfolioHolding
from model.user_model import UserTable
from schema.portfolio_schema import (
    PortfolioCreate, 
    PortfolioUpdate, 
    AddHoldingToPortfolio,
    HoldingUpdate, 
    PortfolioListResponse,
    HoldingItem
)


class PortfolioService:

    @staticmethod
    def get_user_by_email(email: str, db: Session) -> UserTable:
        """Helper to get user by email"""
        user = db.query(UserTable).filter(UserTable.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    # ============ PORTFOLIO CRUD ============
    
    @staticmethod
    def create_portfolio(portfolio_data: PortfolioCreate, db: Session):
        """Create a new portfolio with multiple stocks"""
        try:
            user = PortfolioService.get_user_by_email(portfolio_data.user_email, db)
            
            # Check if portfolio name already exists for this user
            existing = db.query(Portfolio).filter(
                Portfolio.user_email == user.email,
                Portfolio.portfolio_name == portfolio_data.portfolio_name
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Portfolio '{portfolio_data.portfolio_name}' already exists"
                )
            
            # Create portfolio
            new_portfolio = Portfolio(
                user_email=user.email,
                portfolio_name=portfolio_data.portfolio_name,
            )
            db.add(new_portfolio)
            db.flush()  # Get the portfolio ID
            
            # Add all holdings
            for holding in portfolio_data.holdings:
                total_invested = holding.quantity * holding.avg_buy_price
                new_holding = PortfolioHolding(
                    portfolio_id=new_portfolio.id,
                    symbol=holding.symbol.upper(),
                    stock_name=holding.stock_name,
                    quantity=holding.quantity,
                    avg_buy_price=holding.avg_buy_price,
                    total_invested=total_invested,
                    sector=holding.sector
                )
                db.add(new_holding)
            
            db.commit()
            
            # Reload portfolio with holdings properly
            portfolio = db.query(Portfolio).options(
                joinedload(Portfolio.holdings)
            ).filter(Portfolio.id == new_portfolio.id).first()
            
            return portfolio
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error creating portfolio: {str(e)}")

    @staticmethod
    def get_user_portfolios(email: str, db: Session) -> List[PortfolioListResponse]:
        """Get list of all portfolios for a user"""
        try:
            user = PortfolioService.get_user_by_email(email, db)
            
            portfolios = db.query(Portfolio).filter(Portfolio.user_email == user.email).all()
            
            result = []
            for p in portfolios:
                total_holdings = len(p.holdings)
                total_invested = sum(h.total_invested for h in p.holdings)
                result.append(PortfolioListResponse(
                    id=p.id,
                    portfolio_name=p.portfolio_name,
                    total_holdings=total_holdings,
                    total_invested=total_invested,
                    created_at=p.created_at
                ))
            
            return result
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching portfolios: {str(e)}")

    @staticmethod
    def get_portfolio_by_id(portfolio_id: int, db: Session):
        """Get portfolio with all holdings"""
        try:
            portfolio = db.query(Portfolio).options(
                joinedload(Portfolio.holdings)
            ).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            return portfolio
        
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error fetching portfolio: {str(e)}")

    @staticmethod
    def update_portfolio(portfolio_id: int, portfolio_data: PortfolioUpdate, db: Session):
        """Update portfolio metadata"""
        try:
            portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            if portfolio_data.portfolio_name is not None:
                portfolio.portfolio_name = portfolio_data.portfolio_name
            
            
            db.commit()
            
            # Reload with holdings
            portfolio = db.query(Portfolio).options(
                joinedload(Portfolio.holdings)
            ).filter(Portfolio.id == portfolio_id).first()
            
            return portfolio
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating portfolio: {str(e)}")

    @staticmethod
    def delete_portfolio(portfolio_id: int, db: Session):
        """Delete portfolio with all holdings"""
        try:
            portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            holdings_count = len(portfolio.holdings)
            db.delete(portfolio)  # Cascade deletes holdings
            db.commit()
            
            return {"message": f"Portfolio deleted with {holdings_count} holdings"}
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting portfolio: {str(e)}")

    # ============ HOLDING CRUD ============
    
    @staticmethod
    def add_holding_to_portfolio(portfolio_id: int, holding_data: AddHoldingToPortfolio, db: Session):
        """Add a single stock to existing portfolio"""
        try:
            portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            # Check if symbol already exists in this portfolio
            existing = db.query(PortfolioHolding).filter(
                PortfolioHolding.portfolio_id == portfolio_id,
                PortfolioHolding.symbol == holding_data.symbol.upper()
            ).first()
            
            if existing:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Stock {holding_data.symbol} already exists in this portfolio"
                )
            
            total_invested = holding_data.quantity * holding_data.avg_buy_price
            
            new_holding = PortfolioHolding(
                portfolio_id=portfolio_id,
                symbol=holding_data.symbol.upper(),
                stock_name=holding_data.stock_name,
                quantity=holding_data.quantity,
                avg_buy_price=holding_data.avg_buy_price,
                total_invested=total_invested,
                sector=holding_data.sector
            )
            
            db.add(new_holding)
            db.commit()
            db.refresh(new_holding)
            
            return new_holding
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error adding holding: {str(e)}")

    @staticmethod
    def add_multiple_holdings(portfolio_id: int, holdings: List[HoldingItem], db: Session):
        """Add multiple new holdings to an existing portfolio"""
        try:
            portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            added_count = 0
            skipped_symbols = []
            
            for holding in holdings:
                # Check if symbol already exists in this portfolio
                existing = db.query(PortfolioHolding).filter(
                    PortfolioHolding.portfolio_id == portfolio_id,
                    PortfolioHolding.symbol == holding.symbol.upper()
                ).first()
                
                if existing:
                    skipped_symbols.append(holding.symbol.upper())
                    continue
                
                total_invested = holding.quantity * holding.avg_buy_price
                
                new_holding = PortfolioHolding(
                    portfolio_id=portfolio_id,
                    symbol=holding.symbol.upper(),
                    stock_name=holding.stock_name,
                    quantity=holding.quantity,
                    avg_buy_price=holding.avg_buy_price,
                    total_invested=total_invested,
                    sector=holding.sector
                )
                
                db.add(new_holding)
                added_count += 1
            
            if added_count == 0 and skipped_symbols:
                raise HTTPException(
                    status_code=400,
                    detail=f"All symbols already exist in portfolio: {', '.join(skipped_symbols)}"
                )
            
            db.commit()
            
            # Reload portfolio with all holdings
            portfolio = db.query(Portfolio).options(
                joinedload(Portfolio.holdings)
            ).filter(Portfolio.id == portfolio_id).first()
            
            return portfolio
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error adding holdings: {str(e)}")

    @staticmethod
    def update_holding(holding_id: int, holding_data: HoldingUpdate, db: Session):
        """Update an existing holding"""
        try:
            holding = db.query(PortfolioHolding).filter(
                PortfolioHolding.id == holding_id
            ).first()
            
            if not holding:
                raise HTTPException(status_code=404, detail="Holding not found")
            
            if holding_data.quantity is not None:
                holding.quantity = holding_data.quantity
            
            if holding_data.avg_buy_price is not None:
                holding.avg_buy_price = holding_data.avg_buy_price
            
            
            # Recalculate total invested
            holding.total_invested = holding.quantity * holding.avg_buy_price
            
            db.commit()
            db.refresh(holding)
            
            return holding
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error updating holding: {str(e)}")

    @staticmethod
    def delete_holding(holding_id: int, db: Session):
        """Delete a holding from portfolio"""
        try:
            holding = db.query(PortfolioHolding).filter(
                PortfolioHolding.id == holding_id
            ).first()
            
            if not holding:
                raise HTTPException(status_code=404, detail="Holding not found")
            
            db.delete(holding)
            db.commit()
            
            return {"message": f"Holding deleted successfully"}
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error deleting holding: {str(e)}")

    # ============ CSV UPLOAD ============
    
    @staticmethod
    def add_holdings_from_csv(portfolio_id: int, holdings: list, db: Session):
        """Add multiple holdings from CSV data"""
        try:
            portfolio = db.query(Portfolio).filter(Portfolio.id == portfolio_id).first()
            
            if not portfolio:
                raise HTTPException(status_code=404, detail="Portfolio not found")
            
            added = 0
            skipped = 0
            skipped_symbols = []
            
            for holding_data in holdings:
                # Check if symbol already exists in this portfolio
                existing = db.query(PortfolioHolding).filter(
                    PortfolioHolding.portfolio_id == portfolio_id,
                    PortfolioHolding.symbol == holding_data['symbol']
                ).first()
                
                if existing:
                    skipped += 1
                    skipped_symbols.append(holding_data['symbol'])
                    continue
                
                total_invested = holding_data['quantity'] * holding_data['avg_buy_price']
                
                new_holding = PortfolioHolding(
                    portfolio_id=portfolio_id,
                    symbol=holding_data['symbol'],
                    stock_name=holding_data['stock_name'],
                    quantity=holding_data['quantity'],
                    avg_buy_price=holding_data['avg_buy_price'],
                    total_invested=total_invested,
                    sector=holding_data.get('sector')
                )
                
                db.add(new_holding)
                added += 1
            
            db.commit()
            
            return {
                "added": added,
                "skipped": skipped,
                "skipped_symbols": skipped_symbols
            }
        
        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=500, detail=f"Error adding holdings from CSV: {str(e)}")
