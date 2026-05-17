#!/usr/bin/env python3
"""
NSE Fundamental Analyzer

Analyzes fundamental metrics for stocks and assigns scores based on:
1. Valuation (10 points) - P/E, P/B, PEG, EV/EBITDA vs sector
2. Growth (10 points) - Revenue and earnings growth
3. Quality (5 points) - ROE, ROCE, margins
4. Financial Health (5 points) - Debt/equity, interest coverage, FCF

Total: 0-30 points per stock
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


class FundamentalAnalyzer:
    """Analyzes fundamental metrics and assigns scores"""

    def __init__(self):
        self.sector_averages = {}

    def fetch_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch comprehensive fundamental data for a stock.

        Args:
            symbol: NSE stock symbol (without .NS)

        Returns:
            Dict with fundamental metrics or None
        """
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info

            # Extract key fundamental metrics
            data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),

                # Valuation metrics
                'pe_ratio': info.get('trailingPE'),
                'pb_ratio': info.get('priceToBook'),
                'peg_ratio': info.get('pegRatio'),
                'ev_ebitda': info.get('enterpriseToEbitda'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),

                # Growth metrics
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'revenue_quarterly_growth': info.get('revenueQuarterlyGrowth'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth'),

                # Quality metrics
                'roe': info.get('returnOnEquity'),
                'roce': info.get('returnOnAssets'),  # Yahoo doesn't provide ROCE, using ROA as proxy
                'profit_margin': info.get('profitMargins'),
                'operating_margin': info.get('operatingMargins'),
                'gross_margin': info.get('grossMargins'),

                # Financial health
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'free_cashflow': info.get('freeCashflow'),
                'total_cash': info.get('totalCash'),
                'total_debt': info.get('totalDebt'),

                # Additional metrics
                'market_cap': info.get('marketCap'),
                'enterprise_value': info.get('enterpriseValue'),
                'book_value': info.get('bookValue'),
            }

            return data

        except Exception as e:
            logger.error(f"Error fetching fundamental data for {symbol}: {str(e)}")
            return None

    def calculate_sector_averages(self, stocks_df: pd.DataFrame):
        """
        Calculate sector-wise average valuation metrics.

        Args:
            stocks_df: DataFrame with stock fundamental data
        """
        for sector in stocks_df['sector'].unique():
            if sector == 'Unknown':
                continue

            sector_stocks = stocks_df[stocks_df['sector'] == sector]

            self.sector_averages[sector] = {
                'avg_pe': sector_stocks['pe_ratio'].median(),
                'avg_pb': sector_stocks['pb_ratio'].median(),
                'avg_peg': sector_stocks['peg_ratio'].median(),
                'avg_ev_ebitda': sector_stocks['ev_ebitda'].median(),
            }

        logger.info(f"Calculated averages for {len(self.sector_averages)} sectors")

    def score_valuation(self, stock: Dict) -> Tuple[float, Dict]:
        """
        Score valuation metrics (0-10 points).

        Criteria:
        - P/E discount to sector average (4 pts)
        - P/B ratio quality (2 pts)
        - PEG ratio (2 pts)
        - EV/EBITDA (2 pts)

        Args:
            stock: Stock fundamental data dict

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        sector = stock.get('sector', 'Unknown')
        sector_avg = self.sector_averages.get(sector, {})

        # P/E scoring (4 points)
        pe = stock.get('pe_ratio')
        if pe and pe > 0:
            sector_pe = sector_avg.get('avg_pe', pe)
            if sector_pe and sector_pe > 0:
                pe_discount = (sector_pe - pe) / sector_pe * 100

                if pe_discount >= 30:
                    score += 4
                    breakdown['pe_score'] = 4
                elif pe_discount >= 20:
                    score += 3
                    breakdown['pe_score'] = 3
                elif pe_discount >= 10:
                    score += 2
                    breakdown['pe_score'] = 2
                elif pe_discount > 0:
                    score += 1
                    breakdown['pe_score'] = 1
                else:
                    breakdown['pe_score'] = 0

                breakdown['pe_discount_pct'] = round(pe_discount, 1)
            else:
                breakdown['pe_score'] = 0
        else:
            breakdown['pe_score'] = 0

        # P/B scoring (2 points)
        pb = stock.get('pb_ratio')
        roe = stock.get('roe')
        if pb and pb > 0:
            if pb < 1:
                score += 2
                breakdown['pb_score'] = 2
            elif pb < 2 and roe and roe > 0.15:
                score += 1.5
                breakdown['pb_score'] = 1.5
            elif pb < 3:
                score += 1
                breakdown['pb_score'] = 1
            else:
                breakdown['pb_score'] = 0
        else:
            breakdown['pb_score'] = 0

        # PEG scoring (2 points)
        peg = stock.get('peg_ratio')
        if peg and peg > 0:
            if peg < 0.5:
                score += 2
                breakdown['peg_score'] = 2
            elif peg < 1:
                score += 1.5
                breakdown['peg_score'] = 1.5
            elif peg < 1.5:
                score += 1
                breakdown['peg_score'] = 1
            else:
                breakdown['peg_score'] = 0
        else:
            breakdown['peg_score'] = 0

        # EV/EBITDA scoring (2 points)
        ev_ebitda = stock.get('ev_ebitda')
        if ev_ebitda and ev_ebitda > 0:
            if ev_ebitda < 8:
                score += 2
                breakdown['ev_ebitda_score'] = 2
            elif ev_ebitda < 12:
                score += 1
                breakdown['ev_ebitda_score'] = 1
            else:
                breakdown['ev_ebitda_score'] = 0
        else:
            breakdown['ev_ebitda_score'] = 0

        breakdown['valuation_total'] = round(score, 1)
        return score, breakdown

    def score_growth(self, stock: Dict) -> Tuple[float, Dict]:
        """
        Score growth metrics (0-10 points).

        Criteria:
        - Revenue growth YoY (5 pts)
        - Earnings growth YoY (5 pts)

        Args:
            stock: Stock fundamental data dict

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Revenue growth (5 points)
        rev_growth = stock.get('revenue_growth')
        if rev_growth:
            if rev_growth > 0.40:  # >40% growth
                score += 5
                breakdown['revenue_score'] = 5
            elif rev_growth > 0.25:  # >25% growth
                score += 4
                breakdown['revenue_score'] = 4
            elif rev_growth > 0.15:  # >15% growth
                score += 3
                breakdown['revenue_score'] = 3
            elif rev_growth > 0.10:  # >10% growth
                score += 2
                breakdown['revenue_score'] = 2
            elif rev_growth > 0:
                score += 1
                breakdown['revenue_score'] = 1
            else:
                breakdown['revenue_score'] = 0
        else:
            breakdown['revenue_score'] = 0

        # Earnings growth (5 points)
        earn_growth = stock.get('earnings_growth')
        if earn_growth:
            if earn_growth > 0.50:  # >50% growth
                score += 5
                breakdown['earnings_score'] = 5
            elif earn_growth > 0.35:  # >35% growth
                score += 4
                breakdown['earnings_score'] = 4
            elif earn_growth > 0.20:  # >20% growth
                score += 3
                breakdown['earnings_score'] = 3
            elif earn_growth > 0.10:  # >10% growth
                score += 2
                breakdown['earnings_score'] = 2
            elif earn_growth > 0:
                score += 1
                breakdown['earnings_score'] = 1
            else:
                breakdown['earnings_score'] = 0
        else:
            breakdown['earnings_score'] = 0

        breakdown['growth_total'] = round(score, 1)
        return score, breakdown

    def score_quality(self, stock: Dict) -> Tuple[float, Dict]:
        """
        Score quality metrics (0-5 points).

        Criteria:
        - ROE (2 pts)
        - Profit margins (2 pts)
        - ROCE (1 pt)

        Args:
            stock: Stock fundamental data dict

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # ROE scoring (2 points)
        roe = stock.get('roe')
        if roe:
            if roe > 0.25:  # >25%
                score += 2
                breakdown['roe_score'] = 2
            elif roe > 0.15:  # >15%
                score += 1.5
                breakdown['roe_score'] = 1.5
            elif roe > 0.10:  # >10%
                score += 1
                breakdown['roe_score'] = 1
            else:
                breakdown['roe_score'] = 0
        else:
            breakdown['roe_score'] = 0

        # Profit margin scoring (2 points)
        profit_margin = stock.get('profit_margin')
        if profit_margin:
            if profit_margin > 0.20:  # >20%
                score += 2
                breakdown['margin_score'] = 2
            elif profit_margin > 0.10:  # >10%
                score += 1.5
                breakdown['margin_score'] = 1.5
            elif profit_margin > 0.05:  # >5%
                score += 1
                breakdown['margin_score'] = 1
            else:
                breakdown['margin_score'] = 0
        else:
            breakdown['margin_score'] = 0

        # ROCE scoring (1 point)
        roce = stock.get('roce')
        if roce and roce > 0.15:
            score += 1
            breakdown['roce_score'] = 1
        else:
            breakdown['roce_score'] = 0

        breakdown['quality_total'] = round(score, 1)
        return score, breakdown

    def score_financial_health(self, stock: Dict) -> Tuple[float, Dict]:
        """
        Score financial health (0-5 points).

        Criteria:
        - Debt/Equity ratio (2 pts)
        - Current ratio (1 pt)
        - Free cash flow (2 pts)

        Args:
            stock: Stock fundamental data dict

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Debt/Equity scoring (2 points)
        de = stock.get('debt_to_equity')
        if de is not None:
            if de < 0.3:  # Very conservative
                score += 2
                breakdown['de_score'] = 2
            elif de < 0.5:
                score += 1.5
                breakdown['de_score'] = 1.5
            elif de < 1.0:
                score += 1
                breakdown['de_score'] = 1
            else:
                breakdown['de_score'] = 0
        else:
            # Assume 0 debt if not available
            score += 2
            breakdown['de_score'] = 2

        # Current ratio scoring (1 point)
        cr = stock.get('current_ratio')
        if cr and cr >= 1.5:
            score += 1
            breakdown['current_ratio_score'] = 1
        else:
            breakdown['current_ratio_score'] = 0

        # Free cash flow scoring (2 points)
        fcf = stock.get('free_cashflow')
        market_cap = stock.get('market_cap')

        if fcf and market_cap and market_cap > 0:
            fcf_yield = (fcf / market_cap) * 100

            if fcf_yield > 8:
                score += 2
                breakdown['fcf_score'] = 2
            elif fcf_yield > 5:
                score += 1.5
                breakdown['fcf_score'] = 1.5
            elif fcf_yield > 2:
                score += 1
                breakdown['fcf_score'] = 1
            elif fcf_yield > 0:
                score += 0.5
                breakdown['fcf_score'] = 0.5
            else:
                breakdown['fcf_score'] = 0
        else:
            breakdown['fcf_score'] = 0

        breakdown['health_total'] = round(score, 1)
        return score, breakdown

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """
        Complete fundamental analysis for a stock.

        Args:
            symbol: NSE stock symbol

        Returns:
            Dict with scores and metrics
        """
        # Fetch fundamental data
        data = self.fetch_fundamental_data(symbol)
        if not data:
            return None

        # Calculate scores
        valuation_score, val_breakdown = self.score_valuation(data)
        growth_score, growth_breakdown = self.score_growth(data)
        quality_score, quality_breakdown = self.score_quality(data)
        health_score, health_breakdown = self.score_financial_health(data)

        # Total fundamental score
        total_score = valuation_score + growth_score + quality_score + health_score

        # Compile results
        result = {
            'symbol': symbol,
            'name': data['name'],
            'sector': data['sector'],

            # Total score
            'fundamental_score': round(total_score, 1),

            # Component scores
            'valuation_score': round(valuation_score, 1),
            'growth_score': round(growth_score, 1),
            'quality_score': round(quality_score, 1),
            'health_score': round(health_score, 1),

            # Key metrics for reference
            'pe_ratio': data.get('pe_ratio'),
            'pb_ratio': data.get('pb_ratio'),
            'peg_ratio': data.get('peg_ratio'),
            'roe': data.get('roe'),
            'revenue_growth': data.get('revenue_growth'),
            'earnings_growth': data.get('earnings_growth'),
            'profit_margin': data.get('profit_margin'),
            'debt_to_equity': data.get('debt_to_equity'),

            # Breakdown details
            **val_breakdown,
            **growth_breakdown,
            **quality_breakdown,
            **health_breakdown
        }

        return result


