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

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"

# Dynamic UI Preset States
if "ui_theme_preset" not in st.session_state: st.session_state.ui_theme_preset = "UniFi Stealth Slate"
if "wl_client_name" not in st.session_state: st.session_state.wl_client_name = "OmniBuild OS Standard"

# Multi-Tenant Siloed Ledgers
if "tenant_balances" not in st.session_state: st.session_state.tenant_balances = {}
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []
if "system_audit_trail" not in st.session_state: st.session_state.system_audit_trail = []
if "purchase_orders" not in st.session_state: st.session_state.purchase_orders = []

if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Tenant Owner", "Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status", "GC Sign-Off", "Value Release"])

if "field_dispatch_messages" not in st.session_state:
    st.session_state.field_dispatch_messages = []

# Cleaned SaaS Licensing Registry Array
if "generated_license_keys" not in st.session_state:
    st.session_state.generated_license_keys = [
        {"Key Token": "OMNI-ELEC-9821", "Tier": "Growth Team", "Assigned Client": "david@shardvisuals.com", "Status": "Active / Verified"}
    ]

def log_system_event(user, phase, log_string):
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.system_audit_trail.insert(0, {
        "Timestamp": timestamp_str, "User Node": user, "Event Phase": phase, "Log Record String": log_string
    })

# --- 5. THEME MATRIX CONFIGURATIONS ---
theme_matrix = {
    "UniFi Stealth Slate": {"bg": "#070B12", "panel": "#0F172A", "accent": "#38BDF8", "border": "#1E293B", "text": "#94A3B8"},
    "Midnight Onyx Matrix": {"bg": "#020408", "panel": "#090D16", "accent": "#10B981", "border": "#111827", "text": "#A1A1AA"},
    "Cyberpunk Obsidian": {"bg": "#0A0512", "panel": "rgba(22, 11, 42, 0.6)", "accent": "#D946EF", "border": "#3B0764", "text": "#C084FC"}
}

active_colors = theme_matrix[st.session_state.ui_theme_preset]

