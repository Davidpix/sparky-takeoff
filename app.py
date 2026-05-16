import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests
import altair as alt
import random
import string

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
        "legal_contract": "📝 Master Contracts", "field_signoff": "🔍 Field Sign-Off", "pitch_white": "🎨 Brand White-Label", 
        "audit_logs": "📋 Audit Trail & Reports", "procure": "📦 Procurement & POs", "saas_licensing": "🔑 SaaS Tenant Licensing",
        "chat_hub": "💬 Field Dispatch Hub", "api": "☁️ Cloud API"
    }
}

# --- 4. STATE MANAGEMENT (MULTI-TENANT ENHANCED) ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"

# Isolated Account Balances mapped per tenant user email
if "tenant_balances" not in st.session_state:
    st.session_state.tenant_balances = {}

if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []
if "system_audit_trail" not in st.session_state: st.session_state.system_audit_trail = []
if "purchase_orders" not in st.session_state: st.session_state.purchase_orders = []

# Structural data frames augmented with Owner/Tenant relational mapping markers
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Tenant Owner", "Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status"])

if "field_dispatch_messages" not in st.session_state:
    st.session_state.field_dispatch_messages = []

# White-Label Theme State Defaults
if "wl_client_name" not in st.session_state: st.session_state.wl_client_name = "OmniBuild OS Standard"
if "wl_accent_color" not in st.session_state: st.session_state.wl_accent_color = "#38BDF8"
if "wl_bg_tint" not in st.session_state: st.session_state.wl_bg_tint = "#0F172A"

# SaaS Licensing Tracker Key Arrays
if "generated_license_keys" not in st.session_state:
    st.session_state.generated_license_keys = [
        {"Key Token": "OMNI-ELEC-9821", "Tier": "Growth Team", "Assigned Client": "david@shardvisuals.com", "Status": "Active / Verified"}
    ]

def log_system_event(user, phase, log_string):
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.system_audit_trail.insert(0, {
        "Timestamp": timestamp_str, "User Node": user, "Event Phase": phase, "Log Record String": log_string
    })

