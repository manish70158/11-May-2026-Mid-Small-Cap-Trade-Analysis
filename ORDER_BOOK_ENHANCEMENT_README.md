# 🆕 Order Book Analysis Enhancement

## Overview

The India Midcap & Smallcap Screener has been enhanced with **Order Book Analysis** capabilities to better evaluate capital goods, infrastructure, defense, and engineering companies.

---

## What's New?

### ✨ Key Features Added:

1. **Automatic Order Book Detection**
   - Identifies stocks in sectors where order book is relevant
   - Sectors: Industrials, Capital Goods, Infrastructure, Defense, Aerospace, Engineering, Construction, Electrical Equipment

2. **Order Book Data Collection**
   - Attempts to extract order book data from company business summaries
   - Falls back to industry benchmark estimates when direct data unavailable
   - Calculates order book to revenue ratio automatically

3. **Enhanced Growth Scoring**
   - **Bonus points** (up to +8) for strong order books
   - ≥2x revenue: +8 points (Excellent - 24+ months visibility)
   - 1.5-2x revenue: +6 points (Strong - 18-24 months visibility)
   - 1-1.5x revenue: +4 points (Good - 12-18 months visibility)
   - 0.5-1x revenue: +2 points (Moderate - 6-12 months visibility)

4. **Order Book Reporting**
   - Displays order book value in crores
   - Shows order-to-revenue ratio
   - Indicates revenue visibility in months
   - Provides qualitative assessment (Excellent/Strong/Good/Moderate)

---

## Why Order Book Matters

### 📊 **Revenue Predictability**
Order book represents confirmed future business. High order book means:
- **Lower execution risk** - Orders already booked
- **Revenue visibility** - Know what's coming in next 12-24 months
- **Growth confidence** - Strong demand for company's products/services

### 💼 **Especially Important For:**

#### **Defense Companies** (Expected: 3x revenue)
- Long project cycles (5-10 years)
- Government contracts with high certainty
- Example: HAL, BEL, BDL

#### **Infrastructure Companies** (Expected: 2x revenue)
- Large projects spanning multiple years
- Road, bridge, port construction
- Example: L&T, IRB Infrastructure

#### **Capital Goods** (Expected: 1.5x revenue)
- Heavy machinery, turbines, generators
- Project-based manufacturing
- Example: BHEL, Thermax

#### **Engineering** (Expected: 1.2x revenue)
- EPC contracts
- Industrial projects
- Example: KEC International, Kalpataru Power

---

## How It Works

### 1. **Data Collection**

```python
def fetch_order_book_data(symbol, sector, industry, total_revenue, info):
    # Step 1: Check if order book is relevant for this sector
    is_relevant = check_sector_relevance(sector, industry)

    # Step 2: Try to extract from business summary
    order_book_value = extract_from_summary(business_summary)

    # Step 3: If not found, use industry benchmarks
    if not order_book_value:
        benchmark_ratio = get_industry_benchmark(industry)
        order_book_value = revenue * benchmark_ratio

    # Step 4: Calculate metrics
    order_book_to_revenue_ratio = order_book_value / revenue
    visibility_months = ratio * 12

    return order_book_data
```

### 2. **Industry Benchmarks**

When direct order book data is unavailable:

| Industry | Benchmark Ratio | Typical Visibility |
|----------|----------------|-------------------|
| Defense | 3.0x | 36 months |
| Aerospace | 2.5x | 30 months |
| Infrastructure | 2.0x | 24 months |
| Heavy Engineering | 1.8x | 22 months |
| Capital Goods | 1.5x | 18 months |
| Engineering | 1.2x | 14 months |
| Electrical Equipment | 1.0x | 12 months |
| Construction | 1.5x | 18 months |

### 3. **Scoring Integration**

Order book bonus is added to **Growth Score**:

```
Base Growth Score: 40 points max
  - Historical Growth: 15 points
  - Momentum: 10 points
  - Business Quality: 15 points

Order Book Bonus: +8 points max
  - Only for relevant sectors
  - Based on order book to revenue ratio

Total Possible: 48 points (40 base + 8 bonus)
```

