import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime, date
import plotly.express as px
from fpdf import FPDF
import re
import google.generativeai as genai
from theme_manager import apply_user_theme

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="ExpensoX Dashboard", layout="centered")
apply_user_theme()

# --- 2. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS expenses 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, category TEXT, amount REAL, date TEXT, description TEXT)''')
    
    c.execute("PRAGMA table_info(expenses)")
    columns = [col[1] for col in c.fetchall()]
    if 'username' not in columns:
        c.execute("ALTER TABLE expenses ADD COLUMN username TEXT")
    if 'description' not in columns:
        c.execute("ALTER TABLE expenses ADD COLUMN description TEXT")
    conn.commit()
    conn.close()

init_db()

# --- 3. AI FUNCTIONS (TIER 1 / 2026 STABLE) ---
@st.cache_data(show_spinner=False)
def get_ai_behavioral_projection(category_totals, total_spent, days_tracked):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key: return "API Key missing in secrets.toml"
        
        genai.configure(api_key=api_key)
        
        prompt = f"""
        You are ExpensoX, a blunt financial coach. 
        Analyze: ₹{total_spent} spent over {days_tracked} days. 
        Breakdown: {category_totals}.
        Specifically mention 'Smoke' and 'Liquor' costs.
        Predict month-end total and give one 5-word 'Hard Truth' fix.
        """

        # --- 2026 MODEL SELECTOR ---
        # We try the newest model first, then fall back to the generic ones
        model_names = ['gemini-3-flash', 'gemini-2.5-flash', 'gemini-pro']
        
        for m_name in model_names:
            try:
                model = genai.GenerativeModel(m_name)
                response = model.generate_content(prompt)
                return response.text
            except Exception:
                continue # Try the next model in the list
                
        return "All AI models are currently unavailable. Check your Tier 1 billing status."
        
    except Exception as e:
        return f"ExpensoX AI Error: {str(e)}"
    
def create_pdf(dataframe):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(190, 10, "ExpensoX Report", ln=True, align="C")
    pdf.ln(5)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(50, 10, "Date", border=1); pdf.cell(80, 10, "Category", border=1); pdf.cell(60, 10, "Amount", border=1, ln=True)
    pdf.set_font("Arial", "", 12)
    for _, row in dataframe.iterrows():
        pdf.cell(50, 10, str(row['date']), border=1)
        pdf.cell(80, 10, str(row['category']), border=1)
        pdf.cell(60, 10, f"Rs. {row['amount']}", border=1, ln=True)
    return pdf.output(dest='S').encode('latin-1')

# --- 4. DIALOGS ---
@st.dialog("Add New Expense")
def add_expense_dialog():
    amount = st.number_input("Amount (₹)", min_value=1.0, step=10.0)
    category = st.selectbox("Category", ["Food", "Bills", "Rent", "Medicines", "Smoke", "Liquor", "Other"])
    date_val = st.date_input("Date", datetime.today())
    if st.button("Save Expense", use_container_width=True, type="primary"):
        current_user = st.session_state.get('username', 'Guest')
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT INTO expenses (username, category, amount, date) VALUES (?, ?, ?, ?)", 
                  (current_user, category, amount, date_val.strftime("%d/%m/%y")))
        conn.commit(); conn.close()
        st.success("Saved!"); st.rerun()

@st.dialog("🤖 Smart Text Entry")
def ai_text_dialog():
    user_text = st.text_input("Example: '500 on Smoke'", placeholder="Type here...")
    if st.button("Auto-Log", use_container_width=True, type="primary"):
        num = re.search(r'\d+', user_text)
        amount = float(num.group()) if num else None
        found_cat = "Other"
        for cat in ["Food", "Bills", "Rent", "Medicines", "Smoke", "Liquor"]:
            if cat.lower() in user_text.lower(): found_cat = cat; break
        if amount:
            current_user = st.session_state.get('username', 'Guest')
            conn = sqlite3.connect('expenses.db'); c = conn.cursor()
            c.execute("INSERT INTO expenses (username, category, amount, date) VALUES (?, ?, ?, ?)", 
                      (current_user, found_cat, amount, datetime.today().strftime("%d/%m/%y")))
            conn.commit(); conn.close(); st.success("Logged!"); st.rerun()

