from pydantic import BaseModel, Field
from datetime import date
from typing import Optional, List, Literal
from enum import Enum


# ---------------------------------------------------------
# Preset comparison options
# ---------------------------------------------------------
class ComparePreset(str, Enum):
    PREVIOUS_MONTH = "previous_month"
    SAME_MONTH_LAST_YEAR = "same_month_last_year"
    PREVIOUS_WEEK = "previous_week"
    PREVIOUS_QUARTER = "previous_quarter"
    CUSTOM = "custom"


# ---------------------------------------------------------
# Period Input
# ---------------------------------------------------------
class PeriodInput(BaseModel):
    start_date: date
    end_date: date


# ---------------------------------------------------------
# Period Compare Request
# ---------------------------------------------------------
class PeriodCompareRequest(BaseModel):
    symbol: str = Field(..., description="Stock symbol like RELIANCE, TCS")
    period1: PeriodInput = Field(..., description="Current/Primary period to view")
    period2: Optional[PeriodInput] = Field(None, description="Comparison period (optional if using preset)")
    preset: Optional[ComparePreset] = Field(None, description="Quick preset for period2")
    normalize: bool = Field(default=True, description="Normalize data to percentage change from day 1")


# ---------------------------------------------------------
# Single Data Point
# ---------------------------------------------------------
class PeriodDataPoint(BaseModel):
    day: int = Field(..., description="Day number (1, 2, 3...)")
    date: date
    open: float
    high: float
    low: float
    close: float
    volume: int
    change_pct: Optional[float] = Field(None, description="% change from day 1")


# ---------------------------------------------------------
# Period Summary Stats
# ---------------------------------------------------------
class PeriodSummary(BaseModel):
    label: str
    start_date: date
    end_date: date
    total_days: int
    start_price: float
    end_price: float
    period_return_pct: float
    avg_price: float
    min_price: float
    max_price: float
    avg_volume: float
    total_volume: int


# ---------------------------------------------------------
# Single Period Response
# ---------------------------------------------------------
class PeriodData(BaseModel):
    label: str
    summary: PeriodSummary
    data: List[PeriodDataPoint]


# ---------------------------------------------------------
# Full Comparison Response
# ---------------------------------------------------------
class PeriodCompareResponse(BaseModel):
    symbol: str
    period1: PeriodData
    period2: Optional[PeriodData] = None
    comparison: Optional[dict] = Field(None, description="Comparison metrics between periods")
