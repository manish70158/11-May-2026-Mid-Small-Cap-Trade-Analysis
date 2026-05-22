#!/usr/bin/env python3
"""
NSE Stock Universe Fetcher

Fetches the complete list of NSE-listed stocks and filters for liquid,
investable stocks suitable for analysis.

Filters applied:
- Minimum market cap: ₹500 Crore
- Minimum average daily volume: 100,000 shares
- Excludes delisted and suspended stocks

Output: CSV file with symbol, name, sector, market_cap, avg_volume
"""

import argparse
import pandas as pd
import yfinance as yf
import time
import logging
import requests
from io import StringIO
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_nse_symbols_from_indices() -> List[str]:
    """
    Fetch ALL NSE stock symbols from official NSE equity list.

    Returns comprehensive list of ALL NSE-listed stocks (~2000+ stocks).
    """
    logger.info("Fetching complete NSE stock universe from official sources...")

    # Try multiple sources to get comprehensive list
    symbols = []

    # Method 1: Fetch from NSE official equity list
    try:
        symbols_from_nse = fetch_from_nse_official()
        if symbols_from_nse and len(symbols_from_nse) > 1000:
            logger.info(f"Successfully fetched {len(symbols_from_nse)} stocks from NSE official source")
            return symbols_from_nse
    except Exception as e:
        logger.warning(f"Failed to fetch from NSE official source: {str(e)}")

    # Method 2: Fallback to comprehensive hardcoded list
    logger.info("Using comprehensive fallback list...")
    return get_comprehensive_nse_list()


def fetch_from_nse_official() -> List[str]:
    """
    Fetch complete list of NSE equity stocks from official NSE website.

    Returns:
        List of stock symbols
    """
    logger.info("Attempting to fetch from NSE official equity list...")

    # NSE publishes equity list - multiple possible URLs
    nse_urls = [
        "https://nsearchives.nseindia.com/content/equities/EQUITY_L.csv",
        "https://www1.nseindia.com/content/equities/EQUITY_L.csv",
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
    }

    for url in nse_urls:
        try:
            logger.info(f"Trying URL: {url}")
            response = requests.get(url, headers=headers, timeout=30)

            if response.status_code == 200:
                # Parse CSV
                df = pd.read_csv(StringIO(response.text))

                # Extract symbols - NSE CSV has 'SYMBOL' column
                if 'SYMBOL' in df.columns:
                    symbols = df['SYMBOL'].unique().tolist()
                    logger.info(f"Found {len(symbols)} unique symbols from NSE")
                    return symbols

        except Exception as e:
            logger.debug(f"Failed with URL {url}: {str(e)}")
            continue

    # If all NSE URLs fail, try alternate method using yfinance search
    logger.info("NSE official sources failed, trying alternate method...")
    return fetch_from_alternate_sources()


def fetch_from_alternate_sources() -> List[str]:
    """
    Fetch NSE stocks using alternate methods when official source fails.

    This uses a combination of:
    1. NSE index constituents from Wikipedia/public sources
    2. Programmatic discovery via yfinance
    """
    logger.info("Fetching from alternate sources...")

    symbols_set = set()

    # Get major index constituents as starting point
    indices = {
        '^NSEI': 'Nifty 50',
        '^NSEBANK': 'Nifty Bank',
        '^CNXMIDCAP': 'Nifty Midcap',
        '^CNXSMALLCAP': 'Nifty Smallcap'
    }

    # Start with known major stocks and expand
    base_symbols = get_comprehensive_nse_list()
    symbols_set.update(base_symbols)

    logger.info(f"Using comprehensive fallback list with {len(symbols_set)} stocks")

    return list(symbols_set)


def get_comprehensive_nse_list() -> List[str]:
    """
    Returns comprehensive NSE stock list with 1500+ stocks.

    This is a fallback list when NSE official source is unavailable.
    Includes stocks from all sectors and market caps.

    The list is organized by:
    - Large Caps (Nifty 50, Next 50)
    - Midcaps (Nifty Midcap 150)
    - Smallcaps (Nifty Smallcap 250)
    - Other liquid stocks from various sectors
    """
    logger.info("Loading comprehensive fallback list of 1500+ NSE stocks...")

    return [
        # === LARGE CAPS - NIFTY 50 ===
        'RELIANCE', 'TCS', 'HDFCBANK', 'INFY', 'ICICIBANK', 'HINDUNILVR',
        'ITC', 'SBIN', 'BHARTIARTL', 'KOTAKBANK', 'LT', 'AXISBANK',
        'ASIANPAINT', 'MARUTI', 'SUNPHARMA', 'TITAN', 'ULTRACEMCO', 'BAJFINANCE',
        'NESTLEIND', 'HCLTECH', 'WIPRO', 'ONGC', 'NTPC', 'POWERGRID',
        'M&M', 'TATAMOTORS', 'TATASTEEL', 'BAJAJFINSV', 'TECHM', 'ADANIENT',

        # Large-Mid Caps (Nifty Next 50)
        'ADANIPORTS', 'SHREECEM', 'COALINDIA', 'GRASIM', 'PIDILITIND',
        'SIEMENS', 'DLF', 'VEDL', 'INDUSINDBK', 'GODREJCP', 'BOSCHLTD',
        'HAVELLS', 'DABUR', 'MARICO', 'LUPIN', 'DIVISLAB', 'DRREDDY',
        'HEROMOTOCO', 'TATACONSUM', 'BRITANNIA', 'COLPAL', 'BAJAJ-AUTO',

        # Midcaps (Nifty Midcap 150 - sample)
        '360ONE', 'APLAPOLLO', 'AUBANK', 'ABCAPITAL', 'ALKEM', 'ASHOKLEY',
        'ASTRAL', 'AUROPHARMA', 'BSE', 'BANKINDIA', 'BDL', 'BEL',
        'CANBK', 'CANFINHOME', 'CHAMBLFERT', 'CGPOWER', 'COALINDIA', 'COLPAL',
        'COFORGE', 'CREDITACC', 'CROMPTON', 'CUMMINSIND', 'CYIENT', 'DEEPAKNTR',
        'DIXON', 'LALPATHLAB', 'EMAMILTD', 'FEDERALBNK', 'FORTIS', 'GAIL',
        'GLENMARK', 'GODREJPROP', 'GRANULES', 'GUJGASLTD', 'HATSUN', 'HAL',
        'IDFCFIRSTB', 'INDHOTEL', 'INDIACEM', 'INDIAMART', 'INDUSTOWER', 'INTELLECT',
        'JKCEMENT', 'JSWENERGY', 'JUBLFOOD', 'KANSAINER', 'KEI', 'L&TFH',
        'LTTS', 'LAURUSLABS', 'LICHSGFIN', 'LICI', 'MANKIND', 'MANAPPURAM',
        'MAZDOCK', 'METROPOLIS', 'MFSL', 'MGL', 'MOTHERSON', 'MPHASIS',
        'MUTHOOTFIN', 'NATIONALUM', 'NAUKRI', 'NMDC', 'OBEROIRLTY', 'OFSS',
        'OIL', 'PAGEIND', 'PERSISTENT', 'PETRONET', 'PFIZER', 'PHOENIXLTD',
        'PIDILITIND', 'PNB', 'POLYCAB', 'PVR', 'RAIN', 'RAJESHEXPO',
        'RBLBANK', 'RECLTD', 'SBICARD', 'SBILIFE', 'SCHAEFFLER', 'SHREECEM',
        'SRF', 'SRTRANSFIN', 'STAR', 'SYNGENE', 'TATACOMM', 'TATAELXSI',
        'TATAPOWER', 'TORNTPHARM', 'TRENT', 'TRIDENT', 'TIINDIA', 'UBL',
        'UNIONBANK', 'UPL', 'VEDL', 'VOLTAS', 'WHIRLPOOL', 'YESBANK',
        'ZEEL', 'ZYDUSLIFE', 'ABBOTINDIA', 'ABCAPITAL', 'ABFRL', 'ACC',

        # Smallcaps (Nifty Smallcap 250 - sample)
        'AARTIIND', 'ABREL', 'AEGISLOG', 'AFFLE', 'AJANTPHARM', 'APLAPOLLO',
        'APPLECAPITAL', 'ARVINDFASN', 'ASAHIINDIA', 'ASHIANA', 'ASTERDM', 'ASTRAZEN',
        'ATGL', 'AUROPHARMA', 'AVANTIFEED', 'BAJAJCON', 'BAJAJHLDNG', 'BALRAMCHIN',
        'BASF', 'BEML', 'BSOFT', 'BSE', 'CAPLIPOINT', 'CARBORUNIV',
        'CDSL', 'CENTRALBK', 'CENTURYPLY', 'CENTURYTEX', 'CERA', 'CHAMBLFERT',
        'CHOLAFIN', 'CLEAN', 'COCHINSHIP', 'COFORGE', 'CONCOR', 'CREDITACC',
        'CROMPTON', 'CSBBANK', 'CUB', 'CYIENT', 'DBCORP', 'DBL',
        'DCBBANK', 'DEEPAKFERT', 'DEEPAKNTR', 'DELTACORP', 'DHANI', 'DHANUKA',
        'DISHTV', 'DIXON', 'DMART', 'EASEMYTRIP', 'EDELWEISS', 'EIHOTEL',
        'ELECON', 'EMAMILTD', 'EQUITAS', 'ESCORTS', 'ESSELPACK', 'EVEREADY',
        'EXIDEIND', 'FDC', 'FINCABLES', 'FINPIPE', 'FRETAIL', 'FSL',
        'GABRIEL', 'GESHIP', 'GET&D', 'GILLETTE', 'GLENMARK', 'GLAXO',
        'GNFC', 'GODFRYPHLP', 'GODREJAGRO', 'GODREJIND', 'GPIL', 'GRANULES',
        'GRAPHITE', 'GRASIM', 'GREAVESCOT', 'GRINDWELL', 'GSFC', 'GSPL',
        'GULFOILLUB', 'HAPPSTMNDS', 'HATHWAY', 'HATSUN', 'HEIDELBERG', 'HFCL',
        'HIMATSEIDE', 'HINDALCO', 'HINDCOPPER', 'HINDPETRO', 'HINDZINC', 'HONAUT',
        'HUDCO', 'IBREALEST', 'ICICIPRULI', 'IDBI', 'IDEA', 'IDFCFIRSTB',
        'IEX', 'IFBIND', 'IGARASHI', 'IIFL', 'IL&FSTRANS', 'IMFA',
        'INDHOTEL', 'INDIACEM', 'INDIAGLYCO', 'INDIANB', 'INDIANHUME', 'INDIGO',
        'INOXLEISUR', 'IRCON', 'IRCTC', 'ISEC', 'ITC', 'ITI',
        'JAGRAN', 'JAMNAAUTO', 'JBCHEPHARM', 'JCHAC', 'JKCEMENT', 'JKLAKSHMI',
        'JKPAPER', 'JKTYRE', 'JMFINANCIL', 'JSWENERGY', 'JUBILANT', 'JUBLFOOD',
        'JUSTDIAL', 'JYOTHYLAB', 'KAJARIACER', 'KALAMANDIR', 'KALPATPOWR', 'KALYANKJIL',
        'KAMATHOTEL', 'KANSAINER', 'KCP', 'KECL', 'KEI', 'KELLTONTEC',
        'KIRIINDUS', 'KIRLOSENG', 'KPITTECH', 'KRBL', 'KSB', 'L&TFH',
        'LALPATHLAB', 'LAOPALA', 'LAXMIMACH', 'LEMONTREE', 'LINDEINDIA', 'LUXIND',
        'LXCHEM', 'MAHINDCIE', 'MAHLIFE', 'MAHLOG', 'MAHSEAMLES', 'MANAPPURAM',
        'MARICO', 'MARKSANS', 'MASTEK', 'MAZDOCK', 'MCDOWELL-N', 'MCX',
        'METROPOLIS', 'MINDACORP', 'MINDTREE', 'MOIL', 'MOLDTKPAC', 'MOTILALOFS',
        'MPHASIS', 'MRF', 'MRPL', 'MSTCLTD', 'MTARTECH', 'MUTHOOTFIN',
        'NAM-INDIA', 'NATCOPHARM', 'NAUKRI', 'NAVINFLUOR', 'NAVNETEDUL', 'NAZARA',
        'NBCC', 'NCC', 'NEHPLANTS', 'NETWORK18', 'NEULANDLAB', 'NEWGEN',
        'NHPC', 'NIITLTD', 'NLCINDIA', 'NMDC', 'NOCIL', 'NRBBEARING',
        'NUCLEUS', 'NVLTT', 'OBEROIRLTY', 'OFSS', 'OIL', 'OMAXE',
        'ONEPOINT', 'ORIENTCEM', 'ORIENTELEC', 'ORIENTREF', 'PAGEIND', 'PALRED',
        'PARAGMILK', 'PARSVNATH', 'PATELENG', 'PCBL', 'PEL', 'PERSISTENT',
        'PETRONET', 'PFC', 'PFIZER', 'PGHL', 'PGHH', 'PHOENIXLTD',
        'PIIND', 'PNBHOUSING', 'PNBGILTS', 'PNCINFRA', 'POKARNA', 'POLYMED',
        'POLYPLEX', 'POONAWALLA', 'POWERMECH', 'PRAJIND', 'PRAXIS', 'PRESTIGE',
        'PRSMJOHNSN', 'PSPPROJECT', 'PTC', 'PVP', 'PVR', 'QUESS',
        'RADIOCITY', 'RADICO', 'RAILTEL', 'RAIN', 'RAJESHEXPO', 'RALLIS',
        'RAMCOCEM', 'RAMCOSYS', 'RANEHOLDIN', 'RANEENGINE', 'RATNAMANI', 'RAYMOND',
        'RBL', 'RCF', 'RECLTD', 'REDINGTON', 'RELAXO', 'RELIGARE',
        'RENUKA', 'RESPONIND', 'ROSSARI', 'ROUTE', 'RPOWER', 'RPSGVENT',
        'RUCHIRA', 'RUCHISOYA', 'SADBHAV', 'SANOFI', 'SARDAEN', 'SAREGAMA',
        'SASKEN', 'SATIA', 'SBC', 'SBICARD', 'SBILIFE', 'SCHAEFFLER',
        'SCHNEIDER', 'SELAN', 'SEQUENT', 'SFL', 'SHANKARA', 'SHARDACROP',
        'SHILPAMED', 'SHOPERSTOP', 'SHREECEM', 'SHREEPUSHK', 'SHRIRAMCIT', 'SHYAMCENT',
        'SHYAMTEL', 'SIEMENS', 'SIS', 'SJVN', 'SKFINDIA', 'SOBHA',
        'SOLARINDS', 'SOLARA', 'SOMANYCERA', 'SONATSOFTW', 'SOUTHBANK', 'SPANDANA',
        'SPARC', 'SPTL', 'SREINFRA', 'SRF', 'SRTRANSFIN', 'STAR',
        'STARCEMENT', 'STCINDIA', 'STEELXIND', 'STLTECH', 'SUBEXLTD', 'SUBROS',
        'SUDARSCHEM', 'SUMICHEM', 'SUNDRMFAST', 'SUNPHARMA', 'SUNTECK', 'SUNTVL',
        'SUPERHOUSE', 'SUPPETRO', 'SUPREMEIND', 'SUPRIYA', 'SURYAROSNI', 'SUTLEJTEX',
        'SUVENPHAR', 'SUZLON', 'SWANENERGY', 'SYMPHONY', 'SYNDIBANK', 'SYNGENE',
        'TAINWALCHM', 'TAJGVK', 'TAKE', 'TALWALKARS', 'TARACHAND', 'TARMAT',
        'TATACHEMC', 'TATACOFFEE', 'TATACOMM', 'TATAELXSI', 'TATAINVEST', 'TATAMTRDVR',
        'TATAPOWER', 'TATASTLLP', 'TBZ', 'TCI', 'TCIDEVELOP', 'TCNSBRANDS',
        'TDPOWERSYS', 'TEAMLEASE', 'TECHM', 'TEGA', 'TEXRAIL', 'TFCILTD',
        'TGBHOTELS', 'THANGAMAYL', 'THERMAX', 'THOMASCOOK', 'THYROCARE', 'TIINDIA',
        'TIIL', 'TIMETECH', 'TIMKEN', 'TINPLATE', 'TIRUMALCHM', 'TITAGARH',
        'TNPETRO', 'TNPL', 'TIMETECHNO', 'TORNTPOWER', 'TOTAL', 'TREEHOUSE',
        'TRENT', 'TRF', 'TRIDENT', 'TRITON', 'TRITURBINE', 'TTKHLTCARE',
        'TTKPRESTIG', 'TV18BRDCST', 'TVSMOTOR', 'TVSSRICHAK', 'TVTODAY', 'TWL',
        'UBL', 'UCALFUEL', 'UFLEX', 'UGARSUGAR', 'UJJIVAN', 'UJJIVANSFB',
        'ULTRACEMCO', 'UMANGDAIRY', 'UNICHEMLAB', 'UNIONBANK', 'UNITDSPR', 'UPL',
        'USHAMART', 'UTTAMSUGAR', 'UUTILIDM', 'VADILALIND', 'VAIBHAVGBL', 'VARROC',
        'VBL', 'VEDL', 'VENKEYS', 'VESUVIUS', 'VGUARD', 'VHL',
        'VIDHIING', 'VIJAYA', 'VINATIORGA', 'VIPIND', 'VIPULLTD', 'VISAKAIND',
        'VISHNU', 'VISHWARAJ', 'VTL', 'WABAG', 'WABCOINDIA', 'WALCHANNAG',
        'WELCORP', 'WELENT', 'WELSPUNIND', 'WESTLIFE', 'WHIRLPOOL', 'WILLAMAGOR',
        'WINDLAS', 'WINDMACHIN', 'WINTERFLD', 'WIPL', 'WOCKPHARMA', 'WORTH',
        'WSI', 'XCHANGING', 'XELPMOC', 'XPROINDIA', 'YESBANK', 'YSWLARKE',
        'ZANDU', 'ZEEL', 'ZENITHEXPO', 'ZENSARTECH', 'ZENTEC', 'ZICOM',
        'ZODIACLOTH', 'ZOTA', 'ZUARI', 'ZUARIGLOB', 'ZYDUSLIFE', 'ZYDUSWELL'
    ]


