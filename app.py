import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests
import altair as alt

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
        "fin": "💳 OmniPay & Escrow", "bank": "🏦 Bank Portal", "clinic": "🏥 Clinic Infra & Audit", 
        "co_lien": "📝 Change Orders & Liens", "bid": "🎯 AI Bid Optimizer", "sched": "📅 Trade Calendar", 
        "ai_core": "🧠 OmniMind AI Core", "dash": "📊 Telemetry Dashboard", "comm_rollout": "🏢 Commercial Rollout", 
        "legal_contract": "📝 Master Contracts", "field_signoff": "🔍 Field Sign-Off", "api": "☁️ Cloud API"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 25000.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 150000.00
if "bank_connected" not in st.session_state: st.session_state.bank_connected = True
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []

# Persistent multi-unit status array tracking verification signatures
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame([
        {"Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00},
        {"Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Pending Review", "Value Release": 2250.00},
        {"Floor": "Floor 02", "Unit Number": "Room 201", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "In Shop Progress", "Installation Status": "Staged On-Site", "GC Sign-Off": "Awaiting Field Completion", "Value Release": 2250.00},
        {"Floor": "Floor 02", "Unit Number": "Room 202", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "In Shop Progress", "Installation Status": "Pending Delivery", "GC Sign-Off": "Awaiting Field Completion", "Value Release": 2250.00}
    ])

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-gold { background-color: #1A170F !important; border: 1px solid #3B321E !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-green { background-color: #0B1C16 !important; border: 1px solid #143A2E !important; border-left: 3px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
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
                    st.success("Access Verified.")
                    time.sleep(0.5); st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

t = lang_dict[st.session_state.lang]

# --- 7. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"💼 **Profile:** `{st.session_state.user_role}`")
st.sidebar.divider()

# Core menu matrix array assembly routing layers
menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 8. GLOBAL CHECKS DATA FOR ONBOARDING SPREADS ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})
has_materials = raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0
completed_milestones = sum([st.session_state.bank_connected, st.session_state.escrow_locked > 0, (has_materials or len(st.session_state.commercial_units) > 0), bool(st.session_state.contract_agreements)])
onboarding_percentage = (completed_milestones / 4) * 100

# --- 9. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.markdown(f"<div class='unifi-stealth-blade'>Authorized Workspace Profile Node: <b>{st.session_state.company_name}</b></div>", unsafe_allow_html=True)
    st.write("#### 🎯 Your Interactive Onboarding Milestone Map")
    st.progress(onboarding_percentage / 100)
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.bank_connected = True; st.session_state.escrow_locked = 185000.00; st.session_state.wallet_balance = 22500.00
        st.session_state.contract_agreements = [{"Doc ID": "SMA-DEMO", "GC Entity": "Global Development Corp", "Contract Value": 185000.00, "Execution Date": "Simulated Active", "Signatory": "Sandbox Admin", "Status": "Legally Executed"}]
        st.success("Sandbox populated!"); time.sleep(0.5); st.rerun()

elif selected_page == t["matrix"]: st.write(f"### {t['matrix']}")
elif selected_page == t["takeoff"]: st.write(f"### {t['takeoff']}")
elif selected_page == t["bid"]: st.write(f"### {t['bid']}")
elif selected_page == t["clinic"]: st.write(f"### {t['clinic']}")
elif selected_page == t["co_lien"]: st.write(f"### {t['co_lien']}")
elif selected_page == t["fin"]: st.write(f"### {t['fin']}")
elif selected_page == t["bank"]: st.write(f"### {t['bank']}")
elif selected_page == t["sched"]: st.write(f"### {t['sched']}")
elif selected_page == t["ai_core"]: st.write(f"### {t['ai_core']}")
elif selected_page == t["dash"]: st.write(f"### {t['dash']}")
elif selected_page == t["comm_rollout"]: st.write(f"### {t['comm_rollout']}")
elif selected_page == t["legal_contract"]: st.write(f"### {t['legal_contract']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# NEW INTEGRATION MODULE: REAL-TIME FIELD INSPECTION & VALUE RELEASE MATRIX
elif selected_page == t["field_signoff"]:
    st.write(f"### {t['field_signoff']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Field Quality Assurance & Earned Value Validation Portal</b><br>Authorize structural room-by-room physical inspections and execute instantaneous micro-draw escrow fund disbursements.</div>", unsafe_allow_html=True)
    
    st.write("#### 🔍 Active Field Inspection Dashboard Queue")
    st.caption("Review current multi-unit execution paths, approve architectural completions, or request field certification sign-offs:")
    
    # Render the inspection queue directly to the viewport layout
    for idx, row in st.session_state.commercial_units.iterrows():
        with st.expander(f"🏢 {row['Floor']} ∙ {row['Unit Number']} — Status: **{row['GC Sign-Off']}**"):
            st.write(f"**Asset Profile Description:** {row['Asset Type']}")
            st.write(f"**Shop Fabrication Stage:** `{row['Fabrication Status']}` ∙ **Field Installation Stage:** `{row['Installation Status']}`")
            st.write(f"**Locked Earned Unit Value:** `${row['Value Release']:,.2f} USD`")
            
            if row["GC Sign-Off"] == "Pending Review":
                st.markdown("<div class='unifi-stealth-gold' style='padding:10px;'>⚠️ <b>GC ACTION REQUIRED:</b> The field production crew has completed this installation and requested structural quality validation.</div>", unsafe_allow_html=True)
                
                col_btn_approve, _ = st.columns([1, 2])
                with col_btn_approve:
                    if st.button(f"🖋️ Certify Quality & Authorize Fund Release ({row['Unit Number']})", key=f"appr_{idx}", use_container_width=True):
                        # Execute Earned Value payment release loops across state balances
                        unit_payment_value = row['Value Release']
                        if st.session_state.escrow_locked >= unit_payment_value:
                            st.session_state.escrow_locked -= unit_payment_value
                            st.session_state.wallet_balance += unit_payment_value
                            st.session_state.commercial_units.at[idx, "GC Sign-Off"] = "Approved & Certified"
                            
                            st.toast(f"✅ {row['Unit Number']} Certified! Funds routed instantly to subcontractor wallet.", icon="💸")
                            time.sleep(0.5); st.rerun()
                        else:
                            st.error("🚨 Transfer Aborted. Linked project escrow reserves possess insufficient liquidity pools.")
                            
            elif row["GC Sign-Off"] == "Awaiting Field Completion":
                col_btn_sub, _ = st.columns([1, 2])
                with col_btn_sub:
                    if st.button(f"🚀 Mark Installation Complete & Request Inspection ({row['Unit Number']})", key=f"req_{idx}", use_container_width=True):
                        st.session_state.commercial_units.at[idx, "Installation Status"] = "Fully Installed"
                        st.session_state.commercial_units.at[idx, "GC Sign-Off"] = "Pending Review"
                        st.toast(f"Inspection request dispatched for {row['Unit Number']}!", icon="🔍")
                        time.sleep(0.5); st.rerun()
                        
            elif row["GC Sign-Off"] == "Approved & Certified":
                st.markdown("<div class='unifi-stealth-green' style='padding:10px;'>✅ <b>TRANSACTION SETTLED:</b> This unit has cleared quality controls. Capital has been fully decentralized and released into liquid working accounts.</div>", unsafe_allow_html=True)