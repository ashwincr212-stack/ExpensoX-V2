import streamlit as st
import sqlite3
import pandas as pd
import smtplib
import threading
import google.generativeai as genai
from datetime import datetime
from theme_manager import apply_user_theme

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="My Profile", layout="centered")
apply_user_theme()

# --- 2. CSS ---
st.markdown("""
<style>
    .profile-header { background: linear-gradient(90deg, #f43f5e 0%, #fb923c 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 900; text-align: center; margin-bottom: 5px; }
    .profile-sub { text-align: center; color: #64748b; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; }
    .glass-card { background: #ffffff; border-radius: 20px; padding: 25px; border: 1px solid #f0f2f6; margin-bottom: 20px; box-shadow: 0px 10px 30px rgba(0, 0, 0, 0.04); }
    .avatar-img { width: 100px; height: 100px; border-radius: 50%; background: #f8fafc; border: 3px solid #f43f5e; padding: 5px; box-shadow: 0px 5px 15px rgba(244, 63, 94, 0.2); margin: 0 auto; display: block;}
    .username-text { text-align: center; font-size: 1.5rem; font-weight: 900; color: #1e293b; margin-top: 10px; }
    .badge-container { display: flex; justify-content: center; gap: 8px; margin-top: 10px; }
    .badge { background: #1e293b; color: #f8fafc; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; font-weight: 700; }
    .section-title { font-size: 1.1rem; font-weight: 800; color: #334155; margin-bottom: 15px; display: flex; align-items: center; gap: 8px; border-left: 4px solid #f43f5e; padding-left: 10px;}
    .stat-box { background: #f8fafc; border-radius: 15px; padding: 15px; text-align: center; border: 1px solid #e2e8f0; margin-bottom: 10px; }
    .stat-val { font-size: 1.3rem; font-weight: 900; color: #0f172a; }
    .stat-label { font-size: 0.65rem; color: #64748b; text-transform: uppercase; font-weight: 700; }
</style>
""", unsafe_allow_html=True)

# --- 3. MASTER INTELLIGENCE DISPATCHER ---
def full_intelligence_worker(receiver_email, username, wallet_bal, total_spent, tx_count, astro_res, secrets):
    try:
        # 1. AI ASTRO GENERATION
        genai.configure(api_key=secrets["GEMINI_API_KEY"])
        today = datetime.now().strftime("%B %d, %Y")
        
        prompt = f"Act as an elite financial astrologer. Today is {today}. User: {username}, Sign: {astro_res[0]}, Born: {astro_res[1]} at {astro_res[2]}. Provide 4 items: Money Energy, Favorable Focus, Avoid, and 3 specific clock timings (Good/Bad/Money). Keep it sharp and formatted for email."
        model = genai.GenerativeModel('gemini-1.5-flash')
        ai_response = model.generate_content(prompt).text
        
        # 2. MARKET DATA
        gold_24k, gold_22k, usd_inr = "₹7,340/g", "₹6,725/g", "₹83.12"

        # 3. EMAIL SETUP
        msg = MIMEMultipart()
        msg['From'] = f"ExpensoX Intelligence <{secrets['EMAIL_SENDER']}>"
        msg['To'] = receiver_email
        msg['Subject'] = f"🚀 FULL INTELLIGENCE REPORT: {username}"

        body = f"""
        <html><body style="font-family: Arial, sans-serif; color: #1e293b; line-height: 1.6;">
            <h2 style="color: #f43f5e;">ExpensoX Master Intelligence Report</h2>
            <p>Hello <b>{username}</b>, here is your complete personalized briefing for today.</p>
            
            <div style="background: #faf5ff; padding: 20px; border-radius: 12px; border: 1px solid #e9d5ff; margin-bottom: 20px;">
                <h3 style="color: #9333ea; margin-top: 0;">🔮 Daily Astro Insights</h3>
                {ai_response.replace('\n', '<br>')}
            </div>

            <div style="background: #fff7ed; padding: 20px; border-radius: 12px; border: 1px solid #fed7aa; margin-bottom: 20px;">
                <h3 style="color: #ea580c; margin-top: 0;">📈 Market Pulse</h3>
                <p><b>Gold 24K:</b> {gold_24k} | <b>Gold 22K:</b> {gold_22k}<br><b>USD/INR:</b> {usd_inr}</p>
            </div>

            <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                <h3 style="color: #3b82f6; margin-top: 0;">💰 Spend Summary</h3>
                <p><b>Wallet:</b> ₹{wallet_bal:,.2f}<br><b>Spent:</b> ₹{total_spent:,.2f} ({tx_count} tx)</p>
            </div>
        </body></html>
        """
        msg.attach(MIMEText(body, 'html'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(secrets["EMAIL_SENDER"], secrets["EMAIL_PASSWORD"])
        server.send_message(msg)
        server.quit()
    except Exception: pass

# --- 4. DATABASE LOGIC ---
current_user = st.session_state.get('username', 'Guest')
conn = sqlite3.connect('expenses.db')
c = conn.cursor()
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
avatar_url = f"https://api.dicebear.com/7.x/bottts-neutral/svg?seed={current_user}&backgroundColor=ffffff"
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
        st.markdown(f'<div style="background: rgba(192, 132, 252, 0.1); border-radius: 12px; padding: 15px; border: 1px solid rgba(192, 132, 252, 0.3); text-align: center;"><div style="font-size: 1.4rem;">{astro_res[0]}</div><div style="font-size: 0.75rem; color: #475569; font-weight: 600;">DOB: {astro_res[1]}</div><div style="font-size: 0.75rem; color: #475569; font-weight: 600;">Time: {astro_res[2]}</div></div>', unsafe_allow_html=True)
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
            conn = sqlite3.connect('expenses.db'); c = conn.cursor()
            c.execute("INSERT OR REPLACE INTO user_settings VALUES (?, ?, ?)", (current_user, email_input, 1 if is_active else 0))
            conn.commit(); conn.close(); st.success("Saved!")
    with btn_test:
        if st.button("⚡ Send Full Report", use_container_width=True, type="primary"):
            if email_input and astro_res:
                st.toast("AI is generating your full report...")
                threading.Thread(target=full_intelligence_worker, args=(email_input, current_user, wallet_bal, total_spent, tx_count, astro_res, st.secrets)).start()
                st.success("Full report dispatched!")
            else:
                st.warning("Please setup Astro Profile & Email first!")

st.divider()
if st.button("🚪 Log Out", use_container_width=True):
    st.session_state.clear(); st.rerun()