# --- 5. CUSTOM CSS (Global Styles) ---
st.markdown("""
<style>
    .block-container { max-width: 480px; padding-top: 1.5rem; }
    .logo-text { color: #00C78C; font-weight: bold; font-size: 1.6rem; margin: 0; text-align: center; }
    
    .expense-card {
        background-color: #ffffff; padding: 10px 15px; border-radius: 12px;
        border-left: 6px solid #e2e8f0; margin-bottom: 12px;
        display: flex; justify-content: space-between; align-items: center;
        box-shadow: 0px 2px 4px rgba(0,0,0,0.05);
    }
    .card-smoke { border-left-color: #FF4B4B !important; }
    .card-liquor { border-left-color: #7D3CFF !important; }
    .card-amt { font-weight: bold; font-size: 1.1rem; color: #1e293b; }
    .card-date { color: #64748b; font-size: 0.8rem; }
    
    /* CUSTOM HTML CARD STYLES */
    .summary-row {
        display: flex;
        gap: 12px;
        margin-bottom: 20px;
    }
    .summary-card {
        flex: 1;
        background-color: white;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #f0f2f6;
        height: 90px;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    .card-label {
        font-size: 0.7rem;
        font-weight: bold;
        color: #00C78C;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 4px;
    }
    .card-value {
        font-size: 1.4rem;
        font-weight: 800;
        color: #1e293b;
        line-height: 1;
    }
</style>
""", unsafe_allow_html=True)

# --- 6. HEADER ---
c1, c2, c3, c4 = st.columns([1, 4, 1, 1], vertical_alignment="center")
with c1: 
    if st.button("🔙"):
        st.session_state['logged_in'] = False
        st.switch_page("app.py")
with c2: st.markdown("<p class='logo-text'>ExpensoX</p>", unsafe_allow_html=True)
with c3: st.button("📷")
with c4: st.button("📽️")
st.divider()

# --- 7. DATA FETCH ---
current_user = st.session_state.get('username', 'Guest')
conn = sqlite3.connect('expenses.db')
df = pd.read_sql_query("SELECT * FROM expenses WHERE username=? ORDER BY id DESC", conn, params=(current_user,))
conn.close()

tab1, tab2, tab3 = st.tabs(["Your Spends", "Summary", "AI Projections"])

