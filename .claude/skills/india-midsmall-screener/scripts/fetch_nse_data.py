#!/usr/bin/env python3
"""
NSE India Stock Data Fetcher

Fetches stock data for Nifty Midcap 100 and Nifty Smallcap 100 constituents
using Yahoo Finance as the primary data source.

Usage:
    python fetch_nse_data.py --index midcap  # Fetch midcap data
    python fetch_nse_data.py --index smallcap  # Fetch smallcap data
    python fetch_nse_data.py --index both  # Fetch both (default)
"""

import yfinance as yf
import pandas as pd
import argparse
import json
from datetime import datetime, timedelta
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Known Nifty Midcap 100 constituents (sample - update with full list)
NIFTY_MIDCAP_100 = [
    "OBEROIRLTY", "LICI", "TATACOMM", "GAIL", "PEL", "INDHOTEL", "GODREJCP",
    "ABBOTINDIA", "MPHASIS", "INDUSTOWER", "COLPAL", "PERSISTENT", "SRF",
    "VOLTAS", "ESCORTS", "IDEA", "BANKINDIA", "UNIONBANK", "NATIONALUM",
    "GMRINFRA", "JUBLFOOD", "DIXON", "SAIL", "LUPIN", "TORNTPHARM",
    # Add more constituents...
]

# Known Nifty Smallcap 100 constituents (sample - update with full list)
NIFTY_SMALLCAP_100 = [
    "COCHINSHIP", "NLCINDIA", "MOTHERSON", "KAJARIACER", "CESC", "GRAPHITE",
    "JKCEMENT", "CENTRALBK", "KPITTECH", "RADICO", "AIAENG", "BASF",
    "JBCHEPHARM", "CROMPTON", "ASIANPAINT", "BSOFT", "ITI", "RAYMOND",
    # Add more constituents...
]


