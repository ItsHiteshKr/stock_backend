"""
AI Pattern Matcher Service
==========================
Finds the best matching historical period using REAL database data.
Uses Pearson correlation on normalized price movements.

How it works:
1. Fetch current period data (last N days)
2. Use sliding window across all historical data
3. Calculate Pearson correlation for each window
4. Return the window with highest correlation
"""

import math
from datetime import date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func
from model.daily_data import DailyData
from schema.pattern_matcher_schema import (
    PatternMatchRequest, PatternMatchResponse,
    PeriodDataPoint, PeriodSummary, PeriodData
)


def normalize_prices(closes: list[float]) -> list[float]:
    """Normalize prices to percentage change from first day"""
    if not closes or closes[0] == 0:
        return closes
    base = closes[0]
    return [round(((p - base) / base) * 100, 4) for p in closes]


def pearson_correlation(x: list[float], y: list[float]) -> float:
    """
    Calculate Pearson correlation coefficient between two series.
    Returns value between -1 and 1.
    1 = perfect positive correlation (same pattern)
    -1 = perfect negative correlation (opposite pattern)
    0 = no correlation
    """
    n = min(len(x), len(y))
    if n < 5:
        return 0.0
    
    x = x[:n]
    y = y[:n]
    
    sum_x = sum(x)
    sum_y = sum(y)
    sum_x_sq = sum(xi ** 2 for xi in x)
    sum_y_sq = sum(yi ** 2 for yi in y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    
    numerator = n * sum_xy - sum_x * sum_y
    denominator = math.sqrt(
        (n * sum_x_sq - sum_x ** 2) * (n * sum_y_sq - sum_y ** 2)
    )
    
    if denominator == 0:
        return 0.0
    
    return numerator / denominator


def fetch_daily_data(db: Session, symbol: str, start_date: date, end_date: date) -> list:
    """Fetch daily data for a symbol between dates"""
    rows = (
        db.query(DailyData)
        .filter(DailyData.symbol == symbol)
        .filter(DailyData.date >= start_date)
        .filter(DailyData.date <= end_date)
        .order_by(DailyData.date.asc())
        .all()
    )
    return rows


def build_period_data(rows: list, label: str) -> PeriodData:
    """Build PeriodData from database rows"""
    if not rows:
        raise ValueError("No data rows provided")
    
    first_close = rows[0].close
    data_points = []
    
    for idx, r in enumerate(rows, start=1):
        change_pct = round(((r.close - first_close) / first_close) * 100, 2) if first_close > 0 else 0
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
    
    closes = [r.close for r in rows]
    start_price = closes[0]
    end_price = closes[-1]
    period_return = round(((end_price - start_price) / start_price) * 100, 2) if start_price > 0 else 0
    
    summary = PeriodSummary(
        label=label,
        start_date=rows[0].date,
        end_date=rows[-1].date,
        total_days=len(rows),
        start_price=round(start_price, 2),
        end_price=round(end_price, 2),
        period_return_pct=period_return,
        avg_price=round(sum(closes) / len(closes), 2),
        min_price=round(min(closes), 2),
        max_price=round(max(closes), 2)
    )
    
    return PeriodData(
        label=label,
        summary=summary,
        data=data_points
    )


def generate_insights(correlation: float, match_pct: float, 
                       current_return: float, matched_return: float,
                       current_days: int, matched_days: int) -> list[str]:
    """Generate AI-like insights based on the match"""
    insights = []
    
    if correlation >= 0.85:
        insights.append(f"🎯 Strong pattern correlation ({correlation:.2f}) - Price movements are highly similar")
    elif correlation >= 0.65:
        insights.append(f"📊 Good pattern correlation ({correlation:.2f}) - Notable similarity in price movements")
    else:
        insights.append(f"⚠️ Moderate correlation ({correlation:.2f}) - Some pattern similarity detected")
    
    if matched_return >= 0:
        insights.append(f"📈 Historical matched period showed +{matched_return:.2f}% return over {matched_days} trading days")
    else:
        insights.append(f"📉 Historical matched period showed {matched_return:.2f}% return over {matched_days} trading days")
    
    if current_return >= 0 and matched_return >= 0:
        insights.append("💡 Both current and historical periods show bullish trends")
    elif current_return < 0 and matched_return < 0:
        insights.append("⚠️ Both periods show bearish trends - exercise caution")
    elif current_return >= 0 and matched_return < 0:
        insights.append("🔄 Pattern similarity exists but trend direction differs - monitor closely")
    
    # Volatility insight
    return_diff = abs(current_return - matched_return)
    if return_diff < 2:
        insights.append("✅ Return magnitude is very similar between periods")
    elif return_diff < 5:
        insights.append("📏 Return magnitude shows moderate difference between periods")
    
    return insights


def find_best_match(db: Session, request: PatternMatchRequest) -> PatternMatchResponse:
    """
    Main AI function - Find best matching historical period using real data.
    
    Algorithm:
    1. Get current period data (last N trading days)
    2. Get ALL historical data for the stock
    3. Slide a window of same size across historical data
    4. Calculate Pearson correlation for each window
    5. Return the window with highest correlation
    """
    stock = request.stock_symbol.upper().strip()
    exchange = request.exchange.upper().strip()
    period_days = request.period_days
    
    # Build symbol with suffix
    symbol = f"{stock}.NS" if exchange == "NSE" else f"{stock}.BO"
    
    # Current period: last period_days calendar days
    current_end = date.today()
    current_start = current_end - timedelta(days=period_days)
    
    # Fetch current period data
    current_rows = fetch_daily_data(db, symbol, current_start, current_end)
    
    if not current_rows or len(current_rows) < 5:
        raise ValueError(
            f"Not enough current data for {stock} ({exchange}). "
            f"Found {len(current_rows) if current_rows else 0} days, need at least 5."
        )
    
    # Get current period closes for correlation
    current_closes = [r.close for r in current_rows]
    current_normalized = normalize_prices(current_closes)
    num_trading_days = len(current_rows)
    
    # Fetch ALL historical data (excluding last period_days*2 to avoid overlap)
    history_end = current_start - timedelta(days=1)
    # Go back max 5 years for data
    history_start = history_end - timedelta(days=365 * 5)
    
    all_historical = fetch_daily_data(db, symbol, history_start, history_end)
    
    if not all_historical or len(all_historical) < num_trading_days:
        raise ValueError(
            f"Not enough historical data for {stock} ({exchange}). "
            f"Found {len(all_historical) if all_historical else 0} days, "
            f"need at least {num_trading_days}."
        )
    
    # Sliding window - find best correlation
    best_correlation = -2  # Start below minimum possible
    best_start_idx = 0
    
    # Step by 1 trading day for precision
    for i in range(len(all_historical) - num_trading_days + 1):
        window = all_historical[i:i + num_trading_days]
        window_closes = [r.close for r in window]
        window_normalized = normalize_prices(window_closes)
        
        corr = pearson_correlation(current_normalized, window_normalized)
        
        if corr > best_correlation:
            best_correlation = corr
            best_start_idx = i
    
    # Get the best matching window
    matched_rows = all_historical[best_start_idx:best_start_idx + num_trading_days]
    
    # Convert correlation to match percentage (0-100)
    # correlation ranges from -1 to 1, we want 0 to 100
    match_percentage = round(max(0, min(100, (best_correlation + 1) * 50)), 1)
    
    # Build period data objects
    current_label = f"{current_rows[0].date.strftime('%b %d')} - {current_rows[-1].date.strftime('%b %d, %Y')}"
    matched_label = f"{matched_rows[0].date.strftime('%b %d')} - {matched_rows[-1].date.strftime('%b %d, %Y')}"
    
    current_period = build_period_data(current_rows, current_label)
    matched_period = build_period_data(matched_rows, matched_label)
    
    # Generate insights
    insights = generate_insights(
        correlation=round(best_correlation, 4),
        match_pct=match_percentage,
        current_return=current_period.summary.period_return_pct,
        matched_return=matched_period.summary.period_return_pct,
        current_days=current_period.summary.total_days,
        matched_days=matched_period.summary.total_days
    )
    
    # Message
    if match_percentage >= 80:
        message = f"🎯 Excellent pattern match found! {match_percentage}% similarity"
    elif match_percentage >= 65:
        message = f"📊 Good pattern match found with {match_percentage}% similarity"
    else:
        message = f"📈 Best available match found with {match_percentage}% similarity"
    
    return PatternMatchResponse(
        success=True,
        stock_symbol=stock,
        exchange=exchange,
        match_percentage=match_percentage,
        correlation=round(best_correlation, 4),
        current_period=current_period,
        matched_period=matched_period,
        message=message,
        insights=insights
    )


def get_available_stocks(db: Session) -> dict:
    """Get stocks that have data in the database"""
    # Query distinct symbols from daily_data
    symbols = (
        db.query(DailyData.symbol)
        .distinct()
        .order_by(DailyData.symbol)
        .all()
    )
    
    result = {}
    for (sym,) in symbols:
        if sym and sym.endswith('.NS'):
            clean = sym.replace('.NS', '')
            if 'NSE' not in result.get(clean, []):
                result.setdefault(clean, []).append('NSE')
        elif sym and sym.endswith('.BO'):
            clean = sym.replace('.BO', '')
            if 'BSE' not in result.get(clean, []):
                result.setdefault(clean, []).append('BSE')
    
    return result
