---
name: india-midsmall-screener
description: Analyze Nifty Midcap and Nifty Smallcap stocks to identify undervalued investment opportunities with high growth potential (2x in 6-12 months) and lower risk. Use this skill when the user asks about Indian midcap or smallcap stocks, NSE indices, undervalued Indian stocks, investment opportunities in Nifty Midcap 100 or Nifty Smallcap 100, stock screening for Indian markets, or wants recommendations for Indian equities with doubling potential. Trigger even if the user doesn't explicitly mention "midcap" or "smallcap" but asks about Indian stock recommendations, NSE stock analysis, or finding growth stocks in the Indian market.
---

# India Midcap & Smallcap Stock Screener

This skill helps identify undervalued, high-potential stocks from the Nifty Midcap 100 and Nifty Smallcap 100 indices with potential to double in 6-12 months while maintaining acceptable risk levels.

## Data Collection Strategy

### Primary: NSE India Data
NSE India doesn't provide a free public API, but data can be accessed through:

1. **NSE Website Scraping** (if needed):
   - Constituent lists: `https://www.nseindia.com/market-data/live-equity-market`
   - Historical data: NSE Historical Data section
   - Important: Set proper headers to mimic browser requests

2. **Yahoo Finance Fallback** (Recommended for reliability):
   - Indian stocks use `.NS` suffix (e.g., `RELIANCE.NS`)
   - Good coverage of NSE stocks
   - More reliable for programmatic access

3. **Index Constituents** (Complete Lists):

   **Nifty Midcap 100 Constituents (100+ stocks):**
   ```
   ADANIENT, ADANIPORTS, AMBUJACEM, APOLLOHOSP, ASHOKLEY, ASIANPAINT,
   ASTRAL, AUROPHARMA, BAJAJFINSV, BAJAJHLDNG, BALKRISIND, BANDHANBNK,
   BATAINDIA, BEL, BERGEPAINT, BHARATFORG, BHEL, BIOCON, BOSCHLTD,
   CANBK, CHOLAFIN, CIPLA, COALINDIA, COLPAL, CONCOR, COROMANDEL,
   CUMMINSIND, DABUR, DALBHARAT, DEEPAKNTR, DIVISLAB, DLF, ESCORTS,
   EXIDEIND, FEDERALBNK, GAIL, GLENMARK, GODREJCP, GODREJPROP, GRASIM,
   GUJGASLTD, HAL, HAVELLS, HCLTECH, HINDPETRO, HINDUNILVR, ICICIBANK,
   ICICIPRULI, IDEA, IDFCFIRSTB, INDHOTEL, INDIAMART, INDIGO, INDUSTOWER,
   INTELLECT, IOC, JINDALSTEL, JKCEMENT, JUBLFOOD, KOTAKBANK, L&TFH,
   LICHSGFIN, LUPIN, M&M, M&MFIN, MANAPPURAM, MARICO, MCDOWELL-N,
   MFSL, MGL, MOTHERSON, MPHASIS, MRF, MUTHOOTFIN, NAUKRI, NMDC,
   NTPC, OBEROIRLTY, OFSS, OIL, PAGEIND, PERSISTENT, PETRONET, PFC,
   PIDILITIND, PIIND, PNB, POLYCAB, POWERGRID, RECLTD, SBICARD,
   SBILIFE, SHREECEM, SIEMENS, SRF, SRTRANSFIN, SUNPHARMA, SUNTV,
   TATACOMM, TATACONSUM, TATAMOTORS, TATAPOWER, TATASTEEL, TCS, TECHM,
   TITAN, TORNTPHARM, TRENT, TVSMOTOR, UBL, ULTRACEMCO, UPL, VEDL,
   VOLTAS, WIPRO, ZEEL
   ```

   **Nifty Smallcap 100 Constituents (100+ stocks):**
   ```
   AARTIIND, ABBOTINDIA, ABCAPITAL, ABFRL, ACC, ADANIGREEN, ADANIPOWER,
   ADANITRANS, AFFLE, AJANTPHARM, ALKEM, AMARAJABAT, AMBUJACEM, ANGELONE,
   APARINDS, APLAPOLLO, APLLTD, APOLLOTYRE, ASHOKLEY, ASIANPAINT, ASTERDM,
   ASTRAL, ATUL, AUBANK, AUROPHARMA, BAJAJCON, BAJAJHLDNG, BAJFINANCE,
   BALKRISIND, BALRAMCHIN, BANDHANBNK, BANKBARODA, BASF, BATAINDIA, BEL,
   BERGEPAINT, BHARATFORG, BHARTIARTL, BHEL, BIOCON, BIRLACORPN, BLUESTARCO,
   BOSCHLTD, BPCL, BRITANNIA, CANFINHOME, CARBORUNIV, CASTROLIND, CEATLTD,
   CENTURYPLY, CENTURYTEX, CERA, CHAMBLFERT, CHOLAFIN, CIEINDIA, CIPLA,
   COALINDIA, COFORGE, COLPAL, CONCOR, COROMANDEL, CREDITACC, CROMPTON,
   CUMMINSIND, DABUR, DALBHARAT, DEEPAKNTR, DELTACORP, DHANI, DIVISLAB,
   DIXON, DLF, DRREDDY, EICHERMOT, ELGIEQUIP, EMAMILTD, ENDURANCE,
   EQUITAS, ESCORTS, EXIDEIND, FEDERALBNK, FINEORG, GAIL, GILLETTE,
   GLAXO, GLENMARK, GMRINFRA, GNFC, GODFRYPHLP, GODREJCP, GODREJPROP,
   GRANULES, GRASIM, GRINDWELL, GSPL, GUJGASLTD, GULFOILLUB, HAL
   ```

   **Total Universe:** ~200 stocks for comprehensive screening

   **Note:** Constituent lists are subject to periodic changes by NSE. The screener tool
   contains the most up-to-date lists embedded in the Python code.

