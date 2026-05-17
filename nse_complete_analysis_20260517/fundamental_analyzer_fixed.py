#!/usr/bin/env python3
"""
Fixed NSE Fundamental Analyzer with robust error handling
Handles infinity values, NaN, and mixed data types
"""

import argparse
import pandas as pd
import yfinance as yf
import numpy as np
import time
import logging
from typing import Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def clean_numeric_value(value, default=None):
    """Clean numeric value, handling infinity, NaN, and strings"""
    if value is None:
        return default

    # Handle string 'Infinity' or 'inf'
    if isinstance(value, str):
        if value.lower() in ['infinity', 'inf', '-infinity', '-inf']:
            return default
        try:
            value = float(value)
        except:
            return default

    # Handle infinity and NaN
    if np.isinf(value) or np.isnan(value):
        return default

    return float(value)


class FundamentalAnalyzer:
    """Analyzes fundamental metrics with robust error handling"""

    def __init__(self):
        self.sector_averages = {}

    def fetch_fundamental_data(self, symbol: str) -> Optional[Dict]:
        """Fetch fundamental data with error handling"""
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info

            # Extract and clean all metrics
            data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),

                # Valuation metrics - cleaned
                'pe_ratio': clean_numeric_value(info.get('trailingPE')),
                'pb_ratio': clean_numeric_value(info.get('priceToBook')),
                'peg_ratio': clean_numeric_value(info.get('pegRatio')),
                'ev_ebitda': clean_numeric_value(info.get('enterpriseToEbitda')),

                # Growth metrics - cleaned
                'revenue_growth': clean_numeric_value(info.get('revenueGrowth')),
                'earnings_growth': clean_numeric_value(info.get('earningsGrowth')),

                # Quality metrics - cleaned
                'roe': clean_numeric_value(info.get('returnOnEquity')),
                'profit_margin': clean_numeric_value(info.get('profitMargins')),

                # Financial health - cleaned
                'debt_to_equity': clean_numeric_value(info.get('debtToEquity')),
                'current_ratio': clean_numeric_value(info.get('currentRatio')),
            }

            return data

        except Exception as e:
            logger.debug(f"Error fetching {symbol}: {str(e)[:50]}")
            return None

    def calculate_sector_averages(self, stocks_df: pd.DataFrame):
        """Calculate sector averages with proper error handling"""
        for sector in stocks_df['sector'].unique():
            if sector == 'Unknown':
                continue

            sector_stocks = stocks_df[stocks_df['sector'] == sector]

            # Use median and handle NaN properly
            self.sector_averages[sector] = {
                'avg_pe': sector_stocks['pe_ratio'].median() if not sector_stocks['pe_ratio'].isna().all() else None,
                'avg_pb': sector_stocks['pb_ratio'].median() if not sector_stocks['pb_ratio'].isna().all() else None,
                'avg_roe': sector_stocks['roe'].median() if not sector_stocks['roe'].isna().all() else None,
            }

    def score_valuation(self, stock: Dict) -> tuple:
        """Score valuation metrics (0-10 points)"""
        score = 0
        pe_discount = 0

        sector = stock.get('sector', 'Unknown')
        pe = stock.get('pe_ratio')
        pb = stock.get('pb_ratio')

        if sector in self.sector_averages:
            sector_avg_pe = self.sector_averages[sector].get('avg_pe')

            # P/E scoring
            if pe and sector_avg_pe and pe > 0 and sector_avg_pe > 0:
                if pe < sector_avg_pe * 0.7:
                    score += 5
                    pe_discount = ((sector_avg_pe - pe) / sector_avg_pe) * 100
                elif pe < sector_avg_pe * 0.85:
                    score += 3
                    pe_discount = ((sector_avg_pe - pe) / sector_avg_pe) * 100
                elif pe < sector_avg_pe * 1.15:
                    score += 1

            # P/B scoring
            if pb:
                if pb < 1.5:
                    score += 3
                elif pb < 3:
                    score += 2
                elif pb < 5:
                    score += 1

        return min(score, 10), pe_discount

    def score_growth(self, stock: Dict) -> float:
        """Score growth metrics (0-10 points)"""
        score = 0

        rev_growth = stock.get('revenue_growth')
        earn_growth = stock.get('earnings_growth')

        # Revenue growth
        if rev_growth:
            if rev_growth > 0.25:
                score += 5
            elif rev_growth > 0.15:
                score += 3
            elif rev_growth > 0.10:
                score += 2
            elif rev_growth > 0.05:
                score += 1

        # Earnings growth
        if earn_growth:
            if earn_growth > 0.25:
                score += 5
            elif earn_growth > 0.15:
                score += 3
            elif earn_growth > 0.10:
                score += 2
            elif earn_growth > 0.05:
                score += 1

        return min(score, 10)

    def score_quality(self, stock: Dict) -> float:
        """Score quality metrics (0-5 points)"""
        score = 0

        roe = stock.get('roe')
        margin = stock.get('profit_margin')

        # ROE scoring
        if roe:
            if roe > 0.20:
                score += 3
            elif roe > 0.15:
                score += 2
            elif roe > 0.10:
                score += 1

        # Profit margin
        if margin:
            if margin > 0.15:
                score += 2
            elif margin > 0.10:
                score += 1

        return min(score, 5)

    def score_financial_health(self, stock: Dict) -> float:
        """Score financial health (0-5 points)"""
        score = 0

        de_ratio = stock.get('debt_to_equity')
        current_ratio = stock.get('current_ratio')

        # Debt/Equity
        if de_ratio is not None:
            if de_ratio < 0.5:
                score += 3
            elif de_ratio < 1.0:
                score += 2
            elif de_ratio < 2.0:
                score += 1

        # Current ratio
        if current_ratio:
            if current_ratio > 1.5:
                score += 2
            elif current_ratio > 1.0:
                score += 1

        return min(score, 5)


