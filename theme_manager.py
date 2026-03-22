import sqlite3
import streamlit as st

def apply_user_theme():
    # 1. THEME LOGIC
    if st.session_state.get('logged_in') and st.session_state.get('username'):
        username = st.session_state.username
        conn = sqlite3.connect('expenso.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS user_profile (username TEXT PRIMARY KEY, bg_color TEXT)''')
        row = conn.execute("SELECT bg_color FROM user_profile WHERE username=?", (username,)).fetchone()
        conn.close()
        theme_color = row[0] if row else "#020617"
    else:
        theme_color = "#020617"

    # 2. MASTER CSS: The Floating Red Power Button
    st.markdown(f"""
    <style>
        /* Main App Background */
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] {{
            background-color: {theme_color} !important;
        }}

        /* --- 🔴 THE FLOATING RED POWER BUTTON --- */
        /* Targets the button specifically when sidebar is CLOSED */
        [data-testid="stSidebarCollapsedControl"] {{
            left: 20px !important;
            top: 20px !important;
            background-color: #ef4444 !important;
            border-radius: 50% !important; /* Makes it a perfect circle */
            width: 50px !important;
            height: 50px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            box-shadow: 0px 0px 20px rgba(239, 68, 68, 0.6) !important;
            border: 2px solid #ffffff !important;
            z-index: 999999 !important;
            transition: transform 0.3s ease !important;
        }}
        
        [data-testid="stSidebarCollapsedControl"]:hover {{
            transform: scale(1.1) rotate(90deg) !important;
        }}

        /* Icon inside the circle */
        [data-testid="stSidebarCollapsedControl"] svg {{
            fill: white !important;
            width: 25px !important;
            height: 25px !important;
        }}

        /* Targets the 'X' button when sidebar is OPEN */
        [data-testid="stSidebar"] button[kind="header"] {{
            background-color: #ef4444 !important;
            color: white !important;
            border-radius: 10px !important;
        }}

        /* --- MODERN SIDEBAR --- */
        [data-testid="stSidebar"] {{
            background-color: #0f172a !important; 
            border-right: 1px solid rgba(255, 255, 255, 0.1);
        }}

        [data-testid="stSidebarNav"] li {{
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
            margin: 8px 15px !important;
            border: 1px solid rgba(255, 255, 255, 0.05);
        }}

        [data-testid="stSidebarNav"] a span {{
            color: #f8fafc !important; 
            font-weight: 700 !important;
        }}
    </style>
    """, unsafe_allow_html=True)