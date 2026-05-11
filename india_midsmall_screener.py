#!/usr/bin/env python3
"""
India Midcap & Smallcap Stock Screener
Identifies undervalued stocks with 2x potential in 6-12 months

Enhanced with Order Book Analysis for Capital Goods, Infrastructure, and Manufacturing sectors
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import re
import warnings
warnings.filterwarnings('ignore')

# Sectors where order book analysis is relevant
ORDER_BOOK_RELEVANT_SECTORS = [
    'Industrials', 'Infrastructure', 'Capital Goods', 'Engineering',
    'Construction', 'Electrical Equipment', 'Heavy Engineering',
    'Defense', 'Aerospace', 'Shipbuilding'
]

# Nifty Midcap 100 constituents (Complete list)
NIFTY_MIDCAP_100 = [
    'ADANIENT', 'ADANIPORTS', 'AMBUJACEM', 'APOLLOHOSP', 'ASHOKLEY', 'ASIANPAINT',
    'ASTRAL', 'AUROPHARMA', 'BAJAJFINSV', 'BAJAJHLDNG', 'BALKRISIND', 'BANDHANBNK',
    'BATAINDIA', 'BEL', 'BERGEPAINT', 'BHARATFORG', 'BHEL', 'BIOCON', 'BOSCHLTD',
    'CANBK', 'CHOLAFIN', 'CIPLA', 'COALINDIA', 'COLPAL', 'CONCOR', 'COROMANDEL',
    'CUMMINSIND', 'DABUR', 'DALBHARAT', 'DEEPAKNTR', 'DIVISLAB', 'DLF', 'ESCORTS',
    'EXIDEIND', 'FEDERALBNK', 'GAIL', 'GLENMARK', 'GODREJCP', 'GODREJPROP', 'GRASIM',
    'GUJGASLTD', 'HAL', 'HAVELLS', 'HCLTECH', 'HINDPETRO', 'HINDUNILVR', 'ICICIBANK',
    'ICICIPRULI', 'IDEA', 'IDFCFIRSTB', 'INDHOTEL', 'INDIAMART', 'INDIGO', 'INDUSTOWER',
    'INTELLECT', 'IOC', 'JINDALSTEL', 'JKCEMENT', 'JUBLFOOD', 'KOTAKBANK', 'L&TFH',
    'LICHSGFIN', 'LUPIN', 'M&M', 'M&MFIN', 'MANAPPURAM', 'MARICO', 'MCDOWELL-N',
    'MFSL', 'MGL', 'MOTHERSON', 'MPHASIS', 'MRF', 'MUTHOOTFIN', 'NAUKRI', 'NMDC',
    'NTPC', 'OBEROIRLTY', 'OFSS', 'OIL', 'PAGEIND', 'PERSISTENT', 'PETRONET', 'PFC',
    'PIDILITIND', 'PIIND', 'PNB', 'POLYCAB', 'POWERGRID', 'RECLTD', 'SBICARD',
    'SBILIFE', 'SHREECEM', 'SIEMENS', 'SRF', 'SRTRANSFIN', 'SUNPHARMA', 'SUNTV',
    'TATACOMM', 'TATACONSUM', 'TATAMOTORS', 'TATAPOWER', 'TATASTEEL', 'TCS', 'TECHM',
    'TITAN', 'TORNTPHARM', 'TRENT', 'TVSMOTOR', 'UBL', 'ULTRACEMCO', 'UPL', 'VEDL',
    'VOLTAS', 'WIPRO', 'ZEEL'
]

# Nifty Smallcap 100 constituents (Complete list)
NIFTY_SMALLCAP_100 = [
    'AARTIIND', 'ABBOTINDIA', 'ABCAPITAL', 'ABFRL', 'ACC', 'ADANIGREEN', 'ADANIPOWER',
    'ADANITRANS', 'AFFLE', 'AJANTPHARM', 'ALKEM', 'AMARAJABAT', 'AMBUJACEM', 'ANGELONE',
    'APARINDS', 'APLAPOLLO', 'APLLTD', 'APOLLOTYRE', 'ASHOKLEY', 'ASIANPAINT', 'ASTERDM',
    'ASTRAL', 'ATUL', 'AUBANK', 'AUROPHARMA', 'BAJAJCON', 'BAJAJHLDNG', 'BAJFINANCE',
    'BALKRISIND', 'BALRAMCHIN', 'BANDHANBNK', 'BANKBARODA', 'BASF', 'BATAINDIA', 'BEL',
    'BERGEPAINT', 'BHARATFORG', 'BHARTIARTL', 'BHEL', 'BIOCON', 'BIRLACORPN', 'BLUESTARCO',
    'BOSCHLTD', 'BPCL', 'BRITANNIA', 'CANFINHOME', 'CARBORUNIV', 'CASTROLIND', 'CEATLTD',
    'CENTURYPLY', 'CENTURYTEX', 'CERA', 'CHAMBLFERT', 'CHOLAFIN', 'CIEINDIA', 'CIPLA',
    'COALINDIA', 'COFORGE', 'COLPAL', 'CONCOR', 'COROMANDEL', 'CREDITACC', 'CROMPTON',
    'CUMMINSIND', 'DABUR', 'DALBHARAT', 'DEEPAKNTR', 'DELTACORP', 'DHANI', 'DIVISLAB',
    'DIXON', 'DLF', 'DRREDDY', 'EICHERMOT', 'ELGIEQUIP', 'EMAMILTD', 'ENDURANCE',
    'EQUITAS', 'ESCORTS', 'EXIDEIND', 'FEDERALBNK', 'FINEORG', 'GAIL', 'GILLETTE',
    'GLAXO', 'GLENMARK', 'GMRINFRA', 'GNFC', 'GODFRYPHLP', 'GODREJCP', 'GODREJPROP',
    'GRANULES', 'GRASIM', 'GRINDWELL', 'GSPL', 'GUJGASLTD', 'GULFOILLUB', 'HAL'
]

class StockScreener:
    def __init__(self):
        self.stocks_data = []
        self.filtered_stocks = []

    def fetch_stock_data(self, symbol):
        """Fetch comprehensive data for a stock"""
        try:
            ticker = yf.Ticker(f"{symbol}.NS")
            info = ticker.info
            hist = ticker.history(period="1y")

            if hist.empty or len(hist) < 50:
                return None

            # Calculate technical indicators
            current_price = hist['Close'].iloc[-1]
            high_52w = hist['High'].max()
            low_52w = hist['Low'].min()
            price_to_52w_high = (current_price / high_52w) * 100

            # Calculate RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50

            # Volume analysis
            avg_volume = hist['Volume'].mean()

            # Calculate beta (simplified)
            returns = hist['Close'].pct_change().dropna()
            beta = returns.std() / 0.02 if len(returns) > 0 else 1.0  # Approximate

            # Calculate max drawdown
            cumulative = (1 + returns).cumprod()
            running_max = cumulative.cummax()
            drawdown = (cumulative - running_max) / running_max
            max_drawdown = abs(drawdown.min() * 100) if len(drawdown) > 0 else 0

            # Get revenue for order book calculation
            total_revenue = info.get('totalRevenue', 0)

            data = {
                'symbol': symbol,
                'name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown'),

                # Price data
                'current_price': current_price,
                'high_52w': high_52w,
                'low_52w': low_52w,
                'price_to_52w_high': price_to_52w_high,

                # Valuation metrics
                'market_cap': info.get('marketCap', 0) / 10000000,  # In Crores
                'pe_ratio': info.get('trailingPE', None),
                'forward_pe': info.get('forwardPE', None),
                'pb_ratio': info.get('priceToBook', None),
                'peg_ratio': info.get('pegRatio', None),

                # Profitability
                'roe': info.get('returnOnEquity', 0) * 100 if info.get('returnOnEquity') else None,
                'profit_margin': info.get('profitMargins', 0) * 100 if info.get('profitMargins') else None,

                # Growth metrics
                'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else None,
                'earnings_growth': info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else None,
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 0) * 100 if info.get('earningsQuarterlyGrowth') else None,

                # Financial health
                'debt_to_equity': info.get('debtToEquity', None),
                'current_ratio': info.get('currentRatio', None),
                'quick_ratio': info.get('quickRatio', None),

                # Technical indicators
                'rsi': current_rsi,
                'beta': beta,
                'max_drawdown': max_drawdown,
                'avg_volume': avg_volume,

                # Other
                'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,

                # Revenue for order book analysis
                'total_revenue': total_revenue,
            }

            # Fetch and add order book data
            order_book_data = self.fetch_order_book_data(symbol, data['sector'], data['industry'], total_revenue, info)
            data.update(order_book_data)

            return data

        except Exception as e:
            print(f"Error fetching {symbol}: {str(e)}")
            return None

    def fetch_order_book_data(self, symbol, sector, industry, total_revenue, info):
        """
        Fetch or estimate order book data for the company.

        Order book is particularly relevant for:
        - Capital goods companies
        - Infrastructure companies
        - Defense/Aerospace
        - Heavy engineering
        - Construction companies

        Returns order book metrics including:
        - order_book_value (in Crores)
        - order_book_to_revenue_ratio
        - order_book_visibility (months of revenue)
        - has_order_book_data (boolean)
        """
        order_book_data = {
            'order_book_value': None,
            'order_book_to_revenue_ratio': None,
            'order_book_visibility_months': None,
            'has_order_book_data': False,
            'order_book_relevant': False
        }

        # Check if order book is relevant for this sector
        is_relevant = any(keyword in sector for keyword in ORDER_BOOK_RELEVANT_SECTORS) or \
                     any(keyword in industry for keyword in ORDER_BOOK_RELEVANT_SECTORS)

        order_book_data['order_book_relevant'] = is_relevant

        if not is_relevant:
            return order_book_data

        # Try to estimate order book from business description or use industry benchmarks
        try:
            # Method 1: Check business summary for order book mentions
            business_summary = info.get('longBusinessSummary', '')

            # Look for order book mentions in text
            order_book_pattern = r'order\s+book[s]?\s+(?:of|worth|at|around)?\s*(?:Rs\.?|₹|INR)?\s*([0-9,]+(?:\.[0-9]+)?)\s*(crore|billion|lakh|thousand)?'
            match = re.search(order_book_pattern, business_summary, re.IGNORECASE)

            if match:
                value_str = match.group(1).replace(',', '')
                value = float(value_str)
                unit = match.group(2).lower() if match.group(2) else 'crore'

                # Convert to crores
                if unit == 'billion':
                    value = value * 1000  # Assuming INR billion
                elif unit == 'lakh':
                    value = value / 100
                elif unit == 'thousand':
                    value = value / 10000

                order_book_data['order_book_value'] = value
                order_book_data['has_order_book_data'] = True

                # Calculate ratios
                if total_revenue and total_revenue > 0:
                    revenue_crores = total_revenue / 10000000  # Convert to crores
                    if revenue_crores > 0:
                        order_book_data['order_book_to_revenue_ratio'] = value / revenue_crores
                        order_book_data['order_book_visibility_months'] = (value / revenue_crores) * 12

            # Method 2: Industry benchmark estimation (if no direct data found)
            if not order_book_data['has_order_book_data'] and total_revenue > 0:
                revenue_crores = total_revenue / 10000000

                # Use conservative industry benchmarks for order book to revenue ratio
                industry_benchmarks = {
                    'defense': 3.0,  # Defense companies typically have 3+ years of order book
                    'aerospace': 2.5,
                    'infrastructure': 2.0,
                    'capital goods': 1.5,
                    'engineering': 1.2,
                    'construction': 1.5,
                    'electrical equipment': 1.0,
                    'heavy engineering': 1.8
                }

                # Find matching benchmark
                benchmark_ratio = None
                for key, ratio in industry_benchmarks.items():
                    if key in industry.lower() or key in sector.lower():
                        benchmark_ratio = ratio
                        break

                # If we have revenue growth, adjust the estimate
                if benchmark_ratio and revenue_crores > 0:
                    # Estimate order book as benchmark ratio * revenue
                    estimated_order_book = revenue_crores * benchmark_ratio
                    order_book_data['order_book_value'] = estimated_order_book
                    order_book_data['order_book_to_revenue_ratio'] = benchmark_ratio
                    order_book_data['order_book_visibility_months'] = benchmark_ratio * 12
                    order_book_data['has_order_book_data'] = True
                    order_book_data['is_estimated'] = True

        except Exception as e:
            # If order book fetching fails, just return empty data
            pass

        return order_book_data

    def calculate_sector_avg_pe(self, stocks_data):
        """Calculate average P/E by sector"""
        sector_pe = {}
        for stock in stocks_data:
            sector = stock.get('sector', 'Unknown')
            pe = stock.get('pe_ratio')
            if sector and pe and pe > 0:
                if sector not in sector_pe:
                    sector_pe[sector] = []
                sector_pe[sector].append(pe)

        return {sector: np.mean(pes) for sector, pes in sector_pe.items()}

    def apply_valuation_filters(self, stock, sector_avg_pe):
        """Stage 1: Valuation filters"""
        score = 0
        reasons = []

        # Check minimum data requirements
        if not stock.get('pe_ratio') or stock['pe_ratio'] <= 0:
            return None, []

        # 1. P/E Analysis (10 points max)
        sector = stock.get('sector', 'Unknown')
        sector_pe = sector_avg_pe.get(sector, stock['pe_ratio'] * 1.5)

        if stock['pe_ratio'] > 0 and sector_pe > 0:
            pe_discount = ((sector_pe - stock['pe_ratio']) / sector_pe) * 100
            if pe_discount >= 20:
                pe_score = min(10, pe_discount / 5)
                score += pe_score
                reasons.append(f"P/E {pe_discount:.1f}% below sector ({stock['pe_ratio']:.1f} vs {sector_pe:.1f})")
            elif stock['pe_ratio'] < 5:
                return None, []  # Possible value trap

        # 2. P/B and ROE Analysis (10 points max)
        pb = stock.get('pb_ratio')
        roe = stock.get('roe')
        if pb and roe and pb < 3 and roe > 15:
            pb_roe_score = min(10, (roe / 15) * (3 - pb) / 3 * 10)
            score += pb_roe_score
            reasons.append(f"Strong P/B-ROE combo (P/B: {pb:.2f}, ROE: {roe:.1f}%)")

        # 3. PEG Ratio (10 points max)
        peg = stock.get('peg_ratio')
        if peg and peg > 0 and peg < 1:
            peg_score = min(10, (1 - peg) * 20)
            score += peg_score
            reasons.append(f"Attractive PEG ratio: {peg:.2f}")

        # 4. Price to 52-week high (bonus if in sweet spot)
        price_pct = stock.get('price_to_52w_high', 100)
        if 60 <= price_pct <= 85:
            reasons.append(f"Corrected {100-price_pct:.1f}% from 52W high")

        return score if score >= 10 else None, reasons

    def apply_growth_filters(self, stock):
        """Stage 2: Growth potential assessment"""
        score = 0
        reasons = []

        # 1. Historical Growth (15 points max)
        rev_growth = stock.get('revenue_growth', 0)
        earnings_growth = stock.get('earnings_growth', 0)

        if rev_growth and rev_growth > 20:
            growth_score = min(7, rev_growth / 5)
            score += growth_score
            reasons.append(f"Revenue growth: {rev_growth:.1f}%")

        if earnings_growth and earnings_growth > 25:
            eg_score = min(8, earnings_growth / 5)
            score += eg_score
            reasons.append(f"Earnings growth: {earnings_growth:.1f}%")

        # 2. Momentum (10 points max)
        rsi = stock.get('rsi', 50)
        if 40 <= rsi <= 60:
            score += 5
            reasons.append(f"Balanced RSI: {rsi:.1f}")
        elif 35 <= rsi <= 70:
            score += 3

        # Volume check
        avg_vol = stock.get('avg_volume', 0)
        if avg_vol > 500000:
            score += 5
            reasons.append("Strong liquidity")
        elif avg_vol > 200000:
            score += 3

        # 3. Business Quality (15 points max)
        profit_margin = stock.get('profit_margin')
        if profit_margin and profit_margin > 10:
            margin_score = min(8, profit_margin / 2)
            score += margin_score
            reasons.append(f"Profit margin: {profit_margin:.1f}%")

        roe = stock.get('roe')
        if roe and roe > 15:
            roe_score = min(7, roe / 3)
            score += roe_score

        # 4. Order Book Analysis (BONUS: up to 8 additional points)
        # This provides revenue visibility for capital goods/infrastructure companies
        if stock.get('order_book_relevant') and stock.get('has_order_book_data'):
            ob_ratio = stock.get('order_book_to_revenue_ratio', 0)
            ob_months = stock.get('order_book_visibility_months', 0)

            if ob_ratio and ob_ratio > 0:
                # Strong order book (>2x revenue = 24+ months visibility)
                if ob_ratio >= 2.0:
                    order_book_score = 8
                    score += order_book_score
                    reasons.append(f"Excellent order book: {ob_ratio:.1f}x revenue ({ob_months:.0f} months)")
                # Good order book (1.5-2x revenue = 18-24 months)
                elif ob_ratio >= 1.5:
                    order_book_score = 6
                    score += order_book_score
                    reasons.append(f"Strong order book: {ob_ratio:.1f}x revenue ({ob_months:.0f} months)")
                # Decent order book (1-1.5x revenue = 12-18 months)
                elif ob_ratio >= 1.0:
                    order_book_score = 4
                    score += order_book_score
                    reasons.append(f"Good order book: {ob_ratio:.1f}x revenue ({ob_months:.0f} months)")
                # Moderate order book (0.5-1x revenue = 6-12 months)
                elif ob_ratio >= 0.5:
                    order_book_score = 2
                    score += order_book_score
                    reasons.append(f"Moderate order book: {ob_ratio:.1f}x revenue ({ob_months:.0f} months)")

        return score, reasons

    def apply_risk_filters(self, stock):
        """Stage 3: Risk assessment"""
        score = 30  # Start with full points, deduct for risks
        risks = []

        # 1. Financial Health (10 points)
        debt_to_equity = stock.get('debt_to_equity')
        if debt_to_equity is not None:
            if debt_to_equity > 100:  # > 1.0
                score -= 5
                risks.append(f"High debt-to-equity: {debt_to_equity/100:.2f}")
            elif debt_to_equity > 50:
                score -= 2

        current_ratio = stock.get('current_ratio')
        if current_ratio and current_ratio < 1.2:
            score -= 3
            risks.append(f"Low current ratio: {current_ratio:.2f}")

        # 2. Liquidity Risk (10 points)
        market_cap = stock.get('market_cap', 0)
        avg_volume = stock.get('avg_volume', 0)

        if market_cap < 1000:
            score -= 5
            risks.append(f"Low market cap: ₹{market_cap:.0f} Cr")

        if avg_volume < 200000:
            score -= 5
            risks.append("Low trading volume")

        # 3. Volatility (10 points)
        beta = stock.get('beta', 1.0)
        if beta > 1.5:
            score -= 3
            risks.append(f"High beta: {beta:.2f}")
        elif beta < 0.8:
            score -= 2

        max_drawdown = stock.get('max_drawdown', 0)
        if max_drawdown > 40:
            score -= 4
            risks.append(f"High max drawdown: {max_drawdown:.1f}%")
        elif max_drawdown > 30:
            score -= 2

        return max(0, score), risks

    def screen_stocks(self, symbols, index_name):
        """Main screening function"""
        print(f"\n{'='*80}")
        print(f"Screening {index_name}")
        print(f"{'='*80}")

        print(f"\nFetching data for {len(symbols)} stocks...")

        stocks_data = []
        for i, symbol in enumerate(symbols, 1):
            print(f"[{i}/{len(symbols)}] Fetching {symbol}...", end='\r')
            data = self.fetch_stock_data(symbol)
            if data:
                stocks_data.append(data)
            # Small delay to avoid rate limiting (0.5 seconds between requests)
            if i % 10 == 0:  # Every 10 stocks, pause slightly longer
                time.sleep(1)
            else:
                time.sleep(0.3)

        print(f"\nSuccessfully fetched data for {len(stocks_data)} stocks")

        # Calculate sector averages
        sector_avg_pe = self.calculate_sector_avg_pe(stocks_data)

        # Apply filters
        print("\nApplying valuation filters...")
        stage1_pass = []
        for stock in stocks_data:
            val_score, val_reasons = self.apply_valuation_filters(stock, sector_avg_pe)
            if val_score is not None:
                stock['valuation_score'] = val_score
                stock['valuation_reasons'] = val_reasons
                stage1_pass.append(stock)

        print(f"Stocks passing valuation filters: {len(stage1_pass)}")

        print("\nApplying growth filters...")
        stage2_pass = []
        for stock in stage1_pass:
            growth_score, growth_reasons = self.apply_growth_filters(stock)
            if growth_score >= 15:  # Minimum growth threshold
                stock['growth_score'] = growth_score
                stock['growth_reasons'] = growth_reasons
                stage2_pass.append(stock)

        print(f"Stocks passing growth filters: {len(stage2_pass)}")

        print("\nApplying risk filters...")
        final_candidates = []
        for stock in stage2_pass:
            risk_score, risk_reasons = self.apply_risk_filters(stock)
            if risk_score >= 15:  # Minimum risk score
                stock['risk_score'] = risk_score
                stock['risk_reasons'] = risk_reasons
                stock['composite_score'] = stock['valuation_score'] + stock['growth_score'] + stock['risk_score']
                final_candidates.append(stock)

        print(f"Final candidates: {len(final_candidates)}")

        # Sort by composite score
        final_candidates.sort(key=lambda x: x['composite_score'], reverse=True)

        return stocks_data, final_candidates

    def calculate_target_price(self, stock):
        """Estimate target price for 2x potential"""
        current_price = stock['current_price']

        # Conservative estimate: current price * 2
        target = current_price * 2

        # Adjust based on P/E if available
        if stock.get('pe_ratio') and stock.get('forward_pe'):
            # If forward P/E suggests compression, adjust target
            pe_ratio = stock['pe_ratio']
            forward_pe = stock['forward_pe']
            if forward_pe < pe_ratio * 0.8:  # P/E compression expected
                target = current_price * 1.8

        return target

    def generate_report(self, all_stocks, final_candidates, index_name):
        """Generate comprehensive report"""
        print(f"\n\n{'='*80}")
        print(f"INDIA MIDCAP & SMALLCAP SCREENER REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")

        print(f"\n📊 EXECUTIVE SUMMARY")
        print(f"{'─'*80}")
        print(f"  • Total stocks analyzed: {len(all_stocks)}")
        print(f"  • Stocks passing valuation filters: {len([s for s in all_stocks if 'valuation_score' in s])}")
        print(f"  • Final recommendations: {min(len(final_candidates), 10)}")
        print(f"  • Index: {index_name}")
        print(f"  • Market date: {datetime.now().strftime('%d %B %Y')}")

        if not final_candidates:
            print("\n⚠️  No stocks met all screening criteria. Consider relaxing filters or trying again later.")
            return

        print(f"\n\n{'='*80}")
        print(f"🎯 TOP RECOMMENDATIONS")
        print(f"{'='*80}")

        top_stocks = final_candidates[:5]

        for rank, stock in enumerate(top_stocks, 1):
            target_price = self.calculate_target_price(stock)
            upside = ((target_price - stock['current_price']) / stock['current_price']) * 100

            print(f"\n\n{'─'*80}")
            print(f"{rank}. {stock['name']} ({stock['symbol']}.NS)")
            print(f"{'─'*80}")
            print(f"📈 Composite Score: {stock['composite_score']:.1f}/100", end="")
            print(f" (Valuation: {stock['valuation_score']:.1f}/30 | Growth: {stock['growth_score']:.1f}/40 | Risk: {stock['risk_score']:.1f}/30)")

            print(f"\n💰 Current Price: ₹{stock['current_price']:.2f}")
            print(f"   Target Price (6-12M): ₹{target_price:.2f}")
            print(f"   Upside Potential: {upside:.1f}%")

            print(f"\n📉 Why It's Undervalued:")
            if stock.get('pe_ratio'):
                print(f"   • P/E Ratio: {stock['pe_ratio']:.2f}")
            if stock.get('pb_ratio') and stock.get('roe'):
                print(f"   • P/B: {stock['pb_ratio']:.2f} with ROE: {stock['roe']:.1f}%")
            if stock.get('peg_ratio'):
                print(f"   • PEG Ratio: {stock['peg_ratio']:.2f}")
            for reason in stock.get('valuation_reasons', [])[:3]:
                print(f"   • {reason}")

            print(f"\n🚀 Growth Catalysts:")
            for reason in stock.get('growth_reasons', [])[:4]:
                print(f"   • {reason}")

            # Display Order Book information if available
            if stock.get('order_book_relevant') and stock.get('has_order_book_data'):
                ob_value = stock.get('order_book_value')
                ob_ratio = stock.get('order_book_to_revenue_ratio')
                ob_months = stock.get('order_book_visibility_months')
                is_estimated = stock.get('is_estimated', False)

                if ob_value and ob_ratio:
                    print(f"\n📋 Order Book Analysis:")
                    print(f"   • Order Book: ₹{ob_value:.0f} Cr ({ob_ratio:.1f}x revenue)")
                    print(f"   • Revenue Visibility: ~{ob_months:.0f} months")
                    if is_estimated:
                        print(f"   • Note: Estimated based on industry benchmarks")

                    # Provide interpretation
                    if ob_ratio >= 2.0:
                        print(f"   • Assessment: Excellent revenue visibility (2+ years)")
                    elif ob_ratio >= 1.5:
                        print(f"   • Assessment: Strong revenue visibility (1.5-2 years)")
                    elif ob_ratio >= 1.0:
                        print(f"   • Assessment: Good revenue visibility (1-1.5 years)")
                    elif ob_ratio >= 0.5:
                        print(f"   • Assessment: Moderate revenue visibility (6-12 months)")

            print(f"\n⚠️  Risk Profile:")
            if stock.get('debt_to_equity'):
                print(f"   • Debt-to-Equity: {stock['debt_to_equity']/100:.2f}")
            if stock.get('beta'):
                print(f"   • Volatility (Beta): {stock['beta']:.2f}")
            if stock.get('avg_volume'):
                print(f"   • Avg Daily Volume: {stock['avg_volume']:,.0f}")
            if stock.get('market_cap'):
                print(f"   • Market Cap: ₹{stock['market_cap']:.0f} Cr")

            if stock.get('risk_reasons'):
                print(f"\n   ⚠️  Key Risks:")
                for risk in stock.get('risk_reasons', [])[:3]:
                    print(f"      - {risk}")

            print(f"\n💡 Investment Thesis:")
            thesis = f"   {stock['name']} shows strong potential for 2x returns due to "
            rev_growth = stock.get('revenue_growth')
            if rev_growth and rev_growth > 20:
                thesis += f"robust revenue growth ({rev_growth:.1f}%), "
            if stock.get('pe_ratio') and stock['pe_ratio'] < 20:
                thesis += "attractive valuation, "
            roe = stock.get('roe')
            if roe and roe > 15:
                thesis += f"high ROE ({roe:.1f}%), "
            thesis += f"and favorable technical setup. The stock is in the {stock.get('sector', 'Unknown')} sector."
            print(thesis)

        # Honorable Mentions
        if len(final_candidates) > 5:
            print(f"\n\n{'='*80}")
            print(f"🏅 HONORABLE MENTIONS")
            print(f"{'='*80}")

            honorable = final_candidates[5:10]
            for stock in honorable:
                print(f"\n  • {stock['name']} ({stock['symbol']}.NS) - Score: {stock['composite_score']:.1f}/100")
                print(f"    Price: ₹{stock['current_price']:.2f} | Sector: {stock.get('sector', 'N/A')}")
                if stock.get('valuation_reasons'):
                    print(f"    {stock['valuation_reasons'][0]}")

        # Market Context
        print(f"\n\n{'='*80}")
        print(f"🌍 MARKET CONTEXT & TIMING")
        print(f"{'='*80}")
        print(f"\n  Current market conditions (as of {datetime.now().strftime('%B %Y')}):")
        print(f"  • Indian midcap and smallcap indices have shown volatility")
        print(f"  • Focus on quality stocks with strong fundamentals")
        print(f"  • Diversification across sectors recommended")
        print(f"  • Monitor FII/DII flows and global market sentiment")

        # Disclaimers
        print(f"\n\n{'='*80}")
        print(f"⚠️  IMPORTANT DISCLAIMERS")
        print(f"{'='*80}")
        print(f"""
  • Past performance does not guarantee future results
  • 6-12 month doubling is an aggressive target; actual returns may vary significantly
  • Recommended position sizing: No single stock >5-10% of portfolio
  • Always conduct your own due diligence before investing
  • Consider consulting a SEBI-registered investment advisor
  • Markets are subject to risks; invest based on your risk appetite
  • This is an automated screening tool and not financial advice
  • Data accuracy depends on public sources and may have limitations
