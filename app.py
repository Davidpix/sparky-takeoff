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

# --- 4. STATE MANAGEMENT (HOUSEKEEPING PATCH APPLIED) ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 75000.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 185000.00
if "bank_connected" not in st.session_state: st.session_state.bank_connected = True
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []
if "system_audit_trail" not in st.session_state: st.session_state.system_audit_trail = []
if "purchase_orders" not in st.session_state: st.session_state.purchase_orders = []
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status"])

# White-Label Theme State Defaults
if "wl_client_name" not in st.session_state: st.session_state.wl_client_name = "OmniBuild OS Standard"
if "wl_accent_color" not in st.session_state: st.session_state.wl_accent_color = "#38BDF8"
if "wl_bg_tint" not in st.session_state: st.session_state.wl_bg_tint = "#0F172A"

# Cleaned SaaS Licensing Tracker State Block (Ghost Records Purged)
if "generated_license_keys" not in st.session_state:
    st.session_state.generated_license_keys = [
        {"Key Token": "OMNI-ELEC-9821", "Tier": "Growth Team", "Assigned Client": "david@shardvisuals.com", "Status": "Active / Verified"}
    ]

# Persistent array tracking context-bound dispatch messages
if "field_dispatch_messages" not in st.session_state:
    st.session_state.field_dispatch_messages = [
        {"Timestamp": "10:15 AM", "Sender": "david@shardvisuals.com", "Role": "⚡ Subcontractor", "Room Context": "Room 101", "Message String": "Main conduit feeders pulled and secured. Ready for drywall team inspection sign-off."},
        {"Timestamp": "10:22 AM", "Sender": "GC_Admin_Node", "Role": "🏗️ General Contractor", "Room Context": "Room 101", "Message String": "Verified via dashboard telemetry. Field draw release authorized."}
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
    .po-document-box {{ background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 25px; font-family: monospace; font-size: 13px; line-height: 1.5; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION GATEWAY (PASSWORDLESS ACTIVATION ENABLED) ---
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
                else: st.error("Invalid credentials. If you are an invited team member, navigate to the Activate License tab first.")
                
    with tab_activate:
        st.caption("Received an activation code from an administrator? Use this panel to configure your operational credentials:")
        with st.form("activate_license_form"):
            act_email = st.text_input("Invited Account Email (e.g., angel@luxurycountertops.com)").strip()
            act_token = st.text_input("Secure License Token Key", placeholder="e.g., OMNI-STONE-4412").strip()
            act_password = st.text_input("Set Your New Account Password", type="password")
            act_company = st.text_input("Confirm Your Business Entity Name")
            
            if st.form_submit_button("⚡ Initialize Workspace & Set Credentials", use_container_width=True):
                matching_token = [k for k in st.session_state.generated_license_keys if k["Key Token"] == act_token and k["Assigned Client"].lower() == act_email.lower()]
                if matching_token:
                    payload = {
                        "email": act_email,
                        "password_hash": act_password,
                        "company_name": act_company if act_company else "Invited Enterprise Partner",
                        "assigned_role": f"🏗️ {matching_token[0]['Tier']} Tenant"
                    }
                    supabase_api_call(endpoint="user_registry", method="POST", payload=payload)
                    for idx, key in enumerate(st.session_state.generated_license_keys):
                        if key["Key Token"] == act_token:
                            st.session_state.generated_license_keys[idx]["Status"] = "Active / Verified"
                    st.success("🎉 Workspace activated successfully! Flip to the Login tab to log in.")
                    time.sleep(1); st.rerun()
                else: st.error("🚨 Activation Denied. Token does not match the registered client email validation values.")

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

# --- 7. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["pitch_white"], t["audit_logs"], t["procure"], t["saas_licensing"], t["chat_hub"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 8. GLOBAL TELEMETRY BAR HEADER ---
st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

# --- 9. GLOBAL DATABASE CROSS-TABLE RECOVERY ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})
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
completed_milestones = sum([st.session_state.bank_connected, st.session_state.escrow_locked > 0, (has_materials or len(st.session_state.commercial_units) > 0), bool(st.session_state.contract_agreements)])
onboarding_percentage = (completed_milestones / 4) * 100

# --- 10. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.write("#### 🎯 Your Interactive Onboarding Milestone Map")
    st.progress(onboarding_percentage / 100)
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.bank_connected = True; st.session_state.escrow_locked = 220000.00; st.session_state.wallet_balance = 75000.00
        st.session_state.commercial_units = pd.DataFrame([
            {"Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00},
            {"Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Pending Review", "Value Release": 2250.00}
        ])
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
elif selected_page == t["audit_logs"]: st.write(f"### {t['audit_logs']}")
elif selected_page == t["procure"]: st.write(f"### {t['procure']}")
elif selected_page == t["saas_licensing"]: st.write(f"### {t['saas_licensing']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# LIVE DISPATCH HUB ROUTING VIEW
elif selected_page == t["chat_hub"]:
    st.write(f"### {t['chat_hub']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Live Context-Bound Field Dispatch Hub</b></div>", unsafe_allow_html=True)
    col_msg_input, col_msg_feed = st.columns([1, 1.4])
    active_rooms = ["Global Scope Thread", "Room 101", "Room 102", "Room 201", "Room 202"]
    
    with col_msg_input:
        st.write("#### 📣 Dispatch Live Progress Report")
        msg_target_room = st.selectbox("Assign Message to Room Grid Target Node", active_rooms)
        msg_text_raw = st.text_area("Field Update Note / Exception Summary Note")
        if st.button("⚡ Broadcast Update to Project Matrix", use_container_width=True):
            if msg_text_raw:
                user_role_tag = "⚡ Subcontractor" if "Sub" in st.session_state.user_role or "Tenant" in st.session_state.user_role else "🏗️ General Contractor"
                st.session_state.field_dispatch_messages.insert(0, {
                    "Timestamp": datetime.datetime.now().strftime("%I:%M %p"),
                    "Sender": st.session_state.user_email, "Role": user_role_tag, "Room Context": msg_target_room, "Message String": sanitize_input(msg_text_raw)
                })
                st.success("Message broadcasted!")
                time.sleep(0.5); st.rerun()

    with col_msg_feed:
        st.write("#### 📡 Filtered Project Telemetry Feed")
        feed_filter = st.radio("Stream Context View Filter", ["Show All Feed Actions", "Room 101 Logs Only", "Room 102 Logs Only"], horizontal=True)
        filtered_messages = st.session_state.field_dispatch_messages
        if "Room 101" in feed_filter: filtered_messages = [m for m in st.session_state.field_dispatch_messages if m["Room Context"] == "Room 101"]
        elif "Room 102" in feed_filter: filtered_messages = [m for m in st.session_state.field_dispatch_messages if m["Room Context"] == "Room 102"]
        
        for msg in filtered_messages:
            bubble_class = "chat-bubble-gc" if "General" in msg["Role"] else "chat-bubble-sub"
            st.markdown(f"""
            <div class='{bubble_class}'>
                <span style='font-size: 10px; color: #94A3B8; float: right;'>⏱️ {msg['Timestamp']}</span>
                <strong style='color: #F8FAFC;'>{msg['Sender']}</strong> <span style='font-size: 11px; color: #94A3B8;'>({msg['Role']})</span><br>
                <span style='background-color: #070B12; color: #F59E0B; font-size: 10px; padding: 2px 6px; border-radius: 3px; font-family: monospace; display: inline-block; margin: 4px 0;'>📍 {msg['Room Context']}</span><br>
                <p style='margin: 4px 0 0 0; color: #CBD5E1; font-size: 13px;'>{msg['Message String']}</p>
            </div>
            """, unsafe_allow_html=True)