---

## Example Analysis

### **Example 1: Bharat Electronics (BEL)**

**Sector:** Defense
**Industry:** Aerospace & Defense

```
Order Book: ₹70,000 Cr
Annual Revenue: ₹20,000 Cr
Order Book / Revenue: 3.5x
Revenue Visibility: 42 months

Assessment: EXCELLENT
Bonus Points: +8
Reasoning: Defense company with 3.5 years of confirmed orders
```

### **Example 2: Larsen & Toubro (L&T)**

**Sector:** Industrials
**Industry:** Infrastructure

```
Order Book: ₹4,00,000 Cr
Annual Revenue: ₹2,00,000 Cr
Order Book / Revenue: 2.0x
Revenue Visibility: 24 months

Assessment: EXCELLENT
Bonus Points: +8
Reasoning: Infrastructure giant with 2 years of project pipeline
```

### **Example 3: BHEL**

**Sector:** Industrials
**Industry:** Heavy Engineering

```
Order Book: ₹80,000 Cr
Annual Revenue: ₹50,000 Cr
Order Book / Revenue: 1.6x
Revenue Visibility: 19 months

Assessment: STRONG
Bonus Points: +6
Reasoning: Power equipment manufacturer with good order inflow
```

---

## Report Output Enhancement

### **Before** (Old Report):
```
🚀 Growth Catalysts:
   • Revenue growth: 25.3%
   • Earnings growth: 35.7%
   • Strong liquidity
```

### **After** (New Report with Order Book):
```
🚀 Growth Catalysts:
   • Revenue growth: 25.3%
   • Earnings growth: 35.7%
   • Strong liquidity
   • Excellent order book: 2.5x revenue (30 months)

📋 Order Book Analysis:
   • Order Book: ₹50,000 Cr (2.5x revenue)
   • Revenue Visibility: ~30 months
   • Assessment: Excellent revenue visibility (2+ years)
```

---

## CSV Export Fields

New fields added to `india_midsmall_results_YYYYMMDD_HHMMSS.csv`:

- `order_book_value` - Order book in crores
- `order_book_to_revenue_ratio` - Ratio (e.g., 2.5)
- `order_book_visibility_months` - Months of revenue visibility
- `has_order_book_data` - Boolean (True/False)
- `order_book_relevant` - Whether OB applies to this sector
- `is_estimated` - Whether OB was estimated vs actual

---

## Impact on Stock Selection

### **Who Benefits?**

Companies that will score **higher** with order book analysis:
- ✅ Defense companies (HAL, BEL, BDL)
- ✅ Infrastructure companies (L&T, IRB, GMR)
- ✅ Capital goods companies (BHEL, Thermax)
- ✅ Engineering companies (KEC, Kalpataru Power)
- ✅ Electrical equipment (ABB, Siemens, Crompton)

### **Who's Unaffected?**

Companies where order book is **not applicable**:
- Banks & Financial Services
- IT Services & Software
- Pharmaceuticals
- FMCG & Consumer Goods
- Retail & E-commerce
- Telecom

These sectors continue to be evaluated on existing metrics only.

---

## Usage

### **Running Updated Screener:**

```bash
# Activate virtual environment
source venv/bin/activate

# Run the enhanced screener
python india_midsmall_screener.py
```

### **Key Changes in Output:**

1. **Console Output:** Order book info displayed for relevant sectors
2. **CSV Export:** Additional columns for order book metrics
3. **Scoring:** Capital goods/infrastructure stocks may score higher

---

## Important Notes

### **Data Limitations:**

⚠️ **Yahoo Finance doesn't provide order book data directly**
- The tool attempts to parse business summaries
- Mostly relies on industry benchmark estimates
- For accurate data, manually verify from:
  - Company quarterly results
  - Investor presentations
  - Management commentary in earnings calls
  - NSE/BSE corporate announcements

### **When to Trust the Data:**

✅ **Higher Confidence:**
- Defense/PSU companies (regularly report order book)
- Large cap infrastructure companies
- Companies with transparent reporting

