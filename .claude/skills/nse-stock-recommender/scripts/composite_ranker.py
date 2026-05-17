#!/usr/bin/env python3
"""
NSE Composite Ranker

Merges all analysis dimensions and ranks stocks to produce top 20 recommendations.

Scoring weights:
- Fundamental: 30%
- Technical: 30%
- Risk: 20%
- Sentiment: 20%

Also applies sector diversification filter (max 4 stocks per sector in top 20).
"""

import argparse
import pandas as pd
import numpy as np
import logging
from datetime import datetime
from typing import Dict, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class CompositeRanker:
    """Merges analyses and ranks stocks"""

    def __init__(self, weights: Dict[str, float] = None):
        """
        Initialize ranker with scoring weights.

        Args:
            weights: Dict with keys: fundamental, technical, risk, sentiment
                    Default: {fundamental: 0.30, technical: 0.30, risk: 0.20, sentiment: 0.20}
        """
        self.weights = weights or {
            'fundamental': 0.30,
            'technical': 0.30,
            'risk': 0.20,
            'sentiment': 0.20
        }

        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            logger.warning(f"Weights sum to {total}, normalizing to 1.0")
            for k in self.weights:
                self.weights[k] /= total

        logger.info(f"Using weights: {self.weights}")

    def merge_analyses(self, fundamental_df: pd.DataFrame,
                      technical_df: pd.DataFrame,
                      risk_df: pd.DataFrame,
                      sentiment_df: pd.DataFrame) -> pd.DataFrame:
        """
        Merge all analysis DataFrames by symbol.

        Args:
            fundamental_df: Fundamental analysis results
            technical_df: Technical analysis results
            risk_df: Risk analysis results
            sentiment_df: Sentiment analysis results

        Returns:
            Merged DataFrame
        """
        logger.info("Merging analysis results...")

        # Start with fundamental
        merged = fundamental_df[['symbol', 'name', 'sector', 'fundamental_score']].copy()

        # Merge technical
        tech_cols = ['symbol', 'technical_score']
        merged = merged.merge(technical_df[tech_cols], on='symbol', how='inner')

        # Merge risk
        risk_cols = ['symbol', 'risk_score']
        merged = merged.merge(risk_df[risk_cols], on='symbol', how='inner')

        # Merge sentiment
        sent_cols = ['symbol', 'sentiment_score']
        merged = merged.merge(sentiment_df[sent_cols], on='symbol', how='inner')

        logger.info(f"Merged {len(merged)} stocks with all 4 analyses")

        return merged

    def calculate_composite_score(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate composite score using weighted average.

        Args:
            df: DataFrame with individual dimension scores

        Returns:
            DataFrame with composite_score column added
        """
        logger.info("Calculating composite scores...")

        # Normalize scores to 0-100 scale
        df['fundamental_normalized'] = (df['fundamental_score'] / 30) * 100
        df['technical_normalized'] = (df['technical_score'] / 30) * 100
        df['risk_normalized'] = (df['risk_score'] / 20) * 100
        df['sentiment_normalized'] = (df['sentiment_score'] / 20) * 100

        # Calculate weighted composite
        df['composite_score'] = (
            df['fundamental_normalized'] * self.weights['fundamental'] +
            df['technical_normalized'] * self.weights['technical'] +
            df['risk_normalized'] * self.weights['risk'] +
            df['sentiment_normalized'] * self.weights['sentiment']
        )

        df['composite_score'] = df['composite_score'].round(1)

        return df

    def apply_sector_diversification(self, df: pd.DataFrame,
                                    max_per_sector: int = 4) -> pd.DataFrame:
        """
        Apply sector diversification filter.

        Args:
            df: DataFrame sorted by composite_score
            max_per_sector: Maximum stocks per sector in top results

        Returns:
            Filtered DataFrame
        """
        logger.info(f"Applying sector diversification (max {max_per_sector} per sector)...")

        sector_counts = {}
        selected_indices = []

        for idx, row in df.iterrows():
            sector = row['sector']

            if sector_counts.get(sector, 0) < max_per_sector:
                selected_indices.append(idx)
                sector_counts[sector] = sector_counts.get(sector, 0) + 1

        diversified_df = df.loc[selected_indices]

        logger.info(f"After diversification: {len(diversified_df)} stocks")
        logger.info(f"Sector distribution: {sector_counts}")

        return diversified_df

    def calculate_entry_and_target(self, fundamental_df: pd.DataFrame,
                                  technical_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate entry points and target prices.

        Args:
            fundamental_df: Fundamental data with P/E, growth metrics
            technical_df: Technical data with current price, support levels

        Returns:
            DataFrame with entry_price and target_price columns
        """
        # Merge price data
        price_data = technical_df[['symbol', 'current_price', 'sma_50', 'sma_200']].copy()
        fund_data = fundamental_df[['symbol', 'pe_ratio', 'earnings_growth']].copy()

        merged = price_data.merge(fund_data, on='symbol', how='left')

        # Entry point calculation
        # If price near 50-day MA, use current price
        # If price above 50-day MA by >5%, suggest waiting for pullback
        merged['entry_price'] = merged.apply(
            lambda row: row['current_price'] if pd.notna(row['sma_50']) and
                        row['current_price'] <= row['sma_50'] * 1.05
                        else row['sma_50'] if pd.notna(row['sma_50'])
                        else row['current_price'],
            axis=1
        )

        # Target price calculation (1-3 month horizon)
        # Conservative approach: 15-25% upside for short-term
        merged['target_price'] = merged.apply(
            lambda row: row['current_price'] * 1.20  # 20% target
                        if pd.notna(row['earnings_growth']) and row['earnings_growth'] > 0.25
                        else row['current_price'] * 1.15,  # 15% target for moderate growth
            axis=1
        )

        # Calculate expected upside
        merged['expected_upside_pct'] = (
            (merged['target_price'] - merged['entry_price']) / merged['entry_price'] * 100
        ).round(1)

        return merged[['symbol', 'entry_price', 'target_price', 'expected_upside_pct']]

    def generate_markdown_report(self, top_20: pd.DataFrame,
                                 fundamental_df: pd.DataFrame,
                                 technical_df: pd.DataFrame,
                                 risk_df: pd.DataFrame,
                                 sentiment_df: pd.DataFrame,
                                 output_path: str):
        """
        Generate comprehensive markdown report.

        Args:
            top_20: Top 20 stocks DataFrame
            fundamental_df, technical_df, risk_df, sentiment_df: Full analysis results
            output_path: Path to save report
        """
        logger.info("Generating markdown report...")

        report_lines = []

        # Header
        report_lines.append("# NSE Top 20 Stock Recommendations")
        report_lines.append(f"**Analysis Date:** {datetime.now().strftime('%B %d, %Y')}")
        report_lines.append("**Investment Horizon:** Short-term (1-3 months)")
        report_lines.append(f"**Analysis Coverage:** {len(fundamental_df)} NSE stocks screened")
        report_lines.append("")

        # Executive Summary
        report_lines.append("## Executive Summary")
        report_lines.append("")
        report_lines.append("### Key Findings")
        report_lines.append(f"- Total stocks analyzed: {len(fundamental_df)}")
        report_lines.append(f"- Stocks with all 4 analyses: {len(top_20)}")
        report_lines.append(f"- Average composite score: {top_20['composite_score'].mean():.1f}/100")
        report_lines.append(f"- Top 3 sectors: {', '.join(top_20['sector'].value_counts().head(3).index.tolist())}")
        report_lines.append("")

        # Top 20 Recommendations
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## Top 20 Recommendations")
        report_lines.append("")

        for idx, (rank, row) in enumerate(top_20.iterrows(), 1):
            symbol = row['symbol']

            # Get detailed data for this stock
            fund_detail = fundamental_df[fundamental_df['symbol'] == symbol].iloc[0]
            tech_detail = technical_df[technical_df['symbol'] == symbol].iloc[0]
            risk_detail = risk_df[risk_df['symbol'] == symbol].iloc[0]
            sent_detail = sentiment_df[sentiment_df['symbol'] == symbol].iloc[0]

            report_lines.append(f"### Rank {rank}: {row['name']} ({symbol}.NS)")
            report_lines.append(f"**Composite Score: {row['composite_score']:.1f}/100** | Sector: {row['sector']}")
            report_lines.append("")

            # Score table
            report_lines.append("| Dimension | Score | Grade |")
            report_lines.append("|-----------|-------|-------|")
            report_lines.append(f"| Fundamental | {row['fundamental_score']:.1f}/30 | {self._get_grade(row['fundamental_normalized'])} |")
            report_lines.append(f"| Technical | {row['technical_score']:.1f}/30 | {self._get_grade(row['technical_normalized'])} |")
            report_lines.append(f"| Risk | {row['risk_score']:.1f}/20 | {self._get_grade(row['risk_normalized'])} |")
            report_lines.append(f"| Sentiment | {row['sentiment_score']:.1f}/20 | {self._get_grade(row['sentiment_normalized'])} |")
            report_lines.append("")

            # Price and targets
            report_lines.append(f"**Current Price:** ₹{row['entry_price']:.2f}")
            report_lines.append(f"**Entry Point:** ₹{row['entry_price']:.2f}")
            report_lines.append(f"**Target Price (1-3M):** ₹{row['target_price']:.2f}")
            report_lines.append(f"**Expected Upside:** {row['expected_upside_pct']:.1f}%")
            report_lines.append("")

            # Why Buy
            report_lines.append("**Why Buy:**")

            # Fundamental reason
            if fund_detail.get('pe_discount_pct', 0) > 20:
                report_lines.append(f"- **Valuation:** P/E {fund_detail.get('pe_discount_pct', 0):.0f}% below sector average")
            if fund_detail.get('earnings_growth', 0) > 0.25:
                report_lines.append(f"- **Growth:** {fund_detail.get('earnings_growth', 0)*100:.0f}% earnings growth")

            # Technical reason
            if tech_detail.get('rsi_value'):
                report_lines.append(f"- **Technical:** RSI {tech_detail.get('rsi_value'):.0f} (neutral-bullish zone)")

            # Sentiment reason
            if sent_detail.get('recommendation'):
                report_lines.append(f"- **Sentiment:** Analyst rating: {sent_detail.get('recommendation')}")

            report_lines.append("")

            # Key Metrics
            report_lines.append("**Key Metrics:**")
            report_lines.append(f"- P/E: {fund_detail.get('pe_ratio', 'N/A')} | ROE: {fund_detail.get('roe', 'N/A')}")
            report_lines.append(f"- Revenue Growth: {fund_detail.get('revenue_growth', 0)*100:.0f}%")
            report_lines.append(f"- Beta: {risk_detail.get('beta', 'N/A')} | Volatility: {risk_detail.get('annual_volatility_pct', 'N/A'):.0f}%")
            report_lines.append("")

            report_lines.append("---")
            report_lines.append("")

        # Sector Diversification
        report_lines.append("## Sector Diversification")
        report_lines.append("")
        sector_dist = top_20['sector'].value_counts()
        report_lines.append("| Sector | Stocks |")
        report_lines.append("|--------|--------|")
        for sector, count in sector_dist.items():
            report_lines.append(f"| {sector} | {count} |")
        report_lines.append("")

        # Disclaimers
        report_lines.append("---")
        report_lines.append("")
        report_lines.append("## Disclaimers")
        report_lines.append("")
        report_lines.append("⚠️ **Important:**")
        report_lines.append("- This is an automated screening tool, NOT financial advice")
        report_lines.append("- Short-term trading is high risk; you can lose your entire investment")
        report_lines.append("- Past performance and expected returns may not materialize")
        report_lines.append("- Always conduct your own due diligence")
        report_lines.append("- Consult a SEBI-registered investment advisor for personalized advice")
        report_lines.append("")

        report_lines.append("---")
        report_lines.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"**Stocks Screened:** {len(fundamental_df)}")

        # Write to file
        with open(output_path, 'w') as f:
            f.write('\n'.join(report_lines))

        logger.info(f"Report saved to {output_path}")

    def _get_grade(self, normalized_score: float) -> str:
        """Convert normalized score (0-100) to letter grade"""
        if normalized_score >= 85:
            return 'A+'
        elif normalized_score >= 75:
            return 'A'
        elif normalized_score >= 65:
            return 'B+'
        elif normalized_score >= 55:
            return 'B'
        elif normalized_score >= 45:
            return 'C+'
        elif normalized_score >= 35:
            return 'C'
        else:
            return 'D'


