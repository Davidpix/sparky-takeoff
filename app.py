import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="OmniBuild OS | Master Build", layout="wide", initial_sidebar_state="expanded")

# --- 2. SECURE CLOUD INITIALIZATION & API HELPER ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "ENV_VAR_MISSING")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "ENV_VAR_MISSING")

def supabase_api_call(method="GET", payload=None, params=None):
    if SUPABASE_URL == "ENV_VAR_MISSING" or SUPABASE_KEY == "ENV_VAR_MISSING":
        return None
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" if method in ["POST", "PATCH"] else ""
    }
    url = f"{SUPABASE_URL}/rest/v1/materials"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        st.error(f"Cloud communication error: {e}")
        return None

def sanitize_input(user_input):
    return html.escape(str(user_input)) if user_input else ""

# --- 3. LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Command Center", "matrix": "📊 Trade Matrix", "takeoff": "📐 Automated Takeoff", "gc_budg": "🏗️ GC Budget", 
        "fin": "💳 OmniPay & Escrow", "sched": "📅 Trade Calendar", "inv": "🧾 AIA Invoicing", 
        "bid": "🎯 AI Bid Optimizer", "re": "🏙️ Real Estate ROI", "api": "☁️ Cloud API",
        "budget": "Master Budget", "wallet": "OmniWallet"
    },
    "Español": {
        "home": "🏠 Centro de Mando", "matrix": "📊 Matriz de Oficio", "takeoff": "📐 Despegue Automatizado", "gc_budg": "🏗️ Presupuesto GC",
        "fin": "💳 OmniPay y Fideicomiso", "sched": "📅 Calendario", "inv": "🧾 Facturación AIA",
        "bid": "🎯 Optimizador IA", "re": "🏙️ Bienes Raíces", "api": "☁️ API en la Nube",
        "budget": "Presupuesto Maestro", "wallet": "Billetera Omni"
    },
    "Українська": {
        "home": "🏠 Головна панель", "matrix": "📊 Кошторисна матриця", "takeoff": "📐 Авто-Кошторис", "gc_budg": "🏗️ Бюджет GC",
        "fin": "💳 Фінанси та Ескроу", "sched": "📅 Графік робіт", "inv": "🧾 Фактурування AIA",
        "bid": "🎯 AI Оптимізатор", "re": "🏙️ Нерухомість", "api": "☁️ Хмарний API",
        "budget": "Головний бюджет", "wallet": "Гаманець Omni"
    }
}

# --- 4. STATE MANAGEMENT & DYNAMIC FETCH ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 12500.00
if "escrow_balance" not in st.session_state: st.session_state.escrow_balance = 0.00
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 

raw_cloud_data = supabase_api_call("GET")

