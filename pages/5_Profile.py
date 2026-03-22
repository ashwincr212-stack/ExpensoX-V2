import streamlit as st
import sqlite3
import pandas as pd
import smtplib
import threading
import google.generativeai as genai
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from theme_manager import apply_user_theme

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="My Profile", layout="centered")
apply_user_theme()

# --- 2. CSS ---
st.markdown("""
<style>
    .profile-header { background: linear-gradient(90deg, #f43f5e 0%, #fb923c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 900; text-align: center; margin-bottom: 5px; }
    .profile-sub { text-align: center; color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; }
    .glass-card { background: rgba(255, 255, 255, 0.05); border-radius: 20px; padding: 25px; border: 1px solid rgba(255, 255, 255, 0.1); margin-bottom: 20px; backdrop-filter: blur(10px); }
    .avatar-img { width: 100px; height: 100px; border-radius: 50%; background: #f8fafc; border: 3px solid #f43f5e; padding: 5px; margin: 0 auto; display: block;}
    .username-text { text-align: center; font-size: 1.5rem; font-weight: 900; color: #f8fafc; margin-top: 10px; }
    .badge-container { display: flex; justify-content: center; gap: 8px; margin-top: 10px; }
    .badge { background: #f43f5e; color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
    .section-title { font-size: 1.1rem; font-weight: 800; color: #f8fafc; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-left: 4px solid #f43f5e; padding-left: 10px;}
    .stat-box { background: rgba(255, 255, 255, 0.03); border-radius: 15px; padding: 15px; text-align: center; border: 1px solid rgba(255, 255, 255, 0.05); margin-bottom: 10px; }
    .stat-val { font-size: 1.3rem; font-weight: 900; color: #f8fafc; }
    .stat-label { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER INTELLIGENCE DISPATCHER ---
def full_intelligence_worker(receiver_email, username, wallet_bal, total_spent, tx_count, astro_res, secrets):
    try:
        genai.configure(api_key=secrets["GEMINI_API_KEY"])
        today = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"Act as an elite financial astrologer. Today is {today}. User: {username}, Sign: {astro_res[0]}, Born: {astro_res[1]} at {astro_res[2]}. Provide 4 items: Money Energy, Favorable Focus, Avoid, and 3 specific clock timings. Sharp formatting."
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_response = model.generate_content(prompt).text
        
        msg = MIMEMultipart()
        msg['From'] = f"ExpensoX Intelligence <{secrets['EMAIL_SENDER']}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🚀 FULL INTELLIGENCE REPORT: {username}"

        body = f"<html><body><h2 style='color:#f43f5e;'>Intelligence Report</h2><p>{ai_response.replace('\n', '<br>')}</p></body></html>"
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(secrets["EMAIL_SENDER"], secrets["EMAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Email Error: {e}")

# --- 4. DATABASE LOGIC ---
current_user = st.session_state.get('username', 'Guest')
conn = sqlite3.connect('expenso.db') # Consistent with app.py
c = conn.cursor()

# 🚨 Ensure all tables exist for a fresh live environment
c.execute("CREATE TABLE IF NOT EXISTS user_settings (username TEXT PRIMARY KEY, email TEXT, daily_email INTEGER)")
c.execute("CREATE TABLE IF NOT EXISTS wallet (username TEXT PRIMARY KEY, balance REAL)")
c.execute("CREATE TABLE IF NOT EXISTS expenses (username TEXT, category TEXT, amount REAL, date TEXT, description TEXT)")
c.execute("CREATE TABLE IF NOT EXISTS astro_profile (username TEXT PRIMARY KEY, zodiac TEXT, dob TEXT, tob TEXT)")
conn.commit()

c.execute("SELECT email, daily_email FROM user_settings WHERE username=?", (current_user,))
settings_res = c.fetchone()
saved_email = settings_res[0] if settings_res else ""
email_enabled = bool(settings_res[1]) if settings_res else False

c.execute("SELECT balance FROM wallet WHERE username=?", (current_user,))
w_res = c.fetchone()
wallet_bal = w_res[0] if w_res else 0.0

df_exp = pd.read_sql_query("SELECT amount FROM expenses WHERE username=?", conn, params=(current_user,))
total_spent = df_exp['amount'].sum() if not df_exp.empty else 0.0
tx_count = len(df_exp)

c.execute("SELECT zodiac, dob, tob FROM astro_profile WHERE username=?", (current_user,))
astro_res = c.fetchone()
conn.close()

# --- 5. HEADER & PROFILE CARD ---
st.markdown("<h1 class='profile-header'>🧑‍🚀 Command Center</h1><p class='profile-sub'>Intelligence & Automation</p>", unsafe_allow_html=True)
avatar_url = f"https://api.dicebear.com/7.x/bottts-neutral/svg?seed={current_user}"
st.markdown(f'<div class="glass-card"><img src="{avatar_url}" class="avatar-img"><div class="username-text">@{current_user.upper()}</div><div class="badge-container"><div class="badge">PRO MEMBER</div><div class="badge">EARLY ADOPTER</div></div></div>', unsafe_allow_html=True)

# --- 6. STATS & COSMIC GRID ---
col_left, col_right = st.columns(2)
with col_left:
    st.markdown("<div class='section-title'>📊 Lifetime Stats</div>", unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-val">₹{total_spent:,.2f}</div><div class="stat-label">Total Spent</div></div>', unsafe_allow_html=True)
    st.markdown(f'<div class="stat-box"><div class="stat-val">{tx_count}</div><div class="stat-label">Transactions</div></div>', unsafe_allow_html=True)
with col_right:
    st.markdown("<div class='section-title'>✨ Cosmic Profile</div>", unsafe_allow_html=True)
    if astro_res:
        st.markdown(f'<div style="background: rgba(192, 132, 252, 0.1); border-radius: 12px; padding: 15px; border: 1px solid rgba(192, 132, 252, 0.3); text-align: center;"><div style="font-size: 1.4rem; color:white;">{astro_res[0]}</div><div style="font-size: 0.75rem; color: #94a3b8;">DOB: {astro_res[1]}</div></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div style="text-align: center; color: #94a3b8; font-size: 0.8rem; padding: 20px;">No Astro Data.</div>', unsafe_allow_html=True)

# --- 7. AUTOMATION ---
st.markdown("<div class='section-title'>🤖 ExpensoX Automation</div>", unsafe_allow_html=True)
with st.container(border=True):
    email_input = st.text_input("Receiver Email Address", value=saved_email)
    is_active = st.toggle("Enable Daily Reports", value=email_enabled)
    btn_save, btn_test = st.columns(2)
    with btn_save:
        if st.button("🚀 Save Settings", use_container_width=True):
            conn = sqlite3.connect('expenso.db'); c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO user_settings VALUES (?, ?, ?)", (current_user, email_input, 1 if is_active else 0))
            conn.commit(); conn.close(); st.success("Saved!")
    with btn_test:
        if st.button("⚡ Send Full Report", use_container_width=True, type="primary"):
            if email_input and astro_res:
                st.toast("AI Dispatching...")
                threading.Thread(target=full_intelligence_worker, args=(email_input, current_user, wallet_bal, total_spent, tx_count, astro_res, st.secrets)).start()
                st.success("Report Sent!")
            else:
                st.warning("Setup Astro Profile & Email first!")

st.divider()
if st.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear(); st.switch_page("app.py")
