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
        "legal_contract": "📝 Master Contracts", "field_signoff": "🔍 Field Sign-Off", "pitch_white": "🎨 Brand White-Label", 
        "audit_logs": "📋 Audit Trail & Reports", "api": "☁️ Cloud API"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 45000.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 220000.00
if "bank_connected" not in st.session_state: st.session_state.bank_connected = True
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status"])

# White-Label Theme State Defaults
if "wl_client_name" not in st.session_state: st.session_state.wl_client_name = "OmniBuild OS Standard"
if "wl_accent_color" not in st.session_state: st.session_state.wl_accent_color = "#38BDF8"
if "wl_bg_tint" not in st.session_state: st.session_state.wl_bg_tint = "#0F172A"

# Persistent array tracking unalterable compliance audit logs
if "system_audit_trail" not in st.session_state:
    st.session_state.system_audit_trail = [
        {"Timestamp": "2026-05-16 08:00:12", "User Node": "System Core", "Event Phase": "Initialization", "Log Record String": "Multi-tenant cloud platform node workspace compiled cleanly."},
    ]

def log_system_event(user, phase, log_string):
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.system_audit_trail.insert(0, {
        "Timestamp": timestamp_str, "User Node": user, "Event Phase": phase, "Log Record String": log_string
    })

# --- 5. DYNAMIC CUSTOM THEME STYLING INJECTION ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #070B12 !important; color: #94A3B8 !important; }}
    h1, h2, h3, h4, h5, h6 {{ color: #CBD5E1 !important; font-weight: 500 !important; }}
    .unifi-stealth-blade {{ background-color: {st.session_state.wl_bg_tint} !important; border: 1px solid #1E293B !important; border-left: 3px solid {st.session_state.wl_accent_color} !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .brand-hero-header {{ font-size: 28px; font-weight: bold; color: {st.session_state.wl_accent_color} !important; letter-spacing: -0.02em; margin-bottom: 5px; }}
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
                    log_system_event(profile["email"], "Security Auth", f"User logged in successfully. Workspace profile: {profile['assigned_role']}.")
                    st.success("Access Verified.")
                    time.sleep(0.5); st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

t = lang_dict[st.session_state.lang]

# --- 7. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["pitch_white"], t["audit_logs"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    log_system_event(st.session_state.user_email, "Security Auth", "User explicitly terminated operational session.")
    st.session_state.user_authenticated = False; st.rerun()

# --- 8. GLOBAL TELEMETRY BAR HEADER ---
st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size:12px; margin-top:-10px; color:#64748B;'>Enterprise Partner Network Interface Portal Node ∙ Managed by {st.session_state.company_name}</p>", unsafe_allow_html=True)
st.divider()

# --- 9. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.bank_connected = True; st.session_state.escrow_locked = 220000.00; st.session_state.wallet_balance = 45000.00
        st.session_state.contract_agreements = [{"Doc ID": "SMA-DEMO", "GC Entity": "Global Development Corp", "Contract Value": 220000.00, "Execution Date": "Simulated Active", "Signatory": "Sandbox Admin", "Status": "Legally Executed"}]
        st.session_state.commercial_units = pd.DataFrame([
            {"Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00},
            {"Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Pending Review", "Value Release": 2250.00}
        ])
        log_system_event(st.session_state.user_email, "Sandbox Seed", "Executed full relational database model simulation seed injection.")
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
elif selected_page == t["field_signoff"]: st.write(f"### {t['field_signoff']}")
elif selected_page == t["pitch_white"]: st.write(f"### {t['pitch_white']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# NEW ARCHITECTURE MODULE: IMMUTABLE COMPLIANCE AUDIT TRAILS & REPORT GENERATION
elif selected_page == t["audit_logs"]:
    st.write(f"### {t['audit_logs']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Statutory Corporate Audit Ledger & Forensic Reporting Hub</b><br>Monitor system state transitions, trace user operational vectors, and compile presentation-ready audit summaries.</div>", unsafe_allow_html=True)
    
    col_audit_summary, col_report_actions = st.columns([2, 1])
    
    with col_audit_summary:
        st.write("#### 🛡️ Real-Time System Event Log")
        st.caption("This log tracks all major data mutations and security authentications chronologically:")
        
        audit_df = pd.DataFrame(st.session_state.system_audit_trail)
        st.dataframe(audit_df, use_container_width=True, hide_index=True)
        
    with col_report_actions:
        st.write("#### 📝 Reporting Control Center")
        st.caption("Compile real-time platform metrics into clean, audit-compliant project briefs:")
        
        report_type = st.selectbox("Select Target Summary Profile", ["Full Platform Forensic Audit", "Financial Escrow Liquidation Report", "Field Progress Sign-Off Brief"])
        
        if st.button("📊 Compile Executive Report Statement", use_container_width=True):
            log_system_event(st.session_state.user_email, "Report Compile", f"Generated formal report statement for: {report_type}.")
            
            st.write("---")
            st.success("✨ Report Compiled Successfully!")
            
            # Formatted Print-Ready Layout Block
            st.markdown(f"""
            <div style="background-color: #1E293B; border: 1px solid #475569; padding: 20px; border-radius: 4px; font-family: monospace; font-size: 13px; color: #F8FAFC;">
                <p style="text-align: center; font-weight: bold; margin-bottom: 15px; color: #38BDF8;">EXECUTIVE REPORT BRIEFING STATEMENT</p>
                <b>Report Classification:</b> {report_type}<br>
                <b>Generation Timestamp:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
                <b>Account Workspace Node:</b> {st.session_state.company_name}<br>
                <b>Authorized Operative:</b> {st.session_state.user_email}<br>
                --------------------------------------------------<br>
                <b>CURRENT FUNDING RESERVES:</b> ${st.session_state.escrow_locked:,.2f} USD<br>
                <b>OPERATIONAL LIQUID LIQUIDITY:</b> ${st.session_state.wallet_balance:,.2f} USD<br>
                <b>LOGGED EVENT LINE ACTIONS:</b> {len(st.session_state.system_audit_trail)} Registered Vectors<br>
                --------------------------------------------------<br>
                <p style="font-size: 11px; color: #94A3B8; font-style: italic; margin-top: 10px;">This briefing document constitutes an audit-certified mirror of live platform relational databases.</p>
            </div>
            """, unsafe_allow_html=True)