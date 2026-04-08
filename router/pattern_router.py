from fastapi import APIRouter, HTTPException, status
from requests import request
from schema.pattern_schema import PatternMatchRequest, PatternMatchResponse
from service.pattern_service import PatternMatcherService
import logging

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/pattern",
    tags=["Pattern Matching"]
)


@router.post("/match", response_model=PatternMatchResponse, status_code=status.HTTP_200_OK)
def find_pattern_match(request: PatternMatchRequest):
    """
    Find best pattern match for a stock

     symbol: Stock symbol (e.g., TCS.NS, META, etc.),
     years_back : (default: 5),
     window_size : (default: 10),
     use_cache : (default: True),
    """
    try:
        logger.info(f"Pattern match request: {request.symbol}")
        
        # Call service
        response = PatternMatcherService.find_pattern_match(request)
        
        return response
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )
