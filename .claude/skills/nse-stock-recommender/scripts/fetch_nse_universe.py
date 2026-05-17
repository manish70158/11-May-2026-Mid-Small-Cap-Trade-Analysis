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
from datetime import datetime, timedelta
from typing import List, Dict, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def fetch_nse_symbols_from_indices() -> List[str]:
    """
    Fetch NSE stock symbols from major indices.

    Returns comprehensive list from Nifty 50, Next 50, Midcap 150, Smallcap 250
    to cover ~2000 stocks.
    """
    # Major indices constituent lists
    # In production, these should be fetched from NSE website or APIs
    # For now, using Yahoo Finance screening approach

    logger.info("Fetching NSE stock universe...")

    # We'll use a comprehensive approach: fetch from major indices
    # Nifty 50, Nifty Next 50, Nifty Midcap 150, Nifty Smallcap 250
    # This gives us ~500 well-covered stocks

    # For a truly comprehensive list, we'd scrape NSE website or use paid APIs
    # Alternative: Use a pre-compiled list of NSE stocks

    symbols = []

    # Approach: Use Yahoo Finance screener to get NSE stocks
    # This is a practical workaround since NSE doesn't offer free API

    logger.info("Loading known NSE stock universe...")

    # Load from a comprehensive list (should be maintained separately)
    # For demonstration, returning a subset that can be expanded

    # In production, maintain a CSV file with all NSE symbols updated quarterly
    # or scrape from: https://www.nseindia.com/market-data/securities-available-for-trading

    return get_comprehensive_nse_list()


def get_comprehensive_nse_list() -> List[str]:
    """
    Returns comprehensive NSE stock list.

    In production, this should:
    1. Read from maintained CSV file of all NSE stocks
    2. Or scrape from NSE website
    3. Or use paid data provider API

    For now, returns major liquid stocks across market caps.
    """
    # This list should be maintained and updated quarterly
    # Including major stocks from all sectors and market caps

    return [
        # Large Caps (Nifty 50)
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