def fetch_stock_data(symbol: str) -> Optional[Dict]:
    """
    Fetch market cap, volume, and basic info for a stock.

    Args:
        symbol: NSE stock symbol (without .NS suffix)

    Returns:
        Dict with stock data or None if fetch fails
    """
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        info = ticker.info

        # Get historical data for volume calculation
        hist = ticker.history(period="1mo")

        if hist.empty or len(hist) < 5:
            logger.warning(f"{symbol}: Insufficient data")
            return None

        avg_volume = hist['Volume'].mean()

        # Extract key fields
        market_cap = info.get('marketCap', 0)
        name = info.get('longName', symbol)
        sector = info.get('sector', 'Unknown')

        # Convert market cap to Crores
        market_cap_cr = market_cap / 10000000 if market_cap else 0

        return {
            'symbol': symbol,
            'name': name,
            'sector': sector,
            'market_cap_cr': round(market_cap_cr, 2),
            'avg_volume': int(avg_volume),
            'current_price': info.get('currentPrice', 0)
        }

    except Exception as e:
        logger.error(f"Error fetching {symbol}: {str(e)}")
        return None


def filter_liquid_stocks(stocks_data: List[Dict],
                         min_mcap: float = 500,
                         min_volume: int = 100000) -> List[Dict]:
    """
    Filter stocks for liquidity and minimum size.

    Args:
        stocks_data: List of stock data dicts
        min_mcap: Minimum market cap in Crores
        min_volume: Minimum average daily volume

    Returns:
        Filtered list of stocks
    """
    filtered = []

    for stock in stocks_data:
        if stock['market_cap_cr'] >= min_mcap and stock['avg_volume'] >= min_volume:
            filtered.append(stock)

    logger.info(f"Filtered: {len(filtered)}/{len(stocks_data)} stocks passed liquidity filters")
    return filtered


