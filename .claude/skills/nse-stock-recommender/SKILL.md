---
name: nse-stock-recommender
description: Comprehensive NSE stock analysis and recommendation system that scans all NSE-listed stocks using fundamental, technical, risk, and sentiment analysis to recommend the top 20 buy opportunities for short-term (1-3 months) investment. Use this skill when the user asks to find the best NSE stocks to buy, screen all NSE stocks for investment opportunities, recommend top stocks with complete analysis, or wants short-term stock picks based on multiple analysis dimensions. Also trigger when users mention phrases like "top stocks to buy now", "best NSE stocks", "stock screening with technical and fundamental analysis", or "which stocks should I invest in".
---

# NSE Top 20 Stock Recommender

Comprehensive multi-dimensional stock screening system for identifying the best 20 stocks to buy from the entire NSE universe (~2000 stocks) using a 4-pillar analysis approach: Fundamental, Technical, Risk, and Sentiment.

## Investment Parameters

- **Universe**: ALL NSE-listed stocks (~2000 companies)
- **Investment Horizon**: Short-term (1-3 months)
- **Output**: Top 20 ranked stocks with buy rationale
- **Focus**: Liquid stocks with strong near-term potential

## Analysis Framework

This skill uses a **4-Pillar Composite Scoring System**:

1. **Fundamental Analysis (30 points)** - Valuation, growth, quality, financial health
2. **Technical Analysis (30 points)** - Trend, momentum, support/resistance, volume
3. **Risk Assessment (20 points)** - Volatility, concentration, liquidity
4. **Sentiment Analysis (20 points)** - News, analyst ratings, social media

**Total Score: 0-100** (higher = stronger buy candidate)

---

## Workflow

Follow these steps systematically to screen all NSE stocks and generate recommendations:

### Step 1: Fetch NSE Stock Universe

Run the universe fetcher to get the complete list of NSE-listed stocks:

```bash
python scripts/fetch_nse_universe.py --output nse_stocks_universe.csv
```

**What it does:**
- Fetches all NSE stock symbols from official NSE website
- Filters for liquid stocks (minimum ₹500 Cr market cap, 100K daily volume)
- Saves to CSV with: symbol, name, sector, market_cap, avg_volume
- Expected output: ~1500-1800 liquid stocks after filtering

**Why filtering matters:** Analyzing all 2000 stocks would take too long and include many illiquid penny stocks unsuitable for investment. We focus on liquid, investable stocks.

### Step 2: Run Fundamental Analysis

For each stock in the universe, analyze fundamental metrics:

```bash
python scripts/fundamental_analyzer.py \
  --input nse_stocks_universe.csv \
  --output fundamental_scores.csv
```

**Metrics analyzed:**
- **Valuation (10 pts)**: P/E, P/B, PEG, EV/EBITDA vs sector averages
- **Growth (10 pts)**: Revenue growth, earnings growth (YoY and QoQ)
- **Quality (5 pts)**: ROE, ROCE, profit margins
- **Financial Health (5 pts)**: Debt/equity, interest coverage, free cash flow

**Scoring logic:**
- Undervalued stocks (P/E <sector avg) get higher scores
- Strong growth (>20% revenue/earnings) maximizes growth score
- High quality (ROE >15%, margins >10%) earns quality points
- Healthy balance sheets (D/E <1, positive FCF) earn health points

**Output CSV includes:** symbol, fundamental_score (0-30), valuation_score, growth_score, quality_score, health_score, key_metrics

**Time estimate:** ~30-45 minutes for 1500 stocks (rate-limited API calls)

### Step 3: Run Technical Analysis

Analyze price action, momentum, and volume patterns:

```bash
python scripts/technical_analyzer.py \
  --input nse_stocks_universe.csv \
  --output technical_scores.csv
```

**Indicators analyzed:**
- **Trend (10 pts)**: 50-day MA, 200-day MA, golden/death crosses
- **Momentum (10 pts)**: RSI (40-60 ideal), MACD, Stochastic
- **Support/Resistance (5 pts)**: Price relative to key levels
- **Volume (5 pts)**: Accumulation/distribution, volume trends

**Scoring logic:**
- Bullish trend: Price above both 50-day and 200-day MA (max trend score)
- Balanced momentum: RSI 40-60 (not overbought/oversold)
- Price near support with volume accumulation = high score
- Recent breakouts above resistance = bonus points

**Why this matters for short-term (1-3 months):** Technical signals are critical for timing. A fundamentally strong stock with bearish technicals may underperform in the short term.