def fetch_stock_data(symbol, retries=3):
    """
    Fetch comprehensive stock data for a single symbol.

    Args:
        symbol: NSE stock symbol (without .NS suffix)
        retries: Number of retry attempts

    Returns:
        Dictionary with stock data or None if failed
    """
    ticker_symbol = f"{symbol}.NS"

    for attempt in range(retries):
        try:
            ticker = yf.Ticker(ticker_symbol)
            info = ticker.info
            hist = ticker.history(period="1y")

            if hist.empty or not info:
                time.sleep(1)
                continue

            # Calculate technical indicators
            current_price = info.get('currentPrice', hist['Close'].iloc[-1] if not hist.empty else None)
            week_52_high = info.get('fiftyTwoWeekHigh', hist['High'].max())
            week_52_low = info.get('fiftyTwoWeekLow', hist['Low'].min())

            # Calculate price position
            price_to_52w_high = (current_price / week_52_high * 100) if current_price and week_52_high else None

            # Calculate average volume (last 3 months)
            recent_hist = hist.tail(60)
            avg_volume = recent_hist['Volume'].mean() if not recent_hist.empty else None

            # Calculate beta (simplified - price volatility relative to index)
            returns = hist['Close'].pct_change().dropna()
            beta = returns.std() * (252 ** 0.5) if not returns.empty else None

            # Calculate max drawdown
            rolling_max = hist['Close'].expanding().max()
            drawdown = (hist['Close'] - rolling_max) / rolling_max
            max_drawdown = drawdown.min() * 100 if not drawdown.empty else None

            stock_data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),

                # Price data
                'current_price': current_price,
                '52_week_high': week_52_high,
                '52_week_low': week_52_low,
                'price_to_52w_high_pct': price_to_52w_high,

                # Valuation metrics
                'market_cap': info.get('marketCap'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'pb_ratio': info.get('priceToBook'),
                'peg_ratio': info.get('pegRatio'),
                'price_to_sales': info.get('priceToSalesTrailing12Months'),

                # Profitability metrics
                'roe': info.get('returnOnEquity') * 100 if info.get('returnOnEquity') else None,
                'roa': info.get('returnOnAssets') * 100 if info.get('returnOnAssets') else None,
                'profit_margin': info.get('profitMargins') * 100 if info.get('profitMargins') else None,
                'operating_margin': info.get('operatingMargins') * 100 if info.get('operatingMargins') else None,

                # Growth metrics
                'revenue_growth': info.get('revenueGrowth') * 100 if info.get('revenueGrowth') else None,
                'earnings_growth': info.get('earningsGrowth') * 100 if info.get('earningsGrowth') else None,
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth') * 100 if info.get('earningsQuarterlyGrowth') else None,

                # Financial health
                'debt_to_equity': info.get('debtToEquity'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'interest_coverage': info.get('interestCoverage'),

                # Liquidity & volume
                'avg_volume': avg_volume,
                'volume_today': info.get('volume'),
                'free_float': info.get('floatShares'),

                # Risk metrics
                'beta': info.get('beta', beta),
                'max_drawdown_1y_pct': max_drawdown,

                # Ownership
                'promoter_holding': info.get('heldPercentInsiders') * 100 if info.get('heldPercentInsiders') else None,
                'institutional_holding': info.get('heldPercentInstitutions') * 100 if info.get('heldPercentInstitutions') else None,

                # Timestamps
                'fetched_at': datetime.now().isoformat(),
            }

            return stock_data

        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                print(f"Failed to fetch {symbol}: {str(e)}")
                return None

    return None


def fetch_all_stocks(symbols, max_workers=10):
    """
    Fetch data for multiple stocks in parallel.

    Args:
        symbols: List of NSE symbols
        max_workers: Number of parallel threads

    Returns:
        List of stock data dictionaries
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_symbol = {
            executor.submit(fetch_stock_data, symbol): symbol
            for symbol in symbols
        }

        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                data = future.result()
                if data:
                    results.append(data)
                    print(f"✓ Fetched {symbol}")
                else:
                    print(f"✗ Failed {symbol}")
            except Exception as e:
                print(f"✗ Error {symbol}: {str(e)}")

    return results


def calculate_sector_averages(stocks_data):
    """Calculate sector-wise average metrics."""
    df = pd.DataFrame(stocks_data)

    sector_stats = df.groupby('sector').agg({
        'pe_ratio': 'mean',
        'pb_ratio': 'mean',
        'roe': 'mean',
        'debt_to_equity': 'mean',
        'revenue_growth': 'mean',
        'earnings_growth': 'mean',
    }).round(2)

    return sector_stats.to_dict('index')


def main():
    parser = argparse.ArgumentParser(description='Fetch NSE stock data')
    parser.add_argument('--index', choices=['midcap', 'smallcap', 'both'],
                       default='both', help='Which index to fetch')
    parser.add_argument('--output', default='stock_data.json',
                       help='Output JSON file path')
    parser.add_argument('--workers', type=int, default=10,
                       help='Number of parallel workers')

    args = parser.parse_args()

    # Determine which symbols to fetch
    symbols = []
    if args.index in ['midcap', 'both']:
        symbols.extend(NIFTY_MIDCAP_100)
    if args.index in ['smallcap', 'both']:
        symbols.extend(NIFTY_SMALLCAP_100)

    symbols = list(set(symbols))  # Remove duplicates

    print(f"Fetching data for {len(symbols)} stocks...")
    print("=" * 60)

    # Fetch all stock data
    stocks_data = fetch_all_stocks(symbols, max_workers=args.workers)

    print("\n" + "=" * 60)
    print(f"Successfully fetched: {len(stocks_data)}/{len(symbols)} stocks")

    # Calculate sector averages
    sector_averages = calculate_sector_averages(stocks_data)

    # Prepare output
    output = {
        'metadata': {
            'fetched_at': datetime.now().isoformat(),
            'index': args.index,
            'total_stocks': len(stocks_data),
            'total_attempted': len(symbols),
        },
        'sector_averages': sector_averages,
        'stocks': stocks_data,
    }

    # Save to file
    with open(args.output, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nData saved to: {args.output}")

    # Print summary statistics
    df = pd.DataFrame(stocks_data)
    print("\n" + "=" * 60)
    print("SUMMARY STATISTICS")
    print("=" * 60)
    print(f"Sectors represented: {df['sector'].nunique()}")
    print(f"\nAverage P/E: {df['pe_ratio'].mean():.2f}")
    print(f"Average P/B: {df['pb_ratio'].mean():.2f}")
    print(f"Average ROE: {df['roe'].mean():.2f}%")
    print(f"Average Debt/Equity: {df['debt_to_equity'].mean():.2f}")


if __name__ == '__main__':
    main()
