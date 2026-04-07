import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from google import generativeai as genai
import datetime
import json

# ── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Stock Analyst Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Space+Grotesk:wght@300;400;500;600;700&display=swap');

    :root {
        --bg-primary: #0a0e17;
        --bg-secondary: #111827;
        --bg-card: #1a2235;
        --bg-card-hover: #1f2a40;
        --border: #2a3550;
        --text-primary: #e8ecf4;
        --text-secondary: #8899b4;
        --accent-gold: #f0b429;
        --accent-gold-dim: rgba(240, 180, 41, 0.15);
        --accent-green: #10b981;
        --accent-red: #ef4444;
        --accent-blue: #38bdf8;
    }

    .stApp {
        background: var(--bg-primary);
        color: var(--text-primary);
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: var(--bg-secondary) !important;
        border-right: 1px solid var(--border);
    }
    [data-testid="stSidebar"] * {
        color: var(--text-primary) !important;
    }
    [data-testid="stSidebar"] .stTextInput > div > div > input {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stSelectbox > div > div {
        background: var(--bg-card) !important;
        border: 1px solid var(--border) !important;
        color: var(--text-primary) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] .stButton > button {
        background: linear-gradient(135deg, #f0b429, #d4940a) !important;
        color: #0a0e17 !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 8px !important;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        transition: all 0.2s;
    }
    [data-testid="stSidebar"] .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 20px rgba(240, 180, 41, 0.4);
    }

    /* Metric cards */
    .metric-card {
        background: var(--bg-card);
        border: 1px solid var(--border);
        border-radius: 12px;
        padding: 20px;
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent-gold), transparent);
        opacity: 0;
        transition: opacity 0.25s;
    }
    .metric-card:hover {
        background: var(--bg-card-hover);
        border-color: rgba(240, 180, 41, 0.3);
        transform: translateY(-2px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.3);
    }
    .metric-card:hover::before { opacity: 1; }

    .metric-label {
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 1.2px;
        color: var(--text-secondary);
        font-family: 'JetBrains Mono', monospace;
        margin-bottom: 8px;
    }
    .metric-value {
        font-size: 28px;
        font-weight: 700;
        font-family: 'Space Grotesk', sans-serif;
        color: var(--text-primary);
        line-height: 1;
    }
    .metric-sub {
        font-size: 12px;
        color: var(--text-secondary);
        margin-top: 6px;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Signal badge */
    .signal-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 12px 28px;
        border-radius: 50px;
        font-size: 22px;
        font-weight: 800;
        font-family: 'Space Grotesk', sans-serif;
        text-transform: uppercase;
        letter-spacing: 2px;
        animation: pulse-glow 2s ease-in-out infinite;
    }
    .signal-buy {
        background: rgba(16, 185, 129, 0.15);
        color: var(--accent-green);
        border: 2px solid var(--accent-green);
        box-shadow: 0 0 30px rgba(16, 185, 129, 0.2);
    }
    .signal-sell {
        background: rgba(239, 68, 68, 0.15);
        color: var(--accent-red);
        border: 2px solid var(--accent-red);
        box-shadow: 0 0 30px rgba(239, 68, 68, 0.2);
    }
    .signal-hold {
        background: rgba(240, 180, 41, 0.15);
        color: var(--accent-gold);
        border: 2px solid var(--accent-gold);
        box-shadow: 0 0 30px rgba(240, 180, 41, 0.2);
    }

    @keyframes pulse-glow {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.85; }
    }

    /* AI Summary box */
    .ai-summary {
        background: linear-gradient(135deg, var(--bg-card), rgba(240, 180, 41, 0.05));
        border: 1px solid rgba(240, 180, 41, 0.2);
        border-radius: 16px;
        padding: 28px;
        font-size: 15px;
        line-height: 1.75;
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        position: relative;
    }
    .ai-summary::before {
        content: 'AI';
        position: absolute;
        top: -10px; left: 20px;
        background: linear-gradient(135deg, #f0b429, #d4940a);
        color: #0a0e17;
        font-size: 11px;
        font-weight: 800;
        padding: 3px 12px;
        border-radius: 6px;
        letter-spacing: 1.5px;
    }

    /* Section headers */
    .section-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 13px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: var(--accent-gold);
        margin-bottom: 16px;
        padding-bottom: 10px;
        border-bottom: 1px solid var(--border);
    }

    /* Plotly chart fix */
    .js-plotly-plot .plotly .modebar { display: none !important; }

    /* Hide default streamlit elements */
    .stDeployButton { display: none !important; }
    [data-testid="stToolbar"] { display: none !important; }
    [data-testid="stHeader"] { background: var(--bg-primary) !important; }

    /* Fundamentals table */
    .fund-table {
        width: 100%;
        border-collapse: separate;
        border-spacing: 0;
    }
    .fund-table tr td {
        padding: 10px 14px;
        border-bottom: 1px solid var(--border);
        font-size: 14px;
    }
    .fund-table tr td:first-child {
        color: var(--text-secondary);
        font-family: 'JetBrains Mono', monospace;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        width: 40%;
    }
    .fund-table tr td:last-child {
        color: var(--text-primary);
        font-family: 'Space Grotesk', sans-serif;
        font-weight: 600;
        text-align: right;
    }
    .fund-table tr:hover td {
        background: rgba(240, 180, 41, 0.03);
    }

    /* Loading spinner */
    .loading-overlay {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(10, 14, 23, 0.85);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
        backdrop-filter: blur(4px);
    }
    .loading-spinner {
        width: 50px; height: 50px;
        border: 3px solid var(--border);
        border-top-color: var(--accent-gold);
        border-radius: 50%;
        animation: spin 0.8s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: var(--bg-primary); }
    ::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--text-secondary); }
