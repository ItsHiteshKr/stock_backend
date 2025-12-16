from pydantic import BaseModel

class InsightResponse(BaseModel):
    symbol: str
    insight: str

class MomentumResponse(BaseModel):
    symbol: str
    momentum: str
    percent_change: float

class VolatilityResponse(BaseModel):
    symbol: str
    volatility: float
    level: str

class AlertResponse(BaseModel):
    symbol: str
    alerts: list[str]
