from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional


class StartMonitorRequest(BaseModel):
    """
    POST /api/candle/start

    symbols        — list of stock names to monitor
    email_receivers — list of emails to send alerts to (user provides their own)
    """
    symbols:         List[str]  = Field(..., example=["RELIANCE", "TCS"])
    email_receivers: List[str]  = Field(
        ...,
        example=["user@gmail.com", "trader@company.com"],
        description="Alerts sent to these emails when confidence > 80%"
    )


class StopMonitorRequest(BaseModel):
    """
    POST /api/candle/stop
    symbol   — which stock to stop
    interval — optional, if empty stops all intervals for that stock
    """
    symbol: str  = Field(..., example="RELIANCE.NS")
    interval: Optional[str] = Field(None, example="5m")


class MonitorStatusItem(BaseModel):
    symbol:           str
    interval:         str
    candles_today:    int
    is_market_open:   bool
    email_receivers:  List[str]
    last_candle_time: Optional[str]
    last_pattern:     Optional[str]
    last_confidence:  Optional[int]
    last_direction:   Optional[str]
    last_signal:      Optional[str]


class StartMonitorResponse(BaseModel):
    success: bool
    started: List[str]
    message: str


class StopMonitorResponse(BaseModel):
    success: bool
    stopped: List[str]
    message: str


class StatusResponse(BaseModel):
    total_monitors: int
    monitors: List[MonitorStatusItem]


class SymbolsResponse(BaseModel):
    total:   int
    symbols: List[str]


class MarketStatusResponse(BaseModel):
    symbol:  str
    is_open: bool
    message: str