### Data Points to Collect
For each stock, gather:
- **Price data**: Current price, 52-week high/low, historical prices (1Y)
- **Fundamentals**: Market cap, P/E, P/B, PEG, ROE, debt-to-equity, revenue growth, EPS growth
- **Liquidity**: Average daily volume, free float
- **Sector**: Industry classification for peer comparison
- **Order Book** (for capital goods/infrastructure): Order book value, order-to-revenue ratio, revenue visibility in months

## Screening Methodology

### Stage 1: Valuation Filters (Identify Undervalued Stocks)

Apply these filters to identify undervalued candidates:

1. **P/E Ratio Analysis**:
   - Compare stock P/E to its sector/industry average
   - Flag stocks trading at ≤20% discount to sector P/E
   - Exception: Avoid stocks with P/E < 5 (possible value traps) unless fundamentally strong

2. **P/B and ROE Analysis**:
   - Calculate P/B ratio and ROE
   - Look for: P/B < 3 AND ROE > 15%
   - Higher ROE with lower P/B indicates efficient capital use at discount

3. **PEG Ratio**:
   - PEG = (P/E ratio) / (EPS growth rate)
   - Target: PEG < 1 (stock is undervalued relative to growth)
   - Minimum EPS growth: 15% YoY

4. **Price to 52-Week High**:
   - Current price should be 60-85% of 52-week high
   - This indicates correction from peak but not distressed

### Stage 2: Growth Potential (2x in 6-12 Months)

For stocks passing valuation filters, assess growth catalysts:

1. **Historical Growth**:
   - Revenue growth: >20% YoY (last 2 years)
   - EPS growth: >25% YoY (last 2 years)
   - Consistent growth trend (not one-off spikes)

2. **Momentum Indicators**:
   - Stock should show recent accumulation (price stabilization or gradual uptrend)
   - Volume analysis: Increasing volume on up days
   - RSI: 40-60 range (neither overbought nor oversold)

3. **Business Quality**:
   - Improving operating margins (trend analysis)
   - **Strong order book or revenue visibility** (ENHANCED FEATURE)
     - For capital goods, infrastructure, defense, and engineering companies
     - Order book to revenue ratio: >1.5x = Strong (18+ months visibility)
     - Order book to revenue ratio: 1.0-1.5x = Good (12-18 months visibility)
     - Order book to revenue ratio: 0.5-1.0x = Moderate (6-12 months visibility)
     - Provides bonus points in growth scoring (up to +8 points)
   - Market share gains in growing sectors

