from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from db.database import get_db
from service.comparison_service import compare_periods
from schema.comparison_schema import (
    PeriodCompareRequest, 
    PeriodCompareResponse,
    ComparePreset
)

router = APIRouter(prefix="/compare")

# ---------------------------------------------------------
# 1️⃣ Period Comparison (Same stock, different time periods)
# ---------------------------------------------------------
@router.post("/periods", response_model=PeriodCompareResponse)
def api_compare_periods(request: PeriodCompareRequest, db: Session = Depends(get_db)):
    """
    Compare same stock across different time periods.
    
    Examples:
    - Compare Jan 2026 vs Dec 2025 (custom dates)
    - Compare current month vs previous month (preset)
    - Compare this month vs same month last year (preset)
    
    Presets available:
    - previous_month
    - same_month_last_year  
    - previous_week
    - previous_quarter
    """
    try:
        # Validate dates
        if request.period1.start_date > request.period1.end_date:
            raise HTTPException(400, "period1 start_date must be before end_date")
        
        if request.period2:
            if request.period2.start_date > request.period2.end_date:
                raise HTTPException(400, "period2 start_date must be before end_date")
        
        # Must have either period2 or preset
        if not request.period2 and not request.preset:
            raise HTTPException(400, "Provide either period2 dates or a preset option")
        
        result = compare_periods(db, request)
        return result
        
    except ValueError as e:
        raise HTTPException(404, str(e))
    except Exception as e:
        raise HTTPException(500, f"Error comparing periods: {str(e)}")

