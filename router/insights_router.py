from service.insights_service import ai_generated_insight
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from db.database import get_db

from service.insights_service import (
    auto_insight,
    momentum_insight,
    volatility_insight,
    alert_insight,
    buy_sell_hold_decision


)

from schema.insights_schema import (
    InsightResponse,
    MomentumResponse,
    VolatilityResponse,
    AlertResponse
)

router = APIRouter(prefix="/insights", tags=["Insights"])


# ----------------------------------
# 1️⃣ Auto Insights
# /insights/{symbol}
# ----------------------------------
@router.get("/{symbol}", response_model=InsightResponse)
def get_insights(symbol: str, db: Session = Depends(get_db)):
    insight = auto_insight(db, symbol)
    return {"symbol": symbol, "insight": insight}


# ----------------------------------
# 2️⃣ Momentum
# /insights/momentum/{symbol}
# ----------------------------------
@router.get("/momentum/{symbol}", response_model=MomentumResponse)
def get_momentum(symbol: str, db: Session = Depends(get_db)):
    result = momentum_insight(db, symbol)
    return {
        "symbol": symbol,
        "momentum": result["momentum"],
        "percent_change": result["percent_change"]
    }


# ----------------------------------
# 3️⃣ Volatility
# /insights/volatility/{symbol}
# ----------------------------------
@router.get("/volatility/{symbol}", response_model=VolatilityResponse)
def get_volatility(symbol: str, db: Session = Depends(get_db)):
    vol, level = volatility_insight(db, symbol)
    return {"symbol": symbol, "volatility": vol, "level": level}


# ----------------------------------
# 4️⃣ Alerts
# /insights/alerts/{symbol}
# ----------------------------------
@router.get("/alerts/{symbol}", response_model=AlertResponse)
def get_alerts(symbol: str, db: Session = Depends(get_db)):
    alerts = alert_insight(db, symbol)
    return {"symbol": symbol, "alerts": alerts}



@router.get("/ai/{symbol}")
def ai_insight(symbol: str, db: Session = Depends(get_db)):
    insight = ai_generated_insight(db, symbol)
    return {
        "symbol": symbol,
        "ai_insight": insight
    }

@router.get("/insights/decision/{symbol}")
def stock_decision(symbol: str, db: Session = Depends(get_db)):
    return buy_sell_hold_decision(db, symbol)