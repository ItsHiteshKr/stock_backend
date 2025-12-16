from model.daily_data import DailyData
from sqlalchemy.orm import Session
import statistics
import numpy as np

# ------------------------------
# Helper: normalize symbol
# ------------------------------
def normalize_symbol(symbol: str) -> str:
    symbol = symbol.upper()
    if not symbol.endswith(".NS"):
        symbol += ".NS"
    return symbol


# ------------------------------
# Helper: fetch recent prices
# ------------------------------
def get_recent_data(db: Session, symbol: str, days: int = 20):
    symbol = normalize_symbol(symbol)
    return (
        db.query(DailyData)
        .filter(DailyData.symbol == symbol)
        .order_by(DailyData.date.desc())
        .limit(days)
        .all()
    )


# ------------------------------
# Auto Trend Insight
# ------------------------------
def auto_insight(db: Session, symbol: str):
    data = get_recent_data(db, symbol, 10)

    if len(data) < 2:
        return "Not enough data for trend analysis."

    if data[0].close > data[-1].close:
        return "Stock is showing an upward trend 📈"
    else:
        return "Stock is showing a downward trend 📉"


# ------------------------------
# Momentum Insight
# ------------------------------
def momentum_insight(db: Session, symbol: str):
    data = get_recent_data(db, symbol, 7)

    if len(data) < 2:
        return None

    start = data[-1].close
    end = data[0].close
    pct = round(((end - start) / start) * 100, 2)

    return {
        "momentum": "Positive" if pct > 0 else "Negative",
        "percent_change": pct
    }


# ------------------------------
# Volatility Insight
# ------------------------------
def volatility_insight(db: Session, symbol: str):
    data = get_recent_data(db, symbol, 20)
    closes = [d.close for d in data]

    if len(closes) < 2:
        return None

    returns = [
        (closes[i] - closes[i + 1]) / closes[i + 1]
        for i in range(len(closes) - 1)
    ]

    vol = round(statistics.stdev(returns) * 100, 2)

    level = "High" if vol > 3 else "Medium" if vol > 1 else "Low"
    return {
        "volatility_percent": vol,
        "level": level
    }


# ------------------------------
# Alert Insight
# ------------------------------
def alert_insight(db: Session, symbol: str):
    data = get_recent_data(db, symbol, 5)
    alerts = []

    if len(data) < 2:
        return alerts

    if data[0].close > max(d.high for d in data[1:]):
        alerts.append("Price breakout 🚀")

    if data[0].close < min(d.low for d in data[1:]):
        alerts.append("Price breakdown ⚠️")

    return alerts


# ------------------------------
# AI-Generated Insight (Rule-Based)
# ------------------------------
def ai_generated_insight(db: Session, symbol: str):
    symbol = normalize_symbol(symbol)

    data = (
        db.query(DailyData)
        .filter(DailyData.symbol == symbol)
        .order_by(DailyData.date.desc())
        .limit(30)
        .all()
    )

    if len(data) < 15:
        return {
            "symbol": symbol,
            "ai_insight": "Not enough recent data to generate AI insight."
        }

    closes = np.array([d.close for d in reversed(data)])
    returns = np.diff(closes) / closes[:-1]

    avg_return = returns.mean()
    volatility = returns.std()

    if avg_return > 0.002:
        momentum = "positive"
        outlook = "potential upside"
    elif avg_return < -0.002:
        momentum = "negative"
        outlook = "downside risk"
    else:
        momentum = "neutral"
        outlook = "sideways movement"

    risk = "high volatility" if volatility > 0.03 else "stable volatility"

    insight = (
        f"{symbol} is showing {momentum} momentum with {risk}. "
        f"The stock indicates {outlook} in the near term."
    )

    return {
        "symbol": symbol,
        "ai_insight": insight
    }


def buy_sell_hold_decision(db: Session, symbol: str):
    data = get_recent_data(db, symbol, 10)  # last 10 days

    if len(data) < 5:
        return {
            "symbol": normalize_symbol(symbol),
            "decision": "Not enough data"
        }

    closes = np.array([d.close for d in reversed(data)])
    sma5 = closes[-5:].mean()
    today_close = closes[-1]

    # Momentum
    returns = np.diff(closes) / closes[:-1]
    avg_return = returns.mean()

    momentum = "positive" if avg_return > 0.002 else "negative" if avg_return < -0.002 else "neutral"

    # Buy/Sell/Hold logic
    if today_close > sma5 and momentum == "positive":
        decision = "Buy 🟢"
    elif today_close < sma5 and momentum == "negative":
        decision = "Sell 🔴"
    else:
        decision = "Hold ⚪"

    # Optional breakout/breakdown override
    recent_high = max(closes[-5:-1])
    recent_low = min(closes[-5:-1])

    if today_close > recent_high:
        decision = "Strong Buy 🚀"
    elif today_close < recent_low:
        decision = "Strong Sell ⚠️"

    return {
        "symbol": normalize_symbol(symbol),
        "decision": decision,
        "sma5": round(sma5, 2),
        "momentum": momentum,
        "today_close": round(today_close, 2)
    }
