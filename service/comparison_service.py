from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import Session
from model.daily_data import DailyData
from schema.comparison_schema import (
    PeriodInput, PeriodCompareRequest, PeriodDataPoint,
    PeriodSummary, PeriodData, PeriodCompareResponse, ComparePreset
)

# ---------------------------------------------------------
# 4️⃣ PERIOD COMPARISON (Same stock, different time periods)
# ---------------------------------------------------------

def get_period2_from_preset(period1: PeriodInput, preset: ComparePreset) -> PeriodInput:
    """Calculate period2 dates based on preset option"""
    
    if preset == ComparePreset.PREVIOUS_MONTH:
        # Go back 1 month from period1 start
        start = period1.start_date - relativedelta(months=1)
        end = period1.end_date - relativedelta(months=1)
        
    elif preset == ComparePreset.SAME_MONTH_LAST_YEAR:
        # Same dates but 1 year ago
        start = period1.start_date - relativedelta(years=1)
        end = period1.end_date - relativedelta(years=1)
        
    elif preset == ComparePreset.PREVIOUS_WEEK:
        # Go back 7 days
        start = period1.start_date - timedelta(days=7)
        end = period1.end_date - timedelta(days=7)
        
    elif preset == ComparePreset.PREVIOUS_QUARTER:
        # Go back 3 months
        start = period1.start_date - relativedelta(months=3)
        end = period1.end_date - relativedelta(months=3)
        
    else:
        raise ValueError(f"Unknown preset: {preset}")
    
    return PeriodInput(start_date=start, end_date=end)


def fetch_period_data(db: Session, symbol: str, period: PeriodInput, normalize: bool = True) -> PeriodData | None:
    """Fetch stock data for a specific date range"""
    
    rows = (
        db.query(DailyData)
        .filter(DailyData.symbol == symbol.upper())
        .filter(DailyData.date >= period.start_date)
        .filter(DailyData.date <= period.end_date)
        .order_by(DailyData.date.asc())
        .all()
    )
    
    if not rows:
        return None
    
    # Build data points with day numbers
    data_points = []
    first_close = rows[0].close if rows else 0
    
    for idx, r in enumerate(rows, start=1):
        change_pct = None
        if normalize and first_close > 0:
            change_pct = round(((r.close - first_close) / first_close) * 100, 2)
        
        data_points.append(PeriodDataPoint(
            day=idx,
            date=r.date,
            open=round(r.open, 2),
            high=round(r.high, 2),
            low=round(r.low, 2),
            close=round(r.close, 2),
            volume=int(r.volume) if r.volume else 0,
            change_pct=change_pct
        ))
    
    # Calculate summary stats
    closes = [r.close for r in rows]
    volumes = [r.volume or 0 for r in rows]
    
    start_price = closes[0]
    end_price = closes[-1]
    period_return = round(((end_price - start_price) / start_price) * 100, 2)
    
    # Generate label
    start_str = period.start_date.strftime("%b %d")
    end_str = period.end_date.strftime("%b %d, %Y")
    label = f"{start_str} - {end_str}"
    
    summary = PeriodSummary(
        label=label,
        start_date=period.start_date,
        end_date=period.end_date,
        total_days=len(rows),
        start_price=round(start_price, 2),
        end_price=round(end_price, 2),
        period_return_pct=period_return,
        avg_price=round(sum(closes) / len(closes), 2),
        min_price=round(min(closes), 2),
        max_price=round(max(closes), 2),
        avg_volume=round(sum(volumes) / len(volumes), 0),
        total_volume=sum(volumes)
    )
    
    return PeriodData(
        label=label,
        summary=summary,
        data=data_points
    )


def calculate_comparison_metrics(period1: PeriodData, period2: PeriodData) -> dict:
    """Calculate comparison metrics between two periods"""
    
    s1 = period1.summary
    s2 = period2.summary
    
    return {
        "return_difference": round(s1.period_return_pct - s2.period_return_pct, 2),
        "period1_better": s1.period_return_pct > s2.period_return_pct,
        "avg_price_change": round(((s1.avg_price - s2.avg_price) / s2.avg_price) * 100, 2),
        "volume_change_pct": round(((s1.avg_volume - s2.avg_volume) / s2.avg_volume) * 100, 2) if s2.avg_volume > 0 else 0,
        "volatility_comparison": {
            "period1_range": round(s1.max_price - s1.min_price, 2),
            "period2_range": round(s2.max_price - s2.min_price, 2),
            "period1_range_pct": round(((s1.max_price - s1.min_price) / s1.avg_price) * 100, 2),
            "period2_range_pct": round(((s2.max_price - s2.min_price) / s2.avg_price) * 100, 2),
        }
    }


def compare_periods(db: Session, request: PeriodCompareRequest) -> PeriodCompareResponse:
    """Main function to compare two time periods for same stock"""
    
    symbol = request.symbol.upper()
    # Ensure .NS suffix for NSE stocks (database stores with .NS)
    if not symbol.endswith('.NS') and not symbol.startswith('^'):
        symbol = f"{symbol}.NS"
    
    # Fetch period1 data
    period1_data = fetch_period_data(db, symbol, request.period1, request.normalize)
    
    if not period1_data:
        raise ValueError(f"No data found for {symbol} in period1 ({request.period1.start_date} to {request.period1.end_date})")
    
    # Determine period2
    period2 = request.period2
    if not period2 and request.preset:
        period2 = get_period2_from_preset(request.period1, request.preset)
    
    period2_data = None
    comparison = None
    
    if period2:
        period2_data = fetch_period_data(db, symbol, period2, request.normalize)
        
        if period2_data:
            comparison = calculate_comparison_metrics(period1_data, period2_data)
    
    return PeriodCompareResponse(
        symbol=symbol,
        period1=period1_data,
        period2=period2_data,
        comparison=comparison
    )
