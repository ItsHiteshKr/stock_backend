def build_stock_prompt(
    symbol: str,
    trend: str,
    momentum: float,
    volatility: float,
    volume_trend: str
):
    return f"""
You are a stock market analyst.

Analyze the stock below and give a short, clear insight
in simple language for retail investors.

Stock: {symbol}
Trend: {trend}
Momentum (% change): {momentum}
Volatility: {volatility}
Volume Trend: {volume_trend}

Explain what this means and whether the stock looks strong or weak.
"""
