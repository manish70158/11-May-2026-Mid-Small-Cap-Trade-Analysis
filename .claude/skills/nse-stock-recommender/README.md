# NSE Stock Recommender Skill

Comprehensive stock analysis skill that screens all NSE-listed stocks using 4-pillar analysis to recommend the top 20 buy opportunities for short-term (1-3 months) investment.

## Overview

This skill performs multi-dimensional analysis combining:
- **Fundamental Analysis (30%)**: Valuation, growth, quality, financial health
- **Technical Analysis (30%)**: Trend, momentum, support/resistance, volume
- **Risk Assessment (20%)**: Volatility, concentration, liquidity
- **Sentiment Analysis (20%)**: News, analyst ratings, social media

**Output**: Top 20 ranked stocks with detailed report, entry points, and target prices.

## Quick Start

### Installation

The skill is already installed in your Claude Code environment. Simply invoke it by asking Claude to:
- "Find the best NSE stocks to buy right now"
- "Screen all NSE stocks and recommend top 20"
- "Which stocks should I invest in for short-term?"

### Usage Example

```
User: Find me the top 20 NSE stocks to buy for the next 1-3 months with complete analysis

Claude will:
1. Fetch NSE stock universe (~1500-1800 liquid stocks)
2. Run fundamental analysis (valuation, growth, quality, health)
3. Run technical analysis (trend, momentum, S/R, volume)
4. Run risk assessment (volatility, concentration, liquidity)
5. Run sentiment analysis (news, analysts, social media)
6. Rank all stocks by composite score
7. Apply sector diversification
8. Generate top 20 recommendations with detailed report
```

## How It Works

### Step 1: Universe Fetching
- Fetches all NSE-listed stocks from major indices
- Filters for liquid stocks (₹500 Cr+ market cap, 100K+ daily volume)
- Output: ~1500-1800 investable stocks

### Step 2: Four-Pillar Analysis

**Fundamental (30 points)**:
- Valuation: P/E discount, P/B-ROE, PEG, EV/EBITDA
- Growth: Revenue & earnings growth (YoY, QoQ)
- Quality: ROE, ROCE, margins
- Health: Debt/equity, interest coverage, FCF

**Technical (30 points)**:
- Trend: 50-day & 200-day MA, golden/death crosses
- Momentum: RSI, MACD, Stochastic
- S/R: 52-week high/low, breakouts
- Volume: Accumulation/distribution patterns

**Risk (20 points)**:
- Volatility: Beta, annual volatility, max drawdown
- Concentration: Promoter holding, institutional ownership
- Liquidity: Trading volume, market cap

**Sentiment (20 points)**:
- News: Recent articles, earnings announcements
- Analysts: Ratings, target prices, consensus
- Social: Twitter, Reddit discussions

### Step 3: Ranking & Selection
- Composite score calculation (weighted average)
- Sector diversification (max 4 stocks per sector)
- Entry point & target price calculation
- Generate comprehensive markdown report

## Output Format

### CSV File
- Top 20 stocks with all scores and metrics
- Entry prices and target prices
- Expected upside percentages
- Detailed score breakdowns

### Markdown Report
- Executive summary
- Top 20 recommendations (ranked)
- Individual stock analysis:
  - Composite score and grade
  - Why buy (specific reasons)
  - Key metrics
  - Investment thesis
  - Risk flags
- Sector diversification table
- Implementation guidelines
- Disclaimers

## Dependencies

All required Python packages:
- `yfinance` - Stock data fetching
- `pandas` - Data manipulation
- `numpy` - Numerical computations

Install with:
```bash
pip install yfinance pandas numpy
```

## Customization

### Adjust Scoring Weights

You can customize the relative importance of each analysis dimension:

```bash
python scripts/composite_ranker.py \
  --fundamental fundamental_scores.csv \
  --technical technical_scores.csv \
  --risk risk_scores.csv \
  --sentiment sentiment_scores.csv \
  --output top_20.csv \
  --report top_20_report.md \
  --weights "fundamental=0.40,technical=0.30,risk=0.20,sentiment=0.10"
```

**Common Adjustments**:
- **Conservative**: `fundamental=0.40,technical=0.20,risk=0.30,sentiment=0.10`
- **Momentum trader**: `fundamental=0.20,technical=0.40,risk=0.20,sentiment=0.20`
- **Risk-averse**: `fundamental=0.35,technical=0.25,risk=0.30,sentiment=0.10`