def main():
    parser = argparse.ArgumentParser(description='Fundamental Analysis for NSE stocks')
    parser.add_argument('--input', required=True, help='Input CSV with stock universe')
    parser.add_argument('--output', required=True, help='Output CSV with fundamental scores')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Delay between API calls in seconds')

    args = parser.parse_args()

    logger.info("Starting fundamental analysis...")

    # Load stock universe
    universe_df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(universe_df)} stocks from {args.input}")

    analyzer = FundamentalAnalyzer()

    # First pass: fetch all fundamental data to calculate sector averages
    logger.info("Pass 1: Fetching fundamental data for sector averages...")
    all_data = []

    for i, row in universe_df.iterrows():
        symbol = row['symbol']
        logger.info(f"Fetching {i+1}/{len(universe_df)}: {symbol}")

        data = analyzer.fetch_fundamental_data(symbol)
        if data:
            all_data.append(data)

        time.sleep(args.delay)

        if (i + 1) % 50 == 0:
            logger.info(f"Progress: {i+1}/{len(universe_df)} ({(i+1)/len(universe_df)*100:.1f}%)")

    # Calculate sector averages
    if all_data:
        temp_df = pd.DataFrame(all_data)
        analyzer.calculate_sector_averages(temp_df)

    # Second pass: analyze and score each stock
    logger.info("\nPass 2: Scoring stocks...")
    results = []

    for i, row in universe_df.iterrows():
        symbol = row['symbol']
        logger.info(f"Analyzing {i+1}/{len(universe_df)}: {symbol}")

        result = analyzer.analyze_stock(symbol)
        if result:
            results.append(result)

        time.sleep(args.delay)

    # Save results
    results_df = pd.DataFrame(results)
    results_df = results_df.sort_values('fundamental_score', ascending=False)
    results_df.to_csv(args.output, index=False)

    logger.info(f"\nSaved {len(results)} analyzed stocks to {args.output}")

    # Summary statistics
    logger.info("\n=== Fundamental Analysis Summary ===")
    logger.info(f"Stocks analyzed: {len(results)}")
    logger.info(f"Average fundamental score: {results_df['fundamental_score'].mean():.1f}/30")
    logger.info(f"Median fundamental score: {results_df['fundamental_score'].median():.1f}/30")
    logger.info(f"Top score: {results_df['fundamental_score'].max():.1f}/30")

    logger.info(f"\nTop 10 stocks by fundamental score:")
    print(results_df[['symbol', 'name', 'fundamental_score', 'valuation_score',
                      'growth_score', 'quality_score', 'health_score']].head(10))


if __name__ == '__main__':
    main()
