#!/usr/bin/env python3
"""
NSE Technical Analyzer

Analyzes technical indicators and price patterns for stocks:
1. Trend (10 points) - Moving averages, golden/death crosses
2. Momentum (10 points) - RSI, MACD, Stochastic
3. Support/Resistance (5 points) - Key price levels
4. Volume (5 points) - Volume trends and accumulation/distribution

Total: 0-30 points per stock
"""

import argparse
import pandas as pd
import yfinance as yf
import numpy as np
import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Analyzes technical indicators and assigns scores"""

    def fetch_price_data(self, symbol: str, period: str = "1y") -> Optional[pd.DataFrame]:
        """
        Fetch historical price data.

        Args:
            symbol: NSE stock symbol (without .NS)
            period: Data period (default: 1 year)

        Returns:
            DataFrame with OHLCV data or None
        """
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            hist = ticker.history(period=period)

            if hist.empty or len(hist) < 50:
                logger.warning(f"{symbol}: Insufficient price data")
                return None

            return hist

        except Exception as e:
            logger.error(f"Error fetching price data for {symbol}: {str(e)}")
            return None

    def calculate_moving_averages(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate key moving averages.

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with MA columns added
        """
        df['SMA_20'] = df['Close'].rolling(window=20).mean()
        df['SMA_50'] = df['Close'].rolling(window=50).mean()
        df['SMA_200'] = df['Close'].rolling(window=200).mean()

        # Exponential moving averages
        df['EMA_12'] = df['Close'].ewm(span=12, adjust=False).mean()
        df['EMA_26'] = df['Close'].ewm(span=26, adjust=False).mean()

        return df

    def calculate_rsi(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Relative Strength Index.

        Args:
            df: DataFrame with price data
            period: RSI period (default: 14)

        Returns:
            DataFrame with RSI column added
        """
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        return df

    def calculate_macd(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate MACD (Moving Average Convergence Divergence).

        Args:
            df: DataFrame with price data

        Returns:
            DataFrame with MACD columns added
        """
        df['MACD'] = df['EMA_12'] - df['EMA_26']
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Histogram'] = df['MACD'] - df['MACD_Signal']

        return df

    def calculate_stochastic(self, df: pd.DataFrame, period: int = 14) -> pd.DataFrame:
        """
        Calculate Stochastic Oscillator.

        Args:
            df: DataFrame with price data
            period: Stochastic period (default: 14)

        Returns:
            DataFrame with Stochastic columns added
        """
        low_min = df['Low'].rolling(window=period).min()
        high_max = df['High'].rolling(window=period).max()

        df['Stochastic_%K'] = 100 * (df['Close'] - low_min) / (high_max - low_min)
        df['Stochastic_%D'] = df['Stochastic_%K'].rolling(window=3).mean()

        return df

    def score_trend(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score trend indicators (0-10 points).

        Criteria:
        - Price vs 50-day MA (3 pts)
        - Price vs 200-day MA (3 pts)
        - 50-day vs 200-day MA (golden/death cross) (2 pts)
        - Trend strength (2 pts)

        Args:
            df: DataFrame with price and MA data

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        latest = df.iloc[-1]
        current_price = latest['Close']

        # Price vs 50-day MA (3 points)
        sma_50 = latest['SMA_50']
        if pd.notna(sma_50):
            pct_above_50 = ((current_price - sma_50) / sma_50) * 100

            if pct_above_50 > 5:
                score += 3
                breakdown['price_vs_50ma'] = 3
            elif pct_above_50 > 0:
                score += 2
                breakdown['price_vs_50ma'] = 2
            elif pct_above_50 > -5:
                score += 1
                breakdown['price_vs_50ma'] = 1
            else:
                breakdown['price_vs_50ma'] = 0

            breakdown['pct_above_50ma'] = round(pct_above_50, 1)
        else:
            breakdown['price_vs_50ma'] = 0

        # Price vs 200-day MA (3 points)
        sma_200 = latest['SMA_200']
        if pd.notna(sma_200):
            pct_above_200 = ((current_price - sma_200) / sma_200) * 100

            if pct_above_200 > 10:
                score += 3
                breakdown['price_vs_200ma'] = 3
            elif pct_above_200 > 0:
                score += 2
                breakdown['price_vs_200ma'] = 2
            elif pct_above_200 > -10:
                score += 1
                breakdown['price_vs_200ma'] = 1
            else:
                breakdown['price_vs_200ma'] = 0

            breakdown['pct_above_200ma'] = round(pct_above_200, 1)
        else:
            breakdown['price_vs_200ma'] = 0

        # Golden/Death Cross (2 points)
        if pd.notna(sma_50) and pd.notna(sma_200):
            if sma_50 > sma_200:
                # Golden cross - bullish
                pct_gap = ((sma_50 - sma_200) / sma_200) * 100
                if pct_gap > 5:
                    score += 2
                    breakdown['ma_cross'] = 2
                else:
                    score += 1
                    breakdown['ma_cross'] = 1
            else:
                breakdown['ma_cross'] = 0
        else:
            breakdown['ma_cross'] = 0

        # Trend strength - price momentum over 20 days (2 points)
        if len(df) >= 20:
            price_20_days_ago = df['Close'].iloc[-20]
            momentum_20d = ((current_price - price_20_days_ago) / price_20_days_ago) * 100

            if momentum_20d > 10:
                score += 2
                breakdown['trend_strength'] = 2
            elif momentum_20d > 5:
                score += 1.5
                breakdown['trend_strength'] = 1.5
            elif momentum_20d > 0:
                score += 1
                breakdown['trend_strength'] = 1
            else:
                breakdown['trend_strength'] = 0

            breakdown['momentum_20d_pct'] = round(momentum_20d, 1)
        else:
            breakdown['trend_strength'] = 0

        breakdown['trend_total'] = round(score, 1)
        return score, breakdown

    def score_momentum(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score momentum indicators (0-10 points).

        Criteria:
        - RSI (4 pts) - optimal 40-60 range
        - MACD (3 pts) - bullish crossovers
        - Stochastic (3 pts) - not overbought/oversold

        Args:
            df: DataFrame with indicators

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        latest = df.iloc[-1]

        # RSI scoring (4 points) - optimal is 40-60 (neutral-bullish)
        rsi = latest['RSI']
        if pd.notna(rsi):
            if 45 <= rsi <= 55:
                # Perfect neutral zone - ready to move
                score += 4
                breakdown['rsi_score'] = 4
            elif 40 <= rsi <= 60:
                # Good zone
                score += 3
                breakdown['rsi_score'] = 3
            elif 35 <= rsi <= 65:
                # Acceptable
                score += 2
                breakdown['rsi_score'] = 2
            elif 30 <= rsi <= 70:
                score += 1
                breakdown['rsi_score'] = 1
            else:
                # Overbought (>70) or oversold (<30)
                breakdown['rsi_score'] = 0

            breakdown['rsi_value'] = round(rsi, 1)
        else:
            breakdown['rsi_score'] = 0

        # MACD scoring (3 points)
        macd = latest['MACD']
        macd_signal = latest['MACD_Signal']
        macd_hist = latest['MACD_Histogram']

        if pd.notna(macd) and pd.notna(macd_signal):
            if macd > macd_signal and macd_hist > 0:
                # Bullish: MACD above signal
                if macd_hist > 0.5:
                    score += 3
                    breakdown['macd_score'] = 3
                else:
                    score += 2
                    breakdown['macd_score'] = 2
            elif macd > macd_signal:
                score += 1
                breakdown['macd_score'] = 1
            else:
                breakdown['macd_score'] = 0

            breakdown['macd_position'] = 'bullish' if macd > macd_signal else 'bearish'
        else:
            breakdown['macd_score'] = 0

        # Stochastic scoring (3 points)
        stoch_k = latest['Stochastic_%K']
        stoch_d = latest['Stochastic_%D']

        if pd.notna(stoch_k) and pd.notna(stoch_d):
            if 40 <= stoch_k <= 60:
                # Neutral zone - not overbought/oversold
                score += 3
                breakdown['stochastic_score'] = 3
            elif 30 <= stoch_k <= 70:
                score += 2
                breakdown['stochastic_score'] = 2
            elif stoch_k < 30:
                # Oversold - potential bounce
                score += 1
                breakdown['stochastic_score'] = 1
            else:
                # Overbought (>70)
                breakdown['stochastic_score'] = 0

            breakdown['stochastic_k'] = round(stoch_k, 1)
        else:
            breakdown['stochastic_score'] = 0

        breakdown['momentum_total'] = round(score, 1)
        return score, breakdown

    def score_support_resistance(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score support/resistance levels (0-5 points).

        Criteria:
        - Distance from 52-week high (2 pts)
        - Distance from 52-week low (2 pts)
        - Recent breakout/breakdown (1 pt)

        Args:
            df: DataFrame with price data

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        current_price = df['Close'].iloc[-1]
        high_52w = df['High'].max()
        low_52w = df['Low'].min()

        # Distance from 52-week high (2 points)
        # Sweet spot: 10-30% below high (pullback but not broken)
        dist_from_high = ((high_52w - current_price) / high_52w) * 100

        if 10 <= dist_from_high <= 30:
            score += 2
            breakdown['sr_high_score'] = 2
        elif dist_from_high < 10:
            score += 1.5
            breakdown['sr_high_score'] = 1.5
        elif 30 < dist_from_high <= 50:
            score += 1
            breakdown['sr_high_score'] = 1
        else:
            breakdown['sr_high_score'] = 0

        breakdown['dist_from_52w_high_pct'] = round(dist_from_high, 1)

        # Distance from 52-week low (2 points)
        # Better if significantly above low
        dist_from_low = ((current_price - low_52w) / low_52w) * 100

        if dist_from_low > 50:
            score += 2
            breakdown['sr_low_score'] = 2
        elif dist_from_low > 30:
            score += 1.5
            breakdown['sr_low_score'] = 1.5
        elif dist_from_low > 15:
            score += 1
            breakdown['sr_low_score'] = 1
        else:
            breakdown['sr_low_score'] = 0

        breakdown['dist_from_52w_low_pct'] = round(dist_from_low, 1)

        # Recent breakout detection (1 point)
        # Check if price recently broke above 20-day high
        if len(df) >= 20:
            recent_20d = df.iloc[-20:]
            high_20d = recent_20d['High'].max()

            if current_price >= high_20d * 0.98:
                # Near or at 20-day high
                score += 1
                breakdown['breakout_score'] = 1
            else:
                breakdown['breakout_score'] = 0
        else:
            breakdown['breakout_score'] = 0

        breakdown['sr_total'] = round(score, 1)
        return score, breakdown

    def score_volume(self, df: pd.DataFrame) -> Tuple[float, Dict]:
        """
        Score volume patterns (0-5 points).

        Criteria:
        - Volume trend (3 pts)
        - Recent volume spike (2 pts)

        Args:
            df: DataFrame with volume data

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Average volumes
        vol_20d_avg = df['Volume'].iloc[-20:].mean() if len(df) >= 20 else df['Volume'].mean()
        vol_50d_avg = df['Volume'].iloc[-50:].mean() if len(df) >= 50 else vol_20d_avg

        current_vol = df['Volume'].iloc[-1]

        # Volume trend (3 points)
        # Compare recent volume to longer-term average
        vol_trend = ((vol_20d_avg - vol_50d_avg) / vol_50d_avg) * 100 if vol_50d_avg > 0 else 0

        if vol_trend > 20:
            # Strong volume increase
            score += 3
            breakdown['volume_trend_score'] = 3
        elif vol_trend > 10:
            score += 2
            breakdown['volume_trend_score'] = 2
        elif vol_trend > 0:
            score += 1
            breakdown['volume_trend_score'] = 1
        else:
            breakdown['volume_trend_score'] = 0

        breakdown['volume_trend_pct'] = round(vol_trend, 1)

        # Recent volume spike (2 points)
        vol_spike = ((current_vol - vol_20d_avg) / vol_20d_avg) * 100 if vol_20d_avg > 0 else 0

        if vol_spike > 100:
            # More than 2x average
            score += 2
            breakdown['volume_spike_score'] = 2
        elif vol_spike > 50:
            score += 1.5
            breakdown['volume_spike_score'] = 1.5
        elif vol_spike > 20:
            score += 1
            breakdown['volume_spike_score'] = 1
        else:
            breakdown['volume_spike_score'] = 0

        breakdown['volume_spike_pct'] = round(vol_spike, 1)

        breakdown['volume_total'] = round(score, 1)
        return score, breakdown

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """
        Complete technical analysis for a stock.

        Args:
            symbol: NSE stock symbol

        Returns:
            Dict with technical scores and metrics
        """
        # Fetch price data
        df = self.fetch_price_data(symbol)
        if df is None:
            return None

        # Calculate all indicators
        df = self.calculate_moving_averages(df)
        df = self.calculate_rsi(df)
        df = self.calculate_macd(df)
        df = self.calculate_stochastic(df)

        # Score each dimension
        trend_score, trend_breakdown = self.score_trend(df)
        momentum_score, momentum_breakdown = self.score_momentum(df)
        sr_score, sr_breakdown = self.score_support_resistance(df)
        volume_score, volume_breakdown = self.score_volume(df)

        # Total technical score
        total_score = trend_score + momentum_score + sr_score + volume_score

        # Compile results
        result = {
            'symbol': symbol,
            'technical_score': round(total_score, 1),
            'trend_score': round(trend_score, 1),
            'momentum_score': round(momentum_score, 1),
            'sr_score': round(sr_score, 1),
            'volume_score': round(volume_score, 1),

            **trend_breakdown,
            **momentum_breakdown,
            **sr_breakdown,
            **volume_breakdown
        }

        # Add key technical signals
        latest = df.iloc[-1]
        result['current_price'] = round(latest['Close'], 2)
        result['sma_50'] = round(latest['SMA_50'], 2) if pd.notna(latest['SMA_50']) else None
        result['sma_200'] = round(latest['SMA_200'], 2) if pd.notna(latest['SMA_200']) else None
        result['rsi'] = round(latest['RSI'], 1) if pd.notna(latest['RSI']) else None

        return result


def main():
    parser = argparse.ArgumentParser(description='Technical Analysis for NSE stocks')
    parser.add_argument('--input', required=True, help='Input CSV with stock universe')
    parser.add_argument('--output', required=True, help='Output CSV with technical scores')
    parser.add_argument('--delay', type=float, default=0.3,
                       help='Delay between API calls in seconds')

    args = parser.parse_args()

    logger.info("Starting technical analysis...")

    # Load stock universe
    universe_df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(universe_df)} stocks from {args.input}")

    analyzer = TechnicalAnalyzer()
    results = []

    for i, row in universe_df.iterrows():
        symbol = row['symbol']
        logger.info(f"Analyzing {i+1}/{len(universe_df)}: {symbol}")

        result = analyzer.analyze_stock(symbol)
        if result:
            results.append(result)

        time.sleep(args.delay)

        if (i + 1) % 50 == 0:
            logger.info(f"Progress: {i+1}/{len(universe_df)} ({(i+1)/len(universe_df)*100:.1f}%)")

    # Save results
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('technical_score', ascending=False)
    results_df.to_csv(args.output, index=False)

    logger.info(f"\nSaved {len(results)} analyzed stocks to {args.output}")

    # Summary statistics
    logger.info("\n=== Technical Analysis Summary ===")
    logger.info(f"Stocks analyzed: {len(results)}")
    logger.info(f"Average technical score: {results_df['technical_score'].mean():.1f}/30")
    logger.info(f"Median technical score: {results_df['technical_score'].median():.1f}/30")
    logger.info(f"Top score: {results_df['technical_score'].max():.1f}/30")

    logger.info(f"\nTop 10 stocks by technical score:")
    print(results_df[['symbol', 'technical_score', 'trend_score',
                      'momentum_score', 'sr_score', 'volume_score']].head(10))


if __name__ == '__main__':
    main()
