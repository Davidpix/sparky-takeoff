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
        "bid": "🎯 AI Bid Optimizer", "clinic": "🏥 Clinic Infra & Audit", "co_lien": "📝 Change Orders & Liens", "api": "☁️ Cloud API",
        "budget": "Master Budget", "wallet": "OmniWallet"
    },
    "Español": {
        "home": "🏠 Centro de Mando", "matrix": "📊 Matriz de Oficio", "takeoff": "📐 Despegue Automatizado", "gc_budg": "🏗️ Presupuesto GC",
        "fin": "💳 OmniPay y Fideicomiso", "sched": "📅 Calendario", "inv": "🧾 Facturación de Progreso",
        "bid": "🎯 Optimizador IA", "clinic": "🏥 Infraestructura Clínica", "co_lien": "📝 Órdenes de Cambio", "api": "☁️ API en la Nube",
        "budget": "Presupuesto Maestro", "wallet": "Billetera Omni"
    },
    "Українська": {
        "home": "🏠 Головна панель", "matrix": "📊 Кошторисна матриця", "takeoff": "📐 Авто-Кошторис", "gc_budg": "🏗️ Бюджет GC",
        "fin": "💳 Фінанси та Ескроу", "sched": "📅 Графік робіт", "inv": "🧾 Прогресивне виставлення рахунків",
        "bid": "🎯 AI Оптимізатор", "clinic": "🏥 Клінічна Інфраструктура", "co_lien": "📝 Зміни та Відмови від Прав", "api": "☁️ Хмарний API",
        "budget": "Головний бюджет", "wallet": "Гаманець Omni"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 8450.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 75000.00
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 
if "change_orders" not in st.session_state: st.session_state.change_orders = []

# Persistent financial transaction logs
if "transaction_history" not in st.session_state:
    st.session_state.transaction_history = [
        {"Timestamp": "2026-05-10 14:22", "Description": "Initial Capital Reserve Allocation", "Amount": "+$5,000.00", "Type": "Credit Settlement"},
        {"Timestamp": "2026-05-12 09:15", "Description": "Supplies Drop: 3/4\" Conduit Batch", "Amount": "-$1,250.00", "Type": "Vendor Purchase"}
    ]

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-green { background-color: #0B1C16 !important; border: 1px solid #143A2E !important; border-left: 3px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION GATEWAY ---
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
                    st.success("Authentication verified.")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

# --- 7. DYNAMIC CONTRACT VARIANCE TRACKS ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})
approved_co_total = sum(co["Cost Impact"] for co in st.session_state.change_orders if co["Status"] == "Approved & Signed")

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Español", "Українська"], index=0)
t = lang_dict[selected_lang]

st.sidebar.divider()
st.sidebar.write(f"👤 **User:** `{st.session_state.user_email}`")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

if "General Contractor" in st.session_state.user_role:
    menu_options = [t["home"], t["gc_budg"], t["clinic"], t["co_lien"], t["fin"], t["api"]]
else:
    menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["inv"], t["clinic"], t["co_lien"], t["fin"], t["api"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. TOP TELEMETRY MATRIX ---
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>🔒 SECURE ESCROW REVENUE</p><h3 style='margin:0; color: #F59E0B;'>${st.session_state.escrow_locked:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-green'><p style='margin:0; font-size:10px; color:#10B981;'>💳 OPERATIONAL LIQUID BALANCE</p><h3 style='margin:0; color:#10B981;'>${st.session_state.wallet_balance:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Approved Variations Sum</p><h3 style='margin:0;'>${approved_co_total:,.2f}</h3></div>", unsafe_allow_html=True)

# --- 10. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.markdown(f"<div class='unifi-stealth-blade'>Authorized Account Node: <b>{st.session_state.company_name}</b></div>", unsafe_allow_html=True)

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")

elif selected_page == t["inv"]:
    st.write(f"### {t['inv']}")

elif selected_page == t["clinic"]:
    st.write(f"### {t['clinic']}")

elif selected_page == t["co_lien"]:
    st.write(f"### {t['co_lien']}")

# NEW ARCHITECTURE MODULE: OMNIPAY & TRADING ESCROW CLEARANCE ENGINE
elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    st.markdown("<div class='unifi-stealth-blade'><b>OmniPay Financial Routing & Project Escrow Matrix</b><br>Execute instantaneous capital distributions, clear progress draw releases, and track audit-compliant vendor settlements.</div>", unsafe_allow_html=True)
    
    col_pay_actions, col_pay_ledger = st.columns([1, 1.2])
    
    with col_pay_actions:
        st.write("#### 💸 Initiate Capital Draw Request")
        draw_purpose = st.text_input("Allocation / Draw Description", placeholder="e.g., Procurement of secondary fixture arrays")
        draw_amount = st.number_input("Draw Liquidation Amount ($)", min_value=0.0, value=2500.00)
        
        st.write("##### 🛡️ Automated Compliance Clearance Verification")
        compliance_check_1 = st.checkbox("Verify all legal conditional lien releases are securely executed for this draw value line", value=True)
        compliance_check_2 = st.checkbox("Confirm physical work installation validation matches telemetry reports", value=True)
        
        if st.button("⚡ Process Instant Capital Draw Clearance", use_container_width=True):
            if draw_purpose and draw_amount > 0:
                if draw_amount <= st.session_state.escrow_locked:
                    if compliance_check_1 and compliance_check_2:
                        # Process transfer transaction logic execution loops
                        st.session_state.escrow_locked -= draw_amount
                        st.session_state.wallet_balance += draw_amount
                        
                        # Prepend historical data arrays
                        new_tx = {
                            "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                            "Description": draw_purpose,
                            "Amount": f"+${draw_amount:,.2f}",
                            "Type": "Escrow Draw Liquidation"
                        }
                        st.session_state.transaction_history.insert(0, new_tx)
                        st.success(f"✅ Transaction processed! Settle authorization cleared. Funds moved to Liquid Wallet.")
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        st.error("🚨 Settlement Aborted. Core statutory compliance check boxes must be confirmed.")
                else:
                    st.error("🚨 Transaction Denied. Insufficient balance parameters sit inside the locked project escrow account node.")
            else:
                st.error("A comprehensive description allocation title and valid currency line value are required.")

    with col_pay_ledger:
        st.write("#### 📋 Transaction Auditing Statement")
        tx_df = pd.DataFrame(st.session_state.transaction_history)
        st.dataframe(tx_df, use_container_width=True)
        
        st.write("##### ℹ️ Operational Architecture Protocol")
        st.caption("OmniPay settlements clear instantaneously across interconnected operational accounts, bypassing traditional clearing banking settlement delays.")

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")