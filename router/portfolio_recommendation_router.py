from fastapi import APIRouter, HTTPException
from schema.portfolio_recommendation_schema import PortfolioRecommendationRequest, PortfolioRecommendationResponse
from service.portfolio_recommendation_service import portfolio_service

router = APIRouter()

@router.post("/recommendation", response_model=PortfolioRecommendationResponse)
async def get_portfolio_recommendation(request: PortfolioRecommendationRequest):
    try:
        result = portfolio_service.analyze_portfolio(
            request.portfolio, 
            request.months, 
            request.years_of_data
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#@router.get("/health")
#async def health_check():
   # return {"status": "ok", "module": "portfolio_recommendation"} 