**Output CSV includes:** symbol, technical_score (0-30), trend_score, momentum_score, sr_score, volume_score, signals

**Time estimate:** ~20-30 minutes for 1500 stocks

### Step 4: Run Risk Assessment

Evaluate risk factors and volatility:

```bash
python scripts/risk_analyzer.py \
  --input nse_stocks_universe.csv \
  --output risk_scores.csv
```

**Risk metrics:**
- **Volatility Risk (10 pts)**: Beta, standard deviation, max drawdown
- **Concentration Risk (5 pts)**: Promoter holding stability, sector concentration
- **Liquidity Risk (5 pts)**: Trading volume, bid-ask spread

**Scoring logic:**
- Lower volatility = higher score (beta 0.8-1.2 ideal for short-term)
- Stable promoter holding (50-70%, not increasing/decreasing rapidly) = safe
- High liquidity (volume >500K daily) = full liquidity points
- Max drawdown <30% in past year = full volatility points

**Risk score interpretation:** Higher score = lower risk. This is inverted vs other dimensions.

**Output CSV includes:** symbol, risk_score (0-20), volatility_score, concentration_score, liquidity_score, risk_flags

**Time estimate:** ~15-20 minutes

### Step 5: Run Sentiment Analysis

Analyze market sentiment from multiple sources:

```bash
python scripts/sentiment_analyzer.py \
  --input nse_stocks_universe.csv \
  --output sentiment_scores.csv
```

**Sentiment sources:**
- **News Sentiment (8 pts)**: Economic Times, Bloomberg, Moneycontrol (last 30 days)
- **Analyst Ratings (7 pts)**: Motilal Oswal, ICICI Direct, aggregated consensus
- **Social Media (5 pts)**: Twitter, Reddit (r/IndianStockMarket)

**Scoring logic:**
- Positive news (buyout, earnings beat, new orders) = high news score
- Analyst upgrades or "Buy" ratings = high analyst score
- Positive social media buzz without excessive hype = moderate social score
- **Warning:** Excessive social media hype can indicate retail FOMO - penalize slightly

**Why sentiment matters for short-term:** Market sentiment drives near-term price action. A stock with strong fundamentals but negative sentiment may need time to recover.

**Output CSV includes:** symbol, sentiment_score (0-20), news_score, analyst_score, social_score, sentiment_summary

**Time estimate:** ~45-60 minutes (web scraping + API calls)

**Data access notes:**
- News: Scrape Economic Times, Moneycontrol (RSS feeds, public articles)
- Analyst ratings: Scrape from broker websites, use aggregator APIs if available
- Social media: Twitter API (if available), Reddit API, or fallback to public scraping
- If data access is severely limited, sentiment can be weighted down or skipped

### Step 6: Composite Ranking and Recommendations

Merge all scores and rank the top 20 stocks:

```bash
python scripts/composite_ranker.py \
  --fundamental fundamental_scores.csv \
  --technical technical_scores.csv \
  --risk risk_scores.csv \
  --sentiment sentiment_scores.csv \
  --output top_20_recommendations.csv \
  --report top_20_report.md
```

**Ranking methodology:**
1. Merge all four score dimensions by symbol
2. Calculate composite score: Fundamental (30%) + Technical (30%) + Risk (20%) + Sentiment (20%)
3. Rank all stocks by composite score (descending)
4. Apply sector diversification filter: Max 4 stocks per sector in top 20
5. Select top 20 after diversification
6. Calculate entry points and target prices

**Entry point calculation:**
- Current price adjusted for technical support levels
- If price is at resistance, suggest waiting for pullback
- If price is near support with bullish signals, current price is entry

**Target price calculation (1-3 month horizon):**
- For undervalued stocks: Current price × (1 + expected_reversion) = P/E normalization
- For growth stocks: Current price × (1 + growth_momentum) = Momentum continuation
- For technical breakouts: Next resistance level as target
- Conservative approach: Use minimum of the three methods

**Output files:**
1. **top_20_recommendations.csv**: Ranked list with all scores and metrics
2. **top_20_report.md**: Detailed markdown report (see format below)

**Time estimate:** ~5 minutes

---

## Output Report Format

The final report (`top_20_report.md`) should follow this structure:

```markdown
# NSE Top 20 Stock Recommendations
**Analysis Date:** [Date]
**Investment Horizon:** Short-term (1-3 months)
**Analysis Coverage:** [N] NSE stocks screened

## Executive Summary

### Key Findings
- Total stocks analyzed: [N]
- Stocks passing all filters: [N]
- Average composite score: [X]/100
- Sector distribution: [Top 3 sectors]

### Market Context
- [Brief note on current market conditions - Nifty level, sentiment, FII flows]

---

## Top 20 Recommendations

### Rank 1: [Stock Name] ([SYMBOL].NS)
**Composite Score: [X]/100** | Sector: [Sector] | Market Cap: ₹[X] Cr

| Dimension | Score | Grade |
|-----------|-------|-------|
| Fundamental | [X]/30 | [A/B/C] |
| Technical | [X]/30 | [A/B/C] |
| Risk | [X]/20 | [A/B/C] |
| Sentiment | [X]/20 | [A/B/C] |

**Current Price:** ₹[X]
**Entry Point:** ₹[X] - ₹[X]
**Target Price (1-3M):** ₹[X]
**Expected Upside:** [X]%

**Why Buy:**
- [Top fundamental strength - e.g., "P/E 40% below sector, 35% earnings growth"]
- [Technical signal - e.g., "Bullish golden cross, RSI 52 (neutral-bullish)"]
- [Sentiment driver - e.g., "Recent analyst upgrades, positive news on new orders"]

**Key Metrics:**
- P/E: [X] | P/B: [X] | ROE: [X]%
- Revenue Growth: [X]% | Earnings Growth: [X]%
- 50-day MA: ₹[X] | 200-day MA: ₹[X]
- Beta: [X] | Promoter Holding: [X]%

**Investment Thesis:** [2-3 sentences explaining why this stock can deliver returns in 1-3 months]

**Key Risks:** [1-2 main risks to watch]

---

[Repeat for Ranks 2-20]

---

## Sector Diversification

| Sector | Stocks | Total Weight |
|--------|--------|--------------|
| [Sector 1] | [N] | [X]% |
| [Sector 2] | [N] | [X]% |
| [Sector 3] | [N] | [X]% |
| ... | ... | ... |

**Recommendation:** Diversify across at least 5 sectors. No single sector >30% of portfolio.

---

## Sample Portfolio (₹10 Lakh)

**Aggressive (High Growth, Higher Risk):**
- Top 5 stocks with highest composite scores (₹2L each)

**Balanced (Medium Risk-Reward):**
- Top 10 stocks equally weighted (₹1L each)

**Conservative (Diversified, Lower Risk):**
- Top 15 stocks with emphasis on low-risk, high-fundamental scores (₹67K each)

---

## Implementation Guidelines

### Position Sizing
- No single stock >10% of portfolio
- Higher-risk stocks (Risk Score <15) should be <5% each

### Stop Losses
- Set 8-12% stop loss for short-term trades
- Trail stop loss to 5% once 10% profit achieved

### Monitoring
- Review weekly for technical breakdowns
- Exit if fundamental thesis breaks (earnings miss, management issues)
- Rebalance monthly if sector concentration exceeds limits

### Profit Booking
- Book 30-40% at 15% gain
- Book another 30% at 25% gain
- Let remainder run with trailing stop

---

## Data Quality & Limitations

**Data Sources:**
- Fundamental: Yahoo Finance, NSE website
- Technical: Historical price data (Yahoo Finance)
- Sentiment: News scraping, analyst reports, social media APIs
- Last updated: [Date & Time]

**Known Limitations:**
- Sentiment data may be incomplete for less-covered stocks
- Technical indicators are backward-looking
- Short-term performance depends heavily on market conditions
- Not all stocks may have complete fundamental data

---

## Disclaimers

⚠️ **Important:**
- This is an automated screening tool, NOT financial advice
- Short-term trading is high risk; you can lose your entire investment
- Past performance and expected returns may not materialize
- Always conduct your own due diligence
- Consult a SEBI-registered investment advisor for personalized advice
- Never invest more than you can afford to lose

---

**Report Generated:** [Timestamp]
**Analysis Time:** [Total time taken]
**Stocks Screened:** [N]
```

---

## Error Handling & Edge Cases

### Data Unavailability

**If a stock lacks fundamental data:**
- Skip from fundamental scoring (assign 0 points)
- Flag in output as "Incomplete Data - No Fundamental Score"
- Can still be included if other dimensions (technical, sentiment) are very strong

**If technical indicators fail (insufficient history):**
- Assign average technical score (15/30)
- Flag as "Limited Technical History"
- Recent IPOs often have this issue

**If sentiment data is unavailable:**
- For stocks with low coverage, assign neutral sentiment score (10/20)
- Do not penalize for lack of coverage
- Indicate "Low Coverage" in report

### API Rate Limits