</style>
""", unsafe_allow_html=True)


# ── Helper Functions ─────────────────────────────────────────────────────────

def safe_get(info_dict, key, default="N/A"):
    """Safely extract value from yfinance info dict."""
    val = info_dict.get(key, default)
    if val is None or (isinstance(val, float) and np.isnan(val)):
        return default
    return val


def format_large_number(num):
    """Format large numbers into readable strings."""
    if isinstance(num, (int, float)):
        if abs(num) >= 1e12:
            return f"{num / 1e12:.2f}T"
        elif abs(num) >= 1e9:
            return f"{num / 1e9:.2f}B"
        elif abs(num) >= 1e6:
            return f"{num / 1e6:.2f}M"
        elif abs(num) >= 1e3:
            return f"{num / 1e3:.2f}K"
        return f"{num:.2f}"
    return str(num)


def get_technical_signals(df):
    """Calculate basic technical indicators and return signals."""
    signals = {}
    try:
        # SMA
        df['SMA_20'] = df['Close'].rolling(20).mean()
        df['SMA_50'] = df['Close'].rolling(50).mean()
        df['SMA_200'] = df['Close'].rolling(200).mean()

        # RSI
        delta = df['Close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # MACD
        ema12 = df['Close'].ewm(span=12).mean()
        ema26 = df['Close'].ewm(span=26).mean()
        df['MACD'] = ema12 - ema26
        df['MACD_Signal'] = df['MACD'].ewm(span=9).mean()

        current = df.iloc[-1]
        signals['rsi'] = round(current['RSI'], 1) if not np.isnan(current['RSI']) else None
        signals['sma20'] = round(current['SMA_20'], 2) if not np.isnan(current['SMA_20']) else None
        signals['sma50'] = round(current['SMA_50'], 2) if not np.isnan(current['SMA_50']) else None
        signals['sma200'] = round(current['SMA_200'], 2) if not np.isnan(current['SMA_200']) else None
        signals['macd'] = round(current['MACD'], 4) if not np.isnan(current['MACD']) else None
        signals['macd_signal'] = round(current['MACD_Signal'], 4) if not np.isnan(current['MACD_Signal']) else None
        signals['price'] = round(current['Close'], 2)

        # Simple signal logic
        buy_count, sell_count = 0, 0
        if signals['rsi']:
            if signals['rsi'] < 30: buy_count += 2
            elif signals['rsi'] < 40: buy_count += 1
            elif signals['rsi'] > 70: sell_count += 2
            elif signals['rsi'] > 60: sell_count += 1
        if signals['sma20'] and signals['price']:
            if signals['price'] > signals['sma20']: buy_count += 1
            else: sell_count += 1
        if signals['sma50'] and signals['price']:
            if signals['price'] > signals['sma50']: buy_count += 1
            else: sell_count += 1
        if signals['macd'] and signals['macd_signal']:
            if signals['macd'] > signals['macd_signal']: buy_count += 1
            else: sell_count += 1

        if buy_count >= sell_count + 2:
            signals['tech_signal'] = 'BUY'
        elif sell_count >= buy_count + 2:
            signals['tech_signal'] = 'SELL'
        else:
            signals['tech_signal'] = 'HOLD'

    except Exception:
        pass

    return df, signals


def compute_fundamental_signal(info):
    """Compute a fundamental-based signal from yfinance info."""
    score = 0

    pe = safe_get(info, 'trailingPE', None)
    fwd_pe = safe_get(info, 'forwardPE', None)
    peg = safe_get(info, 'pegRatio', None)
    roe = safe_get(info, 'returnOnEquity', None)
    debt_eq = safe_get(info, 'debtToEquity', None)
    profit_margin = safe_get(info, 'profitMargins', None)
    rev_growth = safe_get(info, 'revenueGrowth', None)
    earn_growth = safe_get(info, 'earningsGrowth', None)
    div_yield = safe_get(info, 'dividendYield', None)
    price_to_book = safe_get(info, 'priceToBook', None)

    if isinstance(pe, (int, float)):
        if pe < 15: score += 2
        elif pe < 25: score += 1
        elif pe > 50: score -= 2
        elif pe > 35: score -= 1

    if isinstance(fwd_pe, (int, float)):
        if isinstance(pe, (int, float)) and fwd_pe < pe: score += 1
        elif isinstance(pe, (int, float)) and fwd_pe > pe * 1.2: score -= 1

    if isinstance(peg, (int, float)):
        if peg < 1: score += 2
        elif peg < 1.5: score += 1
        elif peg > 2: score -= 2

    if isinstance(roe, (int, float)):
        if roe > 0.2: score += 2
        elif roe > 0.15: score += 1
        elif roe < 0.05: score -= 2

    if isinstance(debt_eq, (int, float)):
        if debt_eq < 0.3: score += 1
        elif debt_eq > 1.0: score -= 2
        elif debt_eq > 0.5: score -= 1

    if isinstance(profit_margin, (int, float)):
        if profit_margin > 0.2: score += 2
        elif profit_margin > 0.1: score += 1
        elif profit_margin < 0: score -= 2

    if isinstance(rev_growth, (int, float)):
        if rev_growth > 0.2: score += 2
        elif rev_growth > 0.1: score += 1
        elif rev_growth < 0: score -= 1

    if isinstance(earn_growth, (int, float)):
        if earn_growth > 0.2: score += 2
        elif earn_growth > 0: score += 1
        elif earn_growth < -0.1: score -= 2

    if isinstance(div_yield, (int, float)):
        if div_yield > 0.03: score += 1

    if isinstance(price_to_book, (int, float)):
        if price_to_book < 1.5: score += 1
        elif price_to_book > 5: score -= 1

    if score >= 4:
        return 'BUY', score
    elif score <= -3:
        return 'SELL', score
    else:
        return 'HOLD', score


def call_gemini(api_key, stock_symbol, info, technical_signals, fundamental_signal, fund_score):
    """Call Gemini API for AI analysis summary."""
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')

        pe = safe_get(info, 'trailingPE', 'N/A')
        fwd_pe = safe_get(info, 'forwardPE', 'N/A')
        peg = safe_get(info, 'pegRatio', 'N/A')
        roe = safe_get(info, 'returnOnEquity', 'N/A')
        if isinstance(roe, float): roe = f"{roe * 100:.1f}%"
        debt_eq = safe_get(info, 'debtToEquity', 'N/A')
        profit_margin = safe_get(info, 'profitMargins', 'N/A')
        if isinstance(profit_margin, float): profit_margin = f"{profit_margin * 100:.1f}%"
        rev_growth = safe_get(info, 'revenueGrowth', 'N/A')
        if isinstance(rev_growth, float): rev_growth = f"{rev_growth * 100:.1f}%"
        earn_growth = safe_get(info, 'earningsGrowth', 'N/A')
        if isinstance(earn_growth, float): earn_growth = f"{earn_growth * 100:.1f}%"
        price_to_book = safe_get(info, 'priceToBook', 'N/A')
        div_yield = safe_get(info, 'dividendYield', 'N/A')
        if isinstance(div_yield, float): div_yield = f"{div_yield * 100:.2f}%"
        market_cap = safe_get(info, 'marketCap', 'N/A')
        if isinstance(market_cap, (int, float)): market_cap = format_large_number(market_cap)
        fifty_two_high = safe_get(info, 'fiftyTwoWeekHigh', 'N/A')
        fifty_two_low = safe_get(info, 'fiftyTwoWeekLow', 'N/A')
        beta = safe_get(info, 'beta', 'N/A')
        current_price = safe_get(info, 'currentPrice', 'N/A')
        sector = safe_get(info, 'sector', 'N/A')
        industry = safe_get(info, 'industry', 'N/A')

        prompt = f"""You are an expert stock analyst. Provide a concise but insightful analysis of {stock_symbol} based on the following data. Structure your response with clear sections.

