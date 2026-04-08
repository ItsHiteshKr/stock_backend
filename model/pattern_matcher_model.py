import yfinance as yf
import numpy as np
import pandas as pd
from scipy.stats import pearsonr, spearmanr
import hashlib
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
import os
import warnings

warnings.filterwarnings('ignore')


class PatternMatcherModel:
    """
    Stock Pattern Matching Model
    SAME algorithm as best_matcher.py with EXACT same weights
    """
    
    def __init__(self, symbol: str, years_back: int = 5, cache_dir: str = './stock_cache'):
        self.symbol = symbol.upper()
        self.years_back = years_back
        self.cache_dir = cache_dir
        self.df = None
        self.data_hash = None
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def get_cache_path(self) -> str:
        return os.path.join(self.cache_dir, f"{self.symbol}_{self.years_back}y.csv")
    
    def is_cache_fresh(self) -> bool:
        cache_path = self.get_cache_path()
        if not os.path.exists(cache_path):
            return False
        file_time = datetime.fromtimestamp(os.path.getmtime(cache_path))
        age_hours = (datetime.now() - file_time).total_seconds() / 3600
        return age_hours < 24
    
    def load_data(self, use_cache: bool = True) -> Tuple[bool, str]:
        """Load stock data with caching"""
        cache_path = self.get_cache_path()
        
        # Try cache first
        if use_cache and self.is_cache_fresh():
            try:
                self.df = pd.read_csv(cache_path)
                self.df['Date'] = pd.to_datetime(self.df['Date'])
                self.data_hash = hashlib.md5(self.df.to_csv(index=False).encode()).hexdigest()
                return True, f"Loaded from cache ({len(self.df)} days)"
            except:
                pass
        
        # Download fresh data with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            try:
                ticker = yf.Ticker(self.symbol)
                df = ticker.history(period=f"{self.years_back}y")
                
                if df.empty:
                    # Try with max period as fallback
                    if attempt == 0:
                        df = ticker.history(period="max")
                    
                    if df.empty:
                        if attempt < max_retries - 1:
                            continue  # Retry
                        return False, f"No data available for {self.symbol}. Please check symbol and try again."
                
                df = df[['Close', 'Volume']].copy()
                df.reset_index(inplace=True)
                df = df.iloc[:-1].reset_index(drop=True)
                
                # Dynamic minimum
                min_required = 50
                
                if len(df) < min_required:
                    return False, f"Insufficient data: need at least {min_required} days, got {len(df)} days. Stock may be recently listed."
                
                self.df = df
                self.data_hash = hashlib.md5(df.to_csv(index=False).encode()).hexdigest()
                df.to_csv(cache_path, index=False)
                
                return True, f"Downloaded {len(df)} trading days"
                
            except Exception as e:
                if attempt < max_retries - 1:
                    import time
                    time.sleep(1)  # Wait 1 second before retry
                    continue
                return False, f"Download failed after {max_retries} attempts. Please try again later."
        
        return False, f"Failed to download data for {self.symbol}"
    
    def normalize_pattern(self, prices: np.ndarray) -> np.ndarray:
        """SAME normalization as original best_matcher.py"""
        if len(prices) < 2:
            return np.zeros(len(prices))
        
        log_returns = np.log(prices[1:] / prices[:-1])
        log_returns = np.where(np.isfinite(log_returns), log_returns, 0)
        
        mean = np.mean(log_returns)
        std = np.std(log_returns)
        
        if std == 0 or not np.isfinite(std):
            return np.zeros(len(log_returns))
        
        normalized = (log_returns - mean) / std
        normalized = np.where(np.isfinite(normalized), normalized, 0)
        
        return normalized
    
    def calculate_scores(self, curr_pattern: np.ndarray, match_pattern: np.ndarray,
                        curr_return: float, match_return: float) -> float:
        """
        SAME 5 scoring methods as original best_matcher.py
        EXACT weights: Pearson 35%, Cosine 25%, Spearman 20%, Magnitude 15%, Volatility 5%
        """
        
        # 1. Pearson Correlation (35%)
        try:
            mask = np.isfinite(curr_pattern) & np.isfinite(match_pattern)
            if np.sum(mask) >= 2:
                corr, _ = pearsonr(curr_pattern[mask], match_pattern[mask])
                pearson_score = (corr + 1) * 50 if np.isfinite(corr) else 50
            else:
                pearson_score = 50
        except:
            pearson_score = 50
        
        # 2. Cosine Similarity (25%)
        try:
            dot = np.dot(curr_pattern, match_pattern)
            norm1 = np.linalg.norm(curr_pattern)
            norm2 = np.linalg.norm(match_pattern)
            
            if norm1 > 0 and norm2 > 0:
                cosine = dot / (norm1 * norm2)
                cosine_score = (cosine + 1) * 50 if np.isfinite(cosine) else 50
            else:
                cosine_score = 50
        except:
            cosine_score = 50
        
        # 3. Spearman Correlation (20%)
        try:
            mask = np.isfinite(curr_pattern) & np.isfinite(match_pattern)
            if np.sum(mask) >= 2:
                spear, _ = spearmanr(curr_pattern[mask], match_pattern[mask])
                spearman_score = (spear + 1) * 50 if np.isfinite(spear) else 50
            else:
                spearman_score = 50
        except:
            spearman_score = 50
        
        # 4. Magnitude Match (15%)
        if abs(curr_return) > 0.001:
            mag_diff = abs(match_return - curr_return) / abs(curr_return)
            magnitude_score = max(0, 100 * (1 - mag_diff / 2))
        else:
            magnitude_score = 50
        
        # 5. Volatility Match (5%)
        vol1 = np.std(curr_pattern)
        vol2 = np.std(match_pattern)
        if vol1 > 0 and vol2 > 0 and np.isfinite(vol1) and np.isfinite(vol2):
            vol_ratio = min(vol1, vol2) / max(vol1, vol2)
            volatility_score = vol_ratio * 100
        else:
            volatility_score = 50
        
        # Weighted ensemble - SAME as original
        final_score = (
            pearson_score * 0.35 +
            cosine_score * 0.25 +
            spearman_score * 0.20 +
            magnitude_score * 0.15 +
            volatility_score * 0.05
        )
        
        if not np.isfinite(final_score):
            return 0.0
        
        return float(max(0, min(100, final_score)))
    
    def find_best_match(self, window_size: int = 10) -> Optional[Dict]:
        """
        Find best match - SAME algorithm as original
        Returns JSON dict (NO images)
        """
        if self.df is None:
            return None
        
        # Check if we have enough data for this window size
        # Need: window_size for current + window_size for at least one historical match
        min_needed = (window_size + 2) * 2  # 2x largest window + buffer
        
        if len(self.df) < min_needed:
            # Not enough data for this window size - try smaller window
            return None
        
        # Test 3 window sizes - SAME as original
        window_sizes = [window_size - 2, window_size, window_size + 2]
        all_candidates = []
        
        for ws in window_sizes:
            curr_data = self.df.iloc[-ws:].copy()
            curr_close = curr_data['Close'].values
            curr_pattern = self.normalize_pattern(curr_close)
            
            curr_start = curr_close[0]
            curr_end = curr_close[-1]
            curr_change = ((curr_end - curr_start) / curr_start) * 100
            
            for i in range(len(self.df) - ws + 1):
                match_end_date = pd.to_datetime(self.df.iloc[i + ws - 1]['Date'])
                curr_start_date = pd.to_datetime(curr_data.iloc[0]['Date'])
                
                if match_end_date >= curr_start_date:
                    continue
                
                match_close = self.df.iloc[i:i+ws]['Close'].values
                match_pattern = self.normalize_pattern(match_close)
                
                match_start = match_close[0]
                match_end = match_close[-1]
                match_change = ((match_end - match_start) / match_start) * 100
                
                score = self.calculate_scores(
                    curr_pattern, match_pattern,
                    curr_change / 100, match_change / 100
                )
                
                # Trend bonus - SAME as original
                if np.sign(curr_change) == np.sign(match_change):
                    score = min(100, score + 10)
                else:
                    score *= 0.3
                
                all_candidates.append({
                    'idx': i,
                    'window_size': ws,
                    'score': float(score),
                    'date_start': self.df.iloc[i]['Date'].isoformat(),
                    'date_end': self.df.iloc[i+ws-1]['Date'].isoformat(),
                    'start_price': float(match_start),
                    'end_price': float(match_end),
                    'change_percent': float(match_change)
                })
        
        if not all_candidates:
            return None
        
        best = max(all_candidates, key=lambda x: x['score'])
        
        curr_data = self.df.iloc[-window_size:].copy()
        curr_close = curr_data['Close'].values
        curr_change = ((curr_close[-1] - curr_close[0]) / curr_close[0]) * 100
        
        # Return JSON dict (NO images) - ALL NATIVE PYTHON TYPES - CLEAN FORMAT
        return {
            'symbol': self.symbol,
            'current_pattern': {
                'date_start': curr_data.iloc[0]['Date'].strftime('%Y-%m-%d'),  # Clean date format
                'date_end': curr_data.iloc[-1]['Date'].strftime('%Y-%m-%d'),   # Clean date format
                'start_price': round(float(curr_close[0]), 2),  # 2 decimal places
                'end_price': round(float(curr_close[-1]), 2),   # 2 decimal places
                'change_percent': round(float(curr_change), 2), # 2 decimal places
                'trend': 'UP' if curr_change > 0 else 'DOWN',
                'window_size': int(window_size)
            },
            'best_match': {
                'date_start': pd.to_datetime(best['date_start']).strftime('%Y-%m-%d'),  # Clean date
                'date_end': pd.to_datetime(best['date_end']).strftime('%Y-%m-%d'),      # Clean date
                'start_price': round(float(best['start_price']), 2),  # 2 decimal places
                'end_price': round(float(best['end_price']), 2),      # 2 decimal places
                'change_percent': round(float(best['change_percent']), 2),  # 2 decimal places
                'trend': 'UP' if best['change_percent'] > 0 else 'DOWN',
                'window_size': int(best['window_size']),
                'score': round(float(best['score']), 2),  # 2 decimal places
                'trend_match': bool(np.sign(curr_change) == np.sign(best['change_percent'])),
                'confidence': self._get_confidence(best['score'])
            },
            #'algorithm': {
               # 'methods': [
                   # {'name': 'Pearson Correlation', 'weight': 35},
                  #  {'name': 'Cosine Similarity', 'weight': 25},
                 #   {'name': 'Spearman Correlation', 'weight': 20},
                #    {'name': 'Magnitude Match', 'weight': 15},
               #     {'name': 'Volatility Match', 'weight': 5}
              #  ],
             #   'window_sizes_tested': [int(ws) for ws in window_sizes]
            }
       # }
    
    @staticmethod
    def _get_confidence(score: float) -> str:
        if score >= 85:
            return 'Excellent'
        elif score >= 75:
            return 'Very Good'
        elif score >= 65:
            return 'Good'
        elif score >= 55:
            return 'Fair'
        else:
            return 'Weak'