**Yahoo Finance:**
- Respect rate limits: Max 2000 requests/hour
- Batch requests where possible
- If rate-limited, pause for 15 minutes and retry
- Use exponential backoff: 1 min, 5 min, 15 min

**Web Scraping:**
- Add delays between requests (2-3 seconds)
- Rotate user agents
- If blocked, fallback to cached data or skip

### Market Conditions

**Bear Market / High Volatility:**
- Increase weight on Risk dimension (25% instead of 20%)
- Reduce weight on Sentiment (15% instead of 20%)
- Flag in report: "High volatility environment - prioritizing risk management"

**Low Volume Days (Holidays):**
- Do not run analysis on market holidays
- Volume patterns may be distorted
- Check NSE calendar before running

---

## Maintenance & Updates

### When to Rerun

**Daily:** Not recommended (too frequent, noisy signals)
**Weekly:** Ideal for short-term focus - captures new trends
**Monthly:** Minimum frequency to stay updated

**Trigger Rerun When:**
- User explicitly requests fresh analysis
- Major market event (Nifty +/-5% move, policy change)
- Quarterly earnings season
- Significant change in market regime (bull to bear, etc.)

### Updating NSE Universe

NSE stock listings change (IPOs, delistings):
- Refresh universe quarterly
- Check NSE official website for new listings
- Remove delisted stocks from analysis

---

## Advanced Features (Optional)

### Backtesting

To validate the methodology, backtest on historical data:
1. Select a past date (e.g., 3 months ago)
2. Run analysis with data as of that date
3. Track actual returns of top 20 recommendations over next 3 months
4. Compare vs Nifty 50 benchmark
5. Adjust scoring weights if needed

### Customization

Allow users to adjust weights:
```python
# Default weights
WEIGHTS = {
    'fundamental': 0.30,
    'technical': 0.30,
    'risk': 0.20,
    'sentiment': 0.20
}

# User can override
python scripts/composite_ranker.py \
  --weights fundamental=0.40,technical=0.30,risk=0.20,sentiment=0.10
```

**Common adjustments:**
- Conservative investors: Increase fundamental (40%), reduce technical (20%)
- Momentum traders: Increase technical (40%), reduce fundamental (20%)
- Risk-averse: Increase risk weight (30%), reduce sentiment (10%)

---

## Performance Optimization

### Parallel Processing

For faster analysis, process stocks in parallel:
```python
# In each analysis script
from multiprocessing import Pool

def analyze_stock(symbol):
    # Analysis logic
    return result

with Pool(processes=8) as pool:
    results = pool.map(analyze_stock, symbols)
```

**Expected speedup:** 4-6x faster with 8 cores

### Caching

Cache frequently accessed data:
- NSE stock universe (refresh weekly)
- Sector averages (refresh daily)
- Historical price data (append new data, don't refetch)

**Implementation:**
```python
import pickle
from datetime import datetime, timedelta

CACHE_FILE = 'nse_universe_cache.pkl'
CACHE_EXPIRY = timedelta(days=7)

def get_nse_universe():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'rb') as f:
            cache = pickle.load(f)
            if datetime.now() - cache['timestamp'] < CACHE_EXPIRY:
                return cache['data']

    # Fetch fresh data
    data = fetch_from_nse()
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump({'timestamp': datetime.now(), 'data': data}, f)
    return data
```

---

## Troubleshooting

### Common Issues

**"No stocks passed filters"**
- Filters too strict (market cap, volume)
- Adjust thresholds in fetch_nse_universe.py
- Check if NSE data source is accessible

**"API rate limit exceeded"**
- Too many requests too quickly
- Add delays between requests
- Use caching to reduce API calls

**"Sentiment scores all zero"**
- Data sources may be blocked or unavailable
- Check internet connectivity
- Fallback: Run without sentiment, adjust weights accordingly

**"Analysis taking too long"**
- Enable parallel processing (see Performance Optimization)
- Reduce universe size (increase market cap threshold)
- Use cached data where possible

---

## Next Steps After Running

1. **Review the report** - Read through top 20 recommendations carefully
2. **Cross-check** - Verify key metrics independently on Screener.in or Moneycontrol
3. **Monitor news** - Check for any recent negative news before buying
4. **Start small** - Don't deploy full capital immediately; test with 20-30% first
5. **Set alerts** - Use trading apps to set price alerts for entry points
6. **Track performance** - Maintain a spreadsheet to track actual vs expected returns

**Remember:** This is a screening tool to identify candidates. You should still conduct additional research before investing real money.
