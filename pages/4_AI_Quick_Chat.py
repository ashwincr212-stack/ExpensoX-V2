import streamlit as st
import sqlite3
import pandas as pd
import google.generativeai as genai
from theme_manager import apply_user_theme

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="AI Quick Chat", layout="centered")
apply_user_theme()

# --- 2. CLEAN FINTECH CSS ---
st.markdown("""
<style>
    /* Gradient Header Typography */
    .chat-header { 
        background: linear-gradient(90deg, #00C78C 0%, #3b82f6 100%); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent; 
        font-size: 2.5rem; 
        font-weight: 900; 
        text-align: center; 
        margin-bottom: 5px; 
    }
    .chat-sub { 
        text-align: center; 
        color: #64748b; 
        font-size: 0.85rem; 
        text-transform: uppercase; 
        letter-spacing: 3px; 
        margin-bottom: 30px; 
    }
    
    /* Clean White Chat Bubbles with Shadows */
    [data-testid="stChatMessage"] { 
        background-color: #ffffff !important; 
        border-radius: 16px !important; 
        padding: 15px 20px !important; 
        border: 1px solid #f0f2f6 !important; 
        margin-bottom: 15px !important; 
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.05) !important;
    }
    
    /* Force Text Color to be Dark & Readable */
    [data-testid="stChatMessage"] p, [data-testid="stChatMessage"] div {
        color: #1e293b !important;
        font-size: 1.05rem !important;
        line-height: 1.6 !important;
    }
    
    /* Floating Chat Input Container */
    [data-testid="stChatInput"] { 
        background-color: #ffffff !important; 
        border: 1px solid #e2e8f0 !important; 
        border-radius: 25px !important; 
        box-shadow: 0px 8px 25px rgba(0, 0, 0, 0.08) !important; 
        padding-left: 10px !important;
    }
    
    /* Chat Input Text Area */
    [data-testid="stChatInput"] textarea {
        color: #1e293b !important;
        font-size: 1.05rem !important;
    }

    /* Send Button Arrow Color (ExpensoX Green) */
    [data-testid="stChatInputSubmitButton"] {
        color: #00C78C !important;
    }
    [data-testid="stChatInputSubmitButton"]:hover {
        color: #3b82f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HEADER ---
c1, c2, c3 = st.columns([1, 4, 1], vertical_alignment="center")
with c1: 
    if st.button("🔙"): st.switch_page("pages/1_Expense_Tracker.py")
with c2: 
    st.markdown("<h1 class='chat-header'>🧠 ExpensoX AI</h1><p class='chat-sub'>Your Personal Wealth Analyst</p>", unsafe_allow_html=True)
with c3:
    if st.button("🗑️ Clear"):
        st.session_state.messages = []
        st.rerun()

st.divider()

# --- 4. FETCH LIVE DATABASE CONTEXT ---
@st.cache_data(ttl=60)
def get_financial_context(username):
    try:
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        
        c.execute("CREATE TABLE IF NOT EXISTS wallet (username TEXT PRIMARY KEY, balance REAL)")
        c.execute("SELECT balance FROM wallet WHERE username=?", (username,))
        res = c.fetchone()
        wallet_bal = res[0] if res else 0.0
        
        c.execute("CREATE TABLE IF NOT EXISTS expenses (id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT, category TEXT, amount REAL, date TEXT, description TEXT)")
        df = pd.read_sql_query("SELECT category, amount, date FROM expenses WHERE username=? ORDER BY id DESC", conn, params=(username,))
        conn.close()
        
        if df.empty: return f"Wallet Balance: ₹{wallet_bal}. No expenses logged yet."
            
        total_spent = df['amount'].sum()
        cat_summary = df.groupby('category')['amount'].sum().to_dict()
        recent_tx = df.head(5).to_dict('records')
        
        return f"DATA FOR {username.upper()}:\n- Wallet: ₹{wallet_bal}\n- Spent: ₹{total_spent}\n- By Category: {cat_summary}\n- Last 5 Tx: {recent_tx}"
    except Exception as e:
        return f"Could not fetch data: {e}"

current_user = st.session_state.get('username', 'Guest')
user_data_snapshot = get_financial_context(current_user)

# --- 5. INITIALIZE CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": f"System online. I've analyzed your latest data, {current_user.title()}. What would you like to know about your finances today?"}]

# --- 6. DISPLAY CHAT HISTORY ---
for message in st.session_state.messages:
    avatar_icon = "🧠" if message["role"] == "assistant" else "👤"
    with st.chat_message(message["role"], avatar=avatar_icon):
        st.markdown(message["content"])

# --- 7. HANDLE USER INPUT & AI LOGIC ---
if prompt := st.chat_input("Ask about your budget, habits, or financial advice..."):
    # Display user message
    with st.chat_message("user", avatar="👤"): 
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # Secret AI Prompt with injected DB context
    full_prompt = f"Act as ExpensoX, a blunt, highly intelligent financial advisor. User's real-time data: {user_data_snapshot}. User's message: '{prompt}'. Answer directly using their data. Keep it under 3 paragraphs. Use bullet points if helpful."

    # Fetch AI Response
    with st.chat_message("assistant", avatar="🧠"):
        with st.spinner("Analyzing your data..."):
            try:
                api_key = st.secrets.get("GEMINI_API_KEY", "")
                if not api_key:
                    st.error("API Key missing in secrets.toml.")
                else:
                    genai.configure(api_key=api_key)
                    response_text = "API Error."
                    
                    for m_name in ['gemini-3-flash', 'gemini-2.5-flash', 'gemini-pro']:
                        try:
                            model = genai.GenerativeModel(m_name)
                            response = model.generate_content(full_prompt)
                            response_text = response.text
                            break
                        except Exception: continue
                    
                    st.markdown(response_text)
                    st.session_state.messages.append({"role": "assistant", "content": response_text})
            except Exception as e:
                st.error(f"Brain connection lost: {e}")