# --- TAB 1: YOUR SPENDS ---
with tab1:
    today_str = date.today().strftime("%d/%m/%y")
    spent_today = df[df['date'] == today_str]['amount'].sum() if not df.empty else 0
    st.markdown("### Today's Focus")
    
    # Using Custom HTML for Today's Focus too for consistency
    st.markdown(f"""
        <div class="summary-card" style="height: 80px; margin-bottom: 15px; width: 100%;">
            <div class="card-label">Total Spent Today</div>
            <div class="card-value">₹{int(spent_today)}</div>
        </div>
    """, unsafe_allow_html=True)

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("➕ Add New", use_container_width=True, type="primary"):
            add_expense_dialog()
    with col_b:
        if st.button("🤖 AI Entry", use_container_width=True):
            ai_text_dialog()

    st.write("")
    st.markdown("### Monthly Overview")
    totals = {cat: df[df['category'] == cat]['amount'].sum() if not df.empty else 0 
              for cat in ["Food", "Smoke", "Liquor", "Bills"]}
    
    r1c1, r1c2 = st.columns(2)
    with r1c1:
        st.markdown(f"""<div class="summary-card" style="height: 70px;"><div class="card-label">🍲 Food</div><div class="card-value" style="font-size:1.1rem;">₹{int(totals['Food'])}</div></div>""", unsafe_allow_html=True)
    with r1c2:
        st.markdown(f"""<div class="summary-card" style="height: 70px; border-top: 3px solid #FF4B4B;"><div class="card-label" style="color:#FF4B4B;">🚬 Smoke</div><div class="card-value" style="font-size:1.1rem;">₹{int(totals['Smoke'])}</div></div>""", unsafe_allow_html=True)
        
    r2c1, r2c2 = st.columns(2)
    with r2c1:
        st.markdown(f"""<div class="summary-card" style="height: 70px; border-top: 3px solid #7D3CFF;"><div class="card-label" style="color:#7D3CFF;">🍷 Liquor</div><div class="card-value" style="font-size:1.1rem;">₹{int(totals['Liquor'])}</div></div>""", unsafe_allow_html=True)
    with r2c2:
        st.markdown(f"""<div class="summary-card" style="height: 70px; border-top: 3px solid #FFA500;"><div class="card-label" style="color:#FFA500;">💳 Bills</div><div class="card-value" style="font-size:1.1rem;">₹{int(totals['Bills'])}</div></div>""", unsafe_allow_html=True)
    
    st.divider()

    s1, s2 = st.columns([4, 1])
    query = s1.text_input("Search", placeholder="Search entries...", label_visibility="collapsed")
    with s2:
        with st.popover("⚙️"):
            cat_filt = st.selectbox("Filter", ["All", "Food", "Smoke", "Liquor", "Bills", "Rent", "Medicines"])

    view_df = df.copy()
    if query: view_df = view_df[view_df['category'].str.contains(query, case=False)]
    if cat_filt != "All": view_df = view_df[view_df['category'] == cat_filt]

    for _, row in view_df.iterrows():
        card_style = "expense-card"
        icon = "💸"
        if row['category'] == "Smoke": card_style += " card-smoke"; icon = "🚬"
        elif row['category'] == "Liquor": card_style += " card-liquor"; icon = "🍷"
        elif row['category'] == "Food": icon = "🍲"

        card_col, del_col = st.columns([5, 1], vertical_alignment="center")
        with card_col:
            st.markdown(f"""<div class="{card_style}"><div><span style='font-size:1.2rem;'>{icon}</span> 
            <span style='font-weight:600; margin-left:5px;'>{row['category']}</span><br>
            <span class="card-date">{row['date']}</span></div><div class="card-amt">₹{int(row['amount'])}</div></div>""", unsafe_allow_html=True)
        with del_col:
            if st.button("🗑️", key=f"del_{row['id']}"):
                conn = sqlite3.connect('expenses.db'); c = conn.cursor()
                c.execute("DELETE FROM expenses WHERE id=?", (row['id'],)); conn.commit(); conn.close(); st.rerun()

