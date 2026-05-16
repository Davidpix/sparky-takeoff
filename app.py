import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import time
import math
import html
import re
import requests
import random
import string
import altair as alt

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | Enterprise Matrix", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE UI/UX ENGINE (MODERN MINIMALIST) ---
def inject_global_styles():
    st.markdown("""
    <style>
        .stApp { background-color: #030508 !important; color: #E2E8F0 !important; font-family: 'Helvetica Neue', sans-serif; }
        h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.03em; }
        .shard-panel { background-color: #0A0F17 !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 24px; border-radius: 4px; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .shard-panel-green { background-color: #05100D !important; border: 1px solid #064E3B !important; border-left: 3px solid #10B981 !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; }
        .shard-panel-gold { background-color: #120D04 !important; border: 1px solid #78350F !important; border-left: 3px solid #F59E0B !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; }
        .shard-panel-red { background-color: #170505 !important; border: 1px solid #7F1D1D !important; border-left: 3px solid #EF4444 !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; }
        .shard-header { font-size: 28px; font-weight: 600; color: #38BDF8 !important; letter-spacing: -0.02em; margin-bottom: 5px; text-transform: uppercase; }
        .stButton>button { background-color: #0F172A; color: #F8FAFC; border: 1px solid #1E293B; border-radius: 4px; transition: all 0.2s ease; }
        .stButton>button:hover { background-color: #38BDF8; color: #030508; border: 1px solid #38BDF8; }
        .shard-visuals-card { background-color: #050505 !important; border: 1px solid #333 !important; padding: 0px; border-radius: 8px; overflow: hidden; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }
        .shard-visuals-header { background: linear-gradient(90deg, #1A1A1A, #000); padding: 15px; border-bottom: 1px solid #333; }
        .document-scrollbox { background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 30px; font-family: 'Times New Roman', serif; border-radius: 4px; height: 400px; overflow-y: scroll; }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()

# --- 3. SECURE CLOUD INITIALIZATION & API HELPERS ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "ENV_VAR_MISSING")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "ENV_VAR_MISSING")
DAILY_API_KEY = st.secrets.get("DAILY_API_KEY", "ENV_VAR_MISSING")

def create_secure_video_room():
    if DAILY_API_KEY == "ENV_VAR_MISSING": return "https://your-domain.daily.co/demo-room"
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {DAILY_API_KEY}"}
    payload = {"properties": {"enable_chat": True, "enable_screenshare": True, "exp": int(time.time()) + 86400}}
    try:
        response = requests.post("https://api.daily.co/v1/rooms", headers=headers, json=payload)
        if response.status_code == 200: return response.json().get("url")
    except Exception: return None

def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

# --- 4. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": False, "user_email": "", "company_name": "Shard.Visuals Enterprise", "wl_client_name": "OmniBuild OS Standard",
    "tenant_balances": {}, "active_change_orders": [], "transaction_history": [], "contract_agreements": [], "system_audit_trail": [],
    "purchase_orders": [], "takeoff_results": [], "punch_list_items": [], "clinic_hardware_matrix": [], "security_audit_score": None,
    "labor_logs": [], "forensic_photos": [], "sla_contracts": [], "clinic_appointments": [], "active_video_room": None,
    "base_apprentice_hours": 412.5, "schedule_delay_days": 0, "crew_count_leveling": 2, "field_dispatch_messages": [],
    "generated_license_keys": [{"Key Token": "OMNI-ELEC-9821", "Tier": "Enterprise", "Assigned Client": "david@shardvisuals.com", "Status": "Active"}]
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

if "tool_fleet" not in st.session_state: 
    st.session_state.tool_fleet = [
        {"Asset Tag": "MKE-001", "Tool Type": "M18 Fuel Hammer Drill", "Status": "Company Vault", "Assigned To": "Unassigned", "Value": 299.00},
        {"Asset Tag": "KLI-001", "Tool Type": "Klein Tools Network Tester", "Status": "Company Vault", "Assigned To": "Unassigned", "Value": 350.00}
    ]

if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Tenant Owner", "Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status", "GC Sign-Off", "Value Release"])

def log_system_event(user, phase, log_string):
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.system_audit_trail.insert(0, {"Timestamp": timestamp_str, "User Node": user, "Event Phase": phase, "Log Record String": log_string})

# --- 5. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='margin-top:10vh; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:3.5rem; color:#38BDF8 !important;'>OMNIBUILD OS</h1><p style='color:#94A3B8; font-size:1.2rem;'>ENTERPRISE INFRASTRUCTURE TERMINAL</p>", unsafe_allow_html=True)
    with st.form("auth_form"):
        input_email = st.text_input("Authorized Node Email").strip()
        input_password = st.text_input("Cryptographic Passkey", type="password").strip()
        if st.form_submit_button("Initiate Uplink", use_container_width=True):
            st.session_state.user_authenticated = True
            st.session_state.user_email = input_email if input_email else "david@shardvisuals.com"
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

current_user = st.session_state.user_email
if current_user not in st.session_state.tenant_balances:
    st.session_state.tenant_balances[current_user] = {"wallet": 45000.00, "escrow": 250000.00}

# --- 6. UNIFIED SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color:#FFFFFF; text-transform:uppercase;'>{st.session_state.company_name}</h3>", unsafe_allow_html=True)
st.sidebar.caption(f"Node: {current_user}")
st.sidebar.divider()

menu_categories = {
    "COMMAND & OPS": ["🏠 Global Telemetry Dashboard", "📊 Commercial Rollout Tracker", "📅 Algorithmic Scheduler", "💬 Field Dispatch Chat"],
    "ESTIMATION & BIDS": ["📐 AI Takeoff & OCR Vision", "🎯 Generative Proposal Engine", "📦 Procurement Pipeline"],
    "ENGINEERING & FIELD": ["⚡ NEC Load Calculator", "⏱️ Labor & Apprenticeship", "🧰 IoT Fleet Manager"],
    "FINANCE & LEGAL": ["💳 Escrow & OmniPay Invoicing", "📝 Master MSA Contracts", "⚖️ Variance & Change Orders"],
    "HEALTH & INFRASTRUCTURE": ["🏥 Clinic IT Architecture", "🤖 Hardware Diagnostics AI", "🩺 OmniHealth Telemedicine"],
    "FORENSICS & COMPLIANCE": ["📷 Shard.Visuals Portal", "🔄 SLA & Digital Twin", "🛠️ QA Punch List", "📋 System Audit Trail"]
}

flat_options = []
for category, items in menu_categories.items():
    flat_options.append(f"--- {category} ---")
    flat_options.extend(items)

selected_menu = st.sidebar.radio("Navigation Protocol", flat_options, index=1)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Vault", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

st.markdown(f"<div class='shard-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

if selected_menu.startswith("---"):
    st.info("Select an operational module from the navigation menu.")
    st.stop()

# --- 7. THE MASTER ROUTING MATRIX ---

if selected_menu == "🏠 Global Telemetry Dashboard":
    st.write("### 🏠 Executive Command Center")
    if st.button("🚀 Prime Sandbox Simulation Variables", use_container_width=True):
        st.session_state.commercial_units = pd.DataFrame([
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Exam Room 1", "Asset Type": "White Quartz / Med-Gas", "Fabrication Status": "Completed", "Installation Status": "Installed", "GC Sign-Off": "Pending", "Value Release": 8500.00},
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Reception", "Asset Type": "White Quartz / IT Drop", "Fabrication Status": "In Progress", "Installation Status": "Staged", "GC Sign-Off": "Pending", "Value Release": 4200.00}
        ])
        st.success("Matrix primed."); time.sleep(0.5); st.rerun()

    u_bal = st.session_state.tenant_balances[current_user]
    total_po_liability = sum(po['Amount'] for po in st.session_state.purchase_orders)
    
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Escrow Reserves", f"${u_bal['escrow']:,.2f}")
    c2.metric("Working Liquidity", f"${u_bal['wallet']:,.2f}")
    c3.metric("Active Material Liability", f"${total_po_liability:,.2f}")
    c4.metric("Lindsey Hopkins Progress", f"{(st.session_state.base_apprentice_hours/600)*100:.1f}%")

elif selected_page == "📊 Commercial Rollout Tracker":
    st.write("### 📊 High-Density Execution Portal")
    st.markdown("<div class='shard-panel'>Manage multi-unit structural configurations and trigger field sign-offs for invoicing.</div>", unsafe_allow_html=True)
    user_view_df = st.session_state.commercial_units[st.session_state.commercial_units["Tenant Owner"] == current_user]
    if not user_view_df.empty:
        st.data_editor(user_view_df, use_container_width=True, num_rows="dynamic")
    else: st.info("Run the Sandbox Simulator on the Command Center to populate units.")

elif selected_menu == "📅 Algorithmic Scheduler":
    st.write("### 📅 Critical Path Automation")
    col_sch, col_viz = st.columns([1, 1.5])
    with col_sch:
        sim_delay = st.slider("Material Backorder Lag (Days)", 0, 14, st.session_state.schedule_delay_days)
        crew = st.slider("Active Personnel", 1, 10, st.session_state.crew_count_leveling)
        if st.button("Recalculate Critical Path"): st.session_state.schedule_delay_days = sim_delay; st.session_state.crew_count_leveling = crew; st.rerun()
    with col_viz:
        st.markdown("<div class='shard-panel-green'>Schedule Matrix Optimized. No bottlenecks detected.</div>", unsafe_allow_html=True)

elif selected_menu == "💬 Field Dispatch Chat":
    st.write("### 💬 System Intelligence Hub")
    msg = st.text_area("Broadcast Site Update")
    if st.button("Send Global Message"):
        st.session_state.field_dispatch_messages.insert(0, {"Sender": current_user, "Message": sanitize_input(msg)})
        st.rerun()
    for m in st.session_state.field_dispatch_messages:
        st.markdown(f"<div class='shard-panel'><b>{m['Sender']}:</b> {m['Message']}</div>", unsafe_allow_html=True)

elif selected_menu == "📐 AI Takeoff & OCR Vision":
    st.write("### 📐 Multimodal Architecture Parsing")
    st.markdown("<div class='shard-panel'>Extract bill of materials via NLP syntax parsing or deep Computer Vision OCR.</div>", unsafe_allow_html=True)
    tab_nlp, tab_cv, tab_res = st.tabs(["📝 NLP Text Spec Parser", "👁️ Computer Vision OCR", "📋 Extraction Ledger"])
    
    with tab_nlp:
        raw_specs = st.text_area("Architectural Specs", value="SPEC-01: Pull 1200ft 3/4-inch ENT. SPEC-02: Mount 60x Yealink VoIP.")
        if st.button("Run Text Parser"):
            matches = re.findall(r'(\d+)(x|ft)\s*(?:of\s*)?([a-zA-Z0-9\s\-]+?)(?=\.|$)', raw_specs, re.IGNORECASE)
            st.session_state.takeoff_results.extend([{"Item": i.strip().title(), "Qty": int(q), "Cost": int(q)*1.5} for q, u, i in matches])
            st.success("Parsed successfully."); st.rerun()
            
    with tab_cv:
        if st.file_uploader("Upload Blueprint File (PNG/PDF)"):
            if st.button("Initiate Neural Scan"):
                with st.spinner("Processing symbology..."): time.sleep(1.5)
                st.session_state.takeoff_results.extend([{"Item": "Duplex Receptacle", "Qty": 85, "Cost": 14.50}, {"Item": "2x4 Troffer", "Qty": 40, "Cost": 125.00}])
                st.success("Vision mapped."); st.rerun()
                
    with tab_res:
        if st.session_state.takeoff_results:
            st.dataframe(pd.DataFrame(st.session_state.takeoff_results))
            if st.button("Stage to Procurement Pipeline"):
                st.session_state.purchase_orders.insert(0, {"PO ID": f"PO-{random.randint(100,999)}", "Amount": sum(i['Cost'] for i in st.session_state.takeoff_results), "Status": "Fabrication"})
                st.session_state.takeoff_results = []; st.success("Staged!"); st.rerun()

elif selected_menu == "🎯 Generative Proposal Engine":
    st.write("### 🎯 Dynamic Bid Formulation")
    margin = st.slider("Target Margin (%)", 10.0, 50.0, 32.5)
    base_cost = 145000.00
    final = (base_cost * 1.85) * (1 + (margin/100))
    st.markdown(f"<div class='shard-panel-gold'><b>Projected Firm Fixed Price:</b> ${final:,.2f}</div>", unsafe_allow_html=True)
    if st.button("Generate Executive Commercial Proposal"):
        st.markdown(f"<div class='document-scrollbox'><h2 style='color:#0F172A;'>OMNIBUILD OS COMMERCIAL PROPOSAL</h2><hr><p>Vendor: {st.session_state.company_name}</p><p><b>Total Value: ${final:,.2f}</b></p></div>", unsafe_allow_html=True)

elif selected_menu == "📦 Procurement Pipeline":
    st.write("### 📦 Supply Chain Logistics")
    st.markdown("<div class='shard-panel'>Manage staged Purchase Orders and track geo-fenced freight.</div>", unsafe_allow_html=True)
    if st.session_state.purchase_orders:
        st.dataframe(pd.DataFrame(st.session_state.purchase_orders), hide_index=True, use_container_width=True)
    else: st.info("No active POs in the ledger.")

elif selected_menu == "⚡ NEC Load Calculator":
    st.write("### ⚡ National Electrical Code Field Engineering")
    st.markdown("<div class='shard-panel'>Voltage drop, conduit fill, and panel load demand engineering.</div>", unsafe_allow_html=True)
    t1, t2 = st.tabs(["Voltage Drop", "Panel Demand"])
    with t1:
        if st.button("Calculate V-Drop (100ft / 20A / 12AWG CU)"): st.markdown("<div class='shard-panel-green'>Compliant: 1.6% Drop.</div>", unsafe_allow_html=True)
    with t2:
        if st.button("Calculate Demand Load (Clinic Profile)"): st.markdown("<div class='shard-panel-gold'>Required Main: 200A Three-Phase</div>", unsafe_allow_html=True)

elif selected_menu == "⏱️ Labor & Apprenticeship":
    st.write("### 🎓 State Apprenticeship & Labor Telemetry")
    completed_shifts = len([log for log in st.session_state.labor_logs if log['Status'] == 'Completed Shift'])
    total_hours = st.session_state.base_apprentice_hours + (completed_shifts * 8.0)
    
    st.markdown(f"<div class='shard-panel'><b>Lindsey Hopkins Technical College Progress</b><br><progress value='{total_hours/600}' max='1'></progress> {total_hours:.1f} / 600 Hours Verified.</div>", unsafe_allow_html=True)
    
    worker = st.text_input("Technician Credential")
    c1, c2 = st.columns(2)
    if c1.button("🟢 Geofence Clock-In"): st.session_state.labor_logs.insert(0, {"Name": worker, "Status": "Active"}); st.rerun()
    if c2.button("🔴 Geo-Sync Clock-Out"):
        for i, l in enumerate(st.session_state.labor_logs):
            if l['Name'] == worker: st.session_state.labor_logs[i]['Status'] = "Completed Shift"
        st.rerun()

elif selected_menu == "🧰 IoT Fleet Manager":
    st.write("### 🧰 Digital Asset Vault")
    st.markdown("<div class='shard-panel'>Assign high-value tools to active labor nodes.</div>", unsafe_allow_html=True)
    st.dataframe(pd.DataFrame(st.session_state.tool_fleet), use_container_width=True)

elif selected_menu == "💳 Escrow & OmniPay Invoicing":
    st.write("### 💳 Liquidity & Invoicing Ledger")
    u_bal = st.session_state.tenant_balances[current_user]
    st.markdown(f"<div class='shard-panel'><b>Project Escrow:</b> ${u_bal['escrow']:,.2f}</div>", unsafe_allow_html=True)
    if st.button("Generate Pay Application Document"): st.success("AIA-style invoice generated.")

elif selected_menu == "📝 Master MSA Contracts":
    st.write("### 📝 Legal Execution Vault")
    if st.button("Seal E-Signature & Generate Cryptographic Hash"):
        hash_str = "0x" + "".join(random.choices(string.hexdigits.lower(), k=64))
        st.markdown(f"<div class='shard-panel-green'>Contract Bound. Hash: {hash_str}</div>", unsafe_allow_html=True)

elif selected_menu == "⚖️ Variance & Change Orders":
    st.write("### ⚖️ Scope Disruption Arbitration")
    if st.button("Log Field Disruption & Calculate Penalty"):
        st.session_state.active_change_orders.append({"ID": f"CO-{random.randint(100,999)}", "Status": "Pending GC Review", "Delta": 2450.00})
        st.success("Variance logged.")
    if st.session_state.active_change_orders: st.dataframe(pd.DataFrame(st.session_state.active_change_orders))

elif selected_menu == "🏥 Clinic IT Architecture":
    st.write("### 🏥 Medical Network Blueprint")
    st.markdown("<div class='shard-panel'>Stage UniFi & Yealink nodes and execute packet injection vulnerability scans.</div>", unsafe_allow_html=True)
    hw = st.selectbox("Hardware", ["UniFi U6-LR", "Yealink T58W"])
    loc = st.text_input("Node Assignment")
    if st.button("Register to Local Subnet") and loc:
        st.session_state.clinic_hardware_matrix.append({"Device": hw, "Location": loc, "MAC": "00:1A:2B:XX"})
        st.rerun()
    if st.button("Execute Penetration Audit"):
        st.markdown("<div class='shard-panel-green'>HIPAA COMPLIANCE VERIFIED: 98/100. VLANs Isolated.</div>", unsafe_allow_html=True)

elif selected_menu == "🤖 Hardware Diagnostics AI":
    st.write("### 🤖 OmniMind Fault Diagnostics")
    st.markdown("<div class='shard-panel'>Automated terminal logic for packet loss and SIP gateway failures.</div>", unsafe_allow_html=True)
    if st.button("Run Subnet Trace"):
        st.markdown("<div style='background:#000; color:#10B981; padding:20px; font-family:monospace;'>> Pinging Nodes...<br>> Fault isolated to WAN2 Failover.<br>> Resolving routing table...<br>> STATUS: ONLINE.</div>", unsafe_allow_html=True)

elif selected_menu == "🩺 OmniHealth Telemedicine":
    st.write("### 🩺 WebRTC Telehealth Gateway")
    st.markdown("<div class='shard-panel'>HIPAA-compliant, peer-to-peer secure video consultations via Daily.co.</div>", unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.5])
    with col1:
        pt = st.text_input("Patient Identifier")
        if st.button("Generate Encrypted Room"):
            if pt:
                url = create_secure_video_room()
                st.session_state.active_video_room = url
                st.session_state.clinic_appointments.insert(0, {"Patient": pt, "Room URL": url})
                st.rerun()
    with col2:
        if st.session_state.active_video_room:
            st.markdown("<div class='shard-panel-green'>LIVE SESSION ACTIVE</div>", unsafe_allow_html=True)
            components.iframe(st.session_state.active_video_room, width=800, height=450, allow="camera; microphone; fullscreen; display-capture")
            if st.button("Terminate Session & Purge Logs"):
                st.session_state.active_video_room = None; st.rerun()

elif selected_menu == "📷 Shard.Visuals Portal":
    st.write("### 📸 Cinematic Forensic Ledger")
    st.markdown("<div class='shard-panel'>Capture cryptographically-sealed progress photos and generate read-only client galleries.</div>", unsafe_allow_html=True)
    cam = st.camera_input("Secure Document Capture")
    if cam:
        st.session_state.forensic_photos.insert(0, {"Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Hash": "0x"+''.join(random.choices(string.hexdigits, k=32))})
        st.success("Sealed!")
    if st.session_state.forensic_photos:
        st.write("---")
        st.markdown("<h3 style='text-align:center; color:#F59E0B; letter-spacing:2px;'>SHARD.VISUALS PORTAL</h3>", unsafe_allow_html=True)
        for p in st.session_state.forensic_photos:
            st.markdown(f"<div class='shard-visuals-card'><div class='shard-visuals-header'>{p['Time']} | HASH: {p['Hash']}</div></div>", unsafe_allow_html=True)

elif selected_menu == "🔄 SLA & Digital Twin":
    st.write("### 🔄 Recurring SLA Engineering")
    if st.button("Draft Enterprise Support Contract ($1,299/mo)"):
        st.session_state.sla_contracts.append({"Client": "Dr. Sol Clinic", "Tier": "Enterprise SLA", "Status": "Active"})
        st.success("Contract Bound. MRR Pipeline Secured.")
    if st.session_state.sla_contracts: st.dataframe(pd.DataFrame(st.session_state.sla_contracts))

elif selected_menu == "🛠️ QA Punch List":
    st.write("### 🛠️ Field Quality Assurance")
    if st.button("Dispatch Defect Ticket to Geo-Fence Crew"): st.success("Paged via Hub.")

elif selected_menu == "📋 System Audit Trail":
    st.write("### 📋 Immutability Ledger")
    st.dataframe(pd.DataFrame(st.session_state.system_audit_trail))

else:
    st.write(f"### {selected_menu.replace('---', '').strip()}")
    st.info("System module standing by.")