**Stock: {stock_symbol}**
Sector: {sector} | Industry: {industry}
Current Price: {current_price} | Market Cap: {market_cap}
52-Week Range: {fifty_two_low} - {fifty_two_high} | Beta: {beta}

**Fundamentals:**
- Trailing PE: {pe}
- Forward PE: {fwd_pe}
- PEG Ratio: {peg}
- ROE: {roe}
- Debt to Equity: {debt_eq}
- Profit Margin: {profit_margin}
- Revenue Growth: {rev_growth}
- Earnings Growth: {earn_growth}
- Price to Book: {price_to_book}
- Dividend Yield: {div_yield}

**Technical Indicators:**
- RSI(14): {technical_signals.get('rsi', 'N/A')}
- SMA 20: {technical_signals.get('sma20', 'N/A')}
- SMA 50: {technical_signals.get('sma50', 'N/A')}
- SMA 200: {technical_signals.get('sma200', 'N/A')}
- MACD: {technical_signals.get('macd', 'N/A')}
- MACD Signal: {technical_signals.get('macd_signal', 'N/A')}
- Technical Signal: {technical_signals.get('tech_signal', 'N/A')}

**Fundamental Signal: {fundamental_signal}** (Score: {fund_score})

Please provide:
1. **Fundamental Assessment** - Is the stock fundamentally strong or weak? Why?
2. **Technical Outlook** - What do the technical indicators suggest about near-term direction?
3. **Key Risks** - What are the main risks an investor should be aware of?
4. **Verdict** - A final recommendation (BUY/SELL/HOLD) with a 2-3 sentence rationale, similar to how a seasoned analyst would write in a research note. Be direct and opinionated, not wishy-washy.

