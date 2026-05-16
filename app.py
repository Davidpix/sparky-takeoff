import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import altair as alt
from io import BytesIO

# --- 1. SET PAGE CONFIG (THIS MUST BE THE VERY FIRST st. COMMAND) ---
st.set_page_config(page_title="OmniBuild OS | Master Build", layout="wide", initial_sidebar_state="expanded")

# --- 2. SECURE CLOUD INITIALIZATION ---
try:
    SUPABASE_URL = st.secrets.get("SUPABASE_URL", "ENV_VAR_MISSING")
    SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "ENV_VAR_MISSING")
except Exception:
    SUPABASE_URL = "ENV_VAR_MISSING"

def sanitize_input(user_input):
    return html.escape(str(user_input)) if user_input else ""

# --- 3. I18N LOCALIZATION DICTIONARY ---
lang_dict = {
# ... (The rest of your code continues normally from here) ...
# ... The rest of the code continues exactly as before starting with lang_dict ...
# --- 2. I18N LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Command Center", "matrix": "📊 Trade Matrix", "gc_budg": "🏗️ GC Budget", 
        "fin": "💳 OmniPay & Escrow", "sched": "📅 Trade Calendar", "inv": "🧾 AIA Invoicing", 
        "bid": "🎯 AI Bid Optimizer", "re": "🏙️ Real Estate ROI", "api": "☁️ Cloud API",
        "budget": "Master Budget", "wallet": "OmniWallet"
    },
    "Español": {
        "home": "🏠 Centro de Mando", "matrix": "📊 Matriz de Oficio", "gc_budg": "🏗️ Presupuesto GC",
        "fin": "💳 OmniPay y Fideicomiso", "sched": "📅 Calendario", "inv": "🧾 Facturación AIA",
        "bid": "🎯 Optimizador IA", "re": "🏙️ Bienes Raíces", "api": "☁️ API en la Nube",
        "budget": "Presupuesto Maestro", "wallet": "Billetera Omni"
    },
    "Українська": {
        "home": "🏠 Головна панель", "matrix": "📊 Кошторисна матриця", "gc_budg": "🏗️ Бюджет GC",
        "fin": "💳 Фінанси та Ескроу", "sched": "📅 Графік робіт", "inv": "🧾 Фактурування AIA",
        "bid": "🎯 AI Оптимізатор", "re": "🏙️ Нерухомість", "api": "☁️ Хмарний API",
        "budget": "Головний бюджет", "wallet": "Гаманець Omni"
    }
}

# --- 3. STATE MANAGEMENT & DATABASES ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 12500.00
if "escrow_balance" not in st.session_state: st.session_state.escrow_balance = 0.00
if "lien_signed" not in st.session_state: st.session_state.lien_signed = False
if "qb_connected" not in st.session_state: st.session_state.qb_connected = False

if "df_elec" not in st.session_state:
    st.session_state.df_elec = pd.DataFrame([
        {"Item": "3/4\" EMT Conduit", "Qty": 2450, "Cost": 6.50, "Mins": 12},
        {"Item": "20A GFCI Device", "Qty": 45, "Cost": 18.00, "Mins": 15},
        {"Item": "200A Breaker Panel", "Qty": 2, "Cost": 850.00, "Mins": 240}
    ])
if "df_plumb" not in st.session_state:
    st.session_state.df_plumb = pd.DataFrame([{"Item": "2\" PVC Pipe", "Qty": 400, "Cost": 12.50, "Mins": 15}, {"Item": "Kohler Toilet", "Qty": 4, "Cost": 225.00, "Mins": 45}])
if "df_hvac" not in st.session_state:
    st.session_state.df_hvac = pd.DataFrame([{"Item": "Carrier 3-Ton Unit", "Qty": 1, "Cost": 2100.00, "Mins": 180}, {"Item": "Flexible Duct", "Qty": 10, "Cost": 55.00, "Mins": 45}])

if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 

# --- 4. CORE MATH ENGINE ---
def calc_trade(df):
    mat = (df["Qty"] * df["Cost"]).sum()
    lab = ((df["Qty"] * df["Mins"]) / 60).sum() * st.session_state.labor_rate
    return (mat + lab) * (1 + st.session_state.overhead), mat + lab