4. **Sector Tailwinds**:
   - Prioritize sectors with positive outlook (infrastructure, manufacturing, technology, etc.)
   - Government policy support
   - Improving sector fundamentals

### Stage 3: Risk Assessment

Even high-potential stocks must meet risk criteria:

1. **Financial Health**:
   - Debt-to-Equity: <1 (prefer <0.5 for smallcaps)
   - Interest coverage ratio: >3x
   - Current ratio: >1.2

2. **Liquidity Risk**:
   - Average daily volume: >500K shares (midcaps), >200K shares (smallcaps)
   - Avoid stocks with frequent circuit limits
   - Market cap: >₹5000 Cr (midcaps), >₹1000 Cr (smallcaps)

3. **Volatility**:
   - Beta: 0.8-1.5 (not too volatile, but some momentum acceptable)
   - Max drawdown in last year: <40%
   - Lower is better, but some volatility is expected for high-growth stocks

4. **Governance & Quality**:
   - Check for promoter holding stability (>50% and stable/increasing)
   - No major corporate governance red flags
   - Institutional interest (FII/DII holding trends)

### Order Book Analysis (Enhanced Feature)

**What is Order Book?**
Order book represents the total value of confirmed orders that a company has received but not yet executed. It provides revenue visibility and indicates future business pipeline.

**When is Order Book Relevant?**
Order book analysis is applicable primarily for:
- **Capital Goods**: Heavy machinery, turbines, generators
- **Infrastructure**: Construction, roads, bridges, ports
- **Defense & Aerospace**: Defense equipment, aircraft components
- **Engineering**: Heavy engineering, project execution
- **Electrical Equipment**: Transformers, switchgears, power equipment

**Order Book Metrics:**

1. **Order Book Value (in ₹ Crores)**:
   - Absolute value of pending orders
   - Fetched from company announcements or estimated using industry benchmarks

2. **Order Book to Revenue Ratio**:
   - Formula: Order Book Value / Annual Revenue
   - Indicates how many years of revenue the company has locked in
   - Example: Ratio of 2.0 = 2 years of current revenue already booked

3. **Revenue Visibility (in Months)**:
   - Formula: (Order Book / Annual Revenue) × 12
   - Practical measure of execution timeline
   - Example: 18 months visibility = Strong near-term revenue certainty

**Scoring Rubric:**

| Order Book / Revenue | Visibility | Score | Assessment |
|---------------------|------------|-------|------------|
| ≥2.0x | 24+ months | +8 | Excellent - 2+ years visibility |
| 1.5-2.0x | 18-24 months | +6 | Strong - 1.5-2 years visibility |
| 1.0-1.5x | 12-18 months | +4 | Good - 1-1.5 years visibility |
| 0.5-1.0x | 6-12 months | +2 | Moderate - 6-12 months visibility |
| <0.5x | <6 months | 0 | Weak - Limited visibility |

**Data Sources:**

1. **Primary (Preferred)**:
   - Company quarterly results and investor presentations
   - Management commentary in earnings calls
   - NSE/BSE announcements and corporate filings

2. **Estimation Method**:
   - When direct data unavailable, use industry benchmarks
   - Defense companies: Typically 3x revenue (36 months)
   - Infrastructure: Typically 2x revenue (24 months)
   - Capital goods: Typically 1.5x revenue (18 months)
   - Engineering: Typically 1.2x revenue (14 months)

**Why Order Book Matters:**

✅ **Revenue Predictability**: High order book means confirmed future revenue
✅ **Growth Visibility**: Indicates business momentum and demand
✅ **Risk Reduction**: Lower execution risk when orders are pre-booked
✅ **Competitive Position**: Strong order book signals market confidence
✅ **Valuation Support**: Justifies higher valuations due to certainty

**Interpretation Examples:**

- **HAL (Hindustan Aeronautics)**: Order book of ₹90,000 Cr with revenue of ₹30,000 Cr = 3x ratio = Excellent 36-month visibility for defense sector

- **Larsen & Toubro**: Order book of ₹4,00,000 Cr with revenue of ₹2,00,000 Cr = 2x ratio = Strong 24-month visibility for infrastructure/engineering

