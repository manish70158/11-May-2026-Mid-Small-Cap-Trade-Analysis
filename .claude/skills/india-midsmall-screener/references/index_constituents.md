# Nifty Midcap & Smallcap Index Constituents

This file contains the constituent lists for Nifty Midcap 100 and Nifty Smallcap 100 indices.

**Note**: These lists change periodically (typically quarterly). Always verify current constituents from NSE India official website: https://www.nseindia.com

## Nifty Midcap 100 Constituents

Major constituents include (sample list - update from NSE):

### Financial Services
- AUBANK (AU Small Finance Bank)
- CHOLAFIN (Cholamandalam Investment)
- LICHSGFIN (LIC Housing Finance)
- MUTHOOTFIN (Muthoot Finance)
- BANDHANBNK (Bandhan Bank)
- IDFCFIRSTB (IDFC First Bank)
- FEDERALBNK (Federal Bank)

### Automobiles & Auto Components
- ESCORTS (Escorts Kubota)
- ASHOKLEY (Ashok Leyland)
- BALKRISIND (Balkrishna Industries)
- MOTHERSON (Samvardhana Motherson International)
- APOLLOTYRE (Apollo Tyres)

### Technology & Telecom
- PERSISTENT (Persistent Systems)
- COFORGE (Coforge Limited)
- MPHASIS (Mphasis Limited)
- LTTS (L&T Technology Services)
- TATACOMM (Tata Communications)

### Pharmaceuticals
- LUPIN (Lupin Limited)
- TORNTPHARM (Torrent Pharmaceuticals)
- IPCALAB (IPCA Laboratories)
- LALPATHLAB (Dr. Lal PathLabs)

### Consumer Goods & Services
- JUBLFOOD (Jubilant FoodWorks)
- VGUARD (V-Guard Industries)
- CROMPTON (Crompton Greaves Consumer)
- DIXON (Dixon Technologies)
- SUPREMEIND (Supreme Industries)

### Infrastructure & Construction
- CANBK (Canara Bank)
- GMRINFRA (GMR Infrastructure)
- IRCTC (Indian Railway Catering)
- PNB (Punjab National Bank)

### Energy & Utilities
- GAIL (GAIL India)
- PETRONET (Petronet LNG)
- COALINDIA (Coal India)
- NTPC (NTPC Limited)

### Metals & Mining
- NATIONALUM (National Aluminium)
- VEDL (Vedanta Limited)
- SAIL (Steel Authority of India)
- NMDC (NMDC Limited)

### Real Estate
- OBEROIRLTY (Oberoi Realty)
- PRESTIGE (Prestige Estates)
- BRIGADE (Brigade Enterprises)

### Others
- INDUSTOWER (Indus Towers)
- SRF (SRF Limited)
- PIIND (PI Industries)
- TVSMOTOR (TVS Motor Company)

**Full list**: ~100 stocks. Refer to NSE website for complete and updated list.

---

## Nifty Smallcap 100 Constituents

Major constituents include (sample list - update from NSE):

### Industrial Manufacturing
- COCHINSHIP (Cochin Shipyard)
- BEML (BEML Limited)
- TIINDIA (Tube Investments)
- KPITTECH (KPIT Technologies)
- KALYANIJWE (Kalyan Jewellers)

### Infrastructure & Capital Goods
- KEC (KEC International)
- NBCC (NBCC India)
- RVNL (Rail Vikas Nigam)
- NETWORK18 (Network18 Media)

### Chemicals & Materials
- AARTI (Aarti Industries)
- NAVINFLUOR (Navin Fluorine)
- POLYCAB (Polycab India)
- FLUOROCHEM (Gujarat Fluorochemicals)

### Textiles & Apparel
- CENTURYTEX (Century Textiles)
- RAYMOND (Raymond Limited)
- GOKEX (Gokal and Co)

### Consumer Durables
- SYMPHONY (Symphony Limited)
- WHIRLPOOL (Whirlpool of India)
- BLUESTARCO (Blue Star)
- CERA (Cera Sanitaryware)

### Financial Services
- CENTRALBK (Central Bank of India)
- UNIONBANK (Union Bank of India)
- BANKINDIA (Bank of India)
- MAHABANK (Bank of Maharashtra)

### Technology
- ROUTE (Route Mobile)
- INTELLECT (Intellect Design Arena)
- SONATSOFTW (Sonata Software)
- RATEGAIN (RateGain Travel Technologies)

### Pharmaceuticals & Healthcare
- LAURUSLABS (Laurus Labs)
- STRIDES (Strides Pharma)
- BIOCON (Biocon Limited)
- SYNGENE (Syngene International)

### Retail & Consumer Services
- TRENT (Trent Limited - Westside)
- SHOPERSTOP (Shoppers Stop)
- VEDANT (Vedant Fashions)

### Others
- JKCEMENT (JK Cement)
- CENTURYPLY (Century Plyboards)
- AIAENG (AIA Engineering)
- GRAPHITE (Graphite India)

**Full list**: ~100 stocks. Refer to NSE website for complete and updated list.

---

## How to Get Updated Lists

### Method 1: NSE Website Scraping
```python
import requests
from bs4 import BeautifulSoup

def fetch_nifty_constituents(index_name):
    """
    Fetch current constituents from NSE website
    index_name: 'NIFTY MIDCAP 100' or 'NIFTY SMALLCAP 100'
    """
    url = "https://www.nseindia.com/market-data/live-equity-market"
    headers = {
        'User-Agent': 'Mozilla/5.0',
        'Accept-Language': 'en-US,en;q=0.9',
    }

    # NSE requires proper headers to mimic browser
    response = requests.get(url, headers=headers)
    # Parse and extract constituent list
    # Implementation depends on NSE website structure
```

### Method 2: Use Cached Lists
Many financial data providers maintain updated lists:
- NSE India official indices page
- Moneycontrol.com indices section
- Economic Times Markets section
- Financial data APIs (if available)

### Method 3: Yahoo Finance Screening
Search for stocks with market cap ranges:
- Midcap: ₹5,000 Cr - ₹20,000 Cr
- Smallcap: ₹500 Cr - ₹5,000 Cr

---

## Important Notes

1. **Quarterly Rebalancing**: NSE rebalances these indices every quarter (March, June, September, December)

2. **Market Cap Criteria**:
   - Midcap: Between 101st and 250th rank by full market capitalization
   - Smallcap: Between 251st and 500th rank by full market capitalization

3. **Liquidity Requirement**: All constituents must meet minimum liquidity criteria (average daily traded value)

4. **Corporate Actions**: Stocks may be added/removed due to mergers, delistings, or changes in market cap rank

5. **Sector Distribution**: Both indices aim for balanced sector representation reflecting the overall market

---

## Using Constituents in Screening

When analyzing these indices:

1. **Sector Balance**: Ensure recommendations span multiple sectors
2. **Liquidity Check**: Verify trading volumes before recommending
3. **Recent Changes**: If a stock recently moved between indices, it may have momentum
4. **Index Heavyweights**: Larger constituents often have better liquidity but may be less undervalued
5. **Micro-caps within Smallcap**: Smallest stocks in Smallcap 100 carry higher risk
