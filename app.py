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

# --- 4. STATE MANAGEMENT (UNIVERSAL CORE STORAGE) ---
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

# --- 7. AUTHENTICATION GATEWAY (PASSWORDLESS ACTIVATION PIPELINE) ---
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
                else: st.error("Invalid credentials. Enter authorized keys or activate an issued token.")
                
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
                        "email": act_email, "password_hash": act_password,
                        "company_name": act_company if act_company else "Invited Enterprise Partner",
                        "assigned_role": f"🏗️ {matching_token[0]['Tier']} Tenant"
                    }
                    supabase_api_call(endpoint="user_registry", method="POST", payload=payload)
                    for idx, key in enumerate(st.session_state.generated_license_keys):
                        if key["Key Token"] == act_token: st.session_state.generated_license_keys[idx]["Status"] = "Active / Verified"
                    st.success("🎉 Workspace activated cleanly! Head over to the Secure Login tab to enter.")
                    time.sleep(1); st.rerun()
                else: st.error("🚨 Activation Denied. Token does not match registration tracking vectors.")
                
    with tab_register:
        with st.form("reg_form"):
            reg_email = st.text_input("Preferred Login Email")
            reg_password = st.text_input("Secure Password Set", type="password")
            reg_company = st.text_input("Company Name")
            if st.form_submit_button("Create Beta Profile", use_container_width=True):
                payload = {"email": reg_email, "password_hash": reg_password, "company_name": reg_company, "assigned_role": "⚡ Free Beta Tester"}
                supabase_api_call(endpoint="user_registry", method="POST", payload=payload)
                st.success("Beta account generated!")
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

# High-fidelity theme preset control switch
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

# --- 11. CENTRALIZED INTERACTIVE MODULE ROUTING CONTAINERS ---
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
        st.session_state.field_dispatch_messages = [{"Timestamp": "11:02 AM", "Sender": current_user, "Role": "⚡ Tenant", "Room Context": "Room 101", "Message String": "Isolated multi-tenant skin network array checked and active."}]
        log_system_event(current_user, "Sandbox Seed", "Injected complete relational dataset array matrix.")
        st.success("Your private tenant sandbox has been populated!"); time.sleep(0.5); st.rerun()

elif selected_page == t["comm_rollout"]:
    st.write(f"### {t['comm_rollout']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Multi-Unit High-Density Real Estate Scaling Portal</b></div>", unsafe_allow_html=True)
    user_view_df = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    
    if user_view_df.empty:
        st.info("Private database ledger is empty. Activate sandbox data to continue or initialize a row:")
        if st.button("➕ Create Blank Multi-Unit Row"):
            new_row = pd.DataFrame([{"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Quartz Finish", "Fabrication Status": "Raw Slab Inventory", "Installation Status": "Unscheduled", "GC Sign-Off": "Awaiting Field Completion", "Value Release": 2250.00}])
            st.session_state.commercial_units = pd.concat([st.session_state.commercial_units, new_row], ignore_index=True); st.rerun()
    else:
        edited_df = st.data_editor(user_view_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Securely Save Ledger Structural States", use_container_width=True):
            st.session_state.commercial_units = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] != current_user]
            st.session_state.commercial_units = pd.concat([st.session_state.commercial_units, edited_df], ignore_index=True)
            st.success("Data silo updated cleanly.")

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    u_bal = st.session_state.tenant_balances[current_user]
    st.markdown(f"<div class='unifi-stealth-blade'>🔒 <b>SECURE PROJECT ESCROW BALANCE:</b> ${u_bal['escrow']:,.2f} USD</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'>💳 <b>OPERATIONAL LIQUID LIQUIDITY WALLET:</b> ${u_bal['wallet']:,.2f} USD</div>", unsafe_allow_html=True)

elif selected_page == t["chat_hub"]:
    st.write(f"### {t['chat_hub']}")
    col_in, col_fd = st.columns([1, 1.4])
    with col_in:
        msg_room = st.selectbox("Assign Thread Context Pinned Location", ["Global Scope Thread", "Room 101", "Room 102", "Room 201"])
        msg_text = st.text_area("Broadcast Site Update Note Summary")
        if st.button("⚡ Broadcast Update", use_container_width=True):
            if msg_text:
                st.session_state.field_dispatch_messages.insert(0, {"Timestamp": datetime.datetime.now().strftime("%I:%M %p"), "Sender": current_user, "Role": "⚡ Tenant", "Room Context": msg_room, "Message String": sanitize_input(msg_text)})
                st.success("Dispatched!"); time.sleep(0.5); st.rerun()
    with col_fd:
        user_messages = [m for m in st.session_state.field_dispatch_messages if m["Sender"] == current_user]
        for m in user_messages: 
            st.markdown(f"<div class='chat-bubble-sub'>⏱️ {m['Timestamp']} ∙ 📍 <b>{m['Room Context']}</b><br><p style='font-size:13px; margin:4px 0 0 0;'>{m['Message String']}</p></div>", unsafe_allow_html=True)

elif selected_page == t["bank"]:
    st.write(f"### {t['bank']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Corporate Project Funding & Bank Link Hub</b></div>", unsafe_allow_html=True)
    dep_amt = st.number_input("Inbound Wire Allocation Value ($)", min_value=0.0, value=100000.00)
    if st.button("🏢 Authorize Bank Wire Capital Injection", use_container_width=True):
        st.session_state.tenant_balances[current_user]["escrow"] += dep_amt
        log_system_event(current_user, "Finance Wire", f"Injected bank capital buffer sum of ${dep_amt:,.2f}.")
        st.success("Escrow capital reserves filled successfully!"); time.sleep(0.5); st.rerun()

