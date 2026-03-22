import streamlit as st
import sqlite3
import smtplib
from email.message import EmailMessage

# --- 1. STRICT MOBILE CONFIG (MUST BE FIRST) ---
st.set_page_config(
    page_title="Expenso X - Entry", 
    page_icon="🔐", 
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 2. DATABASE AUTO-REPAIR & INIT ---
def init_db():
    conn = sqlite3.connect('expenso.db')
    c = conn.cursor()
    # Create users table with email column if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT)''')
    
    # Check if 'email' column exists (Migration check)
    c.execute("PRAGMA table_info(users)")
    columns = [column[1] for column in c.fetchall()]
    if 'email' not in columns:
        c.execute("ALTER TABLE users ADD COLUMN email TEXT")
        
    conn.commit()
    conn.close()

init_db()

# --- 3. SESSION STATE ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

# --- 4. THEME & MOBILE UI ENGINE (CSS) ---
# If not logged in, we force the dark abyss theme
if not st.session_state.logged_in:
    st.markdown("""
    <style>
        .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"] { 
            background-color: #020617 !important; 
        }
        .block-container { 
            max-width: 380px !important; 
            padding-top: 1.5rem !important; 
            margin: auto !important;
        }
        /* Image Alignment */
        [data-testid="stImage"] { display: flex; justify-content: center; width: 100%; }
        [data-testid="stImage"] > img { border-radius: 12px; }

        /* Input Boxes */
        label { color: #e2e8f0 !important; font-weight: bold; }
        div[data-testid="stTextInput"] input { 
            height: 3.5rem !important; 
            background-color: #0f172a !important; 
            color: white !important;
            border: 1px solid #1e293b !important;
            border-radius: 10px !important;
        }

        /* Tabs & Buttons */
        button[data-baseweb="tab"] { flex-grow: 1 !important; color: #94a3b8 !important; }
        .stButton > button { 
            width: 100% !important; height: 3.5rem !important; 
            background-color: #1e5631 !important; color: white !important;
            border-radius: 12px !important; margin-top: 10px;
        }
        .footer-col { font-size: 0.7rem; color: #475569; text-align: center; }
    </style>
    """, unsafe_allow_html=True)

# --- 5. DATABASE HELPERS ---
def check_login(u, p):
    conn = sqlite3.connect('expenso.db')
    user = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
    conn.close()
    return user

def add_user(u, p, e):
    try:
        conn = sqlite3.connect('expenso.db')
        conn.execute("INSERT INTO users (username, password, email) VALUES (?, ?, ?)", (u, p, e))
        conn.commit()
        conn.close()
        return True
    except:
        return False

# --- 6. THE LOGIN PAGE UI ---
def login_page():
    try:
        st.image("assets/logo.png", use_container_width=True) 
    except:
        st.image("https://via.placeholder.com/400x150.png?text=Expenso+X", use_container_width=True)

    tab1, tab2, tab3 = st.tabs(["Sign IN", "Register", "Recovery"])

    with tab1:
        st.write("<br>", unsafe_allow_html=True)
        u = st.text_input("Username", key="l_u", placeholder="Enter your username")
        p = st.text_input("Password", type="password", key="l_p", placeholder="••••••••")
        if st.button("LOGIN"):
            if check_login(u, p):
                st.session_state.logged_in = True
                st.session_state.username = u
                st.rerun()
            else:
                st.error("Invalid Username or Password.")

    with tab2:
        st.write("<br>", unsafe_allow_html=True)
        with st.expander("📄 View Beta & Privacy Terms"):
            st.markdown("<div style='font-size: 0.8rem; color: #94a3b8;'>Testing Phase 1: Data is stored locally. No sensitive data is shared.</div>", unsafe_allow_html=True)
        
        reg_u = st.text_input("Username", placeholder="Create username", key="reg_user")
        reg_p = st.text_input("Password", type="password", key="r_p", placeholder="Create password")
        reg_e = st.text_input("Email ID", placeholder="your@email.com", key="reg_email")
        agreed = st.checkbox("I understand this is a Beta Version.")

        if st.button("REGISTER"):
            if not agreed:
                st.warning("Please acknowledge terms.")
            elif not reg_u or not reg_p:
                st.error("Fill required fields.")
            else:
                if add_user(reg_u, reg_p, reg_e):
                    st.success("Success! Please Sign IN.")
                else:
                    st.error("User exists or DB error.")

    with tab3:
        st.write("<br>", unsafe_allow_html=True)
        rec_email = st.text_input("Email ID", key="rec_e", placeholder="Registered email")
        if st.button("Recover Password"):
            conn = sqlite3.connect('expenso.db')
            user_data = conn.execute("SELECT username, password FROM users WHERE email=?", (rec_email,)).fetchone()
            conn.close()
            
            if user_data:
                # Note: This requires EMAIL_SENDER/PASSWORD in .streamlit/secrets.toml
                try:
                    msg = EmailMessage()
                    msg['Subject'] = "Expenso X: Recovery"
                    msg['From'] = st.secrets["EMAIL_SENDER"]
                    msg['To'] = rec_email
                    msg.set_content(f"User: {user_data[0]}\nPass: {user_data[1]}")
                    
                    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                        smtp.login(st.secrets["EMAIL_SENDER"], st.secrets["EMAIL_PASSWORD"])
                        smtp.send_message(msg)
                    st.success("✅ Sent to your email!")
                except Exception as e:
                    st.error(f"Setup Secrets to use this feature.")
            else:
                st.error("Email not found.")

    st.write("---")
    st.markdown("<p class='footer-col'>© 2026 | AES-256 Secured</p>", unsafe_allow_html=True)

# --- 7. NAVIGATION ---
# Define the pages
login_screen = st.Page(login_page, title="Log In", icon="🔐")
expense_tracker = st.Page("pages/1_Expense_Tracker.py", title="Expense Tracker", icon="💰")
market_pulse = st.Page("pages/2_Market_Pulse.py", title="Market Pulse", icon="📈")
astro_insights = st.Page("pages/3_Astro_Insights.py", title="Astro Insights", icon="☀️")
ai_chat = st.Page("pages/4_AI_Quick_Chat.py", title="AI Quick Chat", icon="🤖")
profile_page = st.Page("pages/5_Profile.py", title="Profile", icon="👤")

# Route based on login state
if st.session_state.logged_in:
    
    # --- ADD THE LOGOUT BUTTON TO THE SIDEBAR ---
    with st.sidebar:
        # Pushes the button to the bottom under the menu
        st.markdown("<br><br>", unsafe_allow_html=True) 
        if st.button("Log Out", type="primary", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.username = ""
            st.rerun()
    # --------------------------------------------

    pg = st.navigation({
        "Dashboard": [expense_tracker],
        "Intelligence": [market_pulse, astro_insights, ai_chat],
        "Account": [profile_page]
    })
else:
    pg = st.navigation([login_screen])

pg.run()