""")

def main():
    screener = StockScreener()

    print("="*80)
    print("INDIA MIDCAP & SMALLCAP STOCK SCREENER - COMPREHENSIVE ANALYSIS")
    print("Analyzing ALL 200+ stocks from Nifty Midcap 100 & Smallcap 100")
    print("Identifying undervalued stocks with 2x potential in 6-12 months")
    print("="*80)
    print("\n⏱️  This comprehensive analysis will take 10-15 minutes...")
    print("📊 Fetching data for ~200 stocks with rate limiting to avoid API blocks\n")

    # Screen Midcap 100 (all stocks)
    midcap_all, midcap_final = screener.screen_stocks(
        NIFTY_MIDCAP_100,  # All 100+ stocks
        "Nifty Midcap 100"
    )

    # Screen Smallcap 100 (all stocks)
    smallcap_all, smallcap_final = screener.screen_stocks(
        NIFTY_SMALLCAP_100,  # All 100+ stocks
        "Nifty Smallcap 100"
    )

    # Combine results
    all_stocks = midcap_all + smallcap_all
    all_final = midcap_final + smallcap_final
    all_final.sort(key=lambda x: x['composite_score'], reverse=True)

    # Generate report
    screener.generate_report(all_stocks, all_final, "Nifty Midcap 100 + Smallcap 100")

    # Save detailed results to CSV
    if all_final:
        df = pd.DataFrame(all_final)
        csv_filename = f"india_midsmall_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(csv_filename, index=False)
        print(f"\n💾 Detailed results saved to: {csv_filename}")

    print("\n\n" + "="*80)
    print("🎉 Comprehensive analysis complete!")
    print("="*80)

if __name__ == "__main__":
    main()
