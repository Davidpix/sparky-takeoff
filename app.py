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
        "bid": "🎯 AI Bid Optimizer", "clinic": "🏥 Clinic Infra & Audit", "api": "☁️ Cloud API",
        "budget": "Master Budget", "wallet": "OmniWallet"
    },
    "Español": {
        "home": "🏠 Centro de Mando", "matrix": "📊 Matriz de Oficio", "takeoff": "📐 Despegue Automatizado", "gc_budg": "🏗️ Presupuesto GC",
        "fin": "💳 OmniPay y Fideicomiso", "sched": "📅 Calendario", "inv": "🧾 Facturación de Progreso",
        "bid": "🎯 Optimizador IA", "clinic": "🏥 Infraestructura Clínica", "api": "☁️ API en la Nube",
        "budget": "Presupuesto Maestro", "wallet": "Billetera Omni"
    },
    "Українська": {
        "home": "🏠 Головна панель", "matrix": "📊 Кошторисна матриця", "takeoff": "📐 Авто-Кошторис", "gc_budg": "🏗️ Бюджет GC",
        "fin": "💳 Фінанси та Ескроу", "sched": "📅 Графік робіт", "inv": "🧾 Прогресивне виставлення рахунків",
        "bid": "🎯 AI Оптимізатор", "clinic": "🏥 Клінічна Інфраструктура", "api": "☁️ Хмарний API",
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

# Persistent state arrays for clinic asset simulator
if "clinic_assets" not in st.session_state:
    st.session_state.clinic_assets = pd.DataFrame([
        {"Hardware Asset": "Enterprise Core Switch (UniFi 24-Port)", "Location": "Main IT Closet", "Status": "Installed & Provisioned", "Audit Verified": True},
        {"Hardware Asset": "Secure Wireless Access Point", "Location": "Patient Waiting Lobby", "Status": "Installed & Provisioned", "Audit Verified": True},
        {"Hardware Asset": "VoIP Terminal Node (Yealink Handset)", "Location": "Front Reception Desk", "Status": "Staged / Pending Config", "Audit Verified": False},
        {"Hardware Asset": "Secure Medical Workstation Laptop", "Location": "Dr. Sol Consult Room 1", "Status": "Configured & Active", "Audit Verified": True},
        {"Hardware Asset": "HIPAA Backup Storage Array", "Location": "Main IT Closet", "Status": "Pending Physical Drop", "Audit Verified": False}
    ])

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-green { background-color: #0B1C16 !important; border: 1px solid #143A2E !important; border-left: 3px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
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
        # Standard registration fields...
        pass
    st.stop()

# --- 7. DYNAMIC ISOLATED DATA RECOVERY ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})
if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0:
    full_df = pd.DataFrame(raw_cloud_data)
    st.session_state.df_elec = full_df[full_df["trade_type"] == "Electrical"][["id", "item_name", "quantity", "cost_per_unit", "labor_minutes"]].rename(columns={"item_name": "Item", "quantity": "Qty", "cost_per_unit": "Cost", "labor_minutes": "Mins"})
else:
    st.session_state.df_elec = pd.DataFrame(columns=["id", "Item", "Qty", "Cost", "Mins"])

elec_total, elec_raw = calc_trade(st.session_state.df_elec) if 'calc_trade' in globals() else (0.0, 0.0)

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Español", "Українська"], index=0)
t = lang_dict[selected_lang]

st.sidebar.divider()
st.sidebar.write(f"👤 **User:** `{st.session_state.user_email}`")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

# Allow both General Contractor and Electrical Profiles to access the Clinic Dashboard
if "General Contractor" in st.session_state.user_role:
    menu_options = [t["home"], t["gc_budg"], t["clinic"], t["api"]]
else:
    menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["inv"], t["clinic"], t["api"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. VIEWPORTS CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.markdown(f"<div class='unifi-stealth-blade'>Authorized Account Node: <b>{st.session_state.company_name}</b></div>", unsafe_allow_html=True)

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    st.data_editor(st.session_state.df_elec, use_container_width=True)

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")
    blueprint_dump = st.text_area("Drop Architectural Specification Output Notes Block")
    
elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")

elif selected_page == t["inv"]:
    st.write(f"### {t['inv']}")

# NEW INTEGRATION MODULE: CLINIC INFRASTRUCTURE & AUDIT readiness
elif selected_page == t["clinic"]:
    st.write(f"### {t['clinic']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Clinic Deployment Control Portal</b><br>Track physical hardware assets, network drops, and regulatory readiness checklists for healthcare delivery spaces.</div>", unsafe_allow_html=True)
    
    # Calculate audit metrics dynamically
    total_assets = len(st.session_state.clinic_assets)
    verified_assets = st.session_state.clinic_assets["Audit Verified"].sum()
    audit_readiness_score = (verified_assets / total_assets) * 100 if total_assets > 0 else 0.0
    
    c_m1, c_m2, c_m3 = st.columns(3)
    with c_m1: st.metric("Total Infrastructure Nodes", f"{total_assets} Units")
    with c_m2: st.metric("Verified Audit Checkpoints", f"{verified_assets} / {total_assets}")
    with c_m3:
        if audit_readiness_score >= 80:
            st.markdown(f"<div class='unifi-stealth-green' style='padding:5px 15px;'><p style='margin:0; font-size:10px;'>AUDIT READINESS SCORE</p><h3 style='margin:0; color:#10B981;'>{audit_readiness_score:.1f}%</h3></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='unifi-stealth-blade' style='padding:5px 15px; border-left-color:#F59E0B;'><p style='margin:0; font-size:10px;'>AUDIT READINESS SCORE</p><h3 style='margin:0; color:#F59E0B;'>{audit_readiness_score:.1f}%</h3></div>", unsafe_allow_html=True)

    st.write("#### 🛠️ Live Infrastructure Hardware Ledger")
    st.caption("Review or update deployment statuses and compliance metrics below:")
    
    updated_clinic_df = st.data_editor(st.session_state.clinic_assets, use_container_width=True, num_rows="dynamic")
    
    if st.button("💾 Commit Infrastructure Verification to Ledger", use_container_width=True):
        st.session_state.clinic_assets = updated_clinic_df
        st.success("Clinic infrastructure matrix successfully updated and logged!")
        time.sleep(0.5)
        st.rerun()

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")