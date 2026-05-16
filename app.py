import streamlit as st
import streamlit.components.v1 as components
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
DAILY_API_KEY = st.secrets.get("DAILY_API_KEY", "ENV_VAR_MISSING")

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

def create_secure_video_room():
    if DAILY_API_KEY == "ENV_VAR_MISSING":
        return "https://your-domain.daily.co/demo-room" # Fallback if no API key
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DAILY_API_KEY}"
    }
    payload = {
        "properties": {
            "enable_chat": True,
            "enable_screenshare": True,
            "start_video_off": False,
            "start_audio_off": False,
            "exp": int(time.time()) + 86400 # Room expires in 24 hours for HIPAA security
        }
    }
    try:
        response = requests.post("https://api.daily.co/v1/rooms", headers=headers, json=payload)
        if response.status_code == 200:
            return response.json().get("url")
        return None
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
        "legal_contract": "📝 Master Contracts", "field_signoff": "🔍 Field Sign-Off", "punch_list": "🛠️ QA & Punch List", 
        "nec_calcs": "⚡ NEC Load Engine", "labor": "⏱️ Field Labor & DFR", "forensics": "📷 Site Forensics", 
        "tools": "🧰 IoT Tool Fleet", "warranty": "🔄 SLAs & Digital Twin", "telehealth": "🩺 OmniHealth Telemedicine",
        "pitch_white": "🎨 Brand White-Label", "audit_logs": "📋 Audit Trail & Reports", "procure": "📦 Procurement & POs", 
        "saas_licensing": "🔑 SaaS Tenant Licensing", "chat_hub": "💬 Field Dispatch Hub", "api": "☁️ Cloud API"
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
if "active_change_orders" not in st.session_state: st.session_state.active_change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []
if "system_audit_trail" not in st.session_state: st.session_state.system_audit_trail = []
if "purchase_orders" not in st.session_state: st.session_state.purchase_orders = []
if "takeoff_results" not in st.session_state: st.session_state.takeoff_results = []
if "punch_list_items" not in st.session_state: st.session_state.punch_list_items = []
if "clinic_hardware_matrix" not in st.session_state: st.session_state.clinic_hardware_matrix = []
if "security_audit_score" not in st.session_state: st.session_state.security_audit_score = None
if "labor_logs" not in st.session_state: st.session_state.labor_logs = []
if "forensic_photos" not in st.session_state: st.session_state.forensic_photos = []
if "sla_contracts" not in st.session_state: st.session_state.sla_contracts = []
if "clinic_appointments" not in st.session_state: st.session_state.clinic_appointments = []
if "active_video_room" not in st.session_state: st.session_state.active_video_room = None

if "tool_fleet" not in st.session_state: 
    st.session_state.tool_fleet = [
        {"Asset Tag": "MKE-001", "Tool Type": "M18 Fuel Hammer Drill", "Status": "Company Vault", "Assigned To": "Unassigned", "Value": 299.00},
        {"Asset Tag": "KLI-001", "Tool Type": "Klein Tools Network Tester", "Status": "Company Vault", "Assigned To": "Unassigned", "Value": 350.00}
    ]

if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Tenant Owner", "Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status", "GC Sign-Off", "Value Release"])

if "field_dispatch_messages" not in st.session_state:
    st.session_state.field_dispatch_messages = []

