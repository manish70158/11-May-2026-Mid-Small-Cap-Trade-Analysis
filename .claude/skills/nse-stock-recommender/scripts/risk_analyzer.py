#!/usr/bin/env python3
"""
NSE Risk Analyzer

Evaluates risk factors for stocks:
1. Volatility Risk (10 points) - Beta, standard deviation, max drawdown
2. Concentration Risk (5 points) - Promoter holding, sector concentration
3. Liquidity Risk (5 points) - Trading volume, bid-ask spread

Total: 0-20 points per stock (higher score = lower risk)
"""

import argparse
import pandas as pd
import yfinance as yf
import numpy as np
import time
import logging
from typing import Dict, Optional, Tuple

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class RiskAnalyzer:
    """Analyzes risk factors and assigns scores (higher = lower risk)"""

    def fetch_risk_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch risk-related data for a stock.

        Args:
            symbol: NSE stock symbol (without .NS)

        Returns:
            Dict with risk metrics or None
        """
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info
            hist = ticker.history(period="1y")

            if hist.empty or len(hist) < 50:
                logger.warning(f"{symbol}: Insufficient data for risk analysis")
                return None

            # Calculate volatility metrics
            returns = hist['Close'].pct_change().dropna()
            daily_volatility = returns.std()
            annual_volatility = daily_volatility * np.sqrt(252)

            # Calculate maximum drawdown
            cumulative_returns = (1 + returns).cumprod()
            running_max = cumulative_returns.expanding().max()
            drawdown = (cumulative_returns - running_max) / running_max
            max_drawdown = drawdown.min()

            # Average volume
            avg_volume = hist['Volume'].mean()

            data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),

                # Volatility metrics
                'beta': info.get('beta'),
                'annual_volatility': annual_volatility,
                'max_drawdown': max_drawdown,

                # Concentration metrics
                'held_percent_institutions': info.get('heldPercentInstitutions'),
                'held_percent_insiders': info.get('heldPercentInsiders'),
                'float_shares': info.get('floatShares'),
                'shares_outstanding': info.get('sharesOutstanding'),

                # Liquidity metrics
                'avg_volume': avg_volume,
                'market_cap': info.get('marketCap'),
                'bid_ask_spread': info.get('askSize', 0) - info.get('bidSize', 0),  # approximation

                # Additional risk factors
                'short_percent_float': info.get('shortPercentOfFloat'),
                'fifty_two_week_change': info.get('52WeekChange'),
            }

            return data

        except Exception as e:
            logger.error(f"Error fetching risk data for {symbol}: {str(e)}")
            return None

    def score_volatility_risk(self, stock: Dict) -> Tuple[float, Dict]:
        """
        Score volatility risk (0-10 points, higher = lower risk).

        Criteria:
        - Beta (4 pts): Prefer 0.8-1.2 range for short-term
        - Annual volatility (3 pts): Lower is better
        - Max drawdown (3 pts): Lower is better

        Args:
            stock: Stock risk data dict

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Beta scoring (4 points)
        beta = stock.get('beta')
        if beta is not None:
            if 0.8 <= beta <= 1.2:
                # Ideal range - moderate volatility
                score += 4
                breakdown['beta_score'] = 4
            elif 0.6 <= beta <= 1.5:
                score += 3
                breakdown['beta_score'] = 3
            elif 0.4 <= beta <= 1.8:
                score += 2
                breakdown['beta_score'] = 2
            elif beta < 2.5:
                score += 1
                breakdown['beta_score'] = 1
            else:
                breakdown['beta_score'] = 0

            breakdown['beta'] = round(beta, 2)
        else:
            # Assume market beta if not available
            score += 2
            breakdown['beta_score'] = 2

        # Annual volatility scoring (3 points)
        vol = stock.get('annual_volatility')
        if vol is not None:
            vol_pct = vol * 100

            if vol_pct < 25:
                # Low volatility
                score += 3
                breakdown['volatility_score'] = 3
            elif vol_pct < 35:
                score += 2.5
                breakdown['volatility_score'] = 2.5
            elif vol_pct < 50:
                score += 2
                breakdown['volatility_score'] = 2
            elif vol_pct < 70:
                score += 1
                breakdown['volatility_score'] = 1
            else:
                breakdown['volatility_score'] = 0

            breakdown['annual_volatility_pct'] = round(vol_pct, 1)
        else:
            breakdown['volatility_score'] = 0

        # Max drawdown scoring (3 points)
        drawdown = stock.get('max_drawdown')
        if drawdown is not None:
            drawdown_pct = abs(drawdown * 100)

            if drawdown_pct < 20:
                score += 3
                breakdown['drawdown_score'] = 3
            elif drawdown_pct < 30:
                score += 2.5
                breakdown['drawdown_score'] = 2.5
            elif drawdown_pct < 40:
                score += 2
                breakdown['drawdown_score'] = 2
            elif drawdown_pct < 50:
                score += 1
                breakdown['drawdown_score'] = 1
            else:
                breakdown['drawdown_score'] = 0

            breakdown['max_drawdown_pct'] = round(drawdown_pct, 1)
        else:
            breakdown['drawdown_score'] = 0

        breakdown['volatility_risk_total'] = round(score, 1)
        return score, breakdown

    def score_concentration_risk(self, stock: Dict) -> Tuple[float, Dict]:
        """
        Score concentration risk (0-5 points, higher = lower risk).

        Criteria:
        - Institutional holding (2 pts): 20-50% is stable
        - Insider holding (2 pts): 50-70% is ideal (promoter confidence without concentration)
        - Float (1 pt): Higher float is better

        Args:
            stock: Stock risk data dict

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Institutional holding scoring (2 points)
        inst_pct = stock.get('held_percent_institutions')
        if inst_pct is not None:
            inst_pct = inst_pct * 100

            if 20 <= inst_pct <= 50:
                # Goldilocks zone
                score += 2
                breakdown['institutional_score'] = 2
            elif 10 <= inst_pct <= 60:
                score += 1.5
                breakdown['institutional_score'] = 1.5
            elif inst_pct > 0:
                score += 1
                breakdown['institutional_score'] = 1
            else:
                breakdown['institutional_score'] = 0

            breakdown['institutional_holding_pct'] = round(inst_pct, 1)
        else:
            # Assume moderate institutional holding
            score += 1
            breakdown['institutional_score'] = 1

        # Insider/Promoter holding scoring (2 points)
        # In India, this typically reflects promoter holding
        insider_pct = stock.get('held_percent_insiders')
        if insider_pct is not None:
            insider_pct = insider_pct * 100

            if 50 <= insider_pct <= 70:
                # Ideal promoter holding
                score += 2
                breakdown['promoter_score'] = 2
            elif 40 <= insider_pct <= 75:
                score += 1.5
                breakdown['promoter_score'] = 1.5
            elif 30 <= insider_pct <= 80:
                score += 1
                breakdown['promoter_score'] = 1
            else:
                breakdown['promoter_score'] = 0

            breakdown['promoter_holding_pct'] = round(insider_pct, 1)
        else:
            # Assume moderate promoter holding
            score += 1
            breakdown['promoter_score'] = 1

        # Float scoring (1 point)
        float_shares = stock.get('float_shares')
        shares_out = stock.get('shares_outstanding')

        if float_shares and shares_out and shares_out > 0:
            float_pct = (float_shares / shares_out) * 100

            if float_pct > 40:
                score += 1
                breakdown['float_score'] = 1
            elif float_pct > 25:
                score += 0.5
                breakdown['float_score'] = 0.5
            else:
                breakdown['float_score'] = 0

            breakdown['float_pct'] = round(float_pct, 1)
        else:
            # Assume reasonable float
            score += 0.5
            breakdown['float_score'] = 0.5

        breakdown['concentration_risk_total'] = round(score, 1)
        return score, breakdown

    def score_liquidity_risk(self, stock: Dict) -> Tuple[float, Dict]:
        """
        Score liquidity risk (0-5 points, higher = lower risk).

        Criteria:
        - Trading volume (3 pts): Higher is better
        - Market cap (2 pts): Larger is safer for short-term

        Args:
            stock: Stock risk data dict

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Volume scoring (3 points)
        avg_vol = stock.get('avg_volume')
        if avg_vol:
            if avg_vol > 1000000:
                # Very liquid
                score += 3
                breakdown['volume_score'] = 3
            elif avg_vol > 500000:
                score += 2.5
                breakdown['volume_score'] = 2.5
            elif avg_vol > 200000:
                score += 2
                breakdown['volume_score'] = 2
            elif avg_vol > 100000:
                score += 1
                breakdown['volume_score'] = 1
            else:
                breakdown['volume_score'] = 0

            breakdown['avg_volume'] = int(avg_vol)
        else:
            breakdown['volume_score'] = 0

        # Market cap scoring (2 points)
        mcap = stock.get('market_cap')
        if mcap:
            mcap_cr = mcap / 10000000  # Convert to Crores

            if mcap_cr > 50000:
                # Large cap - very liquid
                score += 2
                breakdown['mcap_score'] = 2
            elif mcap_cr > 10000:
                # Mid cap
                score += 1.5
                breakdown['mcap_score'] = 1.5
            elif mcap_cr > 5000:
                score += 1
                breakdown['mcap_score'] = 1
            elif mcap_cr > 1000:
                score += 0.5
                breakdown['mcap_score'] = 0.5
            else:
                breakdown['mcap_score'] = 0

            breakdown['market_cap_cr'] = round(mcap_cr, 0)
        else:
            breakdown['mcap_score'] = 0

        breakdown['liquidity_risk_total'] = round(score, 1)
        return score, breakdown

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """
        Complete risk analysis for a stock.

        Args:
            symbol: NSE stock symbol

        Returns:
            Dict with risk scores and metrics
        """
        # Fetch risk data
        data = self.fetch_risk_data(symbol)
        if not data:
            return None

        # Calculate scores
        vol_score, vol_breakdown = self.score_volatility_risk(data)
        conc_score, conc_breakdown = self.score_concentration_risk(data)
        liq_score, liq_breakdown = self.score_liquidity_risk(data)

        # Total risk score (higher = lower risk)
        total_score = vol_score + conc_score + liq_score

        # Compile results
        result = {
            'symbol': symbol,
            'name': data['name'],
            'sector': data['sector'],

            # Total score
            'risk_score': round(total_score, 1),

            # Component scores
            'volatility_risk_score': round(vol_score, 1),
            'concentration_risk_score': round(conc_score, 1),
            'liquidity_risk_score': round(liq_score, 1),

            # Breakdown details
            **vol_breakdown,
            **conc_breakdown,
            **liq_breakdown
        }

        # Add risk flags
        risk_flags = []

        if vol_breakdown.get('beta', 1) > 1.5:
            risk_flags.append('HIGH_BETA')

        if vol_breakdown.get('annual_volatility_pct', 0) > 60:
            risk_flags.append('HIGH_VOLATILITY')

        if vol_breakdown.get('max_drawdown_pct', 0) > 50:
            risk_flags.append('SEVERE_DRAWDOWN')

        if liq_breakdown.get('avg_volume', 0) < 100000:
            risk_flags.append('LOW_LIQUIDITY')

        result['risk_flags'] = ','.join(risk_flags) if risk_flags else 'NONE'

        return result