### Change Stock Universe

Modify minimum filters in `fetch_nse_universe.py`:
- `--min-mcap`: Minimum market cap in Crores (default: 500)
- `--min-volume`: Minimum daily volume (default: 100,000)

### Adjust Top N

Change number of recommendations:
```bash
python scripts/composite_ranker.py \
  ... \
  --top 30 \
  --max-per-sector 5
```

## Performance

**Typical Runtime** (for ~1500 stocks):
- Universe fetching: ~15-20 minutes
- Fundamental analysis: ~30-45 minutes (rate-limited APIs)
- Technical analysis: ~20-30 minutes
- Risk assessment: ~15-20 minutes
- Sentiment analysis: ~45-60 minutes
- Composite ranking: ~5 minutes

**Total: ~2-3 hours** for complete analysis

**Optimization Tips**:
- Enable parallel processing in scripts (use multiprocessing)
- Cache sector averages and universe data
- Run analysis during off-peak hours
- Consider analyzing in batches (500 stocks at a time)

## Data Sources

- **Stock Data**: Yahoo Finance API (via yfinance)
- **Price History**: 1 year of OHLCV data
- **Fundamentals**: Company financials from Yahoo Finance
- **Analyst Data**: Consensus ratings and target prices
- **News**: Limited via Yahoo Finance (expand with NewsAPI for production)
- **Social Media**: Placeholder implementation (expand with Twitter/Reddit APIs)

## Limitations

1. **Sentiment Analysis**: Current implementation is simplified. For production:
   - Add NewsAPI integration for comprehensive news coverage
   - Add Reddit API for r/IndianStockMarket sentiment
   - Add Twitter API for real-time social sentiment

2. **Data Coverage**: Some stocks may lack complete data (especially smallcaps)
   - Missing metrics assigned neutral scores
   - Flagged in output

3. **Rate Limits**: Yahoo Finance has rate limits
   - Respect delays between requests
   - Use caching where possible

4. **Market Timing**: Analysis is backward-looking
   - Technical indicators lag price
   - Fundamental data may be 1-2 quarters old

## Important Disclaimers

⚠️ **This is NOT financial advice**
- Automated screening tool for educational purposes only
- Short-term trading is high risk
- Past performance doesn't guarantee future results
- Always conduct your own due diligence
- Consult a SEBI-registered investment advisor
- Never invest more than you can afford to lose

## Troubleshooting

**"No stocks passed filters"**
- Filters too strict → Reduce min market cap/volume in `fetch_nse_universe.py`
- Check NSE data source accessibility

**"API rate limit exceeded"**
- Add delays between requests (increase `--delay` parameter)
- Enable caching in scripts

**"Sentiment scores all zero"**
- Yahoo Finance has limited news data
- Integrate additional news/social APIs for better coverage

**"Analysis taking too long"**
- Enable parallel processing (modify scripts to use multiprocessing.Pool)
- Reduce universe size (increase min market cap threshold)
- Use cached data where possible

## Skill Structure

```
nse-stock-recommender/
├── SKILL.md                      # Main skill documentation
├── README.md                     # This file
├── scripts/
│   ├── fetch_nse_universe.py    # Step 1: Fetch stock universe
│   ├── fundamental_analyzer.py  # Step 2: Fundamental analysis
│   ├── technical_analyzer.py    # Step 3: Technical analysis
│   ├── risk_analyzer.py         # Step 4: Risk assessment
│   ├── sentiment_analyzer.py    # Step 5: Sentiment analysis
│   └── composite_ranker.py      # Step 6: Ranking & report generation
└── evals/
    └── evals.json               # Test cases for skill evaluation
```

## Support

For issues, questions, or feature requests related to this skill, please consult:
- SKILL.md for detailed methodology
- Script docstrings for implementation details
- Claude Code documentation for skill usage

## Version

**Version**: 1.0
**Created**: May 2026
**Investment Horizon**: Short-term (1-3 months)
**Analysis Coverage**: ~2000 NSE stocks (filtered to ~1500-1800 liquid stocks)

---

**Remember**: The stock market rewards patience and discipline. This is a screening tool to identify candidates - you must still conduct additional research before investing real money.