def main():
    parser = argparse.ArgumentParser(description='Fixed Fundamental Analysis')
    parser.add_argument('--input', required=True, help='Input CSV with stock universe')
    parser.add_argument('--output', required=True, help='Output CSV for scores')
    args = parser.parse_args()

    logger.info("Starting FIXED fundamental analysis...")
    logger.info("Handling infinity values and data type errors...")

    # Load universe
    universe_df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(universe_df)} stocks")

    analyzer = FundamentalAnalyzer()
    results = []

    # Fetch data for all stocks
    for idx, row in universe_df.iterrows():
        symbol = row['symbol']

        if (idx + 1) % 50 == 0:
            logger.info(f"Progress: {idx + 1}/{len(universe_df)} ({(idx+1)/len(universe_df)*100:.1f}%)")

        data = analyzer.fetch_fundamental_data(symbol)
        if data:
            results.append(data)

        time.sleep(0.5)  # Rate limiting

    # Create DataFrame
    df = pd.DataFrame(results)
    logger.info(f"Successfully fetched data for {len(df)} stocks")

    # Calculate sector averages
    analyzer.calculate_sector_averages(df)

    # Score all stocks
    scored_results = []
    for _, stock in df.iterrows():
        val_score, pe_discount = analyzer.score_valuation(stock)
        growth_score = analyzer.score_growth(stock)
        quality_score = analyzer.score_quality(stock)
        health_score = analyzer.score_financial_health(stock)

        fundamental_score = val_score + growth_score + quality_score + health_score

        scored_results.append({
            'symbol': stock['symbol'],
            'name': stock['name'],
            'sector': stock['sector'],
            'fundamental_score': round(fundamental_score, 1),
            'valuation_score': round(val_score, 1),
            'growth_score': round(growth_score, 1),
            'quality_score': round(quality_score, 1),
            'health_score': round(health_score, 1),
            'pe_ratio': stock['pe_ratio'],
            'pe_discount_pct': round(pe_discount, 1) if pe_discount else 0,
            'revenue_growth': stock['revenue_growth'],
            'earnings_growth': stock['earnings_growth'],
            'roe': stock['roe'],
        })

    # Save results
    output_df = pd.DataFrame(scored_results)
    output_df = output_df.sort_values('fundamental_score', ascending=False)
    output_df.to_csv(args.output, index=False)

    logger.info(f"✅ Saved {len(output_df)} stocks to {args.output}")
    logger.info(f"Top 10 by fundamental score:")
    print(output_df[['symbol', 'fundamental_score', 'sector']].head(10))


if __name__ == '__main__':
    main()