# --- 6. UNIVERSAL CUSTOM LAYOUT INJECTIONS ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {active_colors['bg']} !important; color: {active_colors['text']} !important; }}
    h1, h2, h3, h4, h5, h6 {{ color: #F8FAFC !important; font-weight: 500 !important; }}
    .unifi-stealth-blade {{ background-color: {active_colors['panel']} !important; border: 1px solid {active_colors['border']} !important; border-left: 3px solid {active_colors['accent']} !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .unifi-stealth-gold {{ background-color: #1A170F !important; border: 1px solid #3B321E !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .unifi-stealth-green {{ background-color: #0B1C16 !important; border: 1px solid #143A2E !important; border-left: 3px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .brand-hero-header {{ font-size: 28px; font-weight: bold; color: {active_colors['accent']} !important; letter-spacing: -0.02em; margin-bottom: 5px; }}
    .chat-bubble-sub {{ background-color: {active_colors['panel']} !important; padding: 12px; border-radius: 4px; border-left: 3px solid {active_colors['accent']}; margin-bottom: 8px; }}
    .chat-bubble-gc {{ background-color: #1E1B4B !important; padding: 12px; border-radius: 4px; border-left: 3px solid #10B981; margin-bottom: 8px; }}
    .legal-document-scrollbox {{ background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 30px; font-family: 'Times New Roman', Times, serif; font-size: 14px; line-height: 1.6; border-radius: 4px; height: 350px; overflow-y: scroll; }}
    .po-document-box {{ background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 25px; font-family: monospace; font-size: 13px; line-height: 1.5; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# --- 7. AUTHENTICATION GATEWAY ---
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
                else: st.error("Invalid credentials.")
                
    with tab_activate:
        st.caption("Received an activation code? Enter details below:")
        with st.form("activate_license_form"):
            act_email = st.text_input("Invited Account Email").strip()
            act_token = st.text_input("Secure License Token Key").strip()
            act_password = st.text_input("Set Your New Account Password", type="password")
            act_company = st.text_input("Confirm Your Business Entity Name")
            
            if st.form_submit_button("⚡ Initialize Workspace & Set Credentials", use_container_width=True):
                matching_token = [k for k in st.session_state.generated_license_keys if k["Key Token"] == act_token and k["Assigned Client"].lower() == act_email.lower()]
                if matching_token:
                    payload = {
                        "email": act_email, "password_hash": act_password,
                        "company_name": act_company if act_company else "Invited Enterprise Partner",
                        "assigned_role": f"🏗️ {matching_token[0]['Tier']} Tenant"
                    }
                    supabase_api_call(endpoint="user_registry", method="POST", payload=payload)
                    for idx, key in enumerate(st.session_state.generated_license_keys):
                        if key["Key Token"] == act_token: st.session_state.generated_license_keys[idx]["Status"] = "Active / Verified"
                    st.success("🎉 Workspace activated cleanly! Head over to the Secure Login tab.")
                    time.sleep(1); st.rerun()
                else: st.error("🚨 Activation Denied.")
    st.stop()

t = lang_dict[st.session_state.lang]
current_user = st.session_state.user_email

# Intercept and isolate independent financial ledger allocations per user login
if current_user not in st.session_state.tenant_balances:
    st.session_state.tenant_balances[current_user] = {"wallet": 5000.00, "escrow": 25000.00}

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.write(f"👤 **User Node:** `{current_user}`")
st.sidebar.divider()

# Theme preset selector
chosen_preset = st.sidebar.selectbox("🎨 App Interface Preset Theme", list(theme_matrix.keys()), index=list(theme_matrix.keys()).index(st.session_state.ui_theme_preset))
if chosen_preset != st.session_state.ui_theme_preset:
    st.session_state.ui_theme_preset = chosen_preset
    st.rerun()

st.sidebar.divider()
menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["pitch_white"], t["audit_logs"], t["procure"], t["saas_licensing"], t["chat_hub"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. GLOBAL TELEMETRY BAR HEADER ---
st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

# --- 10. GLOBAL CALCULATIONS LAYER ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{current_user}"})
total_labor_hours = 0.0
total_material_cost = 0.0
has_materials = False

if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0:
    full_df = pd.DataFrame(raw_cloud_data)
    df_elec_clean = full_df[full_df["trade_type"] == "Electrical"]
    total_material_cost = (df_elec_clean["quantity"] * df_elec_clean["cost_per_unit"]).sum()
    total_labor_hours = ((df_elec_clean["quantity"] * df_elec_clean["labor_minutes"]) / 60).sum()
    has_materials = True

calculated_duration_days = max(1, math.ceil(total_labor_hours / 8)) if total_labor_hours > 0 else 5
completed_milestones = sum([st.session_state.bank_connected, st.session_state.tenant_balances[current_user]["escrow"] > 0, (has_materials or len(st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]) > 0), bool(st.session_state.contract_agreements)])
onboarding_percentage = (completed_milestones / 4) * 100

# --- 11. CENTRALIZED RUNNING ROUTING BLOCKS ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.write("#### 🎯 Your Interactive Onboarding Milestone Map")
    st.progress(onboarding_percentage / 100)
    
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.tenant_balances[current_user] = {"wallet": 45000.00, "escrow": 220000.00}
        st.session_state.commercial_units = pd.DataFrame([
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00},
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Pending Review", "Value Release": 2250.00},
            {"Tenant Owner": current_user, "Floor": "Floor 02", "Unit Number": "Room 201", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "In Shop Progress", "Installation Status": "Staged On-Site", "GC Sign-Off": "Awaiting Field Completion", "Value Release": 2250.00}
        ])
        st.session_state.field_dispatch_messages = [{"Timestamp": "11:02 AM", "Sender": current_user, "Role": "⚡ Tenant", "Room Context": "Room 101", "Message String": "Isolated sandbox matrix verified."}]
        log_system_event(current_user, "Sandbox Seed", "Injected complete dataset array frame.")
        st.success("Your private sandbox has been populated! Navigate to any menu option to view the active telemetry data."); time.sleep(0.5); st.rerun()

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Trade Matrix Configuration Layer</b><br>Define cost codes and production units below.</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{"Trade Code": "ELEC-ROUGH", "Title": "Rough-In Conduit", "Rate/Hr": 45.00}, {"Trade Code": "STONE-FAB", "Title": "Countertop Cut", "Rate/Hr": 65.00}]), use_container_width=True)

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📐 Blueprint Automated Material Takeoff Ingestion</b></div>", unsafe_allow_html=True)
    st.text_area("Paste Blueprint Specification Text / Bill of Materials Strings Here")
    st.button("Run Text-Extraction Parser")

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🎯 AI Bid Optimizer Node</b></div>", unsafe_allow_html=True)
    st.write("Calculated Target Bid Margin: **32.5%** ∙ Suggested Commercial Proposal Bond Value: **$185,000.00**")

elif selected_page == t["clinic"]:
    st.write(f"### {t['clinic']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🏥 Clinic Infrastructure Architecture Audit readiness</b></div>", unsafe_allow_html=True)
    st.checkbox("HIPAA Network Isolation Ring Active", value=True)
    st.checkbox("Yealink Secure VoIP Server Handshake Complete", value=True)

elif selected_page == t["co_lien"]:
    st.write(f"### {t['co_lien']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📝 Change Orders & Conditional Statutory Liens</b></div>", unsafe_allow_html=True)
    st.write("Tracking 0 Active Field Variance Disputes.")

elif selected_page == t["comm_rollout"]:
    st.write(f"### {t['comm_rollout']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Multi-Unit High-Density Real Estate Scaling Portal (Isolated)</b></div>", unsafe_allow_html=True)
    user_view_df = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    if user_view_df.empty:
        st.info("Private database ledger empty. Run sandbox mode on Command Center page.")
    else:
        edited_df = st.data_editor(user_view_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Grid Layout Changes"):
            st.session_state.commercial_units = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] != current_user]
            st.session_state.commercial_units = pd.concat([st.session_state.commercial_units, edited_df], ignore_index=True)
            st.success("Silo matrix updated cleanly.")

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    u_bal = st.session_state.tenant_balances[current_user]
    st.markdown(f"<div class='unifi-stealth-blade'>🔒 <b>SECURE PROJECT ESCROW BALANCE:</b> ${u_bal['escrow']:,.2f} USD</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'>💳 <b>OPERATIONAL WORKING WALLET LIQUIDITY:</b> ${u_bal['wallet']:,.2f} USD</div>", unsafe_allow_html=True)

elif selected_page == t["bank"]:
    st.write(f"### {t['bank']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Corporate Project Funding & Bank Link Hub</b></div>", unsafe_allow_html=True)
    dep_amt = st.number_input("Inbound Wire Value ($)", value=50000.00)
    if st.button("🏢 Fund Project Escrow Buffer Pool"):
        st.session_state.tenant_balances[current_user]["escrow"] += dep_amt
        st.success("Escrow loaded!"); time.sleep(0.5); st.rerun()

elif selected_page == t["sched"]:
    st.write(f"### {t['sched']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Algorithmic Gantt Production Scheduling Timeline</b></div>", unsafe_allow_html=True)
    sch_df = pd.DataFrame([
        {"Phase": "Phase 1: Underground & Framing", "Start": "2026-06-01", "End": "2026-06-12", "Status": "Active"},
        {"Phase": "Phase 2: Finishes & Trim-Out", "Start": "2026-06-13", "End": "2026-06-28", "Status": "Staged"}
    ])
    g_chart = alt.Chart(sch_df).mark_bar(size=20).encode(x='Start:T', x2='End:T', y='Phase:N', color='Status:N').properties(height=200, width='container')
    st.altair_chart(g_chart, use_container_width=True)

elif selected_page == t["ai_core"]:
    st.write(f"### {t['ai_core']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🧠 OmniMind Live Cross-Table Cognitive Diagnostics</b></div>", unsafe_allow_html=True)
    st.write("Calculated Risk Score: **Excellent**. Financial capital buffers fully match active crew velocity scales.")

elif selected_page == t["dash"]:
    st.write(f"### {t['dash']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📊 Executive Telemetry Control Panel Graphs</b></div>", unsafe_allow_html=True)
    chart_data = pd.DataFrame({"Project Week": ["W1", "W2", "W3", "W4"], "Capital Position ($)": [20000, 35000, 50000, 75000]})
    st.altair_chart(alt.Chart(chart_data).mark_line(point=True).encode(x='Project Week', y='Capital Position ($)'), use_container_width=True)

elif selected_page == t["legal_contract"]:
    st.write(f"### {t['legal_contract']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📝 Subcontractor Master Agreement Exhibit Generator</b></div>", unsafe_allow_html=True)
    st.markdown("<div class='legal-document-scrollbox'><b>ARTICLE 1. COMPLIANCE SCOPES</b><br>All installations must fulfill statutory structural standards perfectly.</div>", unsafe_allow_html=True)

elif selected_page == t["field_signoff"]:
    st.write(f"### {t['field_signoff']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🔍 Field Quality Assurance Sign-Off Queue</b></div>", unsafe_allow_html=True)
    u_rooms = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    if u_rooms.empty:
        st.caption("No field inspection requests staged inside your data silo partition.")
    for idx, row in u_rooms.iterrows():
        with st.expander(f"Suites {row['Unit Number']} — Review Mode"):
            if st.button(f"Release Funds via Sign-off ({row['Unit Number']})", key=f"fo_{idx}"):
                st.session_state.tenant_balances[current_user]["escrow"] -= 2250.00
                st.session_state.tenant_balances[current_user]["wallet"] += 2250.00
                st.success("Micro-draw executed!"); time.sleep(0.5); st.rerun()

elif selected_page == t["pitch_white"]:
    st.write(f"### {t['pitch_white']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🎨 Custom Brand White-Label Skin Engine</b></div>", unsafe_allow_html=True)
    lbl = st.text_input("Brand Title Name Tag", value=st.session_state.wl_client_name)
    if st.button("Apply Theme Skin Changes"):
        st.session_state.wl_client_name = lbl; st.success("Skin initialized!"); time.sleep(0.5); st.rerun()

elif selected_page == t["audit_logs"]:
    st.write(f"### {t['audit_logs']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📋 Immutable System Forensic Audit Ledger</b></div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.system_audit_trail), use_container_width=True)

elif selected_page == t["procure"]:
    st.write(f"### {t['procure']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📦 Supply-Chain Procurement Purchase Orders</b></div>", unsafe_allow_html=True)
    st.write("Staged PO liabilities: **$0.00**")

elif selected_page == t["saas_licensing"]:
    st.write(f"### {t['saas_licensing']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🔑 SaaS Tenant Invitation & Token Allocation Node</b></div>", unsafe_allow_html=True)
    invited = st.text_input("Subcontractor Client Email Address")
    if st.button("Generate License Code"):
        st.success(f"Token code provisioned safely for {invited}!")

elif selected_page == t["chat_hub"]:
    st.write(f"### {t['chat_hub']}")
    col_in, col_fd = st.columns([1, 1.4])
    with col_in:
        msg_text = st.text_area("Broadcast Site Update Note")
        if st.button("⚡ Send Message", use_container_width=True):
            st.session_state.field_dispatch_messages.insert(0, {"Timestamp": "Live", "Sender": current_user, "Message String": sanitize_input(msg_text)})
            st.success("Dispatched!"); time.sleep(0.5); st.rerun()
    with col_fd:
        user_messages = [m for m in st.session_state.field_dispatch_messages if m["Sender"] == current_user]
        for m in user_messages: st.markdown(f"<div class='chat-bubble-sub'><b>{m['Sender']}:</b> {m['Message String']}</div>", unsafe_allow_html=True)

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")
    st.markdown("<div class='unifi-stealth-blade'><b>☁️ Cloud REST API Infrastructure Integrations</b></div>", unsafe_allow_html=True)
    st.code("curl -X GET https://api.omnibuildos.com/v1/materials -H 'Authorization: Bearer KEY'")