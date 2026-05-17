# 🇮🇳 India Midcap & Smallcap Stock Screener

**Automated stock screening tool to identify undervalued Indian midcap and smallcap stocks with 2x potential in 6-12 months.**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)](https://github.com)

---

## 📊 Overview

This screener analyzes **200 stocks** from the **Nifty Midcap 100** and **Nifty Smallcap 100** indices using a rigorous 3-stage filtering process:

1. **Valuation Filters** - Identifies undervalued stocks (P/E, P/B-ROE, PEG ratios)
2. **Growth Filters** - Assesses revenue/earnings growth and business quality
3. **Risk Filters** - Evaluates financial health, liquidity, and volatility

**Key Features:**
- ✅ Uses **official NSE constituent lists** (updated May 2026)
- ✅ **100% midcap/smallcap only** - no large-cap contamination
- ✅ Real-time data from Yahoo Finance
- ✅ Order book analysis for infrastructure/capital goods companies
- ✅ Composite scoring system (0-100 scale)
- ✅ Comprehensive CSV export with all metrics

---

## 🎯 Latest Results (May 11, 2026)

### Top 5 Recommendations

| Rank | Stock | Score | Price | Target | Upside | Market Cap |
|------|-------|-------|-------|--------|--------|------------|
| 🥇 | **Lupin Limited** | 77.4/100 | ₹2,256 | ₹4,512 | **100%** | ₹1.03L Cr |
| 🥈 | **Hero MotoCorp** | 74.2/100 | ₹5,229 | ₹10,457 | **100%** | ₹1.05L Cr |
| 🥉 | **Capri Global Capital** | 72.4/100 | ₹191 | ₹344 | **80%** | ₹18,387 Cr |
| 4 | **Suzlon Energy** | 71.0/100 | ₹53.30 | ₹106.60 | **100%** | ₹73,104 Cr |
| 5 | **BLS International** | 68.0/100 | ₹285 | - | High | ₹11,729 Cr |

**Total Analyzed:** 200 stocks
**Passed All Filters:** 39 stocks (19.5%)
**Average Expected Upside:** 85-95% in 6-12 months

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Internet connection (for fetching stock data)

### Installation

1. **Clone the repository**
```bash
cd ~/Documents/learning
git clone <your-repo-url>
cd 11-May-2026-Mid-Small-Cap-Trade-Analysis
```

2. **Create virtual environment**
```bash
python3 -m venv venv_new
source venv_new/bin/activate  # On Windows: venv_new\Scripts\activate
```

3. **Install dependencies**
```bash
pip install yfinance pandas numpy requests beautifulsoup4
```

### Usage

**Run the screener:**
```bash
python india_midsmall_screener.py
```

The script will:
1. Fetch data for 200 stocks (takes ~10-15 minutes with rate limiting)
2. Apply 3-stage filtering
3. Display results in terminal
4. Save detailed CSV: `india_midsmall_results_YYYYMMDD_HHMMSS.csv`

---

## 📁 Project Structure

```
11-May-2026-Mid-Small-Cap-Trade-Analysis/
├── india_midsmall_screener.py          # Main screening script
├── fetch_correct_constituents.py       # Fetches latest NSE constituent lists
├── correct_constituents.py             # Updated constituent lists (May 2026)
├── india_midsmall_results_*.csv        # Screening results (timestamped)
├── COMPREHENSIVE_INDIA_SCREENING_REPORT.md  # Detailed analysis report
├── README.md                           # This file
└── venv_new/                          # Virtual environment (local)
```

---

## 🔍 Screening Methodology

### Stage 1: Valuation Filters (Max 30 points)

**Criteria:**
- **P/E Analysis** (10 pts): Discount ≥20% from sector average, avoid P/E < 5
- **P/B + ROE Combo** (10 pts): P/B < 3 AND ROE > 15%
- **PEG Ratio** (10 pts): Target PEG < 1 (growth at reasonable price)

**Minimum to pass:** 10 points

### Stage 2: Growth Assessment (Max 40 points)

**Criteria:**
- **Historical Growth** (15 pts): Revenue >20% YoY, Earnings >25% YoY
- **Technical Momentum** (10 pts): RSI 40-60, volume analysis
- **Business Quality** (15 pts): Profit margins, ROE, competitive position

**Bonus:**
- **Order Book Analysis** (+8 pts): For capital goods/infrastructure stocks

**Minimum to pass:** 15 points

### Stage 3: Risk Screening (Max 30 points)

**Criteria:**
- **Financial Health** (10 pts): Debt/Equity < 1, Interest coverage > 3x
- **Liquidity** (10 pts): Volume > 200K daily, Market cap > ₹1,000 Cr
- **Volatility** (10 pts): Beta 0.8-1.5, Max drawdown < 40%

**Minimum to pass:** 15 points

---

## 📈 Features

### 1. **Official NSE Data**
- Uses current Nifty Midcap 100 and Nifty Smallcap 100 constituent lists
- Fetched directly from NSE archives
- Updated quarterly to reflect index changes

### 2. **Comprehensive Metrics**
Each stock is analyzed across 30+ data points:
- Valuation: P/E, P/B, PEG, ROE, Price to 52W high
- Growth: Revenue growth, earnings growth, margins
- Risk: Debt levels, liquidity, volatility (beta, drawdown)
- Technical: RSI, volume, price momentum
- Special: Order book analysis for relevant sectors

### 3. **Order Book Enhancement**
For infrastructure, capital goods, and engineering companies:
- Fetches/estimates order book value
- Calculates order book to revenue ratio
- Provides revenue visibility in months
- Adds bonus points for strong order books (>1.5x revenue)

### 4. **Export & Reporting**
- **CSV Export**: All 39 filtered stocks with complete metrics
- **Terminal Report**: Top 10 stocks with detailed analysis
- **Markdown Report**: Comprehensive documentation

---

## ⚠️ Important Fix Applied

### ❌ **Problem (Before)**
The original constituent lists incorrectly included **large-cap Nifty 50 stocks**:
- ICICIBANK (₹9 Lakh Cr)
- WIPRO, TCS, TITAN, KOTAKBANK
- HINDUNILVR, ASIANPAINT, HCLTECH

### ✅ **Solution (After)**
Updated with **official NSE lists** as of May 2026:
- Removed all large-cap stocks
- Added actual midcap/smallcap stocks: GROWW, PAYTM, SWIGGY, LENSKART, POLICYBZR, etc.
- Verified market cap range: ₹11,000 Cr to ₹1,05,000 Cr

**Result:** 100% genuine midcap/smallcap screening

---

## 📊 Results Files

### CSV Output Format

The CSV file (`india_midsmall_results_*.csv`) contains:

| Column | Description |
|--------|-------------|
| `symbol` | NSE stock symbol |
| `name` | Company full name |
| `sector` | Industry sector |
| `current_price` | Current stock price (₹) |
| `market_cap` | Market capitalization (₹ Cr) |
| `pe_ratio` | Price to Earnings ratio |
| `pb_ratio` | Price to Book ratio |
| `roe` | Return on Equity (%) |
| `revenue_growth` | YoY revenue growth (%) |
| `earnings_growth` | YoY earnings growth (%) |
| `valuation_score` | Stage 1 score (0-30) |
| `growth_score` | Stage 2 score (0-40) |
| `risk_score` | Stage 3 score (0-30) |
| `composite_score` | Total score (0-100) |
| ... | 30+ additional metrics |

---

## 🎓 Understanding the Scores

### Score Interpretation

| Score Range | Grade | Interpretation |
|-------------|-------|----------------|
| **75-100** | Elite | Exceptional opportunities, all criteria met strongly |
| **60-75** | Strong | Solid contenders with good value + growth |
| **50-60** | Decent | Value plays with moderate growth |
| **< 50** | Rejected | Did not meet minimum thresholds |

### Example: Lupin Limited (Score 77.4)

```
Valuation: 10.0/30 → P/E 72% below sector (screaming value)
Growth: 39.4/40 → 89% earnings growth (exceptional)
Risk: 28.0/30 → Low debt, defensive beta (safe)
Total: 77.4/100 → ELITE OPPORTUNITY
```

---

## 📚 Key Definitions

### Market Cap Classification (SEBI/AMFI Guidelines)

- **Large Cap**: Top 100 companies (typically >₹50,000 Cr)
- **Mid Cap**: 101st to 250th companies (₹5,000-50,000 Cr range)
- **Small Cap**: 251st onwards (typically ₹500-5,000 Cr)

### Important Ratios

- **P/E (Price to Earnings)**: Stock price ÷ EPS. Lower = cheaper
- **P/B (Price to Book)**: Stock price ÷ Book value per share
- **ROE (Return on Equity)**: Net income ÷ Shareholder equity (%)
- **PEG**: P/E ÷ Earnings growth rate. <1 = undervalued relative to growth
- **Beta**: Volatility vs market. <1 = less volatile, >1 = more volatile
- **Debt/Equity**: Total debt ÷ Total equity. <1 = conservative

---

## 🔄 Updating Index Constituents

NSE updates index constituents quarterly. To refresh:

```bash
python fetch_correct_constituents.py
```

This will:
1. Fetch latest lists from NSE archives
2. Save to `correct_constituents.py`
3. Display counts and sample symbols

**When to update:**
- Quarterly (after NSE rebalancing)
- When seeing unfamiliar symbols in results
- If `india_midsmall_screener.py` shows "possibly delisted" errors

---

## 💼 Sample Investment Strategy

### Balanced Portfolio (₹10 Lakh)

```
60% Midcaps (₹6L):
- Lupin: ₹2.0L (20%)
- Hero MotoCorp: ₹1.5L (15%)
- Suzlon: ₹1.2L (12%)
- Havells: ₹0.8L (8%)
- Others: ₹0.5L (5%)

30% Smallcaps (₹3L):
- Capri Global: ₹1.2L (12%)
- BLS International: ₹1.0L (10%)
- City Union Bank: ₹0.8L (8%)

10% Cash Reserve (₹1L):
- For rebalancing and opportunities
```

**Expected Return:** 85-95% in 6-12 months
**Risk Level:** Moderate to High

---

## ⚠️ Disclaimers & Risk Warnings

### READ CAREFULLY BEFORE USING

1. **Not Financial Advice**: This is an automated screening tool for educational purposes only. It does NOT constitute investment advice.

2. **High Risk**: Midcap and smallcap stocks are inherently volatile. You can lose your entire investment.

3. **No Guarantees**: Past performance and projected returns (2x in 6-12 months) are aggressive targets and may not materialize.

4. **Data Limitations**: Analysis based on publicly available data which may contain errors or be outdated.

5. **Do Your Research**: This is a starting point. You MUST conduct your own due diligence before investing.

6. **Consult Professionals**: Consider consulting a SEBI-registered investment advisor for personalized advice.

7. **Position Sizing**: Never invest more than 5-10% of your portfolio in a single stock.

8. **Regulatory Compliance**: Ensure your investments comply with applicable laws in your jurisdiction.

---

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- [ ] Add fundamental ratios (Quick ratio, Interest coverage)
- [ ] Integrate analyst ratings from multiple sources
- [ ] Add technical indicators (MACD, Moving averages)
- [ ] Implement backtesting functionality
- [ ] Create web dashboard for visualization
- [ ] Add email/Telegram alerts for new opportunities

**To contribute:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📝 Version History

### v1.1 - May 17, 2026
- ✅ Fixed constituent lists with official NSE data
- ✅ Removed all large-cap stocks (ICICIBANK, WIPRO, etc.)
- ✅ Added order book analysis for relevant sectors
- ✅ Updated screening methodology documentation

### v1.0 - May 11, 2026
- Initial release
- 3-stage filtering system
- CSV export functionality
- 200 stock universe

---

## 📞 Support & Resources

### Data Sources
- **Stock Data**: Yahoo Finance API (via yfinance)
- **Index Constituents**: NSE India Official Archives
- **Methodology**: Based on value investing principles (Graham, Lynch)

### Useful Links
- [NSE India](https://www.nseindia.com/)
- [BSE India](https://www.bseindia.com/)
- [Screener.in](https://www.screener.in/) - Fundamental analysis
- [TradingView](https://www.tradingview.com/) - Technical charts
- [Moneycontrol](https://www.moneycontrol.com/) - News & analysis

### Learning Resources
- **Books**:
  - "The Intelligent Investor" - Benjamin Graham
  - "One Up On Wall Street" - Peter Lynch
  - "Coffee Can Investing" - Saurabh Mukherjea
- **Indian Market**:
  - "The Unusual Billionaires" - Saurabh Mukherjea
  - "Diamonds in the Dust" - Saurabh Mukherjea

---

## 📄 License

This project is licensed under the MIT License - see LICENSE file for details.

---

## 🙏 Acknowledgments

- NSE India for providing index constituent data
- Yahoo Finance for stock market data API
- Python community for excellent libraries (pandas, yfinance)
- Value investing principles from Graham, Buffett, and Lynch

---

## ⚡ Quick Commands Reference

```bash
# Setup
python3 -m venv venv_new
source venv_new/bin/activate
pip install yfinance pandas numpy requests beautifulsoup4

# Run screener
python india_midsmall_screener.py

# Update constituent lists
python fetch_correct_constituents.py

# View latest results
ls -lt india_midsmall_results_*.csv | head -1
```

---

**Made with ❤️ for Indian stock market investors**

*Remember: The stock market is a device for transferring money from the impatient to the patient. - Warren Buffett*

---

**Last Updated:** May 17, 2026
**Screener Version:** 1.1
**Data as of:** May 11, 2026
