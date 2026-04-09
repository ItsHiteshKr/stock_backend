from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


# Notification schemas

class NotificationOut(BaseModel):
    """
    One alert notification — returned by GET /api/candle/notifications.
    Frontend uses this to show popup/banner to user.
    """
    id:          str
    symbol:      str
    interval:    str
    time:        str
    pattern:     str
    direction:   str
    confidence:  int
    signal:      str
    trend:       str
    support:     Optional[float]
    resistance:  Optional[float]
    candle_open:   float
    candle_high:   float
    candle_low:    float
    candle_close:  float
    created_at:  datetime
    is_read:     bool


class MarkReadRequest(BaseModel):
    """POST /api/candle/notifications/mark-read"""
    ids: List[str] = Field(...,
        example=["RELIANCE.NS:5m:10:15"],
        description="List of notification IDs to mark as read")


class NotificationsResponse(BaseModel):
    """Response for GET /api/candle/notifications"""
    total:         int
    unread_count:  int
    notifications: List[NotificationOut]


# Monitor schemas 

class StartMonitorRequest(BaseModel):
    """
    POST /api/candle/start

    symbols         — stock names to monitor
    email_receivers — optional, send email alerts to these addresses too
                      leave empty [] if you only want API notifications
    """
    symbols:         List[str] = Field(..., example=["RELIANCE", "TCS"])
    email_receivers: List[str] = Field(
        default=[],
        example=["user@gmail.com"],
        description="Optional. Leave empty to use API notifications only."
    )


class StopMonitorRequest(BaseModel):
    symbol:   str           = Field(..., example="RELIANCE.NS")
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
    monitors:       List[MonitorStatusItem]


class SymbolsResponse(BaseModel):
    total:   int
    symbols: List[str]


class MarketStatusResponse(BaseModel):
    symbol:  str
    is_open: bool
    message: str