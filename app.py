import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="OmniBuild OS | Enterprise Platform", layout="wide", initial_sidebar_state="expanded")

# --- 2. SECURE CLOUD INITIALIZATION & API HELPERS ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "ENV_VAR_MISSING")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "ENV_VAR_MISSING")

def supabase_api_call(endpoint="materials", method="GET", payload=None, params=None):
    if SUPABASE_URL == "ENV_VAR_MISSING" or SUPABASE_KEY == "ENV_VAR_MISSING":
        return None
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" if method in ["POST", "PATCH"] else ""
    }
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
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

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 12500.00
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 6. MULTI-USER SECURE GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    
    tab_login, tab_register = st.tabs(["🔒 Secure Login", "📝 Beta Account Registration"])
    
    with tab_login:
        with st.form("auth_form"):
            input_email = st.text_input("Account Email / Username").strip()
            input_password = st.text_input("Secure Password", type="password").strip()
            
            if st.form_submit_button("Verify Credentials", use_container_width=True):
                # Query the live database user_registry table for matching email/password
                user_query = supabase_api_call(endpoint="user_registry", method="GET", params={"email": f"eq.{input_email}", "password_hash": f"eq.{input_password}"})
                
                if user_query and len(user_query) > 0:
                    profile = user_query[0]
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = profile["email"]
                    st.session_state.user_role = profile["assigned_role"]
                    st.session_state.company_name = profile["company_name"]
                    st.success("Authentication successful! Loading environment...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Invalid corporate credentials. Verify email or registration status.")
                    
    with tab_register:
        with st.form("reg_form"):
            reg_email = st.text_input("Preferred Login Email")
            reg_password = st.text_input("Secure Password Set", type="password")
            reg_company = st.text_input("Company / Subcontractor Entity Name")
            reg_role = st.selectbox("Operational Profile Type", ["⚡ Electrical Sub", "💧 Plumbing Sub", "❄️ HVAC Sub", "🏗️ General Contractor"])
            
            if st.form_submit_button("Provision Account Workspace", use_container_width=True):
                if reg_email and reg_password:
                    payload = {"email": reg_email, "password_hash": reg_password, "company_name": reg_company, "assigned_role": reg_role}
                    res = supabase_api_call(endpoint="user_registry", method="POST", payload=payload)
                    if res:
                        st.success("Workspace provisioned successfully! Switch to the Login tab to access your environment.")
                else:
                    st.error("Email and password fields are strictly required for workspace provisioning.")
    st.stop()

# --- 7. DYNAMIC ISOLATED DATA RECOVERY ---
# Notice how we now filter rows by the exact logged-in user email!
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})

if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0:
    full_df = pd.DataFrame(raw_cloud_data)
    st.session_state.df_elec = full_df[full_df["trade_type"] == "Electrical"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
    st.session_state.df_plumb = full_df[full_df["trade_type"] == "Plumbing"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
    st.session_state.df_hvac = full_df[full_df["trade_type"] == "HVAC"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
else:
    # Set blank slate for fresh accounts
    st.session_state.df_elec = pd.DataFrame(columns=["id", "Item", "Qty", "Cost", "Mins"])
    st.session_state.df_plumb = pd.DataFrame(columns=["id", "Item", "Qty", "Cost", "Mins"])
    st.session_state.df_hvac = pd.DataFrame(columns=["id", "Item", "Qty", "Cost", "Mins"])

def calc_trade(df):
    if df.empty: return 0.0, 0.0
    mat = (df["Qty"] * df["Cost"]).sum()
    lab = ((df["Qty"] * df["Mins"]) / 60).sum() * st.session_state.labor_rate
    return (mat + lab) * (1 + st.session_state.overhead), mat + lab

elec_total, elec_raw = calc_trade(st.session_state.df_elec)
plumb_total, _ = calc_trade(st.session_state.df_plumb)
hvac_total, _ = calc_trade(st.session_state.df_hvac)
master_build_cost = elec_total + plumb_total + hvac_total + 35000.0

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Español", "Українська"], index=0)
t = lang_dict[selected_lang]

st.sidebar.divider()
st.sidebar.write(f"👤 **User:** `{st.session_state.user_email}`")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.write(f"💼 **Profile:** `{st.session_state.user_role}`")
st.sidebar.divider()

user_role = st.session_state.user_role

if "General Contractor" in user_role: menu_options = [t["home"], t["gc_budg"], t["api"]]
elif "Electrical" in user_role: menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["api"]]
else: menu_options = [t["home"], t["matrix"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False
    st.rerun()

# --- 9. VIEWPORTS CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.markdown(f"<div class='unifi-stealth-blade'>Authorized Account Node: <b>{st.session_state.company_name}</b> ({st.session_state.user_role})</div>", unsafe_allow_html=True)

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    if st.session_state.df_elec.empty:
        st.warning("Your isolated catalog contains no database objects. Navigate to Automated Takeoff to populate data models.")
    else:
        st.data_editor(st.session_state.df_elec, use_container_width=True, disabled=["id"])

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")
    blueprint_dump = st.text_area("Drop Architectural Specification Output Notes Block", height=180)
    
    if st.button("🚀 Process & Parse Blueprint"):
        conduit_match = re.search(r'(\d+)\s*Qty\s*of\s*3/4"\s*EMT\s*Conduit', blueprint_dump, re.IGNORECASE)
        gfci_match = re.search(r'(\d+)\s*Qty\s*of\s*20A\s*GFCI\s*Device', blueprint_dump, re.IGNORECASE)
        
        parsed_items = []
        if conduit_match: parsed_items.append({"Item": "3/4\" EMT Conduit", "Qty": int(conduit_match.group(1)), "Cost": 6.50, "Mins": 12, "Trade": "Electrical"})
        if gfci_match: parsed_items.append({"Item": "20A GFCI Device", "Qty": int(gfci_match.group(1)), "Cost": 18.00, "Mins": 15, "Trade": "Electrical"})
        
        if parsed_items:
            for item in parsed_items:
                payload = {
                    "item_name": item["Item"], "quantity": item["Qty"], "cost_per_unit": item["Cost"],
                    "labor_minutes": item["Mins"], "trade_type": item["Trade"], "user_email": st.session_state.user_email
                }
                supabase_api_call(endpoint="materials", method="POST", payload=payload)
            st.success("✅ Takeoff parsed and securely isolated to your user email identifier!")
            time.sleep(1)
            st.rerun()

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")
    target_margin = st.slider("Target Gross Margin (%)", 5, 50, 20)
    calculated_bid_price = elec_raw * (1 + (target_margin / 100))
    st.metric("Custom Isolated Final Bid Price Output", f"${calculated_bid_price:,.2f}")

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")
    st.success(f"Cluster Online. Authenticated Node Client: {st.session_state.user_email}")