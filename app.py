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
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    try:
        if method == "GET": response = requests.get(url, headers=headers, params=params)
        elif method == "POST": response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return None

def sanitize_input(user_input):
    return html.escape(str(user_input)) if user_input else ""

# --- 3. LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Command Center", "matrix": "📊 Trade Matrix", "takeoff": "📐 Automated Takeoff", "gc_budg": "🏗️ GC Budget", 
        "fin": "💳 OmniPay & Escrow", "bank": "🏦 Bank Portal", "clinic": "🏥 Clinic Infra & Audit", "co_lien": "📝 Change Orders & Liens", "api": "☁️ Cloud API"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 0.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 0.00
if "bank_connected" not in st.session_state: st.session_state.bank_connected = False
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []

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
            input_email = st.text_input("Account Email").strip()
            input_password = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Verify Credentials", use_container_width=True):
                user_query = supabase_api_call(endpoint="user_registry", method="GET", params={"email": f"eq.{input_email}", "password_hash": f"eq.{input_password}"})
                if user_query and len(user_query) > 0:
                    profile = user_query[0]
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = profile["email"]
                    st.session_state.user_role = profile["assigned_role"]
                    st.session_state.company_name = profile["company_name"]
                    st.success("Authentication verified.")
                    time.sleep(0.5); st.rerun()
    st.stop()

t = lang_dict[st.session_state.lang]

# --- 7. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.write(f"💼 **Profile:** `{st.session_state.user_role}`")
st.sidebar.divider()

if "General Contractor" in st.session_state.user_role:
    menu_options = [t["home"], t["gc_budg"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["api"]]
else:
    menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["api"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 8. TOP TELEMETRY MATRIX ---
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>🔒 PROJECT ESCROW RESERVES</p><h3 style='margin:0; color: #F59E0B;'>${st.session_state.escrow_locked:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-green'><p style='margin:0; font-size:10px; color:#10B981;'>💳 OPERATIONAL LIQUID WALLET</p><h3 style='margin:0; color:#10B981;'>${st.session_state.wallet_balance:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>BANK LINKED STATUS</p><h3 style='margin:0;'>{'✅ CONNECTED' if st.session_state.bank_connected else '❌ DISCONNECTED'}</h3></div>", unsafe_allow_html=True)

# --- 9. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")

elif selected_page == t["matrix"]: st.write(f"### {t['matrix']}")
elif selected_page == t["takeoff"]: st.write(f"### {t['takeoff']}")
elif selected_page == t["bid"]: st.write(f"### {t['bid']}")
elif selected_page == t["clinic"]: st.write(f"### {t['clinic']}")
elif selected_page == t["co_lien"]: st.write(f"### {t['co_lien']}")

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    st.markdown("<div class='unifi-stealth-blade'><b>OmniPay Escrow Draw Panel</b></div>", unsafe_allow_html=True)
    if st.session_state.escrow_locked == 0.0:
        st.warning("⚠️ Escrow reserves are currently $0.00. The General Contractor or Project Owner must navigate to the Bank Portal to fund the project escrow lock before you can execute draw clearings.")
    else:
        draw_amount = st.number_input("Draw Request Amount ($)", min_value=0.0, value=min(1000.0, st.session_state.escrow_locked))
        if st.button("⚡ Process Instant Draw Clearance"):
            st.session_state.escrow_locked -= draw_amount
            st.session_state.wallet_balance += draw_amount
            st.session_state.transaction_history.insert(0, {"Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Description": "Progress Draw Clearance", "Amount": f"+${draw_amount:,.2f}", "Type": "Draw"})
            st.success("Funds transferred successfully!")
            time.sleep(0.5); st.rerun()

# NEW ARCHITECTURE MODULE: BANK CAPITAL INGESTION PORTAL
elif selected_page == t["bank"]:
    st.write(f"### {t['bank']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Corporate Project Funding & Bank Link Management</b><br>Connect construction commercial lending nodes or owner capital reserves directly to the escrow environment.</div>", unsafe_allow_html=True)
    
    if not st.session_state.bank_connected:
        st.info("No bank routing nodes are currently connected to this workspace.")
        with st.form("bank_connect_form"):
            selected_bank = st.selectbox("Select Commercial Banking Entity", ["Chase Commercial", "Bank of America Enterprise", "Wells Fargo Construction Lending", "Citi Corporate"])
            routing_num = st.text_input("Routing Number (9 Digits)", value="123456789")
            account_num = st.text_input("Account Number", type="password", value="987654321")
            
            if st.form_submit_button("🔌 Establish Secure Bank Node Link"):
                st.session_state.bank_connected = True
                st.success(f"Successfully linked secure API node to {selected_bank}!")
                time.sleep(0.5); st.rerun()
    else:
        st.success("⚙️ Bank Connection Node Secure and Online")
        
        col_dep, col_details = st.columns([1, 1.2])
        with col_dep:
            st.write("#### 📥 Deposit Project Capital into Escrow Locked Pool")
            st.caption("This action is typical executed by the General Contractor or Project Owner to fuel operations.")
            deposit_amount = st.number_input("Capital Injection Value ($)", min_value=0.0, value=150000.00)
            
            if st.button("🏢 Authorize Bank Wire & Lock Escrow Pool", use_container_width=True):
                st.session_state.escrow_locked += deposit_amount
                st.session_state.transaction_history.insert(0, {"Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Description": "Bank Wire Inbound Capital Injection", "Amount": f"${deposit_amount:,.2f}", "Type": "Escrow Inbound"})
                st.success("Capital successfully cleared bank verification and locked into Project Escrow Reserves!")
                time.sleep(0.5); st.rerun()
                
        with col_details:
            st.write("#### 💳 Funding Node Metrics")
            st.markdown(f"<div class='unifi-stealth-blade'><b>Linked Routing Stack:</b> Active<br><b>Available Bank Operating Capital Line:</b> $2,500,000.00</div>", unsafe_allow_html=True)
            if st.button("❌ Sever Corporate Bank Link", use_container_width=True):
                st.session_state.bank_connected = False
                st.rerun()

elif selected_page == t["api"]: st.write(f"### {t['api']}")