import yfinance as yf
from prophet import Prophet
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

class PortfolioRecommendationService:
    
    def __init__(self):
        self.default_years = 5
    
    def validate_ticker(self, ticker):
        """
        Validate if ticker exists and return basic info
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            if info and 'symbol' in info:
                return True, None
            return False, f"Invalid ticker: {ticker}"
        except Exception as e:
            return False, f"Error validating {ticker}: {str(e)}"
    
    def analyze_portfolio(self, portfolio_data, projection_months=12, years_of_data=5):
        """
        Analyze portfolio with any stock symbols
        portfolio_data: {"RELIANCE.NS": 10, "AAPL": 5}
        projection_months: How many months to project into future (default: 12)
        years_of_data: How many years of historical data to use (default: 5, max: 15)
        """
        results = []
        invalid_tickers = []
        
        # Ensure years_of_data is within valid range
        years_of_data = max(1, min(15, years_of_data))
        
        for ticker, shares in portfolio_data.items():
            # Validate ticker first
            is_valid, error = self.validate_ticker(ticker)
            if not is_valid:
                invalid_tickers.append({"ticker": ticker, "error": error})
                continue
            
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="{}y".format(years_of_data))
                
                if len(hist) == 0:
                    invalid_tickers.append({"ticker": ticker, "error": "No historical data available"})
                    continue
                
                current_price = info.get('currentPrice', hist['Close'].iloc[-1])
                position_value = current_price * shares
                
                close = hist['Close']
                
                # Technical indicators
                sma_20 = close.rolling(20).mean().iloc[-1] if len(close) >= 20 else current_price
                sma_50 = close.rolling(50).mean().iloc[-1] if len(close) >= 50 else current_price
                sma_200 = close.rolling(200).mean().iloc[-1] if len(close) >= 200 else current_price
                
                delta = close.diff()
                gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                rs = gain / loss
                rsi = 100 - (100 / (1 + rs))
                current_rsi = rsi.iloc[-1] if len(rsi) > 0 else 50
                
                ema_12 = close.ewm(span=12).mean()
                ema_26 = close.ewm(span=26).mean()
                macd = ema_12 - ema_26
                signal_line = macd.ewm(span=9).mean()
                macd_hist = macd - signal_line
                current_macd = macd_hist.iloc[-1] if len(macd_hist) > 0 else 0
                
                momentum = close.pct_change(periods=10).iloc[-1] if len(close) > 10 else 0
                volatility = close.pct_change().std() * np.sqrt(252) * 100
                
                # Technical score calculation
                technical_score = 0
                
                if current_price > sma_20:
                    technical_score += 1
                if current_price > sma_50:
                    technical_score += 1
                if current_price > sma_200:
                    technical_score += 1
                
                if current_rsi < 30:
                    technical_score += 2
                elif current_rsi < 50:
                    technical_score += 1
                elif current_rsi > 70:
                    technical_score -= 2
                
                if current_macd > 0:
                    technical_score += 2
                elif current_macd < 0:
                    technical_score -= 1
                
                if momentum > 0.02:
                    technical_score += 2
                elif momentum > 0:
                    technical_score += 1
                elif momentum < -0.02:
                    technical_score -= 2
                
                # Prophet forecasting (uses all historical data specified)
                try:
                    prophet_df = pd.DataFrame({
                        'ds': hist.index.tz_localize(None),
                        'y': hist['Close'].values
                    })
                    
                    # More data = better predictions
                    model = Prophet(
                        daily_seasonality=False,
                        yearly_seasonality=True,
                        weekly_seasonality=True,
                        changepoint_prior_scale=0.05
                    )
                    
                    with warnings.catch_warnings():
                        warnings.simplefilter("ignore")
                        model.fit(prophet_df)
                    
                    future = model.make_future_dataframe(periods=projection_months*30)
                    forecast = model.predict(future)
                    
                    projected_price = forecast['yhat'].iloc[-1]
                    confidence_lower = forecast['yhat_lower'].iloc[-1]
                    confidence_upper = forecast['yhat_upper'].iloc[-1]
                    
                except:
                    trend = close.pct_change(30).mean()
                    projected_price = current_price * (1 + trend * projection_months)
                    confidence_lower = projected_price * 0.8
                    confidence_upper = projected_price * 1.2
                
                projected_value = projected_price * shares
                price_change_pct = ((projected_price - current_price) / current_price) * 100
                
                # Signal determination
                if technical_score >= 5 and price_change_pct > 10:
                    signal = 1
                    action = "STRONG_BUY"
                elif technical_score >= 3 and price_change_pct > 5:
                    signal = 1
                    action = "BUY"
                elif technical_score <= -3 or price_change_pct < -10:
                    signal = -1
                    action = "SELL"
                elif price_change_pct < -5:
                    signal = -1
                    action = "SELL"
                else:
                    signal = 0
                    action = "HOLD"
                
                # Get company name
                company_name = info.get('longName', info.get('shortName', ticker))
                
                results.append({
                    'ticker': ticker,
                    'company_name': company_name,
                    'shares': int(shares),
                    'current_price': round(float(current_price), 2),
                    'projected_price': round(float(projected_price), 2),
                    'current_value': round(float(position_value), 2),
                    'projected_value': round(float(projected_value), 2),
                    'change_percent': round(float(price_change_pct), 2),
                    'signal': int(signal),
                    'action': action,
                    'confidence_lower': round(float(confidence_lower), 2),
                    'confidence_upper': round(float(confidence_upper), 2),
                    'volatility': round(float(volatility), 2),
                    'rsi': round(float(current_rsi), 2),
                    'macd': round(float(current_macd), 2),
                    'technical_score': technical_score
                })
            
            except Exception as e:
                invalid_tickers.append({"ticker": ticker, "error": str(e)})
                continue
        
        total_current = sum(r['current_value'] for r in results)
        total_projected = sum(r['projected_value'] for r in results)
        total_return = ((total_projected - total_current) / total_current) * 100 if total_current > 0 else 0
        
        buy_count = sum(1 for r in results if r['signal'] == 1)
        sell_count = sum(1 for r in results if r['signal'] == -1)
        hold_count = sum(1 for r in results if r['signal'] == 0)
        
        return {
            'stocks': results,
            'portfolio_summary': {
                'current_value': round(float(total_current), 2),
                'projected_value': round(float(total_projected), 2),
                'expected_return': round(float(total_return), 2),
                'projection_months': int(projection_months),
                'total_stocks': len(results),
                'valid_stocks': len(results),
                'invalid_stocks': len(invalid_tickers),
                'years_of_data_used': int(years_of_data)
            },
            'signal_distribution': {
                'buy': int(buy_count),
                'sell': int(sell_count),
                'hold': int(hold_count)
            },
            'invalid_tickers': invalid_tickers
        }

portfolio_service = PortfolioRecommendationService()