# --- TAB 2: SUMMARY (Fixed Identical Boxes) ---
with tab2:
    if not df.empty:
        total_spent = df['amount'].sum()
        cat_sums = df.groupby('category')['amount'].sum().sort_values(ascending=False)
        top_cat = cat_sums.idxmax()

        st.markdown("### Total Overview")
        
        st.markdown(f"""
        <div class="summary-row">
            <div class="summary-card">
                <div class="card-label">Total Monthly</div>
                <div class="card-value">₹{int(total_spent)}</div>
            </div>
            <div class="summary-card">
                <div class="card-label">Top Drain</div>
                <div class="card-value" style="font-size:1.2rem;">{top_cat}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.divider()
        st.markdown("### Spend Distribution")
        color_map = {"Smoke": "#FF4B4B", "Liquor": "#7D3CFF", "Food": "#00C78C", "Bills": "#FFA500", "Rent": "#007BFF", "Medicines": "#FF69B4", "Other": "#94a3b8"}
        fig = px.pie(df, values='amount', names='category', hole=0.7, color='category', color_discrete_map=color_map)
        fig.update_layout(showlegend=True, legend=dict(orientation="h", y=-0.2, xanchor="center", x=0.5), height=300, margin=dict(t=0, b=0, l=0, r=0))
        fig.add_annotation(text=f"₹{int(total_spent)}", showarrow=False, font_size=20, font_color="#1e293b", font_weight="bold")
        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

        st.markdown("### Category Intensity")
        for cat, amt in cat_sums.items():
            percentage = (amt / total_spent)
            col_l, col_r = st.columns([3, 1])
            col_l.markdown(f"**{cat}** <span style='color:gray; font-size:0.8rem;'>({int(percentage*100)}%)</span>", unsafe_allow_html=True)
            col_r.markdown(f"<p style='text-align:right; font-weight:bold;'>₹{int(amt)}</p>", unsafe_allow_html=True)
            st.progress(min(percentage, 1.0))
            
    else:
        st.info("Log an expense first!")

# --- TAB 3: AI PROJECTIONS (Alignment & Rendering Fix) ---
with tab3:
    st.markdown("### 🤖 Smart Forecast Station")
    
    if df.empty or len(df) < 2:
        st.info("Log at least 2 days of expenses to unlock AI projections.")
    else:
        # 1. CALCULATIONS
        total_spent = df['amount'].sum()
        first_date = datetime.strptime(df['date'].iloc[-1], "%d/%m/%y")
        days_tracked = max((datetime.today() - first_date).days, 1)
        daily_avg = total_spent / days_tracked
        projected_total = int(daily_avg * 30)

        # 2. CSS FOR SLIM TILES
        st.markdown("""
        <style>
            .top-insight-container {
                display: flex;
                justify-content: space-between;
                gap: 10px;
                width: 100%;
                margin-bottom: 20px;
            }
            .slim-tile {
                flex: 1;
                background-color: white;
                border-radius: 12px;
                padding: 10px;
                text-align: center;
                box-shadow: 0px 4px 6px rgba(0,0,0,0.05);
                border: 1px solid #f0f2f6;
                display: flex;
                flex-direction: column;
                justify-content: center;
                height: 80px;
            }
            .tile-label { font-size: 0.6rem; font-weight: bold; color: #64748b; text-transform: uppercase; margin-bottom: 2px; }
            .tile-value { font-size: 1.1rem; font-weight: 800; color: #1e293b; }
            
            .meter-bg { width: 100%; height: 6px; background: #e2e8f0; border-radius: 10px; margin-top: 5px; overflow: hidden; }
        </style>
        """, unsafe_allow_html=True)

        # Habit Math
        smoke_total = df[df['category'] == 'Smoke']['amount'].sum()
        liquor_total = df[df['category'] == 'Liquor']['amount'].sum()
        habit_perc = ((smoke_total + liquor_total) / total_spent)
        risk_color = "#00C78C" if habit_perc < 0.15 else "#FFA500" if habit_perc < 0.25 else "#FF4B4B"

        # 3. RENDER TILES (Crucial: unsafe_allow_html=True added)
        st.markdown(f"""
            <div class="top-insight-container">
                <div class="slim-tile" style="border-top: 3px solid #00C78C;">
                    <div class="tile-label">Est. Month End</div>
                    <div class="tile-value">₹{projected_total}</div>
                </div>
                <div class="slim-tile" style="border-top: 3px solid #7D3CFF;">
                    <div class="tile-label">Daily Burn</div>
                    <div class="tile-value">₹{int(daily_avg)}</div>
                </div>
                <div class="slim-tile" style="border-top: 3px solid {risk_color}; flex: 1.2;">
                    <div class="tile-label" style="color:{risk_color};">Habit Leakage</div>
                    <div class="tile-value" style="color:{risk_color};">{int(habit_perc * 100)}%</div>
                    <div class="meter-bg"><div style="width:{min(habit_perc, 1.0)*100}%; height:100%; background:{risk_color};"></div></div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # 4. AI ADVICE
        st.markdown("### 🧠 ExpensoX AI Advice")
        category_totals = df.groupby('category')['amount'].sum().to_dict()
        
        with st.spinner("Analyzing patterns..."):
            ai_report = get_ai_behavioral_projection(category_totals, total_spent, days_tracked)
            st.markdown(f"""
                <div style="background-color: #f8fafc; padding: 18px; border-radius: 15px; border-left: 5px solid #00C78C; font-size: 0.9rem; color: #1e293b;">
                    {ai_report}
                </div>
            """, unsafe_allow_html=True)
            
# --- 8. FOOTER ---
st.divider()
if not df.empty:
    st.download_button("📄 Download PDF Report", create_pdf(df), "report.pdf", "application/pdf", use_container_width=True)