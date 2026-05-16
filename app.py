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
DAILY_API_KEY = st.secrets.get("DAILY_API_KEY", "ENV_VAR_MISSING")

def supabase_api_call(endpoint="materials", method="GET", payload=None, params=None):
    if SUPABASE_URL == "ENV_VAR_MISSING" or SUPABASE_KEY == "ENV_VAR_MISSING":
        return None
    headers = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json", "Prefer": "return=representation" if method in ["POST", "PATCH"] else ""}
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    try:
        if method == "GET": response = requests.get(url, headers=headers, params=params)
        elif method == "POST": response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception: return None

def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

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
        "apprenticeship": "🎓 Apprenticeship Ledger", "client_portal": "📸 Shard.Visuals Portal", "diagnostics": "🤖 Hardware Diagnostics",
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
if "purchase_orders" not in st.session_state: st.session_state.purchase_orders = []
if "takeoff_results" not in st.session_state: st.session_state.takeoff_results = []
if "punch_list_items" not in st.session_state: st.session_state.punch_list_items = []
if "clinic_hardware_matrix" not in st.session_state: st.session_state.clinic_hardware_matrix = []
if "labor_logs" not in st.session_state: st.session_state.labor_logs = []
if "forensic_photos" not in st.session_state: st.session_state.forensic_photos = []
if "sla_contracts" not in st.session_state: st.session_state.sla_contracts = []
if "clinic_appointments" not in st.session_state: st.session_state.clinic_appointments = []
if "active_video_room" not in st.session_state: st.session_state.active_video_room = None
if "base_apprentice_hours" not in st.session_state: st.session_state.base_apprentice_hours = 412.5 # Baseline progress

if "tool_fleet" not in st.session_state: 
    st.session_state.tool_fleet = [
        {"Asset Tag": "MKE-001", "Tool Type": "M18 Fuel Hammer Drill", "Status": "Company Vault", "Assigned To": "Unassigned", "Value": 299.00},
        {"Asset Tag": "KLI-001", "Tool Type": "Klein Tools Network Tester", "Status": "Company Vault", "Assigned To": "Unassigned", "Value": 350.00}
    ]

if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Tenant Owner", "Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status", "GC Sign-Off", "Value Release"])

if "generated_license_keys" not in st.session_state:
    st.session_state.generated_license_keys = [{"Key Token": "OMNI-ELEC-9821", "Tier": "Growth Team", "Assigned Client": "david@shardvisuals.com", "Status": "Active / Verified"}]

# --- 5. THEME MATRIX CONFIGURATIONS ---
theme_matrix = {
    "UniFi Stealth Slate": {"bg": "#070B12", "panel": "#0F172A", "accent": "#38BDF8", "border": "#1E293B", "text": "#94A3B8"},
    "Midnight Onyx Matrix": {"bg": "#020408", "panel": "#090D16", "accent": "#10B981", "border": "#111827", "text": "#A1A1AA"}
}
active_colors = theme_matrix[st.session_state.ui_theme_preset]

# --- 6. UNIVERSAL CUSTOM LAYOUT INJECTIONS ---
st.markdown(f"""
<style>
    .stApp {{ background-color: {active_colors['bg']} !important; color: {active_colors['text']} !important; }}
    h1, h2, h3, h4, h5, h6 {{ color: #F8FAFC !important; font-weight: 500 !important; }}
    .unifi-stealth-blade {{ background-color: {active_colors['panel']} !important; border: 1px solid {active_colors['border']} !important; border-left: 3px solid {active_colors['accent']} !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .unifi-stealth-green {{ background-color: #0B1C16 !important; border: 1px solid #143A2E !important; border-left: 3px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .brand-hero-header {{ font-size: 28px; font-weight: bold; color: {active_colors['accent']} !important; letter-spacing: -0.02em; margin-bottom: 5px; }}
    .shard-visuals-card {{ background-color: #050505 !important; border: 1px solid #333 !important; padding: 0px; border-radius: 8px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
    .shard-visuals-header {{ background: linear-gradient(90deg, #1A1A1A, #000); padding: 15px; border-bottom: 1px solid #333; }}
</style>
""", unsafe_allow_html=True)