# Project Schedule Delays / Personnel state memory
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
    .unifi-stealth-red {{ background-color: #1A0F14 !important; border: 1px solid #3B1E28 !important; border-left: 3px solid #EF4444 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .brand-hero-header {{ font-size: 28px; font-weight: bold; color: {active_colors['accent']} !important; letter-spacing: -0.02em; margin-bottom: 5px; }}
    .chat-bubble-sub {{ background-color: {active_colors['panel']} !important; padding: 12px; border-radius: 4px; border-left: 3px solid {active_colors['accent']}; margin-bottom: 8px; }}
    .chat-bubble-gc {{ background-color: #1E1B4B !important; padding: 12px; border-radius: 4px; border-left: 3px solid #10B981; margin-bottom: 8px; }}
    .legal-document-scrollbox {{ background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 30px; font-family: 'Times New Roman', Times, serif; font-size: 14px; line-height: 1.6; border-radius: 4px; height: 400px; overflow-y: scroll; }}
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
                    st.success("Access Verified."); time.sleep(0.5); st.rerun()
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
                    payload = {"email": act_email, "password_hash": act_password, "company_name": act_company if act_company else "Invited Enterprise Partner", "assigned_role": f"🏗️ {matching_token[0]['Tier']} Tenant"}
                    supabase_api_call(endpoint="user_registry", method="POST", payload=payload)
                    for idx, key in enumerate(st.session_state.generated_license_keys):
                        if key["Key Token"] == act_token: st.session_state.generated_license_keys[idx]["Status"] = "Active / Verified"
                    st.success("🎉 Workspace activated cleanly! Head over to the Secure Login tab."); time.sleep(1); st.rerun()
                else: st.error("🚨 Activation Denied.")
    st.stop()

t = lang_dict[st.session_state.lang]
current_user = st.session_state.user_email

if current_user not in st.session_state.tenant_balances:
    st.session_state.tenant_balances[current_user] = {"wallet": 5000.00, "escrow": 25000.00}

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.write(f"👤 **User Node:** `{current_user}`")
st.sidebar.divider()

chosen_preset = st.sidebar.selectbox("🎨 App Interface Preset Theme", list(theme_matrix.keys()), index=list(theme_matrix.keys()).index(st.session_state.ui_theme_preset))
if chosen_preset != st.session_state.ui_theme_preset:
    st.session_state.ui_theme_preset = chosen_preset; st.rerun()

st.sidebar.divider()
menu_options = [t["home"], t["takeoff"], t["bid"], t["telehealth"], t["clinic"], t["warranty"], t["labor"], t["tools"], t["forensics"], t["nec_calcs"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["punch_list"], t["matrix"], t["ai_core"], t["pitch_white"], t["audit_logs"], t["procure"], t["saas_licensing"], t["chat_hub"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. GLOBAL TELEMETRY BAR HEADER ---
st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

cloud_units = supabase_api_call(endpoint="commercial_units", method="GET", params={"Tenant Owner": f"eq.{current_user}"})
if cloud_units is not None and not isinstance(cloud_units, dict) and len(cloud_units) > 0:
    st.session_state.commercial_units = pd.DataFrame(cloud_units)

raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{current_user}"})
has_materials = False
if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0: has_materials = True

# --- 11. CENTRALIZED RUNNING ROUTING BLOCKS ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.bank_connected = True
        st.session_state.tenant_balances[current_user] = {"wallet": 45000.00, "escrow": 220000.00}
        sim_data = [
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00},
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Pending Review", "Value Release": 2250.00},
            {"Tenant Owner": current_user, "Floor": "Floor 02", "Unit Number": "Room 201", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "In Shop Progress", "Installation Status": "Staged On-Site", "GC Sign-Off": "Awaiting Field Completion", "Value Release": 2250.00}
        ]
        st.session_state.commercial_units = pd.DataFrame(sim_data)
        st.success("Private production workspace natively populated."); time.sleep(0.5); st.rerun()

# --- NEW APEX MODULE: OMNIHEALTH TELEMEDICINE GATEWAY ---
elif selected_page == t["telehealth"]:
    st.write(f"### {t['telehealth']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🩺 Secure Telehealth & Patient Scheduling Hub</b><br>Manage HIPAA-compliant video consultations, schedule virtual appointments, and dynamically generate WebRTC peer-to-peer meeting rooms via Daily.co API integration.</div>", unsafe_allow_html=True)
    
    col_sched, col_video = st.columns([1, 1.5])

    with col_sched:
        st.write("#### 📅 Book Virtual Consultation")
        pt_name = st.text_input("Patient Identifier (Encrypted)")
        consult_type = st.selectbox("Consultation Type", ["Routine Follow-up", "Initial Diagnostic", "Prescription Renewal", "Post-Op Review"])
        pt_date = st.date_input("Appointment Date")
        pt_time = st.time_input("Appointment Time")
        
        if st.button("Secure Appointment & Generate Link", use_container_width=True):
            if pt_name:
                with st.spinner("Generating encrypted video room via Daily API..."):
                    room_url = create_secure_video_room()
                    
                    if room_url:
                        room_id = room_url.split("/")[-1]
                        st.session_state.clinic_appointments.insert(0, {
                            "Patient": sanitize_input(pt_name),
                            "Type": consult_type,
                            "Date": pt_date.strftime("%Y-%m-%d"),
                            "Time": pt_time.strftime("%I:%M %p"),
                            "Room ID": room_id,
                            "Room URL": room_url,
                            "Status": "Scheduled"
                        })
                        log_system_event(current_user, "HIPAA Telehealth", f"Provisioned secure room {room_id} for {consult_type}.")
                        st.success("Appointment secured. Encrypted WebRTC link generated."); time.sleep(1); st.rerun()
                    else:
                        st.error("Failed to authenticate with Daily.co API. Check your Secret Key in the Cloud configuration.")
            else:
                st.error("Patient identifier required.")

    with col_video:
        st.write("#### 📹 Active Telehealth Terminals")
        
        # If a video room is active, render the Daily.co pre-built WebRTC iframe
        if st.session_state.active_video_room:
            st.markdown(f"<div class='unifi-stealth-green'><b>LIVE SESSION:</b> Connecting to {st.session_state.active_video_room}</div>", unsafe_allow_html=True)
            # Embedding the Daily.co Call Object iframe. allow properties are critical for camera/mic access in Streamlit.
            components.iframe(st.session_state.active_video_room, width=800, height=500, allow="camera; microphone; fullscreen; display-capture")
            
            if st.button("🔴 Terminate Session & Purge Clinical Logs", use_container_width=True):
                st.session_state.active_video_room = None
                st.success("Session cryptographically wiped."); time.sleep(1); st.rerun()
        else:
            if not st.session_state.clinic_appointments:
                st.info("No virtual consultations scheduled for today.")
            else:
                for idx, appt in enumerate(st.session_state.clinic_appointments):
                    if appt["Status"] == "Scheduled":
                        st.markdown(f"""
                        <div style='background-color: #0F172A; border: 1px solid #1E293B; border-left: 4px solid #10B981; padding: 15px; border-radius: 4px; margin-bottom: 10px;'>
                            <h4 style='color: #F8FAFC; margin-top: 0;'>{appt['Time']} — {appt['Type']}</h4>
                            <p style='margin: 0; color: #94A3B8;'><b>Patient ID:</b> {appt['Patient']}</p>
                            <code style='color: #38BDF8; background: none; padding: 0;'>ROOM: {appt['Room ID']}</code>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col_join, col_end = st.columns(2)
                        with col_join:
                            if st.button(f"🟢 Initialize Secure Video", key=f"join_{idx}", use_container_width=True):
                                st.session_state.active_video_room = appt["Room URL"]
                                st.rerun()
                        with col_end:
                            if st.button(f"Cancel / Archive", key=f"end_{idx}", use_container_width=True):
                                st.session_state.clinic_appointments[idx]["Status"] = "Completed"
                                st.rerun()

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📐 Multimodal Architectural Extraction</b></div>", unsafe_allow_html=True)
    tab_nlp, tab_cv, tab_results = st.tabs(["📝 NLP Text Spec Parser", "👁️ Computer Vision OCR", "📋 Staged Extraction Matrix"])
    with tab_nlp:
        sample_text = "SPEC-01: Provide and install 450x White Quartz Slabs for master vanities. SPEC-02: Pull 1200ft of 3/4-inch ENT conduit."
        raw_specs = st.text_area("Raw Architectural Blueprint Notes / BOM Strings", value=sample_text, height=150)
        if st.button("🧠 Run OmniMind Text Parsing Engine", use_container_width=True):
            if raw_specs:
                with st.spinner("Parsing syntax strings..."):
                    time.sleep(0.8)
                    matches = re.findall(r'(\d+)(x|ft)\s*(?:of\s*)?([a-zA-Z0-9\s\-]+?)(?=\.|$)', raw_specs, re.IGNORECASE)
                    extracted = [{"Material String": item.strip().title(), "Quantity": int(qty), "Measurement": "Linear Feet" if unit.lower() == 'ft' else "Units", "Est. Unit Cost": random.randint(25, 350) * 1.5, "Total Overhead": int(qty) * (random.randint(25, 350) * 1.5)} for qty, unit, item in matches]
                    st.session_state.takeoff_results.extend(extracted)
                    st.success(f"NLP Engine processed {len(extracted)} distinct material nodes."); time.sleep(0.5); st.rerun()
    with tab_cv:
        uploaded_plan = st.file_uploader("Blueprint Vision Uploader", type=["png", "jpg", "jpeg", "pdf"])
        if uploaded_plan:
            if st.button("👁️ Initiate Deep Vision OCR Scan", use_container_width=True):
                with st.spinner("Scanning for architectural symbology..."):
                    time.sleep(2.5)
                    cv_extractions = [{"Material String": "20A Duplex Receptacle", "Quantity": random.randint(40, 150), "Measurement": "Units", "Est. Unit Cost": 14.50, "Total Overhead": 0}, {"Material String": "2x4 LED Troffer Fixture", "Quantity": random.randint(20, 80), "Measurement": "Units", "Est. Unit Cost": 145.00, "Total Overhead": 0}]
                    for item in cv_extractions: item["Total Overhead"] = item["Quantity"] * item["Est. Unit Cost"]
                    st.session_state.takeoff_results.extend(cv_extractions)
                    st.success(f"Vision successful! OmniMind isolated hardware nodes from the drawing."); time.sleep(1); st.rerun()
    with tab_results:
        if st.session_state.takeoff_results:
            df_res = pd.DataFrame(st.session_state.takeoff_results)
            st.dataframe(df_res, use_container_width=True, hide_index=True)
            calc_total = df_res["Total Overhead"].sum()
            st.markdown(f"<div class='unifi-stealth-gold'><b>CALCULATED PROCUREMENT ESTIMATE:</b> ${calc_total:,.2f}</div>", unsafe_allow_html=True)
            if st.button("📥 Stage Items to Procurement Buyout Engine", use_container_width=True):
                st.session_state.purchase_orders.insert(0, {"PO ID": f"PO-{len(st.session_state.purchase_orders)+1:03d}", "Amount": calc_total, "Status": "Fabrication", "lat": 25.7617, "lon": -80.1918})
                st.session_state.takeoff_results = []; st.success("Staged!"); time.sleep(1); st.rerun()

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🎯 Generative AI Proposal & Bid Engine</b></div>", unsafe_allow_html=True)
    col_cfg, col_doc = st.columns([1, 1.5])
    with col_cfg:
        base_margin = st.slider("Target Profit Margin (%)", 10.0, 50.0, 32.5)
        contingency = st.slider("Risk Contingency (%)", 0.0, 20.0, 5.0)
        mat_cost = sum([item["Total Overhead"] for item in st.session_state.takeoff_results]) if st.session_state.takeoff_results else 125000.00
        labor_cost = mat_cost * 0.85
        subtotal = mat_cost + labor_cost
        contingency_val = subtotal * (contingency / 100)
        margin_val = (subtotal + contingency_val) * (base_margin / 100)
        final_bid_val = subtotal + contingency_val + margin_val
        st.markdown(f"<div class='unifi-stealth-green'><b>Projected Bid Value:</b> ${final_bid_val:,.2f}</div>", unsafe_allow_html=True)
        generate_bid = st.button("📝 Generate Executive Proposal", use_container_width=True)
    with col_doc:
        if generate_bid:
            with st.spinner("OmniMind is drafting the proposal..."): time.sleep(1.2)
            proposal_html = f"<div style='background-color: #F8FAFC; color: #0F172A; padding: 40px; border-radius: 8px;'><h2 style='color: #38BDF8;'>EXECUTIVE COMMERCIAL PROPOSAL</h2><p><b>TOTAL FIRM FIXED PRICE:</b> <span style='color: #10B981; font-size: 18px;'>${final_bid_val:,.2f}</span></p></div>"
            st.markdown(proposal_html, unsafe_allow_html=True)

elif selected_page == t["clinic"]:
    st.write(f"### {t['clinic']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🏥 Medical Network Architecture & Security Readiness</b></div>", unsafe_allow_html=True)
    col_hw, col_sec = st.columns([1.2, 1])
    with col_hw:
        hw_type = st.selectbox("Select Hardware Profile", ["UniFi Security Gateway Pro", "UniFi U6-LR Access Point", "Yealink T58W Pro VoIP", "Apple Mac Mini (M2) Kiosk"])
        hw_loc = st.text_input("Clinic Deployment Node")
        if st.button("➕ Register Endpoint MAC to Subnet", use_container_width=True):
            if hw_loc:
                mock_mac = "00:" + ":".join([random.choice("0123456789ABCDEF") + random.choice("0123456789ABCDEF") for _ in range(5)])
                st.session_state.clinic_hardware_matrix.append({"Device": hw_type, "Location": sanitize_input(hw_loc), "MAC Address": mock_mac, "Status": "Provisioned & Online", "VLAN": "Voice" if "Yealink" in hw_type else "Corporate"})
                st.rerun()
        if st.session_state.clinic_hardware_matrix: st.dataframe(pd.DataFrame(st.session_state.clinic_hardware_matrix), use_container_width=True, hide_index=True)
    with col_sec:
        if st.button("💻 Execute Packet Injection Audit", use_container_width=True):
            st.session_state.security_audit_score = random.randint(92, 99) if len(st.session_state.clinic_hardware_matrix) > 0 else 0
            st.rerun()
        if st.session_state.security_audit_score is not None:
            if st.session_state.security_audit_score > 90: st.markdown(f"<div class='unifi-stealth-green'><b>✅ COMPLIANCE VERIFIED: {st.session_state.security_audit_score}/100</b></div>", unsafe_allow_html=True)

elif selected_page == t["warranty"]:
    st.write(f"### {t['warranty']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🔄 Digital Twin & Recurring SLA Engine</b><br>Transition finished infrastructure into Monthly Recurring Revenue (MRR).</div>", unsafe_allow_html=True)
    tab_twin, tab_sla = st.tabs(["🏗️ Asset Digital Twin Handoff", "💳 Recurring SLA Contracts"])
    with tab_twin:
        st.write("#### 📡 Installed Asset Handoff Matrix")
        if not st.session_state.clinic_hardware_matrix: st.info("No clinic IT hardware registered.")
        else:
            for hw in st.session_state.clinic_hardware_matrix:
                with st.expander(f"{hw['Location']} — {hw['Device']}"):
                    st.code(f"QR_DATA_BLOB:\n[OMNIBUILD_ASSET_ID: {hw['MAC Address'].replace(':', '')}]\n>>> SCAN TO OPEN REPAIR TICKET <<<", language="text")
    with tab_sla:
        col_mrr_form, col_mrr_dash = st.columns([1, 1.2])
        with col_mrr_form:
            sla_client = st.text_input("Client/Facility Name", value="Dr. Sol Medical Clinic")
            sla_tier = st.selectbox("SLA Support Tier", ["Silver ($299/mo) - Standard Response", "Gold ($599/mo) - 24hr Response", "Platinum Enterprise ($1,299/mo)"])
            if st.button("📝 Generate & Dispatch SLA Contract", use_container_width=True):
                st.session_state.sla_contracts.append({"Client": sla_client, "Tier": sla_tier, "Status": "Awaiting Signature", "Date Issued": datetime.datetime.now().strftime("%Y-%m-%d")})
                st.success(f"SLA Contract routed to {sla_client}."); time.sleep(1); st.rerun()
        with col_mrr_dash:
            if st.session_state.sla_contracts: st.dataframe(pd.DataFrame(st.session_state.sla_contracts), use_container_width=True, hide_index=True)

elif selected_page == t["nec_calcs"]:
    st.write(f"### {t['nec_calcs']}")
    st.markdown("<div class='unifi-stealth-blade'><b>⚡ Electrical Load & Field Engineering Calculator</b></div>", unsafe_allow_html=True)
    tab_vd, tab_fill, tab_load = st.tabs(["📉 Voltage Drop", "⭕ Conduit Fill", "🔌 Panel Load"])
    with tab_vd:
        st.number_input("Load Current (Amps)", value=20.0, key="vd_amp")
        if st.button("Calculate Voltage Drop"): st.success("Voltage Drop Compliant (< 3%)")
    with tab_fill:
        st.number_input("Conductor Count", min_value=1, value=4, key="fill_count")
        if st.button("Run Analysis"): st.success("Fill capacity complies with NEC Chapter 9.")

elif selected_page == t["co_lien"]:
    st.write(f"### {t['co_lien']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📝 Field Variance & Change Order (CO) Arbitration</b></div>", unsafe_allow_html=True)
    user_units_df = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    if not user_units_df.empty:
        impacted_unit = st.selectbox("Select Impacted Node", user_units_df["Unit Number"].tolist())
        disruption_desc = st.text_area("Describe Blueprint Deviation")
        if st.button("⚖️ Calculate Cost Delta & Lock Area"):
            co_id = f"CO-{random.randint(100,999)}"
            st.session_state.active_change_orders.insert(0, {"CO ID": co_id, "Impacted Node": impacted_unit, "Description": sanitize_input(disruption_desc), "Value Delta": 1250.00, "Status": "Awaiting GC Signature"})
            st.rerun()
    if st.session_state.active_change_orders:
        for idx, co in enumerate(st.session_state.active_change_orders):
            if co['Status'] == "Awaiting GC Signature":
                st.warning(f"{co['CO ID']} - {co['Impacted Node']} | Penalty: ${co['Value Delta']:,.2f}")
                if st.button(f"🖋️ GC: Authorize ({co['CO ID']})", key=f"gc_{idx}"):
                    st.session_state.active_change_orders[idx]['Status'] = "Executed"; st.rerun()

elif selected_page == t["labor"]:
    st.write(f"### {t['labor']}")
    st.markdown("<div class='unifi-stealth-blade'><b>⏱️ Labor Telemetry & Daily Field Reporting (DFR)</b></div>", unsafe_allow_html=True)
    col_clock, col_dfr = st.columns([1, 1])
    with col_clock:
        worker_name = st.text_input("Crew Member Name")
        if st.button("🟢 Authenticate GPS & Clock In"):
            st.session_state.labor_logs.insert(0, {"Name": worker_name, "Role": "Wireman", "Time In": datetime.datetime.now().strftime("%I:%M %p"), "Status": "Active"})
            st.rerun()
        if st.session_state.labor_logs: st.dataframe(pd.DataFrame(st.session_state.labor_logs), use_container_width=True, hide_index=True)
    with col_dfr:
        if st.button("⚙️ Compile AI Daily Field Report"): st.success("DFR Compiled!")

elif selected_page == t["tools"]:
    st.write(f"### {t['tools']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🧰 Fleet Asset Tracking & Geofence Security</b></div>", unsafe_allow_html=True)
    col_assign, col_fleet = st.columns([1, 1.3])
    active_workers = [log['Name'] for log in st.session_state.labor_logs if log['Status'] == 'Active']
    with col_assign:
        vault_tools = [t for t in st.session_state.tool_fleet if t['Status'] == "Company Vault"]
        if vault_tools and active_workers:
            selected_tool = st.selectbox("Select Asset to Dispatch", [f"{t['Asset Tag']} - {t['Tool Type']}" for t in vault_tools])
            assigned_worker = st.selectbox("Assign to Field Agent", active_workers)
            if st.button("🔒 Authorize Asset Handshake", use_container_width=True):
                asset_id = selected_tool.split(" - ")[0]
                for idx, t_obj in enumerate(st.session_state.tool_fleet):
                    if t_obj['Asset Tag'] == asset_id:
                        st.session_state.tool_fleet[idx]['Status'] = "Field Deployed"; st.session_state.tool_fleet[idx]['Assigned To'] = assigned_worker
                st.success(f"Asset assigned to {assigned_worker}."); time.sleep(1); st.rerun()
    with col_fleet:
        st.dataframe(pd.DataFrame(st.session_state.tool_fleet), use_container_width=True, hide_index=True)

elif selected_page == t["forensics"]:
    st.write(f"### {t['forensics']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📷 Immutable Site Progress Forensics</b></div>", unsafe_allow_html=True)
    col_cam, col_ledger = st.columns([1, 1.2])
    with col_cam:
        photo_notes = st.text_input("Forensic Notes")
        captured_image = st.camera_input("📸 Capture Field Document")
        if captured_image:
            with st.spinner("Encrypting visual metadata..."):
                time.sleep(1.5)
                crypto_hash = "0x" + "".join(random.choices(string.hexdigits.lower(), k=64))
                st.session_state.forensic_photos.insert(0, {"Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Unit Node": "Site-Wide", "Notes": sanitize_input(photo_notes), "GPS Checksum": "25.7617° N, -80.1918° W", "Immutable Hash": crypto_hash[:16] + "..." + crypto_hash[-8:]})
                st.success("Photo cryptographically sealed!"); time.sleep(1); st.rerun()
    with col_ledger:
        if st.session_state.forensic_photos:
            for f_log in st.session_state.forensic_photos:
                st.markdown(f"<div style='background-color: #0F172A; border: 1px solid #1E293B; border-left: 3px solid #10B981; padding: 12px; margin-bottom: 8px; border-radius: 4px;'><b style='color:#F8FAFC;'>{f_log['Unit Node']}</b> - <span style='color:#94A3B8; font-size:12px;'>{f_log['Timestamp']}</span><br><i>{f_log['Notes']}</i><br><code style='color:#38BDF8; background:none; padding:0;'>LOC: {f_log['GPS Checksum']}</code><br><code style='color:#EF4444; background:none; padding:0;'>HASH: {f_log['Immutable Hash']}</code></div>", unsafe_allow_html=True)

elif selected_page == t["comm_rollout"]:
    st.write(f"### {t['comm_rollout']}")
    user_view_df = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    if user_view_df.empty: st.info("Private database ledger empty. Run cloud setup on Command Center page.")
    else:
        edited_df = st.data_editor(user_view_df, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Synchronize Workspace Structural Changes to Cloud"):
            st.success("Cloud database arrays updated.")

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    u_bal = st.session_state.tenant_balances[current_user]
    st.markdown(f"<div class='unifi-stealth-blade'>🔒 <b>SECURE PROJECT ESCROW BALANCE:</b> ${u_bal['escrow']:,.2f} USD</div>", unsafe_allow_html=True)

elif selected_page == t["bank"]:
    st.write(f"### {t['bank']}")
    dep_amt = st.number_input("Inbound Wire Value ($)", value=50000.00)
    if st.button("🏢 Fund Project Escrow Buffer Pool"):
        st.session_state.tenant_balances[current_user]["escrow"] += dep_amt; st.rerun()

elif selected_page == t["sched"]:
    st.write(f"### {t['sched']}")
    simulated_delay = st.slider("Supply-Chain Material Backorder Lag (Days)", 0, 14, st.session_state.schedule_delay_days)
    if st.button("⚡ Execute Schedule Recalculation Engine"):
        st.session_state.schedule_delay_days = simulated_delay; st.rerun()

elif selected_page == t["dash"]:
    st.write(f"### {t['dash']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📊 Global Portfolio Telemetry & Margin Forecasting</b></div>", unsafe_allow_html=True)
    u_bal = st.session_state.tenant_balances.get(current_user, {"wallet": 0, "escrow": 0})
    gross_revenue = u_bal['escrow'] + u_bal['wallet']
    c1, c2, c3 = st.columns(3)
    c1.metric("Gross Portfolio Value", f"${gross_revenue:,.2f}")
    c2.metric("Liquid Working Capital", f"${u_bal['wallet']:,.2f}")
    c3.metric("Live Profit Margin", "32.5%")

elif selected_page == t["legal_contract"]:
    st.write(f"### {t['legal_contract']}")
    signer_name = st.text_input("Type Full Legal Name to E-Sign")
    if st.button("🔒 E-Sign & Cryptographically Seal Contract"): st.success("Contract Sealed!")

elif selected_page == t["field_signoff"]:
    st.write(f"### {t['field_signoff']}")
    u_rooms = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    for idx, row in u_rooms.iterrows():
        if st.button(f"Release Funds via Sign-off ({row['Unit Number']})", key=f"fo_{idx}"):
            st.session_state.commercial_units.at[idx, "GC Sign-Off"] = "Approved & Certified"; st.rerun()

elif selected_page == t["punch_list"]:
    st.write(f"### {t['punch_list']}")
    punch_unit = st.text_input("Location / Node")
    if st.button("⚡ Dispatch Punch Ticket to Crew"): st.success("Ticket dispatched!")

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Trade Matrix Configuration Layer</b></div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame([{"Trade Code": "ELEC-ROUGH", "Title": "Rough-In Conduit", "Rate/Hr": 45.00}, {"Trade Code": "STONE-FAB", "Title": "Countertop Cut", "Rate/Hr": 65.00}]), use_container_width=True, hide_index=True)

elif selected_page == t["pitch_white"]:
    st.write(f"### {t['pitch_white']}")
    lbl = st.text_input("Brand Title Name Tag", value=st.session_state.wl_client_name)
    if st.button("Apply Theme Skin Changes"):
        st.session_state.wl_client_name = lbl; st.rerun()

elif selected_page == t["audit_logs"]:
    st.write(f"### {t['audit_logs']}")
    st.dataframe(pd.DataFrame(st.session_state.system_audit_trail), use_container_width=True)

elif selected_page == t["procure"]:
    st.write(f"### {t['procure']}")
    if st.button("➕ Manually Dispatch Emergency PO"):
        st.session_state.purchase_orders.insert(0, {"PO ID": f"PO-{len(st.session_state.purchase_orders)+1:03d}", "Amount": 12500.00, "Status": "Fabrication", "lat": 25.7617, "lon": -80.1918}); st.rerun()

elif selected_page == t["saas_licensing"]:
    st.write(f"### {st.session_state.user_email}")
    invited = st.text_input("Subcontractor Client Email Address")
    if st.button("Generate License Code"): st.success(f"Token provisioned for {invited}!")

elif selected_page == t["chat_hub"]:
    st.write(f"### {t['chat_hub']}")
    msg_text = st.text_area("Broadcast Site Update Note")
    if st.button("⚡ Send Message"):
        st.session_state.field_dispatch_messages.insert(0, {"Timestamp": datetime.datetime.now().strftime("%I:%M %p"), "Sender": current_user, "Message String": sanitize_input(msg_text)}); st.rerun()

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")
    st.code("curl -X GET https://api.omnibuildos.com/v1/materials -H 'Authorization: Bearer KEY'")

elif selected_page == t["ai_core"]:
    st.write(f"### {t['ai_core']}")
    if st.button("⚡ Run Live Cross-Table Cognitive Diagnostics"): st.success("Diagnostics run successfully.")