elif selected_page == t["field_signoff"]:
    st.write(f"### {t['field_signoff']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Field Quality Sign-Off & Micro-Draw Verification Panel</b></div>", unsafe_allow_html=True)
    u_rooms = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    
    for idx, row in u_rooms.iterrows():
        with st.expander(f"🏢 {row['Floor']} ∙ {row['Unit Number']} — Status: {row['GC Sign-Off']}"):
            if row["GC Sign-Off"] == "Pending Review":
                if st.button(f"🖋️ Approve Inspection Quality & Clear Fund Release ({row['Unit Number']})", key=f"fo_{idx}"):
                    val = row["Value Release"]
                    st.session_state.tenant_balances[current_user]["escrow"] -= val
                    st.session_state.tenant_balances[current_user]["wallet"] += val
                    st.session_state.commercial_units.at[idx, "GC Sign-Off"] = "Approved & Certified"
                    st.success("Capital cleared micro-draw sequences successfully!"); time.sleep(0.5); st.rerun()
            else:
                st.write(f"Asset Status Description Profile: `{row['GC Sign-Off']}`")

elif selected_page == t["saas_licensing"]:
    st.write(f"### {t['saas_licensing']}")
    st.markdown("<div class='unifi-stealth-blade'><b>SaaS Core Tenant Key Allocation Administrative Console</b></div>", unsafe_allow_html=True)
    target_email = sanitize_input(st.text_input("Target Client Invitation Email Address"))
    tier_pick = st.selectbox("Product SaaS License Tier", ["Solo Contractor ($199/mo)", "Growth Team ($499/mo)", "Enterprise Multi-Trade ($1,299/mo)"])
    
    if st.button("⚡ Provision Licensing Activation Token", use_container_width=True):
        if target_email:
            token_code = f"OMNI-{tier_pick.split(' ')[0].upper()}-" + ''.join(random.choices(string.digits, k=4))
            st.session_state.generated_license_keys.append({"Key Token": token_code, "Tier": tier_pick.split(" ($")[0], "Assigned Client": target_email, "Status": "Staged / Awaiting Activation"})
            st.success(f"License generated! Key code: `{token_code}`"); time.sleep(0.5); st.rerun()
    st.dataframe(pd.DataFrame(st.session_state.generated_license_keys), use_container_width=True, hide_index=True)

elif selected_page == t["pitch_white"]:
    st.write(f"### {t['pitch_white']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Enterprise Client Presentation White-Label Settings</b></div>", unsafe_allow_html=True)
    client_lbl = st.text_input("Prospective Client Identity Tag Name", value=st.session_state.wl_client_name)
    if st.button("⚡ Lock Presentation Brand Skin", use_container_width=True):
        st.session_state.wl_client_name = client_lbl; st.success("Branding skin transformed!"); time.sleep(0.5); st.rerun()

elif selected_page == t["audit_logs"]:
    st.write(f"### {t['audit_logs']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Statutory Corporate Forensic Compliance Logs</b></div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.system_audit_trail), use_container_width=True, hide_index=True)

elif selected_page == t["procure"]:
    st.write(f"### {t['procure']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Supply-Chain Logistics Buyout Control Matrix</b></div>", unsafe_allow_html=True)
    v_cost = total_material_cost if total_material_cost > 0 else (len(st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]) * 1250.00)
    st.metric("Calculated Wholesale Procurement Overhead", f"${v_cost:,.2f}")
    if st.button("⚡ Execute Secure Purchase Order Dispatch", use_container_width=True):
        if st.session_state.tenant_balances[current_user]["wallet"] >= v_cost:
            st.session_state.tenant_balances[current_user]["wallet"] -= v_cost
            st.session_state.purchase_orders.insert(0, {"PO ID": f"PO-{len(st.session_state.purchase_orders)+1:03d}", "Amount": v_cost, "Status": "Dispatched Site"})
            log_system_event(current_user, "Procure PO", f"Dispatched corporate materials purchase order buyout tracker.")
            st.success("PO dispatched successfully!"); time.sleep(0.5); st.rerun()
        else: st.error("Insufficient liquidity reserves inside operational wallet lines.")

elif selected_page == t["sched"]:
    st.write(f"### {t['sched']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Algorithmic Gantt Production Scheduling Timeline</b></div>", unsafe_allow_html=True)
    sch_df = pd.DataFrame([
        {"Phase": "Phase 1: Materials Fabrication", "Start": "2026-06-01", "End": "2026-06-10", "Status": "Active"},
        {"Phase": "Phase 2: Site Freight & Install", "Start": "2026-06-11", "End": "2026-06-25", "Status": "Staged"}
    ])
    g_chart = alt.Chart(sch_df).mark_bar(size=20).encode(x='Start:T', x2='End:T', y='Phase:N', color='Status:N').properties(height=200, width='container')
    st.altair_chart(g_chart, use_container_width=True)

# Passthrough layout frames for remaining asset arrays
elif selected_page == t["matrix"]: st.write(f"### {t['matrix']}")
elif selected_page == t["takeoff"]: st.write(f"### {t['takeoff']}")
elif selected_page == t["bid"]: st.write(f"### {t['bid']}")
elif selected_page == t["clinic"]: st.write(f"### {t['clinic']}")
elif selected_page == t["co_lien"]: st.write(f"### {t['co_lien']}")
elif selected_page == t["ai_core"]: st.write(f"### {t['ai_core']}")
elif selected_page == t["dash"]: st.write(f"### {t['dash']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")