def main():
    parser = argparse.ArgumentParser(description='Risk Analysis for NSE stocks')
    parser.add_argument('--input', required=True, help='Input CSV with stock universe')
    parser.add_argument('--output', required=True, help='Output CSV with risk scores')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Delay between API calls in seconds')

    args = parser.parse_args()

    logger.info("Starting risk analysis...")

    # Load stock universe
    universe_df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(universe_df)} stocks from {args.input}")

    analyzer = RiskAnalyzer()
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
    results_df = results_df.sort_values('risk_score', ascending=False)  # Higher score = lower risk
    results_df.to_csv(args.output, index=False)

    logger.info(f"\nSaved {len(results)} analyzed stocks to {args.output}")

    # Summary statistics
    logger.info("\n=== Risk Analysis Summary ===")
    logger.info(f"Stocks analyzed: {len(results)}")
    logger.info(f"Average risk score: {results_df['risk_score'].mean():.1f}/20")
    logger.info(f"Median risk score: {results_df['risk_score'].median():.1f}/20")
    logger.info(f"Best risk score: {results_df['risk_score'].max():.1f}/20")

    logger.info(f"\nTop 10 lowest-risk stocks:")
    print(results_df[['symbol', 'name', 'risk_score', 'volatility_risk_score',
                      'concentration_risk_score', 'liquidity_risk_score']].head(10))

    # Count stocks with risk flags
    flagged = results_df[results_df['risk_flags'] != 'NONE']
    logger.info(f"\nStocks with risk flags: {len(flagged)}/{len(results)}")


if __name__ == '__main__':
    main()
