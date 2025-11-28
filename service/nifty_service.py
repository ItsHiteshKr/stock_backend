from sqlalchemy.orm import Session
from model.nifty_model import NiftyTable
from schema.nifty_schema import NiftyData
from fastapi import HTTPException, UploadFile
import csv
import io
from datetime import datetime
from typing import List


def upload_csv_data(file: UploadFile, db: Session) -> dict:
    """
    Upload and process CSV file containing Nifty stock data
    Expected CSV format: date,open,high,low,close,volume
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed")
    
    try:
        # Read file content
        contents = file.file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        added_count = 0
        skipped_count = 0
        errors = []
        
        for row_num, row in enumerate(csv_reader, start=2):  # Start from 2 (1 is header)
            try:
                # Parse date (adjust format as needed)
                date_str = row.get('date', '').strip()
                if not date_str:
                    errors.append(f"Row {row_num}: Missing date")
                    continue
                
                # Try different date formats
                try:
                    date_obj = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    try:
                        date_obj = datetime.strptime(date_str, '%d-%m-%Y').date()
                    except ValueError:
                        date_obj = datetime.strptime(date_str, '%d/%m/%Y').date()
                
                # Check if data already exists
                existing = db.query(NiftyTable).filter(NiftyTable.date == date_obj).first()
                if existing:
                    skipped_count += 1
                    continue
                
                # Create new entry
                nifty_data = NiftyTable(
                    date=date_obj,
                    open=float(row.get('Open', row.get('open', 0))),
                    high=float(row.get('High', row.get('high', 0))),
                    low=float(row.get('Low', row.get('low', 0))),
                    close=float(row.get('Close', row.get('close', 0))),
                    shares_traded=int(float(row.get('Shares Traded', row.get('Shares_Traded', row.get('shares_traded', 0))))),
                    turnover_in_crores=float(row.get('Turnover (Rs. Cr)', row.get('Turnover_in_Crores', row.get('turnover_in_crores', 0)))) if row.get('Turnover (Rs. Cr)', row.get('Turnover_in_Crores', row.get('turnover_in_crores'))) else None
                )
                
                db.add(nifty_data)
                added_count += 1
                
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
                continue
        
        # Commit all changes
        db.commit()
        
        return {
            "message": "CSV processed successfully",
            "added": added_count,
            "skipped": skipped_count,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing CSV: {str(e)}")
    finally:
        file.file.close()


def get_all_nifty_data(db: Session, skip: int = 0, limit: int = 100) -> List[NiftyTable]:
    """Get all Nifty data with pagination"""
    return db.query(NiftyTable).offset(skip).limit(limit).all()


def get_nifty_by_date(date, db: Session) -> NiftyTable:
    """Get Nifty data by specific date"""
    nifty_data = db.query(NiftyTable).filter(NiftyTable.date == date).first()
    if not nifty_data:
        raise HTTPException(status_code=404, detail="Data not found for this date")
    return nifty_data


def create_nifty_data(nifty: NiftyData, db: Session) -> NiftyTable:
    """Create new Nifty data entry"""
    existing_data = db.query(NiftyTable).filter(NiftyTable.date == nifty.date).first()
    if existing_data:
        raise HTTPException(status_code=400, detail="Data for this date already exists")
    
    db_nifty = NiftyTable(
        date=nifty.date,
        open=nifty.open,
        high=nifty.high,
        low=nifty.low,
        close=nifty.close,
        shares_traded=nifty.shares_traded,
        turnover_in_crores=nifty.turnover_in_crores
    )
    db.add(db_nifty)
    db.commit()
    db.refresh(db_nifty)
    return db_nifty


def update_nifty_data(date, nifty: NiftyData, db: Session) -> NiftyTable:
    """Update Nifty data for a specific date"""
    db_nifty = db.query(NiftyTable).filter(NiftyTable.date == date).first()
    if not db_nifty:
        raise HTTPException(status_code=404, detail="Data not found for this date")
    
    db_nifty.open = nifty.open
    db_nifty.high = nifty.high
    db_nifty.low = nifty.low
    db_nifty.close = nifty.close
    db_nifty.shares_traded = nifty.shares_traded
    db_nifty.turnover_in_crores = nifty.turnover_in_crores
    
    db.commit()
    db.refresh(db_nifty)
    return db_nifty


def delete_nifty_data(date, db: Session) -> dict:
    """Delete Nifty data for a specific date"""
    db_nifty = db.query(NiftyTable).filter(NiftyTable.date == date).first()
    if not db_nifty:
        raise HTTPException(status_code=404, detail="Data not found for this date")
    
    db.delete(db_nifty)
    db.commit()
    return {"message": "Data deleted successfully"}