Keep the total response under 300 words. Be specific, not generic."""

        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error calling Gemini API: {str(e)}"


# ── Chart Builders ───────────────────────────────────────────────────────────

def build_price_chart(df, stock_symbol):
    """Build an interactive price chart with volume subplot."""
    df, signals = get_technical_signals(df)

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.08,
        row_heights=[0.75, 0.25],
        subplot_titles=(f'{stock_symbol} Price', 'Volume')
    )

    # Price line
    fig.add_trace(go.Scatter(
        x=df.index, y=df['Close'],
        mode='lines',
        name='Close',
        line=dict(color='#f0b429', width=2),
        fill='tozeroy',
        fillcolor='rgba(240, 180, 41, 0.05)',
        hovertemplate='%{x|%b %d, %Y}<br>Price: $%{y:.2f}<extra></extra>'
    ), row=1, col=1)

    # SMA lines
    if signals.get('sma20'):
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_20'],
            mode='lines', name='SMA 20',
            line=dict(color='#38bdf8', width=1, dash='dot'),
            opacity=0.7,
            hovertemplate='SMA 20: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)
    if signals.get('sma50'):
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_50'],
            mode='lines', name='SMA 50',
            line=dict(color='#a78bfa', width=1, dash='dot'),
            opacity=0.7,
            hovertemplate='SMA 50: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)
    if signals.get('sma200'):
        fig.add_trace(go.Scatter(
            x=df.index, y=df['SMA_200'],
            mode='lines', name='SMA 200',
            line=dict(color='#f472b6', width=1, dash='dot'),
            opacity=0.7,
            hovertemplate='SMA 200: $%{y:.2f}<extra></extra>'
        ), row=1, col=1)

    # Volume bars
    colors = ['#10b981' if c >= o else '#ef4444' for c, o in zip(df['Close'], df['Open'])]
    fig.add_trace(go.Bar(
        x=df.index, y=df['Volume'],
        name='Volume',
        marker_color=colors,
        opacity=0.5,
        hovertemplate='Vol: %{y:,.0f}<extra></extra>'
    ), row=2, col=1)

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Grotesk, sans-serif', color='#8899b4'),
        margin=dict(l=50, r=30, t=40, b=30),
        legend=dict(
            orientation='h', y=1.01, x=0,
            font=dict(size=11),
            bgcolor='rgba(0,0,0,0)'
        ),
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )

    fig.update_yaxes(
        gridcolor='rgba(42, 53, 80, 0.5)',
        zeroline=False,
        tickfont=dict(size=11)
    )
    fig.update_xaxes(
        gridcolor='rgba(42, 53, 80, 0.3)',
        tickfont=dict(size=10)
    )

    # Subtitle styling
    for annotation in fig['layout']['annotations']:
        annotation['font'] = dict(size=13, color='#8899b4', family='Space Grotesk')

    return fig, signals


def build_rsi_chart(df):
    """Build RSI indicator chart."""
    if 'RSI' not in df.columns:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df.index, y=df['RSI'],
        mode='lines',
        name='RSI (14)',
        line=dict(color='#f0b429', width=1.5),
        hovertemplate='RSI: %{y:.1f}<extra></extra>'
    ))
    # Overbought / Oversold zones
    fig.add_hline(y=70, line_dash='dash', line_color='#ef4444', opacity=0.5, annotation_text='Overbought')
    fig.add_hline(y=30, line_dash='dash', line_color='#10b981', opacity=0.5, annotation_text='Oversold')
    fig.add_hrect(y0=30, y1=70, fillcolor='rgba(240, 180, 41, 0.05)', line_width=0)

    fig.update_layout(
        template='plotly_dark',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(family='Space Grotesk', color='#8899b4', size=11),
        margin=dict(l=50, r=20, t=10, b=30),
        height=200,
        xaxis_rangeslider_visible=False,
        showlegend=False,
        hovermode='x unified'
    )
    fig.update_yaxes(gridcolor='rgba(42, 53, 80, 0.4)', zeroline=False, range=[0, 100])
    fig.update_xaxes(gridcolor='rgba(42, 53, 80, 0.3)')
    return fig


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("""
    <div style="padding: 10px 0 20px;">
        <div style="font-family: 'Space Grotesk'; font-size: 22px; font-weight: 700; color: #f0b429; letter-spacing: -0.5px;">
            Stock Analyst
        </div>
        <div style="font-family: 'JetBrains Mono'; font-size: 10px; color: #8899b4; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px;">
            Powered by Gemini AI
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section-title">Configuration</div>', unsafe_allow_html=True)

    gemini_key = st.text_input("Gemini API Key", type="password", placeholder="Enter your API key...")

    stock_symbol = st.text_input("Stock Symbol", value="TCS.NS", placeholder="e.g. AAPL, TCS.NS, MSFT")
    stock_symbol = stock_symbol.strip().upper()

    period_options = {
        "1 Month": "1mo",
        "3 Months": "3mo",
        "6 Months": "6mo",
        "1 Year": "1y",
        "2 Years": "2y",
        "5 Years": "5y",
    }
    selected_period = st.selectbox("Time Period", list(period_options.keys()), index=3)

    analyze_clicked = st.button("Analyze Stock", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="font-size: 11px; color: #556; font-family: 'JetBrains Mono'; line-height: 1.6;">
        Data source: Yahoo Finance<br>
        AI Engine: Gemini 2.0 Flash<br>
        Signals are for reference only.
    </div>
    """, unsafe_allow_html=True)


# ── Main Content ─────────────────────────────────────────────────────────────

if analyze_clicked and stock_symbol:
    if not gemini_key:
        st.error("Please enter your Gemini API key in the sidebar.")
        st.stop()

    # Loading state
    with st.spinner("Fetching data & analyzing..."):
        try:
            ticker = yf.Ticker(stock_symbol)
            info = ticker.info
            period = period_options[selected_period]
            df = ticker.history(period=period)

            if df.empty:
                st.error(f"No data found for symbol '{stock_symbol}'. Please check the ticker symbol.")
                st.stop()

            # ── Header ──────────────────────────────────────────────
            company_name = safe_get(info, 'longName', stock_symbol)
            current_price = safe_get(info, 'currentPrice', df['Close'].iloc[-1])
            prev_close = safe_get(info, 'previousClose', df['Close'].iloc[-2] if len(df) > 1 else current_price)
            change = current_price - prev_close if isinstance(current_price, (int, float)) and isinstance(prev_close, (int, float)) else 0
            change_pct = (change / prev_close * 100) if prev_close and prev_close != 0 else 0

            price_color = "#10b981" if change >= 0 else "#ef4444"
            arrow = "▲" if change >= 0 else "▼"

            st.markdown(f"""
            <div style="margin-bottom: 8px;">
                <span style="font-family: 'Space Grotesk'; font-size: 32px; font-weight: 700; color: #e8ecf4;">
                    {stock_symbol}
                </span>
                <span style="font-family: 'Space Grotesk'; font-size: 16px; color: #8899b4; margin-left: 12px;">
                    {company_name}
                </span>
            </div>
            <div style="display: flex; align-items: baseline; gap: 16px; margin-bottom: 6px;">
                <span style="font-family: 'Space Grotesk'; font-size: 44px; font-weight: 700; color: {price_color};">
                    ${current_price:.2f}
                </span>
                <span style="font-family: 'JetBrains Mono'; font-size: 16px; color: {price_color};">
                    {arrow} {abs(change):.2f} ({abs(change_pct):.2f}%)
                </span>
            </div>
            <div style="font-family: 'JetBrains Mono'; font-size: 11px; color: #556; letter-spacing: 0.5px;">
                {safe_get(info, 'exchange', '')} · {safe_get(info, 'sector', '')} · {safe_get(info, 'currency', 'USD').upper()}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height: 24px;'></div>", unsafe_allow_html=True)

            # ── Metrics Row ─────────────────────────────────────────
            mkt_cap = format_large_number(safe_get(info, 'marketCap', 0))
            pe_val = safe_get(info, 'trailingPE', 'N/A')
            fwd_pe_val = safe_get(info, 'forwardPE', 'N/A')
            roe_val = safe_get(info, 'returnOnEquity', 'N/A')
            if isinstance(roe_val, float): roe_val = f"{roe_val * 100:.1f}%"

            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Market Cap</div>
                    <div class="metric-value">${mkt_cap}</div>
                    <div class="metric-sub">{safe_get(info, 'sector', '')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Trailing PE</div>
                    <div class="metric-value">{pe_val}</div>
                    <div class="metric-sub">Fwd PE: {fwd_pe_val}</div>
                </div>
                """, unsafe_allow_html=True)
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">ROE</div>
                    <div class="metric-value">{roe_val}</div>
                    <div class="metric-sub">Profit Margin: {safe_get(info, 'profitMargins', 'N/A')}</div>
                </div>
                """, unsafe_allow_html=True)
            with col4:
                high_52 = safe_get(info, 'fiftyTwoWeekHigh', 'N/A')
                low_52 = safe_get(info, 'fiftyTwoWeekLow', 'N/A')
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">52-Week Range</div>
                    <div class="metric-value" style="font-size: 20px;">${low_52}</div>
                    <div class="metric-sub">High: ${high_52}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

            # ── Price Chart ─────────────────────────────────────────
            price_fig, tech_signals = build_price_chart(df, stock_symbol)
            st.plotly_chart(price_fig, use_container_width=True, config={'displayModeBar': False})

            # ── RSI Chart ───────────────────────────────────────────
            rsi_fig = build_rsi_chart(df)
            if rsi_fig:
                st.plotly_chart(rsi_fig, use_container_width=True, config={'displayModeBar': False})

            st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

            # ── Signal + Fundamentals Side by Side ──────────────────
            fund_signal, fund_score = compute_fundamental_signal(info)

            # Combine tech + fundamental signals
            tech_sig = tech_signals.get('tech_signal', 'HOLD')
            signal_map = {'BUY': 2, 'HOLD': 1, 'SELL': 0}
            combined_score = signal_map.get(tech_sig, 1) + signal_map.get(fund_signal, 1)
            if combined_score >= 4:
                final_signal = 'BUY'
            elif combined_score <= 1:
                final_signal = 'SELL'
            else:
                final_signal = 'HOLD'

            left_col, right_col = st.columns([1, 1.5])

            with left_col:
                st.markdown('<div class="section-title">Signal (Buy / Sell / Hold)</div>', unsafe_allow_html=True)

                signal_class = f"signal-{final_signal.lower()}"
                signal_icon = {"BUY": "🟢", "SELL": "🔴", "HOLD": "🟡"}[final_signal]
                st.markdown(f"""
                <div style="text-align: center; padding: 30px 0;">
                    <div class="signal-badge {signal_class}">
                        {signal_icon} {final_signal}
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown(f"""
                <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 10px; padding: 16px; margin-top: 8px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #8899b4; font-size: 12px; font-family: 'JetBrains Mono';">TECHNICAL</span>
                        <span style="font-weight: 700; font-size: 14px; color: {'#10b981' if tech_sig == 'BUY' else '#ef4444' if tech_sig == 'SELL' else '#f0b429'}; font-family: 'Space Grotesk';">{tech_sig}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #8899b4; font-size: 12px; font-family: 'JetBrains Mono';">FUNDAMENTAL</span>
                        <span style="font-weight: 700; font-size: 14px; color: {'#10b981' if fund_signal == 'BUY' else '#ef4444' if fund_signal == 'SELL' else '#f0b429'}; font-family: 'Space Grotesk';">{fund_signal}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; padding-top: 10px; border-top: 1px solid var(--border);">
                        <span style="color: #8899b4; font-size: 12px; font-family: 'JetBrains Mono';">FUND SCORE</span>
                        <span style="font-weight: 700; font-size: 14px; color: {'#10b981' if fund_score > 0 else '#ef4444' if fund_score < 0 else '#f0b429'}; font-family: 'Space Grotesk';">{fund_score:+d}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #8899b4; font-size: 12px; font-family: 'JetBrains Mono';">RSI (14)</span>
                        <span style="font-weight: 700; font-size: 14px; color: var(--text-primary); font-family: 'Space Grotesk';">{tech_signals.get('rsi', 'N/A')}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            with right_col:
                st.markdown('<div class="section-title">Fundamentals</div>', unsafe_allow_html=True)

                fundamentals = [
                    ("Trailing P/E", safe_get(info, 'trailingPE', 'N/A')),
                    ("Forward P/E", safe_get(info, 'forwardPE', 'N/A')),
                    ("PEG Ratio", safe_get(info, 'pegRatio', 'N/A')),
                    ("Price / Book", safe_get(info, 'priceToBook', 'N/A')),
                    ("Return on Equity", roe_val),
                    ("Profit Margin", safe_get(info, 'profitMargins', 'N/A')),
                    ("Operating Margin", safe_get(info, 'operatingMargins', 'N/A')),
                    ("Revenue Growth", safe_get(info, 'revenueGrowth', 'N/A')),
                    ("Earnings Growth", safe_get(info, 'earningsGrowth', 'N/A')),
                    ("Debt / Equity", safe_get(info, 'debtToEquity', 'N/A')),
                    ("Dividend Yield", safe_get(info, 'dividendYield', 'N/A')),
                    ("Beta", safe_get(info, 'beta', 'N/A')),
                ]

                rows_html = ""
                for label, value in fundamentals:
                    # Format percentage values
                    display_val = value
                    if isinstance(value, float):
                        if abs(value) < 10 and label not in ["Beta", "PEG Ratio", "Price / Book"]:
                            display_val = f"{value * 100:.1f}%"
                        else:
                            display_val = f"{value:.2f}"

                    rows_html += f"<tr><td>{label}</td><td>{display_val}</td></tr>"

                st.markdown(f"""
                <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; padding: 4px; max-height: 460px; overflow-y: auto;">
                    <table class="fund-table">{rows_html}</table>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)

            # ── AI Summary ──────────────────────────────────────────
            st.markdown('<div class="section-title">AI Summary (Gemini)</div>', unsafe_allow_html=True)

            with st.spinner("Generating AI analysis..."):
                ai_response = call_gemini(gemini_key, stock_symbol, info, tech_signals, fund_signal, fund_score)

            # Clean up markdown from Gemini response
            clean_response = ai_response.replace('**', '<strong>').replace('</strong><strong>', '')
            # Fix double bold
            parts = clean_response.split('<strong>')
            final_parts = []
            for i, part in enumerate(parts):
                if i > 0:
                    close_idx = part.find('</strong>')
                    if close_idx != -1:
                        final_parts.append('<strong>' + part[:close_idx + 9] + part[close_idx + 9:])
                    else:
                        final_parts.append('<strong>' + part)
                else:
                    final_parts.append(part)
            clean_response = ''.join(final_parts)

            st.markdown(f'<div class="ai-summary">{clean_response}</div>', unsafe_allow_html=True)

            st.markdown("<div style='height: 32px;'></div>", unsafe_allow_html=True)

            # ── Disclaimer ──────────────────────────────────────────
            st.markdown("""
            <div style="text-align: center; font-size: 11px; color: #445; font-family: 'JetBrains Mono'; padding: 16px; border-top: 1px solid var(--border);">
                ⚠ This dashboard is for informational purposes only. It does not constitute financial advice.<br>
                Always do your own research before making investment decisions.
            </div>
            """, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.markdown("""
            <div style="background: rgba(239,68,68,0.1); border: 1px solid rgba(239,68,68,0.3); border-radius: 12px; padding: 20px; margin-top: 16px;">
                <p style="color: #ef4444; font-family: 'Space Grotesk'; margin: 0;">
                    Possible causes: Invalid stock symbol, network error, or API rate limit.<br>
                    Try a different symbol (e.g., AAPL, MSFT, TCS.NS, RELIANCE.NS).
                </p>
            </div>
            """, unsafe_allow_html=True)

elif not analyze_clicked:
    # Empty state
    st.markdown("""
    <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 70vh; text-align: center;">
        <div style="font-size: 64px; margin-bottom: 20px; opacity: 0.15;">📊</div>
        <div style="font-family: 'Space Grotesk'; font-size: 28px; font-weight: 700; color: #e8ecf4; margin-bottom: 8px;">
            Stock Analyst Dashboard
        </div>
        <div style="font-family: 'Space Grotesk'; font-size: 15px; color: #8899b4; max-width: 420px; line-height: 1.7;">
            Enter your Gemini API key and a stock symbol in the sidebar,<br>
            then click <strong style="color: #f0b429;">Analyze Stock</strong> to get started.
        </div>
        <div style="margin-top: 32px; display: flex; gap: 12px; flex-wrap: wrap; justify-content: center;">
            <span style="background: var(--bg-card); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-family: 'JetBrains Mono'; font-size: 11px; color: #8899b4;">AAPL</span>
            <span style="background: var(--bg-card); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-family: 'JetBrains Mono'; font-size: 11px; color: #8899b4;">MSFT</span>
            <span style="background: var(--bg-card); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-family: 'JetBrains Mono'; font-size: 11px; color: #8899b4;">TCS.NS</span>
            <span style="background: var(--bg-card); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-family: 'JetBrains Mono'; font-size: 11px; color: #8899b4;">RELIANCE.NS</span>
            <span style="background: var(--bg-card); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-family: 'JetBrains Mono'; font-size: 11px; color: #8899b4;">GOOGL</span>
            <span style="background: var(--bg-card); border: 1px solid var(--border); padding: 6px 14px; border-radius: 20px; font-family: 'JetBrains Mono'; font-size: 11px; color: #8899b4;">TSLA</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