- **ABB India**: Order book of ₹12,000 Cr with revenue of ₹10,000 Cr = 1.2x ratio = Good 14-month visibility for electrical equipment

**Important Notes:**

- Order book quality matters: Check order conversion rate and execution capability
- Some orders may be subject to cancellation or deferral
- Long execution cycles (>3 years) may indicate project delays
- Compare order book growth YoY to assess business momentum
- Not applicable to banks, IT services, pharma, FMCG, or other sectors without project-based revenue

## Analysis Workflow

Follow these steps systematically:

1. **Fetch Index Constituents**:
   - Get current Nifty Midcap 100 constituents
   - Get current Nifty Smallcap 100 constituents
   - Total universe: ~200 stocks

2. **Apply Valuation Filters**:
   - Run all stocks through Stage 1 filters
   - Expected shortlist: 30-50 stocks

3. **Assess Growth Potential**:
   - Analyze Stage 2 criteria for shortlisted stocks
   - Narrow down to: 15-25 stocks

4. **Risk Screening**:
   - Apply Stage 3 risk filters
   - Final list: 5-10 stocks with best risk-adjusted potential

5. **Rank and Recommend**:
   - Score each stock (composite scoring explained below)
   - Provide top 5 recommendations with detailed rationale

## Composite Scoring System

Calculate a total score (0-100) for each final candidate:

- **Valuation Score (30 points)**:
  - P/E discount to sector: 0-10 points (bigger discount = more points)
  - P/B + ROE: 0-10 points (lower P/B with higher ROE = more points)
  - PEG ratio: 0-10 points (lower = more points, max at PEG <0.5)

- **Growth Score (40 points + up to 8 bonus)**:
  - Historical growth: 0-15 points (revenue + EPS growth rates)
  - Momentum: 0-10 points (technical indicators, volume)
  - Business quality: 0-15 points (margins, competitive position)
  - **Order Book BONUS: 0-8 points** (capital goods/infrastructure sectors only)
    - Order book ≥2x revenue: +8 points (24+ months visibility)
    - Order book 1.5-2x revenue: +6 points (18-24 months visibility)
    - Order book 1-1.5x revenue: +4 points (12-18 months visibility)
    - Order book 0.5-1x revenue: +2 points (6-12 months visibility)

- **Risk Score (30 points)**:
  - Financial health: 0-10 points (debt, coverage ratios)
  - Liquidity: 0-10 points (volume, market cap)
  - Volatility: 0-10 points (beta, drawdown history)

Higher total score = better investment candidate.

## Output Format

Present results in this structure:

### Executive Summary
- Total stocks analyzed: [number]
- Stocks passing valuation filters: [number]
- Final recommendations: [number]
- Market conditions context: [brief note on current Indian market environment]

### Top Recommendations

For each recommended stock (ranked by composite score):

#### [Rank]. [Stock Name] ([NSE Symbol])
**Composite Score: [X]/100** (Valuation: X/30 | Growth: X/40 | Risk: X/30)

**Current Price**: ₹[price] | **Target Price (6-12M)**: ₹[target] | **Upside Potential**: [X]%

**Why It's Undervalued**:
- P/E: [X] vs Sector Avg: [Y] ([Z]% discount)
- P/B: [X] with ROE: [Y]%
- PEG: [X]

**Growth Catalysts**:
- [Key catalyst 1]
- [Key catalyst 2]
- [Key catalyst 3]

**Risk Profile**:
- Debt-to-Equity: [X]
- Volatility (Beta): [X]
- Liquidity: [Average daily volume]

**Investment Thesis**: [2-3 sentences explaining why this stock could double in 6-12 months]

**Key Risks**: [1-2 main risks to watch]

---

