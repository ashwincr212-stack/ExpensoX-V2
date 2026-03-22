import streamlit as st
import sqlite3
import google.generativeai as genai
from datetime import date, time, datetime
from theme_manager import apply_user_theme

# --- 1. SETUP & THEME ---
st.set_page_config(page_title="Astro Insights", layout="centered")
apply_user_theme()

# --- 2. DATABASE SETUP FOR ASTRO PROFILE ---
def init_astro_db():
    conn = sqlite3.connect('expenses.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS astro_profile 
                 (username TEXT PRIMARY KEY, name TEXT, zodiac TEXT, dob TEXT, tob TEXT)''')
    conn.commit()
    conn.close()

init_astro_db()

# --- 3. ADVANCED NEBULA CSS ---
st.markdown("""
<style>
    .astro-title { text-align: center; background: linear-gradient(to right, #c084fc, #f472b6); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2.5rem; font-weight: 900; margin-bottom: 5px; letter-spacing: 1px; }
    .astro-sub { text-align: center; color: #94a3b8; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 3px; margin-bottom: 30px; }
    
    button[data-testid="baseButton-primary"] { background: linear-gradient(90deg, #7e22ce 0%, #db2777 100%) !important; color: white !important; border: none !important; padding: 10px 24px !important; font-size: 1.1rem !important; font-weight: 800 !important; border-radius: 12px !important; box-shadow: 0px 4px 15px rgba(219, 39, 119, 0.3) !important; transition: all 0.3s ease !important; width: 100%; margin-top: 5px; }
    button[data-testid="baseButton-primary"]:hover { transform: translateY(-2px); box-shadow: 0px 6px 20px rgba(219, 39, 119, 0.5) !important; }
    
    .oracle-card { background: #1e293b; border: 1px solid rgba(192, 132, 252, 0.3); border-radius: 20px; padding: 25px; margin-top: 25px; box-shadow: 0px 10px 25px rgba(0,0,0,0.1); }
    .oracle-header { text-align: center; font-size: 1.2rem; color: #e879f9; text-transform: uppercase; letter-spacing: 2px; font-weight: 900; margin-bottom: 20px; }
    
    .reading-box { background: rgba(255, 255, 255, 0.05); border-radius: 12px; padding: 15px; margin-bottom: 12px; border-left: 4px solid; }
    .box-title { font-size: 0.75rem; text-transform: uppercase; font-weight: 800; margin-bottom: 5px; letter-spacing: 1px;}
    .box-text { font-size: 1rem; line-height: 1.5; color: #f8fafc; }
    
    .timing-header { text-align: center; margin-top: 25px; font-size: 0.85rem; color: #a78bfa; font-weight: 800; text-transform: uppercase; letter-spacing: 2px; }
    .timing-row { display: flex; justify-content: space-between; margin-top: 10px; background: rgba(0,0,0,0.2); border-radius: 12px; padding: 15px; }
    .timing-col { text-align: center; flex: 1; }
    .timing-label { font-size: 0.65rem; color: #94a3b8; text-transform: uppercase; font-weight: bold; margin-bottom: 4px; }
    .timing-val { font-size: 0.95rem; font-weight: 900; }
</style>
""", unsafe_allow_html=True)

# --- 4. HEADER ---
c1, c2, c3 = st.columns([1, 4, 1], vertical_alignment="center")
with c1: 
    if st.button("🔙"): st.switch_page("pages/1_Expense_Tracker.py")
with c2: 
    st.markdown("<h1 class='astro-title'>✨ Astro Insights</h1><p class='astro-sub'>Quantitative Astrology</p>", unsafe_allow_html=True)
with c3: pass

# --- 5. LOAD SAVED PROFILE ---
current_user = st.session_state.get('username', 'Guest')
conn = sqlite3.connect('expenses.db')
c = conn.cursor()
c.execute("SELECT name, zodiac, dob, tob FROM astro_profile WHERE username=?", (current_user,))
saved_data = c.fetchone()
conn.close()

zodiac_list = ["Aries ♈", "Taurus ♉", "Gemini ♊", "Cancer ♋", "Leo ♌", "Virgo ♍", "Libra ♎", "Scorpio ♏", "Sagittarius ♐", "Capricorn ♑", "Aquarius ♒", "Pisces ♓"]
def_name = ""
def_z_index = 0
def_dob = date(1995, 1, 1)
def_tob = time(12, 0)

if saved_data:
    def_name = saved_data[0]
    if saved_data[1] in zodiac_list: def_z_index = zodiac_list.index(saved_data[1])
    try: def_dob = datetime.strptime(saved_data[2], "%Y-%m-%d").date()
    except: pass
    try: def_tob = datetime.strptime(saved_data[3], "%H:%M").time()
    except: pass

# --- 6. MAIN INTERFACE (INPUTS) ---
r1c1, r1c2 = st.columns(2)
with r1c1: user_name = st.text_input("First Name", value=def_name, placeholder="e.g. Rahul")
with r1c2: zodiac = st.selectbox("Star Sign", zodiac_list, index=def_z_index)

r2c1, r2c2 = st.columns(2)
with r2c1: dob = st.date_input("Date of Birth", value=def_dob, min_value=date(1920, 1, 1), max_value=date.today())
with r2c2: tob = st.time_input("Birth Time", value=def_tob)

# --- 7. SAVE / CLEAR OPTIONS ---
st.write("")
opt1, opt2 = st.columns(2)
with opt1:
    if st.button("💾 Save for Daily Updates", use_container_width=True):
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("INSERT OR REPLACE INTO astro_profile (username, name, zodiac, dob, tob) VALUES (?, ?, ?, ?, ?)", 
                  (current_user, user_name, zodiac, dob.strftime("%Y-%m-%d"), tob.strftime("%H:%M")))
        conn.commit()
        conn.close()
        st.success("Cosmic Profile Saved! 🌟")
with opt2:
    if st.button("🔄 Re-enter / Clear Cache", use_container_width=True):
        conn = sqlite3.connect('expenses.db')
        c = conn.cursor()
        c.execute("DELETE FROM astro_profile WHERE username=?", (current_user,))
        conn.commit()
        conn.close()
        st.cache_data.clear() # Clears the AI memory so it generates fresh!
        st.rerun()

st.divider()

# --- 8. AI STRUCTURAL EXTRACTION ---
@st.cache_data(show_spinner=False)
def get_financial_horoscope(today_date, name, sign, user_dob, user_time):
    try:
        api_key = st.secrets.get("GEMINI_API_KEY", "")
        if not api_key: return "Error|Missing API Key|Setup required.|--|--|--"
        genai.configure(api_key=api_key)
        
        # STRICT PROMPT to force clock times
        prompt = f"""Act as an elite financial astrologer. Today is {today_date}. User's name is {name}, sign is {sign}, born on {user_dob} at {user_time}. 
        You MUST return EXACTLY 6 short items separated by a single '|' character. No other text.
        CRITICAL: Items 4, 5, and 6 MUST be strictly clock time ranges ONLY (e.g., '10:00 AM - 11:30 AM'). DO NOT write sentences for the timings.
        Format: Overall Money Energy | Favorable Focus | Strictly Avoid | Good Time | Bad Time | Best Money Time"""
        
        model_names = ['gemini-3-flash', 'gemini-2.5-flash', 'gemini-pro']
        for m_name in model_names:
            try: return genai.GenerativeModel(m_name).generate_content(prompt).text
            except Exception: continue
        return "Stars clouded.|Try again.|Connection lost.|--|--|--"
    except Exception as e: return f"Error|{e}|Fix required.|--|--|--"

# --- 9. ACTION & OUTPUT ---
if st.button("🔮 Consult the Cosmos", use_container_width=True, type="primary"):
    if not user_name:
        st.warning("Please enter your name so the cosmos knows who to guide!")
    else:
        with st.spinner(f"Aligning the stars for {user_name}..."):
            today = date.today().strftime("%B %d, %Y")
            dob_str = dob.strftime("%B %d, %Y")
            tob_str = tob.strftime("%I:%M %p")
            
            raw_reading = get_financial_horoscope(today, user_name, zodiac, dob_str, tob_str)
            parts = raw_reading.split('|')
            
            if len(parts) >= 6: energy, favorable, avoid, t_good, t_bad, t_money = parts[0], parts[1], parts[2], parts[3], parts[4], parts[5]
            else: energy, favorable, avoid, t_good, t_bad, t_money = "Data unclear.", "Proceed with caution.", "Impulse buys.", "--", "--", "--"
            
            html_ui = f'<div class="oracle-card"><div class="oracle-header">Cosmic Reading for {user_name.upper()}</div>'
            html_ui += f'<div class="reading-box" style="border-left-color: #a855f7;"><div class="box-title" style="color: #c084fc;">✨ Cosmic Energy</div><div class="box-text">{energy.strip()}</div></div>'
            html_ui += f'<div class="reading-box" style="border-left-color: #10b981;"><div class="box-title" style="color: #34d399;">🍀 Favorable Focus</div><div class="box-text">{favorable.strip()}</div></div>'
            html_ui += f'<div class="reading-box" style="border-left-color: #ef4444;"><div class="box-title" style="color: #fb7185;">⚠️ Strictly Avoid</div><div class="box-text">{avoid.strip()}</div></div>'
            html_ui += '<div class="timing-header">⏳ Your Daily Timings</div>'
            html_ui += '<div class="timing-row">'
            html_ui += f'<div class="timing-col"><div class="timing-label">✅ Good Time</div><div class="timing-val" style="color:#10b981;">{t_good.strip()}</div></div>'
            html_ui += f'<div class="timing-col" style="border-left:1px solid rgba(255,255,255,0.1); border-right:1px solid rgba(255,255,255,0.1);"><div class="timing-label">⛔ Bad Time</div><div class="timing-val" style="color:#ef4444;">{t_bad.strip()}</div></div>'
            html_ui += f'<div class="timing-col"><div class="timing-label">💰 Money Time</div><div class="timing-val" style="color:#eab308;">{t_money.strip()}</div></div>'
            html_ui += '</div></div>'
            
            st.markdown(html_ui, unsafe_allow_html=True)