# --- 5. THEME STYLING INJECTION ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #070B12 !important; color: #94A3B8 !important; }}
    h1, h2, h3, h4, h5, h6 {{ color: #CBD5E1 !important; font-weight: 500 !important; }}
    .unifi-stealth-blade {{ background-color: {st.session_state.wl_bg_tint} !important; border: 1px solid #1E293B !important; border-left: 3px solid {st.session_state.wl_accent_color} !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .unifi-stealth-gold {{ background-color: #1A170F !important; border: 1px solid #3B321E !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .unifi-stealth-green {{ background-color: #0B1C16 !important; border: 1px solid #143A2E !important; border-left: 3px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .brand-hero-header {{ font-size: 28px; font-weight: bold; color: {st.session_state.wl_accent_color} !important; letter-spacing: -0.02em; margin-bottom: 5px; }}
    .chat-bubble-sub {{ background-color: #1E293B !important; padding: 12px; border-radius: 4px; border-left: 3px solid #38BDF8; margin-bottom: 8px; }}
    .chat-bubble-gc {{ background-color: #1E1B4B !important; padding: 12px; border-radius: 4px; border-left: 3px solid #10B981; margin-bottom: 8px; }}
</style>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    tab_login, tab_activate, tab_register = st.tabs(["🔒 Secure Login", "🔑 Activate License Key Token", "📝 Free Beta Signup"])
    
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
                    st.success("Access Verified.")
                    time.sleep(0.5); st.rerun()
                else: st.error("Invalid credentials. Verify your inputs or activate an issued license token.")
                
    with tab_activate:
        st.caption("Received an activation code? Enter details below to launch your dedicated multi-tenant operational frame:")
        with st.form("activate_license_form"):
            act_email = st.text_input("Invited Account Email").strip()
            act_token = st.text_input("Secure License Token Key").strip()
            act_password = st.text_input("Set Your New Account Password", type="password")
            act_company = st.text_input("Confirm Your Business Entity Name")
            
            if st.form_submit_button("⚡ Initialize Workspace & Set Credentials", use_container_width=True):
                matching_token = [k for k in st.session_state.generated_license_keys if k["Key Token"] == act_token and k["Assigned Client"].lower() == act_email.lower()]
                if matching_token:
                    payload = {
                        "email": act_email,
                        "password_hash": act_password,
                        "company_name": act_company if act_company else "Invited Enterprise Partner",
                        "assigned_role": f"🏗| {matching_token[0]['Tier']} Tenant"
                    }
                    supabase_api_call(endpoint="user_registry", method="POST", payload=payload)
                    for idx, key in enumerate(st.session_state.generated_license_keys):
                        if key["Key Token"] == act_token:
                            st.session_state.generated_license_keys[idx]["Status"] = "Active / Verified"
                    st.success("🎉 Workspace activated cleanly! Head over to the Secure Login tab.")
                    time.sleep(1); st.rerun()
                else: st.error("🚨 Activation Denied. Inbound verification metrics mismatch.")
    st.stop()

t = lang_dict[st.session_state.lang]

# --- 7. TENANT INTERCEPT DATA SAFETY LOOPS ---
current_user = st.session_state.user_email

# Initialize unique financial balances for the tenant if they don't exist
if current_user not in st.session_state.tenant_balances:
    st.session_state.tenant_balances[current_user] = {"wallet": 5000.00, "escrow": 25000.00}

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.write(f"👤 **User:** `{current_user}`")
st.sidebar.divider()

menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["pitch_white"], t["audit_logs"], t["procure"], t["saas_licensing"], t["chat_hub"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. GLOBAL TELEMETRY BAR HEADER ---
st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

# --- 10. MULTI-TENANT ISOLATED MODULE DATA FILTER ROUTING ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.markdown(f"<div class='unifi-stealth-blade'>Authorized Workspace Profile Node: <b>{st.session_state.company_name}</b></div>", unsafe_allow_html=True)
    
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.tenant_balances[current_user] = {"wallet": 45000.00, "escrow": 220000.00}
        
        # Inject mock room unit configurations linked explicitly to the logged-in user email
        st.session_state.commercial_units = pd.DataFrame([
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed"},
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed"}
        ])
        
        st.session_state.field_dispatch_messages = [
            {"Timestamp": "11:02 AM", "Sender": current_user, "Role": "⚡ Subcontractor", "Room Context": "Room 101", "Message String": "Isolated multi-tenant data stream verified."}
        ]
        st.success("Your private tenant sandbox has been cleanly populated!"); time.sleep(0.5); st.rerun()

# COMMERICAL ROLLOUT SUB-VIEW - FULLY DATA ISOLATED
elif selected_page == t["comm_rollout"]:
    st.write(f"### {t['comm_rollout']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Multi-Unit High-Density Real Estate Scaling Portal (Isolated)</b></div>", unsafe_allow_html=True)
    
    # Filter the layout matrix to show ONLY rows belonging to the logged-in customer email
    user_view_df = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    
    if user_view_df.empty:
        st.info("Your private business ledger is currently empty. Head to the Command Center to trigger Sandbox Simulation mode or log room metrics manually.")
        
        if st.button("➕ Initialize Blank Room Row"):
            new_blank_row = pd.DataFrame([{"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Quartz Line", "Fabrication Status": "Raw Slab Inventory", "Installation Status": "Unscheduled"}])
            st.session_state.commercial_units = pd.concat([st.session_state.commercial_units, new_blank_row], ignore_index=True)
            st.rerun()
    else:
        st.write("#### 🧱 Your Private Multi-Unit Grid Matrix")
        edited_df = st.data_editor(user_view_df, use_container_width=True, num_rows="dynamic")
        
        if st.button("💾 Save Ledger Modifications"):
            # Cleanly merge alterations back into the global registry database pool
            st.session_state.commercial_units = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] != current_user]
            st.session_state.commercial_units = pd.concat([st.session_state.commercial_units, edited_df], ignore_index=True)
            st.success("Ledger states updated safely within your data silo.")

# OMNIPAY DRAW SUB-VIEW - FULLY DATA ISOLATED
elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    u_bal = st.session_state.tenant_balances[current_user]
    
    f_c1, f_c2 = st.columns(2)
    f_c1.metric("Your Private Operational Wallet Balance", f"${u_bal['wallet']:,.2f}")
    f_c2.metric("Your Private Locked Escrow Fund Pool", f"${u_bal['escrow']:,.2f}")

# FIELD CHAT HUB VIEW - FULLY DATA ISOLATED
elif selected_page == t["chat_hub"]:
    st.write(f"### {t['chat_hub']}")
    col_in, col_fd = st.columns([1, 1.4])
    
    with col_in:
        msg_text = st.text_area("Broadcast Update Note")
        if st.button("⚡ Send", use_container_width=True):
            if msg_text:
                st.session_state.field_dispatch_messages.insert(0, {
                    "Timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                    "Sender": current_user, "Role": "⚡ Tenant", "Room Context": "Global Scope", "Message String": sanitize_input(msg_text)
                })
                st.success("Dispatched!"); time.sleep(0.5); st.rerun()
                
    with col_fd:
        # Filter stream logs to show ONLY communications involving this specific user workspace
        user_messages = [m for m in st.session_state.field_dispatch_messages if m["Sender"] == current_user or current_user in m["Message String"]]
        
        if not user_messages:
            st.caption("No private field updates logged under this workspace context.")
        else:
            for m in user_messages:
                st.markdown(f"<div class='chat-bubble-sub'><strong>{m['Sender']}</strong><br><p style='font-size:13px; color:#CBD5E1;'>{m['Message String']}</p></div>", unsafe_allow_html=True)

# Passthrough routing markers for secondary modules
elif selected_page == t["matrix"]: st.write(f"### {t['matrix']}")
elif selected_page == t["takeoff"]: st.write(f"### {t['takeoff']}")
elif selected_page == t["bid"]: st.write(f"### {t['bid']}")
elif selected_page == t["clinic"]: st.write(f"### {t['clinic']}")
elif selected_page == t["co_lien"]: st.write(f"### {t['co_lien']}")
elif selected_page == t["bank"]: st.write(f"### {t['bank']}")
elif selected_page == t["sched"]: st.write(f"### {t['sched']}")
elif selected_page == t["ai_core"]: st.write(f"### {t['ai_core']}")
elif selected_page == t["dash"]: st.write(f"### {t['dash']}")
elif selected_page == t["legal_contract"]: st.write(f"### {t['legal_contract']}")
elif selected_page == t["field_signoff"]: st.write(f"### {t['field_signoff']}")
elif selected_page == t["pitch_white"]: st.write(f"### {t['pitch_white']}")
elif selected_page == t["audit_logs"]: st.write(f"### {t['audit_logs']}")
elif selected_page == t["procure"]: st.write(f"### {t['procure']}")
elif selected_page == t["saas_licensing"]: st.write(f"### {t['saas_licensing']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")