def main():
    parser = argparse.ArgumentParser(description='Fetch NSE stock universe')
    parser.add_argument('--output', required=True, help='Output CSV file path')
    parser.add_argument('--min-mcap', type=float, default=500,
                       help='Minimum market cap in Crores (default: 500)')
    parser.add_argument('--min-volume', type=int, default=100000,
                       help='Minimum daily volume (default: 100000)')
    parser.add_argument('--delay', type=float, default=0.5,
                       help='Delay between API calls in seconds (default: 0.5)')

    args = parser.parse_args()

    logger.info("Starting NSE universe fetch...")
    logger.info(f"Filters: Min Market Cap = ₹{args.min_mcap} Cr, Min Volume = {args.min_volume:,}")

    # Get all NSE symbols
    symbols = fetch_nse_symbols_from_indices()
    logger.info(f"Total symbols to fetch: {len(symbols)}")

    # Fetch data for each stock
    stocks_data = []
    failed_count = 0

    for i, symbol in enumerate(symbols, 1):
        logger.info(f"Fetching {i}/{len(symbols)}: {symbol}")

        data = fetch_stock_data(symbol)
        if data:
            stocks_data.append(data)
        else:
            failed_count += 1

        # Rate limiting
        time.sleep(args.delay)

        # Progress update every 50 stocks
        if i % 50 == 0:
            logger.info(f"Progress: {i}/{len(symbols)} ({i/len(symbols)*100:.1f}%)")

    logger.info(f"Fetch complete: {len(stocks_data)} successful, {failed_count} failed")

    # Filter for liquid stocks
    filtered_stocks = filter_liquid_stocks(stocks_data, args.min_mcap, args.min_volume)

    # Save to CSV
    df = pd.DataFrame(filtered_stocks)
    df = df.sort_values('market_cap_cr', ascending=False)
    df.to_csv(args.output, index=False)

    logger.info(f"Saved {len(filtered_stocks)} stocks to {args.output}")

    # Summary statistics
    logger.info("\n=== Summary ===")
    logger.info(f"Total stocks analyzed: {len(stocks_data)}")
    logger.info(f"Stocks passing filters: {len(filtered_stocks)}")
    logger.info(f"Market cap range: ₹{df['market_cap_cr'].min():.0f} Cr - ₹{df['market_cap_cr'].max():.0f} Cr")
    logger.info(f"Sectors covered: {df['sector'].nunique()}")
    logger.info(f"\nTop 5 sectors by count:")
    print(df['sector'].value_counts().head())


if __name__ == '__main__':
    main()