### Honorable Mentions
[List 3-5 additional stocks that scored well but didn't make top 5, with brief 1-line explanation each]

### Market Context & Timing
- Current Nifty Midcap/Smallcap index levels and trends
- Sectoral rotation patterns
- Macro factors affecting midcaps/smallcaps (interest rates, liquidity, FII flows)

### Important Disclaimers
- Past performance doesn't guarantee future results
- 6-12 month doubling is an aggressive target; actual returns may vary significantly
- Recommend position sizing: No single stock >5-10% of portfolio
- Always conduct your own due diligence
- Consider consulting a SEBI-registered investment advisor
- Markets are subject to risks; invest based on your risk appetite

## Implementation Notes

### Data Collection Script

If creating a Python script to fetch data, structure it like this:

```python
import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

def get_nifty_midcap_constituents():
    """Fetch Nifty Midcap 100 constituent list"""
    # Implementation: scrape NSE website or use cached list
    pass

def get_nifty_smallcap_constituents():
    """Fetch Nifty Smallcap 100 constituent list"""
    # Implementation: scrape NSE website or use cached list
    pass

def fetch_stock_data(symbol):
    """Fetch fundamental and price data for a stock"""
    ticker = yf.Ticker(f"{symbol}.NS")
    info = ticker.info
    hist = ticker.history(period="1y")

    return {
        'price': info.get('currentPrice'),
        'pe': info.get('trailingPE'),
        'pb': info.get('priceToBook'),
        'roe': info.get('returnOnEquity'),
        'debt_to_equity': info.get('debtToEquity'),
        'revenue_growth': info.get('revenueGrowth'),
        'earnings_growth': info.get('earningsGrowth'),
        # ... more fields
    }
```

### Handling Missing Data

- If data is unavailable for specific stocks, note it and skip to next candidate
- For P/E comparisons, use industry average from available stocks in same sector
- If NSE scraping fails, fall back to Yahoo Finance
- Document any data quality issues in final output

### Performance Optimization

- Cache index constituent lists (they change quarterly)
- Batch API requests where possible
- Parallel processing for large stock universes
- Use dataframes for efficient filtering

## Best Practices

1. **Regular Updates**: Index constituents change; refresh quarterly
2. **Market Context**: Always consider current market conditions (bull/bear phase)
3. **Diversification**: Recommend stocks across different sectors
4. **Transparency**: Clearly explain scoring methodology to users
5. **Risk Emphasis**: Always emphasize that 2x returns in 6-12 months are aggressive targets
6. **Local Factors**: Consider India-specific factors (budget announcements, RBI policy, monsoons for certain sectors)

## When to Recommend Caution

- During extreme market volatility (VIX India >30)
- When valuations are stretched across the board (median P/E significantly above historical average)
- During liquidity crunches (FII sustained outflows)
- User's risk profile doesn't match the aggressive target (suggest longer timeframes)

---

## Appendix: Complete Stock Universe Reference

### Nifty Midcap 100 - Major Constituents by Sector

**Banking & Financial Services (20+ stocks):**
- Banks: CANBK, FEDERALBNK, IDFCFIRSTB, KOTAKBANK, PNB, BANDHANBNK, ICICIBANK
- NBFCs: BAJAJFINSV, CHOLAFIN, LICHSGFIN, M&MFIN, MANAPPURAM, MFSL, MUTHOOTFIN, L&TFH, SBICARD
- Insurance: ICICIPRULI, SBILIFE
- Broking: PFC, RECLTD

**Infrastructure & Capital Goods (15+ stocks):**
- Industrials: ABB, BEL, BHEL, BOSCHLTD, CUMMINSIND, HAL, SIEMENS
- Engineering: BHARATFORG, DALBHARAT, ESCORTS, MOTHERSON, POLYCAB, VOLTAS
- Cement: AMBUJACEM, SHREECEM, ULTRACEMCO
- Steel: JINDALSTEL, TATASTEEL

**IT & Technology (8+ stocks):**
- IT Services: HCLTECH, INTELLECT, MPHASIS, OFSS, PERSISTENT, TCS, TECHM, WIPRO
- Online: INDIAMART, NAUKRI

**Consumer Goods (12+ stocks):**
- FMCG: BRITANNIA, COLPAL, DABUR, GODREJCP, HINDUNILVR, MARICO, TATACONSUM
- Paints: ASIANPAINT, BERGEPAINT
- Footwear: BATAINDIA
- Auto: ASHOKLEY, EICHERMOT, M&M, TATAMOTORS, TVSMOTOR
- Tires: MRF

**Pharmaceuticals (8+ stocks):**
- ALKEM, AUROPHARMA, BIOCON, CIPLA, DIVISLAB, DRREDDY, GLENMARK, LUPIN, SUNPHARMA, TORNTPHARM

**Real Estate & Hospitality (5+ stocks):**
- Real Estate: DLF, GODREJPROP, OBEROIRLTY
- Hospitality: INDHOTEL
- Online Real Estate: (various)

**Oil, Gas & Power (10+ stocks):**
- Oil & Gas: GAIL, HINDPETRO, IOC, OIL, PETRONET
- Power: NTPC, POWERGRID, TATAPOWER
- Gas Distribution: GUJGASLTD, MGL

**Telecom & Media (5+ stocks):**
- Telecom: BHARTIARTL, IDEA, INDUSTOWER, TATACOMM
- Media: SUNTV, ZEEL

**Materials & Chemicals (8+ stocks):**
- Chemicals: AARTIIND, DEEPAKNTR, GNFC, PIDILITIND, SRF, UPL
- Specialty: ASTRAL, COROMANDEL
- Mining: COALINDIA, NMDC, VEDL

**Retail & E-commerce (5+ stocks):**
- Retail: JUBLFOOD, TRENT
- Auto Ancillary: BALKRISIND, EXIDEIND
- Conglomerates: ADANIENT, ADANIPORTS, GRASIM

**Aviation & Logistics (3+ stocks):**
- Airlines: INDIGO
- Logistics: CONCOR
- Port: ADANIPORTS

---

### Nifty Smallcap 100 - Major Constituents by Sector

**Banking & Financial Services (25+ stocks):**
- Banks: AUBANK, BANKBARODA, EQUITAS
- NBFCs: ABCAPITAL, CANFINHOME, CREDITACC, MANAPPURAM
- Housing Finance: CANFINHOME, LICHSGFIN
- Broking & Fintech: ANGELONE, DHANI
- Holdings: BAJAJHLDNG

**Infrastructure & Capital Goods (20+ stocks):**
- Engineering: CARBORUNIV, CIEINDIA, ELGIEQUIP, ENDURANCE, GRINDWELL
- Construction: GMRINFRA
- Electrical: CROMPTON, HAVELLS
- Capital Goods: ABB, BEL, BHEL, BOSCHLTD, CUMMINSIND, HAL, SIEMENS

**IT & Technology (10+ stocks):**
- IT Services: COFORGE, HAPPSTMNDS, INTELLECT, MPHASIS, OFSS, PERSISTENT
- Internet: AFFLE

**Consumer Goods & Retail (25+ stocks):**
- FMCG: BRITANNIA, COLPAL, DABUR, EMAMILTD, GODREJCP, GODFRYPHLP, MARICO
- Paints: ASIANPAINT, BERGEPAINT
- Footwear: BATAINDIA
- Auto: APOLLOTYRE, ASHOKLEY, EICHERMOT, ESCORTS, M&M, TVSMOTOR
- Auto Ancillary: BALKRISIND, CEATLTD, ENDURANCE, EXIDEIND
- Appliances: BLUESTARCO, DIXON, VOLTAS
- Furniture: CENTURYPLY
- Sanitaryware: CERA

**Pharmaceuticals (15+ stocks):**
- Large: ABBOTINDIA, AJANTPHARM, ALKEM, AUROPHARMA, BIOCON, CIPLA, DIVISLAB, DRREDDY, GLAXO, GLENMARK, IPCALAB, LUPIN
- Mid-size: GRANULES
- Specialty: Various

**Textiles & Apparel (5+ stocks):**
- Textiles: CENTURYTEX
- Apparel: ABFRL

**Materials & Chemicals (15+ stocks):**
- Chemicals: AARTIIND, ATUL, BASF, DEEPAKNTR, FINEORG, GNFC, GSPL, PIDILITIND
- Fertilizers: CHAMBLFERT, COROMANDEL
- Specialty Materials: APARINDS, ASTRAL, SRF

**Real Estate & Construction (8+ stocks):**
- Real Estate: DLF, GODREJPROP, IBREALEST, OBEROIRLTY
- Cement: ACC, AMBUJACEM, HEIDELBERG, JKCEMENT, JKLAKSHMI, SHREECEM

**Energy & Power (15+ stocks):**
- Renewable: ADANIGREEN
- Power: ADANIPOWER, NTPC, TATAPOWER
- Oil & Gas: BPCL, GAIL, HINDPETRO, IOC, OIL
- Gas Distribution: GUJGASLTD, GULFOILLUB, MGL
- Coal: COALINDIA

**Consumer Durables (10+ stocks):**
- Appliances: BLUESTARCO, CROMPTON, DIXON, HAVELLS, VOLTAS
- Lighting: (various)
- Consumer Electronics: DIXON

**Food & Beverages (8+ stocks):**
- Packaged Foods: BRITANNIA, HATSUN, JUBLFOOD
- Beverages: Various
- QSR: JUBLFOOD

---

### Stock Symbols Quick Reference (Alphabetical)

**A-B:**
AARTIIND, ABBOTINDIA, ABCAPITAL, ABFRL, ABB, ACC, ADANIENT, ADANIGREEN, ADANIPOWER, ADANIPORTS, ADANITRANS, AFFLE, AJANTPHARM, ALKEM, AMARAJABAT, AMBUJACEM, ANGELONE, APARINDS, APLAPOLLO, APLLTD, APOLLOHOSP, APOLLOTYRE, ASHOKLEY, ASIANPAINT, ASTERDM, ASTRAL, ATUL, AUBANK, AUROPHARMA, BAJAJCON, BAJAJFINSV, BAJAJHLDNG, BAJFINANCE, BALKRISIND, BALRAMCHIN, BANDHANBNK, BANKBARODA, BASF, BATAINDIA, BEL, BERGEPAINT, BHARATFORG, BHARTIARTL, BHEL, BIOCON, BIRLACORPN, BLUESTARCO, BOSCHLTD, BPCL, BRITANNIA

**C-D:**
CANBK, CANFINHOME, CARBORUNIV, CASTROLIND, CEATLTD, CENTURYPLY, CENTURYTEX, CERA, CHAMBLFERT, CHOLAFIN, CIEINDIA, CIPLA, COALINDIA, COFORGE, COLPAL, CONCOR, COROMANDEL, CREDITACC, CROMPTON, CUMMINSIND, DABUR, DALBHARAT, DEEPAKNTR, DELTACORP, DHANI, DIVISLAB, DIXON, DLF, DRREDDY

**E-H:**
EICHERMOT, ELGIEQUIP, EMAMILTD, ENDURANCE, EQUITAS, ESCORTS, EXIDEIND, FEDERALBNK, FINEORG, GAIL, GILLETTE, GLAXO, GLENMARK, GMRINFRA, GNFC, GODREJCP, GODREJPROP, GODFRYPHLP, GRANULES, GRASIM, GRINDWELL, GSPL, GUJGASLTD, GULFOILLUB, HAL, HAPPSTMNDS, HATSUN, HAVELLS, HCLTECH, HEIDELBERG, HINDPETRO, HINDUNILVR, HONAUT

**I-L:**
IBREALEST, ICICIBANK, ICICIPRULI, IDEA, IDFCFIRSTB, IIFLWAM, INDHOTEL, INDIAMART, INDIGO, INDUSTOWER, INOXLEISUR, INTELLECT, IOC, IPCALAB, JINDALSTEL, JKCEMENT, JKLAKSHMI, JSWHL, JUBLFOOD, KOTAKBANK, L&TFH, LICHSGFIN, LUPIN

**M-P:**
M&M, M&MFIN, MANAPPURAM, MARICO, MCDOWELL-N, MFSL, MGL, MOTHERSON, MPHASIS, MRF, MUTHOOTFIN, NAUKRI, NMDC, NTPC, OBEROIRLTY, OFSS, OIL, PAGEIND, PERSISTENT, PETRONET, PFC, PIDILITIND, PIIND, PNB, POLYCAB, POWERGRID

**R-Z:**
RECLTD, SBICARD, SBILIFE, SHREECEM, SIEMENS, SRF, SRTRANSFIN, SUNPHARMA, SUNTV, TATACOMM, TATACONSUM, TATAMOTORS, TATAPOWER, TATASTEEL, TCS, TECHM, TITAN, TORNTPHARM, TRENT, TVSMOTOR, UBL, ULTRACEMCO, UPL, VEDL, VOLTAS, WIPRO, ZEEL

---

### Notable Stocks by Market Cap & Quality

**Large Cap within Midcap Index (>₹1 Lakh Cr):**
- ICICIBANK, KOTAKBANK, HCLTECH, TCS, SUNPHARMA, TITAN, BAJAJFINSV, ASIANPAINT, ULTRACEMCO

**Quality PSUs (Public Sector):**
- Banks: CANBK, PNB, BANKBARODA
- Power: NTPC, POWERGRID
- Oil: IOC, BPCL, HINDPETRO, OIL
- Defense: BEL, HAL
- Infrastructure: RECLTD, PFC, NMDC, COALINDIA

**Quality Private Sector:**
- Banks: ICICIBANK, KOTAKBANK, BANDHANBNK, FEDERALBNK
- NBFCs: BAJAJFINSV, CHOLAFIN, MUTHOOTFIN, M&MFIN
- IT: HCLTECH, TCS, TECHM, WIPRO, PERSISTENT, MPHASIS
- Pharma: LUPIN, CIPLA, AUROPHARMA, BIOCON, ALKEM

**High Growth (Revenue >30% CAGR):**
- Technology: INDIAMART, NAUKRI, PERSISTENT, INTELLECT, COFORGE
- NBFCs: ANGELONE, CHOLAFIN
- New Age: DIXON, AFFLE, INDIGO

**Dividend Aristocrats (Consistent Dividends):**
- COLPAL, HINDUNILVR, NESTLEIND, PIDILITIND, MARICO, ITC

**Turnaround Stories (Potential):**
- BHEL, IDEA, SUNTV, ZEEL, ASHOKLEY

---

### Sector-Wise Order Book Relevance

**High Order Book Visibility (>2x Revenue):**
- Defense: BEL, HAL, BDL (if listed)
- Aerospace: Various

**Good Order Book Visibility (1.5-2x Revenue):**
- Infrastructure: L&T (if in index), GMRINFRA
- Heavy Engineering: BHEL, CUMMINSIND
- Capital Goods: THERMAX (if in index)

**Moderate Order Book (1-1.5x Revenue):**
- Engineering: CARBORUNIV, GRINDWELL, ELGIEQUIP
- Electrical: ABB, SIEMENS, HAVELLS, CROMPTON
- Construction: Various EPC players

**Order Book Not Applicable:**
- Banking & NBFCs: All financial services stocks
- IT Services: HCLTECH, TCS, TECHM, WIPRO, etc.
- Pharma: All pharmaceutical stocks
- FMCG: All consumer goods stocks
- Retail & E-commerce: All retail stocks

---

## Index Update Schedule

**Important:** NSE reviews and updates index constituents:
- **Quarterly Rebalancing:** March, June, September, December
- **Announcement:** Typically 2-3 weeks before implementation
- **Implementation:** Last working day of the review month

**Always verify current constituents at:**
- NSE India Website: https://www.nseindia.com
- Index factsheets published monthly
- Corporate announcements for additions/deletions

**Screener Update Recommendation:**
- Update constituent lists quarterly after NSE rebalancing
- Re-run comprehensive screening after updates
- Monitor for stocks moving between indices (midcap ↔ largecap, smallcap ↔ midcap)

---

## Notable Index Additions/Deletions (Track These)

**Potential Additions (Companies Growing into Index):**
- Fast-growing midcaps approaching largecap status
- Smallcaps with improving fundamentals entering midcap

**Potential Deletions (Companies Falling Out):**
- Midcaps declining to smallcap territory
- Smallcaps with deteriorating fundamentals
- Companies getting delisted or merged

**Impact on Screening:**
- New additions: May have momentum (index buying)
- Deletions: May face selling pressure (index funds exiting)
- Monitor 2-3 months before/after rebalancing for opportunities

---

*Last Updated: May 2026*
*Stock lists based on india_midsmall_screener.py v1.1*
*Verify current constituents from NSE official sources before using*