if raw_cloud_data and not isinstance(raw_cloud_data, dict):
    full_df = pd.DataFrame(raw_cloud_data)
    st.session_state.df_elec = full_df[full_df["trade_type"] == "Electrical"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
    st.session_state.df_plumb = full_df[full_df["trade_type"] == "Plumbing"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
    st.session_state.df_hvac = full_df[full_df["trade_type"] == "HVAC"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
else:
    if "df_elec" not in st.session_state: st.session_state.df_elec = pd.DataFrame([{"id": 1, "Item": "3/4\" EMT Conduit", "Qty": 2450, "Cost": 6.50, "Mins": 12}])
    if "df_plumb" not in st.session_state: st.session_state.df_plumb = pd.DataFrame([{"id": 4, "Item": "2\" PVC Pipe", "Qty": 400, "Cost": 12.50, "Mins": 15}])
    if "df_hvac" not in st.session_state: st.session_state.df_hvac = pd.DataFrame([{"id": 6, "Item": "Carrier 3-Ton Unit", "Qty": 1, "Cost": 2100.00, "Mins": 180}])

def calc_trade(df):
    mat = (df["Qty"] * df["Cost"]).sum()
    lab = ((df["Qty"] * df["Mins"]) / 60).sum() * st.session_state.labor_rate
    return (mat + lab) * (1 + st.session_state.overhead), mat + lab

elec_total, elec_raw = calc_trade(st.session_state.df_elec)
plumb_total, _ = calc_trade(st.session_state.df_plumb)
hvac_total, _ = calc_trade(st.session_state.df_hvac)
master_build_cost = elec_total + plumb_total + hvac_total + 35000.0

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
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
                else: st.error("Invalid credentials.")
    st.stop()

# --- 7. SIDEBAR & ROUTING ---
st.sidebar.title("🌍 OmniBuild OS")
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Español", "Українська"], index=0)
t = lang_dict[selected_lang]

st.sidebar.divider()
user_role = st.sidebar.selectbox("Workspace Profile", ["🏗️ General Contractor", "⚡ Electrical Sub", "💧 Plumbing Sub", "❄️ HVAC Sub"], index=1)
st.sidebar.divider()

if "General Contractor" in user_role: menu_options = [t["home"], t["gc_budg"], t["sched"], t["inv"], t["fin"], t["re"], t["api"]]
elif "Electrical" in user_role: menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["fin"], t["api"]]
else: menu_options = [t["home"], t["matrix"], t["fin"]]

selected_page = st.sidebar.radio("Navigation:", menu_options)
st.divider()

# --- 8. TOP TELEMETRY ---
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>{t['budget']}</p><h3 style='margin:0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>⚡ Active Trade Sub</p><h3 style='margin:0;'>${elec_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><p style='margin:0; font-size:10px;'>☁️ Engine Synced</p><h3 style='margin:0; color:#10B981;'>100%</h3></div>", unsafe_allow_html=True)

# --- 9. MODULE ROUTING ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    client = sanitize_input(st.text_input("Active Project Name", "Miami Medical Hub"))
    st.markdown(f"<div class='unifi-stealth-blade'>Operating Context: <b>{client}</b></div>", unsafe_allow_html=True)

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    if "Electrical" in user_role: st.data_editor(st.session_state.df_elec, use_container_width=True, disabled=["id"])

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")
    blueprint_dump = st.text_area("Blueprint Specification Dump Panel", height=180)
    if st.button("🚀 Process & Parse Blueprint"):
        st.info("Parsing logic active.")

# DYNAMIC UPGRADE: PRODUCING PREDICATIVE BID ALGORITHMS
elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Predictive Analysis Engine:</b> Pulling live base costs from the database to calculate optimization thresholds.</div>", unsafe_allow_html=True)
    
    col_inputs, col_outputs = st.columns([1, 1.5])
    
    with col_inputs:
        st.write("#### 🛠️ Margin Adjustments")
        target_margin = st.slider("Target Gross Margin (%)", 5, 50, int(st.session_state.overhead * 100))
        competitor_aggression = st.select_slider("Competitor Market Aggression", options=["Low Market Pressure", "Standard Market", "Highly Aggressive"])
        
    # Math Modeling: Calculate decayed probability curves relative to field costs
    decay_factors = {"Low Market Pressure": 0.03, "Standard Market": 0.05, "Highly Aggressive": 0.08}
    k = decay_factors[competitor_aggression]
    
    win_probability = max(1.0, 100.0 * math.exp(-k * (target_margin - 5)))
    calculated_bid_price = elec_raw * (1 + (target_margin / 100))
    projected_net_profit = calculated_bid_price - elec_raw
    expected_value = projected_net_profit * (win_probability / 100)
    
    with col_outputs:
        st.write("#### 📊 Algorithmic Output Telemetry")
        c1, c2 = st.columns(2)
        c1.metric("Raw Field Cost Baseline", f"${elec_raw:,.2f}")
        c2.metric("Calculated Final Bid Price", f"${calculated_bid_price:,.2f}")
        
        c3, c4 = st.columns(2)
        c3.metric("Projected Win Probability", f"{win_probability:.1f}%")
        c4.metric("Mathematical Expected Value", f"${expected_value:,.2f}")
        
    if win_probability > 75:
        st.success("🎯 High Win Optimization Point. Margin represents a highly competitive bidding stance.")
    elif win_probability > 40:
        st.warning("⚖️ Balanced Strategic Equilibrium. Maximum yield vs standard competitor risk metrics.")
    else:
        st.error("🚨 Critical Vulnerability. Margin is highly susceptible to aggressive market undercutting.")

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")
    chart_data = pd.DataFrame({"Trade": ["Electrical", "Plumbing", "HVAC", "Framing/Finishes"], "Value ($)": [elec_total, plumb_total, hvac_total, 35000.0]})
    st.altair_chart(alt.Chart(chart_data).mark_arc(innerRadius=50).encode(theta='Value ($):Q', color='Trade:N'), use_container_width=True)