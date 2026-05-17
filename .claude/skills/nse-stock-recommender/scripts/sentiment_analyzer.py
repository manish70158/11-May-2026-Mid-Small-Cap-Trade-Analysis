#!/usr/bin/env python3
"""
NSE Sentiment Analyzer

Analyzes market sentiment from multiple sources:
1. News Sentiment (8 points) - Recent news articles, earnings announcements
2. Analyst Ratings (7 points) - Broker recommendations, target prices
3. Social Media (5 points) - Twitter, Reddit discussion volume

Total: 0-20 points per stock

Note: This is a simplified implementation. In production, you would use:
- News APIs (NewsAPI, GNews, etc.)
- Analyst data APIs (FinViz, TipRanks, etc.)
- Social media APIs (Twitter API, Reddit API)
"""

import argparse
import pandas as pd
import yfinance as yf
import time
import logging
from typing import Dict, Optional, Tuple
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Analyzes sentiment from various sources"""

    def fetch_analyst_data(self, symbol: str) -> Optional[Dict]:
        """
        Fetch analyst recommendations and target prices.

        Args:
            symbol: NSE stock symbol (without .NS)

        Returns:
            Dict with analyst data or None
        """
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info

            # Get analyst recommendations
            recommendations = None
            try:
                recommendations = ticker.recommendations
            except:
                pass

            data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),

                # Analyst ratings
                'recommendation_mean': info.get('recommendationMean'),
                'recommendation_key': info.get('recommendationKey'),
                'number_of_analyst_opinions': info.get('numberOfAnalystOpinions'),

                # Target price
                'target_mean_price': info.get('targetMeanPrice'),
                'target_high_price': info.get('targetHighPrice'),
                'target_low_price': info.get('targetLowPrice'),
                'current_price': info.get('currentPrice'),

                # Recommendations breakdown
                'recommendations_df': recommendations
            }

            return data

        except Exception as e:
            logger.error(f"Error fetching analyst data for {symbol}: {str(e)}")
            return None

    def fetch_news_sentiment(self, symbol: str) -> Optional[Dict]:
        """
        Fetch recent news articles (simplified version).

        In production, this would:
        - Use News APIs (NewsAPI, GNews, etc.)
        - Perform NLP sentiment analysis
        - Track earnings announcements
        - Monitor corporate actions

        Current implementation: Uses Yahoo Finance news (limited)

        Args:
            symbol: NSE stock symbol

        Returns:
            Dict with news sentiment or None
        """
        try:
            ticker = yf.Ticker(f"{symbol}.NS")

            # Yahoo Finance provides limited news
            news = []
            try:
                news = ticker.news
            except:
                pass

            # Simple sentiment based on news volume and recency
            recent_news_count = len(news) if news else 0

            return {
                'news_count': recent_news_count,
                'has_recent_news': recent_news_count > 0
            }

        except Exception as e:
            logger.error(f"Error fetching news for {symbol}: {str(e)}")
            return None

    def score_news_sentiment(self, news_data: Dict) -> Tuple[float, Dict]:
        """
        Score news sentiment (0-8 points).

        In production, this would analyze:
        - Positive vs negative news sentiment
        - Earnings beats/misses
        - Corporate announcements
        - Merger/acquisition news

        Current simplified version: Based on news presence

        Args:
            news_data: News sentiment data

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Simplified scoring based on news activity
        news_count = news_data.get('news_count', 0)

        if news_count > 10:
            # High news coverage - assume positive interest
            score += 5
            breakdown['news_coverage_score'] = 5
        elif news_count > 5:
            score += 4
            breakdown['news_coverage_score'] = 4
        elif news_count > 2:
            score += 3
            breakdown['news_coverage_score'] = 3
        elif news_count > 0:
            score += 2
            breakdown['news_coverage_score'] = 2
        else:
            # No news - neutral
            score += 4  # Neutral score
            breakdown['news_coverage_score'] = 4

        breakdown['news_count'] = news_count

        # Note: In production, add actual sentiment analysis here
        # For now, assign moderate points for having news
        score += 3  # Placeholder for sentiment analysis
        breakdown['news_sentiment_score'] = 3

        breakdown['news_total'] = round(score, 1)
        return score, breakdown

    def score_analyst_ratings(self, analyst_data: Dict) -> Tuple[float, Dict]:
        """
        Score analyst ratings (0-7 points).

        Criteria:
        - Recommendation rating (4 pts): 1=Strong Buy, 5=Strong Sell
        - Target price upside (3 pts): Higher upside = higher score

        Args:
            analyst_data: Analyst recommendation data

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Recommendation mean scoring (4 points)
        # Scale: 1.0=Strong Buy, 2.0=Buy, 3.0=Hold, 4.0=Sell, 5.0=Strong Sell
        rec_mean = analyst_data.get('recommendation_mean')

        if rec_mean:
            if rec_mean <= 1.5:
                # Strong Buy
                score += 4
                breakdown['recommendation_score'] = 4
                breakdown['recommendation'] = 'Strong Buy'
            elif rec_mean <= 2.5:
                # Buy
                score += 3
                breakdown['recommendation_score'] = 3
                breakdown['recommendation'] = 'Buy'
            elif rec_mean <= 3.5:
                # Hold
                score += 2
                breakdown['recommendation_score'] = 2
                breakdown['recommendation'] = 'Hold'
            elif rec_mean <= 4.5:
                # Sell
                score += 1
                breakdown['recommendation_score'] = 1
                breakdown['recommendation'] = 'Sell'
            else:
                # Strong Sell
                breakdown['recommendation_score'] = 0
                breakdown['recommendation'] = 'Strong Sell'

            breakdown['recommendation_mean'] = round(rec_mean, 2)
        else:
            # No analyst coverage - neutral
            score += 2
            breakdown['recommendation_score'] = 2
            breakdown['recommendation'] = 'No Coverage'

        # Target price upside scoring (3 points)
        target_price = analyst_data.get('target_mean_price')
        current_price = analyst_data.get('current_price')

        if target_price and current_price and current_price > 0:
            upside_pct = ((target_price - current_price) / current_price) * 100

            if upside_pct > 30:
                score += 3
                breakdown['target_upside_score'] = 3
            elif upside_pct > 15:
                score += 2.5
                breakdown['target_upside_score'] = 2.5
            elif upside_pct > 5:
                score += 2
                breakdown['target_upside_score'] = 2
            elif upside_pct > 0:
                score += 1
                breakdown['target_upside_score'] = 1
            else:
                breakdown['target_upside_score'] = 0

            breakdown['target_upside_pct'] = round(upside_pct, 1)
            breakdown['target_price'] = round(target_price, 2)
        else:
            # No target price - neutral
            score += 1.5
            breakdown['target_upside_score'] = 1.5

        # Number of analysts following
        num_analysts = analyst_data.get('number_of_analyst_opinions')
        breakdown['num_analysts'] = num_analysts if num_analysts else 0

        breakdown['analyst_total'] = round(score, 1)
        return score, breakdown

    def score_social_sentiment(self, symbol: str) -> Tuple[float, Dict]:
        """
        Score social media sentiment (0-5 points).

        In production, this would analyze:
        - Twitter mentions and sentiment
        - Reddit discussions (r/IndianStockMarket, r/IndiaInvestments)
        - StockTwits sentiment
        - Social media momentum

        Current simplified version: Placeholder implementation

        Args:
            symbol: Stock symbol

        Returns:
            Tuple of (score, breakdown dict)
        """
        score = 0
        breakdown = {}

        # Placeholder: In production, fetch from social media APIs
        # For now, assign neutral scores

        # Twitter sentiment (3 points)
        # In production: Analyze tweet sentiment, volume, influential accounts
        score += 1.5  # Neutral
        breakdown['twitter_score'] = 1.5
        breakdown['twitter_mentions'] = 'N/A'

        # Reddit sentiment (2 points)
        # In production: Analyze r/IndianStockMarket discussion sentiment
        score += 1  # Neutral
        breakdown['reddit_score'] = 1
        breakdown['reddit_discussions'] = 'N/A'

        breakdown['social_total'] = round(score, 1)
        breakdown['social_note'] = 'Simplified implementation - expand with social APIs'

        return score, breakdown

    def analyze_stock(self, symbol: str) -> Optional[Dict]:
        """
        Complete sentiment analysis for a stock.

        Args:
            symbol: NSE stock symbol

        Returns:
            Dict with sentiment scores and data
        """
        # Fetch analyst data
        analyst_data = self.fetch_analyst_data(symbol)
        if not analyst_data:
            return None

        # Fetch news data
        news_data = self.fetch_news_sentiment(symbol)
        if not news_data:
            news_data = {'news_count': 0, 'has_recent_news': False}

        # Calculate scores
        news_score, news_breakdown = self.score_news_sentiment(news_data)
        analyst_score, analyst_breakdown = self.score_analyst_ratings(analyst_data)
        social_score, social_breakdown = self.score_social_sentiment(symbol)

        # Total sentiment score
        total_score = news_score + analyst_score + social_score

        # Compile results
        result = {
            'symbol': symbol,
            'name': analyst_data['name'],
            'sector': analyst_data['sector'],

            # Total score
            'sentiment_score': round(total_score, 1),

            # Component scores
            'news_score': round(news_score, 1),
            'analyst_score': round(analyst_score, 1),
            'social_score': round(social_score, 1),

            # Breakdown details
            **news_breakdown,
            **analyst_breakdown,
            **social_breakdown
        }

        # Sentiment summary
        if total_score >= 16:
            result['sentiment_summary'] = 'Very Positive'
        elif total_score >= 13:
            result['sentiment_summary'] = 'Positive'
        elif total_score >= 10:
            result['sentiment_summary'] = 'Neutral'
        elif total_score >= 7:
            result['sentiment_summary'] = 'Negative'
        else:
            result['sentiment_summary'] = 'Very Negative'

        return result


def main():
    parser = argparse.ArgumentParser(description='Sentiment Analysis for NSE stocks')
    parser.add_argument('--input', required=True, help='Input CSV with stock universe')
    parser.add_argument('--output', required=True, help='Output CSV with sentiment scores')
    parser.add_argument('--delay', type=float, default=1.0,
                       help='Delay between API calls in seconds')

    args = parser.parse_args()

    logger.info("Starting sentiment analysis...")
    logger.info("Note: This is a simplified implementation.")
    logger.info("For production use, integrate:")
    logger.info("  - News APIs (NewsAPI, GNews)")
    logger.info("  - Analyst data providers (TipRanks, FinViz)")
    logger.info("  - Social media APIs (Twitter, Reddit)")

    # Load stock universe
    universe_df = pd.read_csv(args.input)
    logger.info(f"Loaded {len(universe_df)} stocks from {args.input}")

    analyzer = SentimentAnalyzer()
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
    results_df = results_df.sort_values('sentiment_score', ascending=False)
    results_df.to_csv(args.output, index=False)

    logger.info(f"\nSaved {len(results)} analyzed stocks to {args.output}")

    # Summary statistics
    logger.info("\n=== Sentiment Analysis Summary ===")
    logger.info(f"Stocks analyzed: {len(results)}")
    logger.info(f"Average sentiment score: {results_df['sentiment_score'].mean():.1f}/20")
    logger.info(f"Median sentiment score: {results_df['sentiment_score'].median():.1f}/20")
    logger.info(f"Top score: {results_df['sentiment_score'].max():.1f}/20")

    logger.info(f"\nSentiment distribution:")
    print(results_df['sentiment_summary'].value_counts())

    logger.info(f"\nTop 10 stocks by sentiment:")
    print(results_df[['symbol', 'name', 'sentiment_score', 'news_score',
                      'analyst_score', 'sentiment_summary']].head(10))


if __name__ == '__main__':
    main()