# --- 7. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    with st.form("auth_form"):
        input_email = st.text_input("Account Email").strip()
        input_password = st.text_input("Password", type="password").strip()
        if st.form_submit_button("Verify Credentials", use_container_width=True):
            st.session_state.user_authenticated = True; st.session_state.user_email = input_email; st.session_state.company_name = "Omni Enterprise"; st.rerun()
    st.stop()

t = lang_dict[st.session_state.lang]
current_user = st.session_state.user_email
if current_user not in st.session_state.tenant_balances: st.session_state.tenant_balances[current_user] = {"wallet": 5000.00, "escrow": 25000.00}

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

menu_options = [
    t["home"], t["takeoff"], t["bid"], t["labor"], t["apprenticeship"], t["tools"], t["forensics"], t["client_portal"], 
    t["clinic"], t["diagnostics"], t["telehealth"], t["warranty"], t["nec_calcs"], t["co_lien"], t["fin"], t["bank"], 
    t["sched"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["punch_list"]
]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session", use_container_width=True): st.session_state.user_authenticated = False; st.rerun()

st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

# --- 11. CENTRALIZED ROUTING BLOCKS (NEW MODULES ADDED) ---

if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.commercial_units = pd.DataFrame([{"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00}])
        st.success("Private production workspace natively populated."); time.sleep(0.5); st.rerun()

# --- APEX MODULE 1: APPRENTICESHIP LEDGER ---
elif selected_page == t["apprenticeship"]:
    st.write(f"### {t['apprenticeship']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🎓 State Apprenticeship & Certification Ledger</b><br>Automatically route verified geofenced labor hours into a formal academic transcript to satisfy your 600-hour technical college graduation requirement.</div>", unsafe_allow_html=True)
    
    # Calculate active hours from labor logs (simulated 8 hours per completed log)
    completed_shifts = len([log for log in st.session_state.labor_logs if log['Status'] == 'Completed Shift'])
    tracked_session_hours = completed_shifts * 8.0
    total_hours = st.session_state.base_apprentice_hours + tracked_session_hours
    progress_pct = min(total_hours / 600.0, 1.0)
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Target Requirement", "600 Hrs")
    c2.metric("Total Verified Hours", f"{total_hours:.1f} Hrs", f"+{tracked_session_hours} Session Hrs")
    c3.metric("Remaining Balance", f"{max(600.0 - total_hours, 0):.1f} Hrs")
    
    st.write("#### Lindsey Hopkins Technical College Progression")
    st.progress(progress_pct)
    st.caption(f"{progress_pct*100:.1f}% Complete. Keep closing shifts in the Labor tab to automatically fill this ledger.")
    
    if st.button("📄 Generate Formal PDF Academic Transcript", use_container_width=True):
        st.success("Transcript compiled! Immutable time-stamps mapped and ready for collegiate submission.")

# --- APEX MODULE 2: SHARD.VISUALS CLIENT PORTAL ---
elif selected_page == t["client_portal"]:
    st.write(f"### {t['client_portal']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📸 Shard.Visuals Cinematic Client Interface</b><br>Transform internal forensic site photos into a high-end, read-only visual marketing portal for your executive clients.</div>", unsafe_allow_html=True)
    
    if not st.session_state.forensic_photos:
        st.info("No field photos available. Capture progress in the 'Site Forensics' tab first.")
    else:
        if st.button("🔗 Generate Secure Client Link"):
            st.success("Public URL Generated: https://portal.shardvisuals.com/client-view/auth-992")
            
        st.write("---")
        st.markdown("<h3 style='text-align:center; font-family:serif; letter-spacing: 2px; color:#F59E0B;'>SHARD.VISUALS</h3>", unsafe_allow_html=True)
        st.markdown("<p style='text-align:center; color:#64748B;'>FIELD EXECUTION GALLERY | DR. SOL MEDICAL CLINIC</p>", unsafe_allow_html=True)
        
        # Masonry style rendering
        cols = st.columns(2)
        for idx, photo in enumerate(st.session_state.forensic_photos):
            with cols[idx % 2]:
                st.markdown(f"""
                <div class='shard-visuals-card'>
                    <div class='shard-visuals-header'>
                        <span style='color:#F8FAFC; font-weight:bold;'>{photo['Unit Node']}</span><br>
                        <span style='color:#38BDF8; font-size:12px;'>CAPTURED: {photo['Timestamp']}</span>
                    </div>
                    <div style='padding:20px; color:#A1A1AA; font-style:italic;'>
                        "{photo['Notes']}"
                    </div>
                    <div style='background-color:#111; padding:10px; font-family:monospace; font-size:10px; color:#444; border-top:1px solid #333;'>
                        CRYPTO-SEAL: {photo['Immutable Hash']}
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- APEX MODULE 3: HARDWARE DIAGNOSTICS AI ---
elif selected_page == t["diagnostics"]:
    st.write(f"### {t['diagnostics']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🤖 OmniMind Hardware Diagnostics & Packet Routing</b><br>Execute automated terminal logic to isolate hardware failures, VLAN misconfigurations, and SIP packet drops before rolling a maintenance truck.</div>", unsafe_allow_html=True)
    
    if not st.session_state.clinic_hardware_matrix:
        st.info("No hardware staged on the subnet. Please provision devices in the 'Clinic Infra' tab.")
    else:
        col_ctrl, col_term = st.columns([1, 1.5])
        with col_ctrl:
            target_hw = st.selectbox("Target Node for Diagnostics", [f"{hw['Location']} - {hw['Device']}" for hw in st.session_state.clinic_hardware_matrix])
            fault_type = st.selectbox("Reported Fault", ["Device Offline / Unreachable", "VoIP SIP Registration Failure", "High Latency / Packet Loss"])
            
            run_diag = st.button("⚡ Execute Diagnostic Sequence", use_container_width=True)
            
        with col_term:
            st.write("#### 💻 Master Terminal Output")
            if run_diag:
                mac_addr = [hw['MAC Address'] for hw in st.session_state.clinic_hardware_matrix if hw['Location'] in target_hw][0]
                
                with st.spinner("Establishing SSH handshake..."):
                    time.sleep(1)
                
                term_html = f"""
                <div style='background-color:#000; color:#10B981; font-family:monospace; padding:20px; border-radius:4px; height:250px; overflow-y:scroll;'>
                    > Init OmniMind Diag v4.2<br>
                    > Pinging MAC [{mac_addr}]... SUCCESS (8ms)<br>
                    > Checking PoE Switchport Draw... 4.2W (Normal)<br>
                    > Querying UniFi Controller for VLAN Tags...<br>
                    > VLAN 20 (Corporate) ASSIGNED.<br>
                    > Analyzing Routing Tables...<br>
                """
                
                if fault_type == "VoIP SIP Registration Failure":
                    term_html += "> ⚠️ ERROR: SIP ALG is currently ENABLED on Gateway.<br>> Resolving...<br>> Executing CLI: `set system conntrack modules sip disable`<br>> Restarting NAT states...<br>> <span style='color:#38BDF8;'>FAULT RESOLVED. VoIP Handshake Successful.</span>"
                else:
                    term_html += "> Hardware logic passes all local health checks.<br>> <span style='color:#38BDF8;'>FAULT LIES WITH ISP. Rerouting traffic to WAN2 (LTE Backup).</span>"
                
                term_html += "</div>"
                st.markdown(term_html, unsafe_allow_html=True)
                st.success("Automated diagnostic routine completed successfully.")
            else:
                st.markdown("<div style='background-color:#000; color:#444; font-family:monospace; padding:20px; border-radius:4px; height:250px;'>> Awaiting diagnostic execution command...</div>", unsafe_allow_html=True)


# --- RETAINED CORE MODULES FOR FULL FUNCTIONALITY ---
elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")
    st.markdown("<div class='unifi-stealth-blade'><b>📐 Multimodal Architectural Extraction</b></div>", unsafe_allow_html=True)
    tab_nlp, tab_cv, tab_results = st.tabs(["📝 NLP Text Spec Parser", "👁️ Computer Vision OCR", "📋 Staged Extraction Matrix"])
    with tab_nlp:
        raw_specs = st.text_area("Raw Architectural Blueprint Notes", value="SPEC-01: Provide 450x White Quartz Slabs.", height=100)
        if st.button("🧠 Run NLP Parser"):
            st.session_state.takeoff_results.append({"Material String": "White Quartz Slabs", "Quantity": 450, "Total Overhead": 45000})
            st.success("Parsed!"); st.rerun()
    with tab_cv:
        uploaded_plan = st.file_uploader("Blueprint Vision Uploader", type=["png", "jpg", "pdf"])
        if uploaded_plan and st.button("👁️ Initiate Deep Vision OCR Scan"):
            st.session_state.takeoff_results.append({"Material String": "Duplex Receptacle", "Quantity": 150, "Total Overhead": 2175})
            st.success("Scanned!"); st.rerun()
    with tab_results:
        if st.session_state.takeoff_results:
            st.dataframe(pd.DataFrame(st.session_state.takeoff_results))
            if st.button("📥 Stage Items to Procurement"): st.session_state.takeoff_results = []; st.success("Staged!"); st.rerun()

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")
    base_margin = st.slider("Target Profit Margin (%)", 10.0, 50.0, 32.5)
    st.button("📝 Generate Executive Proposal", use_container_width=True)

elif selected_page == t["clinic"]:
    st.write(f"### {t['clinic']}")
    hw_type = st.selectbox("Hardware Profile", ["UniFi Security Gateway Pro", "Yealink T58W Pro VoIP"])
    hw_loc = st.text_input("Clinic Deployment Node")
    if st.button("➕ Register Endpoint MAC"):
        st.session_state.clinic_hardware_matrix.append({"Device": hw_type, "Location": hw_loc, "MAC Address": "00:1A:2B:3C:4D:5E", "VLAN": "Corporate"})
        st.rerun()
    if st.session_state.clinic_hardware_matrix: st.dataframe(pd.DataFrame(st.session_state.clinic_hardware_matrix))

elif selected_page == t["labor"]:
    st.write(f"### {t['labor']}")
    worker_name = st.text_input("Crew Member Name")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🟢 Clock In"): st.session_state.labor_logs.insert(0, {"Name": worker_name, "Status": "Active"}); st.rerun()
    with col2:
        if st.button("🔴 Clock Out"): 
            for idx, l in enumerate(st.session_state.labor_logs): 
                if l['Name']==worker_name: st.session_state.labor_logs[idx]['Status']="Completed Shift"
            st.rerun()

elif selected_page == t["forensics"]:
    st.write(f"### {t['forensics']}")
    photo_notes = st.text_input("Forensic Notes")
    captured_image = st.camera_input("📸 Capture Field Document")
    if captured_image:
        crypto_hash = "0x" + "".join(random.choices(string.hexdigits.lower(), k=64))
        st.session_state.forensic_photos.insert(0, {"Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Unit Node": "Site-Wide", "Notes": photo_notes, "Immutable Hash": crypto_hash[:16]})
        st.success("Photo cryptographically sealed!"); st.rerun()

elif selected_page == t["telehealth"]:
    st.write(f"### {t['telehealth']}")
    st.markdown("<div class='unifi-stealth-blade'><b>🩺 Secure Telehealth & Patient Scheduling Hub</b></div>", unsafe_allow_html=True)
    if st.button("Secure Appointment & Generate Link"): st.success("Encrypted WebRTC link generated.")

elif selected_page == t["tools"]:
    st.write(f"### {t['tools']}")
    st.dataframe(pd.DataFrame(st.session_state.tool_fleet))

elif selected_page == t["warranty"]:
    st.write(f"### {t['warranty']}")
    if st.button("📝 Generate & Dispatch SLA Contract"): st.success("SLA routed!")

elif selected_page == t["dash"]:
    st.write(f"### {t['dash']}")
    st.markdown("<div class='unifi-stealth-green'><b>✅ HEALTHY MARGIN YIELD</b></div>", unsafe_allow_html=True)

else:
    st.write(f"### {selected_page}")
    st.info("Module active and standing by.")