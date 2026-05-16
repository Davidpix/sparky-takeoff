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
        "fin": "💳 OmniPay & Escrow", "sched": "📅 Trade Calendar", "inv": "🧾 Progress Billings", 
        "bid": "🎯 AI Bid Optimizer", "re": "🏙️ Real Estate ROI", "api": "☁️ Cloud API",
        "budget": "Master Budget", "wallet": "OmniWallet"
    },
    "Español": {
        "home": "🏠 Centro de Mando", "matrix": "📊 Matriz de Oficio", "takeoff": "📐 Despegue Automatizado", "gc_budg": "🏗️ Presupuesto GC",
        "fin": "💳 OmniPay y Fideicomiso", "sched": "📅 Calendario", "inv": "🧾 Facturación de Progreso",
        "bid": "🎯 Optimizador IA", "re": "🏙️ Bienes Raíces", "api": "☁️ API en la Nube",
        "budget": "Presupuesto Maestro", "wallet": "Billetera Omni"
    },
    "Українська": {
        "home": "🏠 Головна панель", "matrix": "📊 Кошторисна матриця", "takeoff": "📐 Авто-Кошторис", "gc_budg": "🏗️ Бюджет GC",
        "fin": "💳 Фінанси та Ескроу", "sched": "📅 Графік робіт", "inv": "🧾 Прогресивне виставлення рахунків",
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

# Simulated historical draw persistence memory
if "prev_billing_drawn" not in st.session_state: st.session_state.prev_billing_drawn = 0.0

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .invoice-table-header { background-color: #1E293B; color: #F8FAFC; font-weight: bold; padding: 10px; text-align: left; }
</style>
""", unsafe_allow_html=True)

# --- 6. GATEWAY (LOGIN) ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["🔒 Secure Login", "📝 Beta Account Registration"])
    with tab_login:
        with st.form("auth_form"):
            input_email = st.text_input("Account Email / Username").strip()
            input_password = st.text_input("Secure Password", type="password").strip()
            if st.form_submit_button("Verify Credentials", use_container_width=True):
                user_query = supabase_api_call(endpoint="user_registry", method="GET", params={"email": f"eq.{input_email}", "password_hash": f"eq.{input_password}"})
                if user_query and len(user_query) > 0:
                    profile = user_query[0]
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = profile["email"]
                    st.session_state.user_role = profile["assigned_role"]
                    st.session_state.company_name = profile["company_name"]
                    st.success("Authentication successful!")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Invalid credentials.")
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
                    if res: st.success("Workspace provisioned successfully! Switch to login.")
    st.stop()

# --- 7. DYNAMIC ISOLATED DATA RECOVERY ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})

if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0:
    full_df = pd.DataFrame(raw_cloud_data)
    st.session_state.df_elec = full_df[full_df["trade_type"] == "Electrical"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
    st.session_state.df_plumb = full_df[full_df["trade_type"] == "Plumbing"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
    st.session_state.df_hvac = full_df[full_df["trade_type"] == "HVAC"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
else:
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

# Define active target framework contract total based on profile role
current_contract_total = elec_total if "Electrical" in st.session_state.user_role else master_build_cost

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
elif "Electrical" in user_role: menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["inv"], t["api"]]
else: menu_options = [t["home"], t["matrix"], t["inv"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. VIEWPORTS CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.markdown(f"<div class='unifi-stealth-blade'>Authorized Account Node: <b>{st.session_state.company_name}</b> ({st.session_state.user_role})</div>", unsafe_allow_html=True)

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    st.data_editor(st.session_state.df_elec, use_container_width=True, disabled=["id"])

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")
    blueprint_dump = st.text_area("Drop Architectural Specification Output Notes Block", height=180)
    if st.button("🚀 Process & Parse Blueprint"):
        # Parsing logic...
        pass

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")
    target_margin = st.slider("Target Gross Margin (%)", 5, 50, 20)
    st.metric("Custom Isolated Final Bid Price Output", f"${elec_raw * (1 + (target_margin / 100)):,.2f}")

# NEW INTEGRATION MODULE: DYNAMIC PROGRESS BILLINGS ENGINE
elif selected_page == t["inv"]:
    st.write(f"### {t['inv']}")
    st.markdown("<div class='unifi-stealth-blade'><b>AIA-Style Application and Certificate for Payment</b><br>Manages real-time contract completions, draw cycles, and structural retainage tracks.</div>", unsafe_allow_html=True)
    
    if current_contract_total == 0.0:
        st.warning("Your active contract valuation is $0.00. Please run a blueprint takeoff to populate materials values before running draw applications.")
    else:
        col_bill_input, col_bill_metrics = st.columns([1.2, 2])
        
        with col_bill_input:
            st.write("#### 📝 Current Period Draw Parameters")
            bill_period_pct = st.slider("Work Completed This Period (%)", 0, 100, 25)
            retainage_rate = st.slider("Contract Retainage Rate (%)", 0, 15, 10)
            
            st.divider()
            st.write("#### ⏳ Historical Draw Data Adjustment")
            st.session_state.prev_billing_drawn = st.number_input("Prior Periods Completed Work ($)", min_value=0.0, max_value=float(current_contract_total), value=float(st.session_state.prev_billing_drawn))
            
        # AIA G702 Mathematical Logic Formulations
        total_contract_sum = current_contract_total
        work_completed_this_period = total_contract_sum * (bill_period_pct / 100)
        total_completed_to_date = st.session_state.prev_billing_drawn + work_completed_this_period
        
        # Guard clause to ensure totals don't exceed contract parameters
        if total_completed_to_date > total_contract_sum:
            st.error("🚨 Total completed work cannot exceed 100% of the base contract sum value. Adjust inputs.")
            total_completed_to_date = total_contract_sum
            work_completed_this_period = total_contract_sum - st.session_state.prev_billing_drawn
            
        balance_to_finish = total_contract_sum - total_completed_to_date
        calculated_retainage = total_completed_to_date * (retainage_rate / 100)
        total_earned_less_retainage = total_completed_to_date - calculated_retainage
        
        # Prior line calculations
        prev_retainage = st.session_state.prev_billing_drawn * (retainage_rate / 100)
        prev_earned_less_retainage = st.session_state.prev_billing_drawn - prev_retainage
        net_amount_due_this_period = total_earned_less_retainage - prev_earned_less_retainage
        
        with col_bill_metrics:
            st.write("#### 📊 Application Summary (AIA G702 Form Layout)")
            
            # Form Presentation Elements
            m1, m2 = st.columns(2)
            m1.metric("Original Contract Sum", f"${total_contract_sum:,.2f}")
            m2.metric("Total Completed To Date", f"${total_completed_to_date:,.2f}")
            
            m3, m4 = st.columns(2)
            m3.metric(f"Retainage Held ({retainage_rate}%)", f"${calculated_retainage:,.2f}")
            m4.metric("Balance To Finish Contract", f"${balance_to_finish:,.2f}")
            
            st.markdown(f"""
            <div style="background-color: #1E1B4B; border: 1px solid #4338CA; border-left: 5px solid #10B981; padding: 20px; border-radius: 4px; margin-top: 15px; text-align: center;">
                <p style="margin: 0; font-size: 12px; text-transform: uppercase; letter-spacing: 0.05em; color: #93C5FD;">NET PAYMENT DUE THIS PERIOD</p>
                <h1 style="margin: 5px 0 0 0; color: #10B981; font-family: monospace; font-size: 36px;">${net_amount_due_this_period:,.2f}</h1>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button("🔒 Finalize Draw Period & Save Progress", use_container_width=True):
                st.session_state.prev_billing_drawn = total_completed_to_date
                st.success("Application for payment successfully logged! Prior periods metrics updated.")
                time.sleep(1)
                st.rerun()

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")