def parse_weights(weights_str: str) -> Dict[str, float]:
    """
    Parse weights string to dict.

    Example: "fundamental=0.40,technical=0.30,risk=0.20,sentiment=0.10"
    """
    weights = {}
    for pair in weights_str.split(','):
        key, value = pair.split('=')
        weights[key.strip()] = float(value.strip())
    return weights


def main():
    parser = argparse.ArgumentParser(description='Composite Ranking for NSE stocks')
    parser.add_argument('--fundamental', required=True, help='Fundamental analysis CSV')
    parser.add_argument('--technical', required=True, help='Technical analysis CSV')
    parser.add_argument('--risk', required=True, help='Risk analysis CSV')
    parser.add_argument('--sentiment', required=True, help='Sentiment analysis CSV')
    parser.add_argument('--output', required=True, help='Output CSV for top 20')
    parser.add_argument('--report', required=True, help='Output markdown report')
    parser.add_argument('--weights', help='Custom weights (e.g., "fundamental=0.40,technical=0.30,risk=0.20,sentiment=0.10")')
    parser.add_argument('--top', type=int, default=20, help='Number of top stocks to recommend (default: 20)')
    parser.add_argument('--max-per-sector', type=int, default=4, help='Max stocks per sector (default: 4)')

    args = parser.parse_args()

    logger.info("Starting composite ranking...")

    # Load all analyses
    fundamental_df = pd.read_csv(args.fundamental)
    technical_df = pd.read_csv(args.technical)
    risk_df = pd.read_csv(args.risk)
    sentiment_df = pd.read_csv(args.sentiment)

    logger.info(f"Loaded analyses:")
    logger.info(f"  Fundamental: {len(fundamental_df)} stocks")
    logger.info(f"  Technical: {len(technical_df)} stocks")
    logger.info(f"  Risk: {len(risk_df)} stocks")
    logger.info(f"  Sentiment: {len(sentiment_df)} stocks")

    # Parse weights if provided
    weights = parse_weights(args.weights) if args.weights else None

    # Initialize ranker
    ranker = CompositeRanker(weights=weights)

    # Merge analyses
    merged_df = ranker.merge_analyses(fundamental_df, technical_df, risk_df, sentiment_df)

    # Calculate composite score
    scored_df = ranker.calculate_composite_score(merged_df)

    # Sort by composite score
    scored_df = scored_df.sort_values('composite_score', ascending=False)

    # Apply sector diversification
    diversified_df = ranker.apply_sector_diversification(scored_df, args.max_per_sector)

    # Select top N
    top_n = diversified_df.head(args.top).copy()

    # Calculate entry and target prices
    entry_target = ranker.calculate_entry_and_target(fundamental_df, technical_df)
    top_n = top_n.merge(entry_target, on='symbol', how='left')

    # Save CSV
    top_n.to_csv(args.output, index=False)
    logger.info(f"Saved top {args.top} recommendations to {args.output}")

    # Generate report
    ranker.generate_markdown_report(top_n, fundamental_df, technical_df,
                                   risk_df, sentiment_df, args.report)

    # Print summary
    logger.info("\n=== Top 20 Recommendations ===")
    print(top_n[['symbol', 'name', 'sector', 'composite_score',
                 'fundamental_score', 'technical_score', 'risk_score',
                 'sentiment_score', 'expected_upside_pct']].to_string(index=False))


if __name__ == '__main__':
    main()