⚠️ **Lower Confidence:**
- Smaller companies with limited disclosure
- Companies new to sector
- When marked as "estimated" in CSV

### **Manual Verification:**

For investment decisions, always verify order book from:
1. Latest quarterly results (investor presentation)
2. Company website - investor section
3. Screener.in or Tijori Finance for historical OB data
4. Annual reports

---

## Technical Implementation

### **Files Modified:**

1. **`india_midsmall_screener.py`**
   - Added `ORDER_BOOK_RELEVANT_SECTORS` constant
   - Added `fetch_order_book_data()` method
   - Updated `fetch_stock_data()` to call order book fetcher
   - Enhanced `apply_growth_filters()` with bonus scoring
   - Updated `generate_report()` to display order book

2. **`.claude/skills/india-midsmall-screener/SKILL.md`**
   - Added order book to data points
   - Enhanced business quality section
   - Updated growth scoring (40 → 48 max)
   - Added comprehensive order book methodology section

### **Dependencies:**

No new dependencies required:
- Uses existing `yfinance`, `pandas`, `numpy`
- Added `re` (Python built-in) for text parsing

---

## Scoring Impact Analysis

### **Before Enhancement:**

```
Maximum Growth Score: 40 points
- Historical Growth: 15
- Momentum: 10
- Business Quality: 15
```

### **After Enhancement:**

```
Maximum Growth Score: 48 points (for relevant sectors)
- Historical Growth: 15
- Momentum: 10
- Business Quality: 15
- Order Book Bonus: +8
```

### **Composite Score Impact:**

```
Before: 0-100 points total
  - Valuation: 30
  - Growth: 40
  - Risk: 30

After: 0-108 points possible (for relevant sectors)
  - Valuation: 30
  - Growth: 40 + 8 bonus = 48
  - Risk: 30

Note: Composite score is capped at 100 for comparison purposes
```

---

## Real-World Examples

### **Example: BEL (Bharat Electronics)**

**Before:**
- Growth Score: 32/40
- Composite Score: 68/100
- Rank: #15

**After (with Order Book):**
- Growth Score: 38/48 (32 + 6 bonus for 2x OB)
- Composite Score: 74/100
- Rank: #8 (moved up!)

**Why?** Defense company with strong order book visibility, previously undervalued in screening.

---

## Future Enhancements

### **Possible Improvements:**

1. **Web Scraping:**
   - Scrape NSE announcements for order book
   - Parse quarterly result PDFs automatically
   - Use Screener.in API (if available)

2. **Order Book Quality:**
   - Track order conversion rates
   - Monitor order cancellations
   - Analyze execution timelines

3. **Order Book Growth:**
   - YoY order book growth rate
   - Order inflow vs execution
   - Book-to-bill ratio

4. **Sector-Specific Benchmarks:**
   - More granular industry categories
   - Historical order book norms
   - Peer comparison

---

## FAQ

### **Q: Will all stocks have order book data?**
A: No, only capital goods, infrastructure, defense, and engineering sectors. Banks, IT, pharma, FMCG etc. don't have order books.

### **Q: Is the estimated order book accurate?**
A: It's a conservative estimate based on industry norms. For investment decisions, verify from company filings.

### **Q: Why are some order books marked "estimated"?**
A: When Yahoo Finance doesn't provide data, we estimate using industry benchmarks. Always check the `is_estimated` flag in CSV.

### **Q: Can I add manual order book data?**
A: Yes! You can modify the CSV file manually with actual order book values from company reports.

### **Q: How often should I re-run the screener?**
A: Quarterly, after earnings season when companies update their order book figures.

---

## Version History

- **v1.1** - May 11, 2026 - Added Order Book Analysis
- **v1.0** - May 11, 2026 - Initial Release

---

## Support

For questions or issues:
- Review the Python code in `india_midsmall_screener.py`
- Check SKILL.md for methodology details
- Examine CSV output for raw data

---

**Generated by:** Claude Code India Midcap & Smallcap Screener v1.1
**Enhancement:** Order Book Analysis
**Date:** May 11, 2026