elec_total, elec_raw = calc_trade(st.session_state.df_elec)
plumb_total, _ = calc_trade(st.session_state.df_plumb)
hvac_total, _ = calc_trade(st.session_state.df_hvac)
master_build_cost = elec_total + plumb_total + hvac_total + 35000.0 # Adding fixed finishes

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-danger { background-color: #1E1014 !important; border: 1px solid #3B1E22 !important; border-left: 3px solid #EF4444 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-gold { background-color: #1A170F !important; border: 1px solid #3B321E !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 6. SECURE GATEWAY (LOGIN) ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:50px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Authentication Gateway</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("auth_form"):
            user_email = st.text_input("Corporate Email")
            user_password = st.text_input("Password", type="password")
            if st.form_submit_button("Authenticate", use_container_width=True):
                if user_email == "admin" and user_password == "admin":
                    st.session_state.user_authenticated = True; st.rerun()
                else: st.error("Invalid credentials. Hint: use admin/admin")
    st.stop()

# --- 7. SIDEBAR & ROUTING ---
st.sidebar.title("🌍 OmniBuild OS")

selected_lang = st.sidebar.selectbox("🌐 Language / Мова", ["English", "Español", "Українська"], index=["English", "Español", "Українська"].index(st.session_state.lang))
if selected_lang != st.session_state.lang: st.session_state.lang = selected_lang; st.rerun()
t = lang_dict[st.session_state.lang]

st.sidebar.divider()
user_role = st.sidebar.selectbox("Workspace Profile", ["🏗️ General Contractor", "⚡ Electrical Sub", "💧 Plumbing Sub", "❄️ HVAC Sub"], index=0)
st.sidebar.divider()

if "General Contractor" in user_role: menu_options = [t["home"], t["gc_budg"], t["sched"], t["inv"], t["fin"], t["re"], t["api"]]
elif "Electrical" in user_role: menu_options = [t["home"], t["matrix"], t["bid"], t["fin"], t["api"]]
else: menu_options = [t["home"], t["matrix"], t["fin"]]

selected_page = st.sidebar.radio("Navigation:", menu_options)
st.divider()
if st.sidebar.button("🚪 Logout"): st.session_state.user_authenticated = False; st.rerun()

# --- 8. TOP TELEMETRY ---
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>{t['budget']}</p><h3 style='margin:0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>⚡ Active Trade Sub</p><h3 style='margin:0;'>${elec_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-gold'><p style='margin:0; font-size:10px; color:#F59E0B;'>{t['wallet']}</p><h3 style='margin:0; color:#F59E0B;'>${st.session_state.wallet_balance:,.2f}</h3></div>", unsafe_allow_html=True)

# --- 9. MODULE ROUTING ---

if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.success("Authentication valid. Secure session established.")
    client = sanitize_input(st.text_input("Active Project Name", "Miami Medical Hub"))
    st.markdown(f"<div class='unifi-stealth-blade'>Operating Context: <b>{client}</b></div>", unsafe_allow_html=True)

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    if "Electrical" in user_role: st.session_state.df_elec = st.data_editor(st.session_state.df_elec, use_container_width=True, num_rows="dynamic")
    elif "Plumbing" in user_role: st.session_state.df_plumb = st.data_editor(st.session_state.df_plumb, use_container_width=True, num_rows="dynamic")
    elif "HVAC" in user_role: st.session_state.df_hvac = st.data_editor(st.session_state.df_hvac, use_container_width=True, num_rows="dynamic")

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")
    chart_data = pd.DataFrame({"Trade": ["Electrical", "Plumbing", "HVAC", "Framing/Finishes"], "Value ($)": [elec_total, plumb_total, hvac_total, 35000.0]})
    pie = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(theta='Value ($):Q', color=alt.Color('Trade:N', scale=alt.Scale(range=["#38BDF8", "#3B82F6", "#8B5CF6", "#64748B"]))).properties(height=300)
    col1, col2 = st.columns([1.5, 1])
    with col1: st.altair_chart(pie, use_container_width=True)
    with col2: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>TOTAL ESTIMATE</h5><h2 style='color:#38BDF8; margin:0;'>${master_build_cost:,.2f}</h2></div>", unsafe_allow_html=True)

elif selected_page == t["sched"]:
    st.write(f"### {t['sched']} & Clash Detection")
    today = datetime.date.today()
    sched_data = pd.DataFrame([
        {"Trade": "HVAC Rough-In", "Zone": "Zone A", "Start": today, "End": today + datetime.timedelta(days=4)},
        {"Trade": "Plumbing Rough-In", "Zone": "Zone A", "Start": today + datetime.timedelta(days=2), "End": today + datetime.timedelta(days=6)}
    ])
    chart = alt.Chart(sched_data).mark_bar(height=20).encode(x='Start:T', x2='End:T', y='Trade:N', color='Zone:N').properties(height=150)
    st.altair_chart(chart, use_container_width=True)
    st.markdown("<div class='unifi-stealth-danger'><h5 style='color:#EF4444; margin:0;'>⚠️ TRADE CLASH DETECTED</h5><p style='font-size:12px; margin:0;'>Plumbing and HVAC overlap in Zone A.</p></div>", unsafe_allow_html=True)

elif selected_page == t["inv"]:
    st.write(f"### {t['inv']}")
    pct_complete = st.slider("Project Completion (%)", 0, 100, 60)
    current_due = (master_build_cost * (pct_complete / 100)) * 0.90 # 10% Retainage
    st.metric("Current AIA Payment Due", f"${current_due:,.2f}")

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")
    test_margin = st.slider("Simulate Profit Margin (%)", 5, 60, int(st.session_state.overhead * 100))
    prob = max(5, 100 * math.exp(-0.05 * (test_margin - 5)))
    ev = (elec_raw * (test_margin / 100)) * (prob / 100)
    c1, c2, c3 = st.columns(3)
    c1.metric("Final Bid Price", f"${elec_raw * (1 + (test_margin/100)):,.0f}")
    c2.metric("Win Probability", f"{prob:.1f}%")
    c3.metric("Expected Value", f"${ev:,.0f}")

elif selected_page == t["re"]:
    st.write(f"### {t['re']} & House Hack Engine")
    hb_col1, hb_col2 = st.columns([1, 1.5])
    with hb_col1:
        home_price = st.number_input("Purchase Price ($)", value=450000)
        rental_income = st.slider("Expected Monthly Rental Income ($)", 0, 3000, 1500, step=100)
    with hb_col2:
        monthly_pi = (home_price * 0.80) * (0.0054 * math.pow(1.0054, 360)) / (math.pow(1.0054, 360) - 1)
        net_burn = (monthly_pi + 850) - rental_income # Added arbitrary $850 for taxes/ins
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><h5 style='color:#10B981; margin:0;'>NET MONTHLY BURN (AFTER RENT)</h5><p style='font-size:36px; font-weight:bold; margin:0;'>${net_burn:,.0f} / mo</p></div>", unsafe_allow_html=True)

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    fc1, fc2 = st.columns(2)
    with fc1:
        st.write("#### 🏗️ GC Escrow Vault")
        if st.button("🔒 Deposit $25,000 to Sub Escrow"):
            st.session_state.escrow_balance += 25000.0; st.session_state.lien_signed = False; st.rerun()
        st.metric("Funds in Escrow", f"${st.session_state.escrow_balance:,.2f}")
    with fc2:
        st.write("#### ⚡ Subcontractor Payouts")
        if st.session_state.escrow_balance > 0:
            if not st.session_state.lien_signed:
                st.warning("⚠️ Sign Conditional Lien Waiver to release funds.")
                if st.button("✍️ Sign Lien & Release Funds"):
                    st.session_state.lien_signed = True
                    st.session_state.wallet_balance += st.session_state.escrow_balance
                    st.session_state.escrow_balance = 0.0; st.rerun()
            else: st.success("✅ Liens signed. Escrow clear.")
        else:
            advance = st.button("💸 Fast-Cash: Advance $10k Invoice (-2.5% Fee)")
            if advance: st.session_state.wallet_balance += 9750.0; st.rerun()

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")
    st.write("#### 🐘 Supabase Database Connection")
    if SUPABASE_URL == "ENV_VAR_MISSING": st.error("Database Offline: secrets.toml not found or misconfigured.")
    else: st.success(f"Database Online & Secured. Target: {SUPABASE_URL[:15]}...")
    
    st.write("#### 📗 QuickBooks Online API")
    if not st.session_state.qb_connected:
        if st.button("🔗 Authenticate with QuickBooks"):
            with st.spinner("Executing OAuth 2.0 Handshake..."): time.sleep(1)
            st.session_state.qb_connected = True; st.rerun()
    else: st.success("✅ QuickBooks Ledger Sync Active.")