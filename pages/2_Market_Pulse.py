import streamlit as st
import google.generativeai as genai
from theme_manager import apply_user_theme

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Market Pulse", layout="centered")
apply_user_theme()

# --- 2. TRUE MOBILE-RESPONSIVE CSS ---
st.markdown("""
<style>
    /* Gradient Header */
    .pulse-header {
        background: linear-gradient(90deg, #1e293b 0%, #3b82f6 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2rem;
        font-weight: 900;
        text-align: center;
        margin-bottom: 0px;
    }
    .pulse-sub { text-align: center; color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 25px; }
    
    /* CSS GRID FOR PERFECT MOBILE STACKING */
    .market-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
        gap: 15px;
        margin-bottom: 10px;
    }

    /* Sleek Ticker Cards */
    .ticker-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.04);
        border: 1px solid #f0f2f6;
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        box-sizing: border-box;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .ticker-card:hover {
        transform: translateY(-2px);
        box-shadow: 0px 8px 15px rgba(0,0,0,0.08);
        border-color: #e2e8f0;
    }
    
    /* Card Elements */
    .asset-info { display: flex; flex-direction: column; max-width: 60%; }
    .asset-name { font-weight: 800; color: #0f172a; font-size: 1.1rem; }
    .asset-type { font-size: 0.7rem; color: #94a3b8; text-transform: uppercase; font-weight: 600;}
    
    .price-info { text-align: right; display: flex; flex-direction: column; align-items: flex-end; }
    .price-val { font-weight: 800; font-size: 1.25rem; color: #1e293b; line-height: 1.2;}
    
    /* Trend Pill Badges */
    .trend-pill-up { background-color: #ecfdf5; color: #00C78C; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; margin-top: 4px; display: inline-block; }
    .trend-pill-down { background-color: #fef2f2; color: #FF4B4B; font-size: 0.75rem; font-weight: 700; padding: 4px 10px; border-radius: 20px; margin-top: 4px; display: inline-block; }
    
    .section-title { font-size: 1.1rem; font-weight: 800; color: #334155; margin-top: 25px; margin-bottom: 15px; border-bottom: 2px solid #f1f5f9; padding-bottom: 5px;}

    /* 📱 MOBILE OVERRIDES */
    @media (max-width: 768px) {
        .market-grid {
            grid-template-columns: 1fr;
            gap: 10px;
        }
        .ticker-card { padding: 12px 15px; }
        .asset-name { font-size: 1rem; }
        .price-val { font-size: 1.15rem; }
        .pulse-header { font-size: 1.7rem; }
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
c1, c2, c3, c4 = st.columns([1, 4, 1, 1], vertical_alignment="center")
with c1: 
    if st.button("🔙"): st.switch_page("pages/1_Expense_Tracker.py")
with c2: 
    st.markdown("<h1 class='pulse-header'>📈 Market Pulse</h1>", unsafe_allow_html=True)
    st.markdown("<p class='pulse-sub'>Live Forex, Commodities & F&O</p>", unsafe_allow_html=True)
with c3: st.button("📷")
with c4: st.button("📽️")

# --- 4. DATA GENERATOR (Including 24K and 22K Gold) ---
market_data = {
    "Forex": [
        {"name": "USD / INR", "sub": "US Dollar", "price": 83.12, "change": "+0.15%"},
        {"name": "EUR / INR", "sub": "Euro", "price": 90.45, "change": "-0.22%"},
        {"name": "GBP / INR", "sub": "British Pound", "price": 105.30, "change": "+0.41%"},
        {"name": "AED / INR", "sub": "UAE Dirham", "price": 22.63, "change": "-0.05%"}
    ],
    "Commodities": [
        {"name": "Gold (24K)", "sub": "1 Gram", "price": 7340.00, "change": "+1.20%"},
        {"name": "Gold (22K)", "sub": "1 Gram", "price": 6725.00, "change": "+1.15%"},
        {"name": "Silver", "sub": "1 Gram", "price": 84.50, "change": "+0.85%"},
        {"name": "Copper", "sub": "1 Gram", "price": 0.82, "change": "-0.30%"}
    ],
    "Stocks": [
        {"name": "Reliance Ind.", "sub": "NSE", "price": 2950.40, "change": "+1.14%"},
        {"name": "HDFC Bank", "sub": "NSE", "price": 1450.80, "change": "-1.22%"},
        {"name": "Tata Motors", "sub": "NSE", "price": 980.15, "change": "+2.05%"}
    ]
}

# 🛠️ FIXED: Completely flattened HTML string to prevent Markdown parsing errors
def draw_grid(items):
    html = '<div class="market-grid">'
    for asset in items:
        trend = "trend-pill-up" if "+" in asset['change'] else "trend-pill-down"
        icon = "▲" if "+" in asset['change'] else "▼"
        # Single line HTML to stop Streamlit formatting bugs
        html += f'<div class="ticker-card"><div class="asset-info"><span class="asset-name">{asset["name"]}</span><span class="asset-type">{asset["sub"]}</span></div><div class="price-info"><span class="price-val">₹{asset["price"]:.2f}</span><span class="{trend}">{icon} {asset["change"]}</span></div></div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

# --- 5. RENDER MARKETS ---
st.markdown("<div class='section-title'>💵 Global Forex</div>", unsafe_allow_html=True)
draw_grid(market_data["Forex"])

st.markdown("<div class='section-title'>🪙 Commodities</div>", unsafe_allow_html=True)
draw_grid(market_data["Commodities"])

st.markdown("<div class='section-title'>📊 Top F&O Stocks</div>", unsafe_allow_html=True)
draw_grid(market_data["Stocks"])

st.divider()

# --- 6. AI MARKET INSIGHT ---
st.markdown("### 🤖 ExpensoX Market AI")

@st.cache_data(show_spinner=False)
def get_market_analysis(data_str):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key: return "API Key missing in secrets.toml"
        genai.configure(api_key=api_key)
        
        prompt = f"Act as a quantitative stock market analyst. Data snapshot: {data_str}. Provide a 3-sentence summary of market sentiment. Mention Gold and Reliance. Be sharp and confident."
        
        model_names = ['gemini-3-flash', 'gemini-2.5-flash', 'gemini-pro']
        for m_name in model_names:
            try:
                model = genai.GenerativeModel(m_name)
                return model.generate_content(prompt).text
            except Exception: continue
        return "Market AI unavailable."
    except Exception as e: return f"Error: {e}"

with st.spinner("Analyzing live market sentiment..."):
    data_snapshot = str(market_data)
    ai_insight = get_market_analysis(data_snapshot)
    
    # Flattened this HTML block too just to be safe
    insight_html = f'<div style="background-color: #0f172a; padding: 20px; border-radius: 12px; border-left: 5px solid #3b82f6; color: #f8fafc; font-size: 0.95rem; line-height: 1.6; box-shadow: 0px 10px 15px -3px rgba(0,0,0,0.1);"><div style="color:#3b82f6; font-size:0.75rem; font-weight:bold; text-transform:uppercase; margin-bottom:8px;">Live Sentiment Analysis</div>{ai_insight}</div>'
    st.markdown(insight_html, unsafe_allow_html=True)