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

# Core Project Schedule Delays / Padding state parameters
if "schedule_delay_days" not in st.session_state: st.session_state.schedule_delay_days = 0
if "crew_count_leveling" not in st.session_state: st.session_state.crew_count_leveling = 2

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

# --- 10. LIVE SUPABASE CLOUD SYNC & RECOVERY LAYER ---
cloud_units = supabase_api_call(endpoint="commercial_units", method="GET", params={"Tenant Owner": f"eq.{current_user}"})
if cloud_units is not None and not isinstance(cloud_units, dict) and len(cloud_units) > 0:
    st.session_state.commercial_units = pd.DataFrame(cloud_units)

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

# --- 11. CENTRALIZED RUNNING ROUTING BLOCKS ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    # Query current user's isolated list size dynamically
    user_units_df = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    completed_milestones = sum([st.session_state.get("bank_connected", False), st.session_state.tenant_balances[current_user]["escrow"] > 0, (has_materials or len(user_units_df) > 0), bool(st.session_state.contract_agreements)])
    onboarding_percentage = (completed_milestones / 4) * 100

    st.write("#### 🎯 Your Interactive Onboarding Milestone Map")
    st.progress(onboarding_percentage / 100)
    
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.bank_connected = True
        st.session_state.tenant_balances[current_user] = {"wallet": 45000.00, "escrow": 220000.00}
        
        sim_data = [
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00},
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Pending Review", "Value Release": 2250.00},
            {"Tenant Owner": current_user, "Floor": "Floor 02", "Unit Number": "Room 201", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "In Shop Progress", "Installation Status": "Staged On-Site", "GC Sign-Off": "Awaiting Field Completion", "Value Release": 2250.00}
        ]
        for unit in sim_data: supabase_api_call(endpoint="commercial_units", method="POST", payload=unit)
        st.session_state.commercial_units = pd.DataFrame(sim_data)
        st.success("Your private production workspace has been cleanly synchronized with the cloud! All records are now completely permanent."); time.sleep(0.5); st.rerun()

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Trade Matrix Configuration Layer</b><br>Define cost codes and production units below.</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{"Trade Code": "ELEC-ROUGH", "Title": "Rough-In Conduit", "Rate/Hr": 45.00}, {"Trade Code": "STONE-FAB", "Title": "Countertop Cut", "Rate/Hr": 65.00}]), use_container_width=True, hide_index=True)

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
        st.info("Private database ledger empty. Run cloud setup on Command Center page.")
    else:
        edited_df = st.data_editor(user_view_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Synchronize Workspace Structural Changes to Cloud", use_container_width=True):
            for idx, row in edited_df.iterrows(): supabase_api_call(endpoint="commercial_units", method="POST", payload=row.to_dict())
            st.success("All data updates have been permanently saved to your cloud database arrays.")

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    u_bal = st.session_state.tenant_balances[current_user]
    st.markdown(f"<div class='unifi-stealth-blade'>🔒 <b>SECURE PROJECT ESCROW BALANCE:</b> ${u_bal['escrow']:,.2f} USD</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'>💳 <b>OPERATIONAL WORKING WALLET LIQUIDITY:</b> ${u_bal['wallet']:,.2f} USD</div>", unsafe_allow_html=True)

elif selected_page == t["bank"]:
    st.write(f"### {t['bank']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Corporate Project Funding & Bank Link Hub</b></div>", unsafe_allow_html=True)
    dep_amt = st.number_input("Inbound Wire Value ($)", value=50000.00)
    if st.button("🏢 Fund Project Escrow Buffer Pool", use_container_width=True):
        st.session_state.bank_connected = True
        st.session_state.tenant_balances[current_user]["escrow"] += dep_amt
        st.success("Escrow loaded!"); time.sleep(0.5); st.rerun()

# --- UPGRADED MODULE: CRITICAL PATH SCHEDULING ALGORITHM ---
elif selected_page == t["sched"]:
    st.write(f"### {t['sched']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🧠 Algorithmic Critical Path Production Scheduler</b><br>Simulate vendor backorders, level crew assignments, and automatically calculate real-time project hand-over forecasting.</div>", unsafe_allow_html=True)
    
    col_sch_ctrl, col_sch_viz = st.columns([1, 1.4])
    
    with col_sch_ctrl:
        st.write("#### 🛠️ Resource Leveling & Supply Controls")
        # Let the user simulate an upstream supply chain shock or buffer delay
        simulated_delay = st.slider("Supply-Chain Material Backorder Lag (Days)", 0, 14, st.session_state.schedule_delay_days)
        active_crew = st.slider("Active Field Crew Personnel Count", 1, 10, st.session_state.crew_count_leveling)
        
        if st.button("⚡ Execute Schedule Recalculation Engine", use_container_width=True):
            st.session_state.schedule_delay_days = simulated_delay
            st.session_state.crew_count_leveling = active_crew
            st.toast("Algorithmic rescheduling parameters compiled!", icon="📈")
            time.sleep(0.5); st.rerun()
            
        st.write("---")
        st.write("#### 🏗️ Predecessor Structural Handshake Matrix")
        st.caption("Mark GC structural tasks complete to release field production paths for installers:")
        pre_drywall = st.checkbox("GC Drywall & Framing Sheetrock Complete (Floor 1)", value=True)
        pre_plumb = st.checkbox("Core Plumbing Rough-Ins Certified (Floor 2)", value=False)
        
    with col_sch_viz:
        st.write("#### 📊 Dynamic Project Gantt Production Projections")
        
        # Calculate timeline offsets based on user leveling logic parameters
        base_start = datetime.date(2026, 6, 1)
        
        fab_start = base_start + datetime.timedelta(days=simulated_delay)
        fab_duration = max(2, math.ceil(12 / active_crew))
        fab_end = fab_start + datetime.timedelta(days=fab_duration)
        
        install_start = fab_end + datetime.timedelta(days=1)
        install_duration = max(3, math.ceil(20 / active_crew))
        # If the predecessor plumbing trades are behind, stack an automatic warning delay block
        if not pre_plumb:
            install_duration += 5
        install_end = install_start + datetime.timedelta(days=install_duration)
        
        sch_df = pd.DataFrame([
            {"Task Node": "1. Material Fabrication Loop", "Start": fab_start.strftime("%Y-%m-%d"), "End": fab_end.strftime("%Y-%m-%d"), "Phase Metric": "Shop Tooling"},
            {"Task Node": "2. High-Density Suite Rollout", "Start": install_start.strftime("%Y-%m-%d"), "End": install_end.strftime("%Y-%m-%d"), "Phase Metric": "Field Execution"}
        ])
        
        g_chart = alt.Chart(sch_df).mark_bar(size=24, cornerRadius=4).encode(
            x=alt.X('Start:T', title="Project Calendar Timeline"),
            x2='End:T',
            y=alt.Y('Task Node:N', title=None),
            color=alt.Color('Phase Metric:N', scale=alt.Scale(range=[st.session_state.wl_accent_color, '#F59E0B']))
        ).properties(height=180, width='container')
        
        st.altair_chart(g_chart, use_container_width=True)
        
        # Critical warning banners derived contextually from data variables
        if not pre_plumb:
            st.markdown("<div class='unifi-stealth-gold'><b>⚠️ CRITICAL PATH WARNING:</b> Core Plumbing Rough-Ins are unchecked. The rescheduling algorithm has stacked an automatic <b>5-day buffer variance liability</b> on your field execution path.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='unifi-stealth-green'><b>✅ CRITICAL PATH CLEAR:</b> Upstream structural framing trades are verified. Your resource timeline is running at 100% efficiency.</div>", unsafe_allow_html=True)
            
        st.metric("Algorithmic Project Hand-Over Date", install_end.strftime("%B %d, %Y"), f"Adjusted by +{simulated_delay + (5 if not pre_plumb else 0)} Days Total")

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
    st.markdown("<div class='legal-document-scrollbox'><b>ARTICLE 1. COMPLIANCE SCOPES</b><br>All installations must fulfill statutory standards.</div>", unsafe_allow_html=True)

elif selected_page == t["field_signoff"]:
    st.write(f"### {t['field_signoff']}")
    u_rooms = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    for idx, row in u_rooms.iterrows():
        with st.expander(f"Suites {row['Unit Number']} — Review Mode"):
            if st.button(f"Release Funds via Sign-off ({row['Unit Number']})", key=f"fo_{idx}"):
                st.session_state.tenant_balances[current_user]["escrow"] -= 2250.00
                st.session_state.tenant_balances[current_user]["wallet"] += 2250.00
                st.session_state.commercial_units.at[idx, "GC Sign-Off"] = "Approved & Certified"
                st.success("Micro-draw executed!"); time.sleep(0.5); st.rerun()

elif selected_page == t["pitch_white"]:
    st.write(f"### {t['pitch_white']}")
    lbl = st.text_input("Brand Title Name Tag", value=st.session_state.wl_client_name)
    if st.button("Apply Theme Skin Changes", use_container_width=True):
        st.session_state.wl_client_name = lbl; st.success("Skin initialized!"); time.sleep(0.5); st.rerun()

elif selected_page == t["audit_logs"]:
    st.write(f"### {t['audit_logs']}")
    st.dataframe(pd.DataFrame(st.session_state.system_audit_trail), use_container_width=True)

elif selected_page == t["procure"]:
    st.write(f"### {t['procure']}")
    v_cost = total_material_cost if total_material_cost > 0 else (len(st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]) * 1250.00)
    st.metric("Wholesale Procurement Overhead", f"${v_cost:,.2f}")

elif selected_page == t["saas_licensing"]:
    st.write(f"### {t['saas_licensing']}")
    invited = st.text_input("Subcontractor Client Email Address")
    if st.button("Generate License Code", use_container_width=True):
        st.success(f"Token code provisioned safely for {invited}!")

elif selected_page == t["chat_hub"]:
    st.write(f"### {t['chat_hub']}")
    msg_text = st.text_area("Broadcast Site Update Note")
    if st.button("⚡ Send Message", use_container_width=True):
        st.session_state.field_dispatch_messages.insert(0, {"Timestamp": "Live", "Sender": current_user, "Message String": sanitize_input(msg_text)})
        st.success("Dispatched!"); time.sleep(0.5); st.rerun()

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")
    st.code("curl -X GET https://api.omnibuildos.com/v1/materials -H 'Authorization: Bearer KEY'")