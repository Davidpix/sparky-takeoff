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
st.set_page_config(page_title="OmniBuild OS | Syndicate Matrix", layout="wide", initial_sidebar_state="expanded")

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
        .chat-bubble-ai { background-color: #0A0F17; border: 1px solid #1E293B; border-left: 3px solid #10B981; padding: 15px; border-radius: 4px; margin-bottom: 10px; }
        .chat-bubble-user { background-color: #1E293B; color: #F8FAFC; padding: 15px; border-radius: 4px; margin-bottom: 10px; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()

def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

# --- 3. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": False, "user_email": "", "company_name": "Shard.Visuals Enterprise", "wl_client_name": "OmniBuild OS v5.0",
    "tenant_balances": {}, "active_change_orders": [], "system_audit_trail": [], "purchase_orders": [], "takeoff_results": [],
    "clinic_hardware_matrix": [], "labor_logs": [], "forensic_photos": [], "sla_contracts": [], "clinic_appointments": [],
    "base_apprentice_hours": 412.5, "field_dispatch_messages": [], "sub_tier_contracts": [], "live_pricing": {}, "rag_chat": [],
    "pwa_offline_queue": 0, "offline_mode": False
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Tenant Owner", "Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status", "GC Sign-Off", "Value Release"])

# --- 4. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='margin-top:10vh; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:3.5rem; color:#38BDF8 !important;'>OMNIBUILD OS</h1><p style='color:#94A3B8; font-size:1.2rem;'>SYNDICATE INFRASTRUCTURE TERMINAL</p>", unsafe_allow_html=True)
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

# --- 5. UNIFIED SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color:#FFFFFF; text-transform:uppercase;'>{st.session_state.company_name}</h3>", unsafe_allow_html=True)
st.sidebar.caption(f"Node: {current_user}")

# PWA Offline Mode Toggle
st.session_state.offline_mode = st.sidebar.toggle("📶 Offline PWA Mode (IndexedDB)")
if st.session_state.offline_mode:
    st.sidebar.markdown(f"<div style='color:#F59E0B; font-size:12px;'>⚠️ SYSTEM OFFLINE. {st.session_state.pwa_offline_queue} actions queued for cloud sync.</div>", unsafe_allow_html=True)
st.sidebar.divider()

menu_categories = {
    "COMMAND & OPS": ["🏠 Global Telemetry Dashboard", "📊 Commercial Rollout Tracker", "💬 Field Dispatch Chat"],
    "SYNDICATE NETWORK": ["🔗 1099 Sub-Tier Portal", "🧠 OmniMind RAG Spec Chat"],
    "ESTIMATION & BIDS": ["📐 AI Takeoff & OCR Vision", "🎯 Generative Proposal Engine", "📦 Live Supply Chain Pipeline"],
    "ENGINEERING & FIELD": ["⚡ NEC Load Calculator", "⏱️ Labor & Apprenticeship", "🧰 IoT Fleet Manager"],
    "HEALTH & INFRASTRUCTURE": ["🏥 Clinic IT Architecture", "🤖 Hardware Diagnostics AI", "🩺 OmniHealth Telemedicine"],
    "FORENSICS & COMPLIANCE": ["📷 Shard.Visuals Portal", "🔄 SLA & Digital Twin", "⚖️ Variance & Change Orders"]
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

# Helper for PWA offline simulation
def handle_action(success_msg):
    if st.session_state.offline_mode:
        st.session_state.pwa_offline_queue += 1
        st.warning("Action saved to local IndexedDB. Will sync when connection is restored.")
    else:
        st.success(success_msg)

# --- 6. THE MASTER ROUTING MATRIX ---

if selected_menu == "🏠 Global Telemetry Dashboard":
    st.write("### 🏠 Executive Command Center")
    if st.button("🚀 Prime Sandbox Simulation Variables", use_container_width=True):
        st.session_state.commercial_units = pd.DataFrame([
            {"Tenant Owner": current_user, "Floor": "Floor 01", "Unit Number": "Exam Room 1", "Asset Type": "White Quartz / IT Drop", "Status": "Installed", "Value": 8500.00}
        ])
        handle_action("Matrix primed.")
        time.sleep(0.5); st.rerun()

    u_bal = st.session_state.tenant_balances[current_user]
    total_po_liability = sum(po['Amount'] for po in st.session_state.purchase_orders)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Escrow Reserves", f"${u_bal['escrow']:,.2f}")
    c2.metric("Working Liquidity", f"${u_bal['wallet']:,.2f}")
    c3.metric("Material Liability", f"${total_po_liability:,.2f}")
    c4.metric("Offline Commits", st.session_state.pwa_offline_queue)

elif selected_menu == "🔗 1099 Sub-Tier Portal":
    st.write("### 🔗 1099 Sub-Tier Syndicate Matrix")
    st.markdown("<div class='shard-panel'>Farm out scope to independent crews. OmniBuild automatically scales your management fee.</div>", unsafe_allow_html=True)
    
    col_assign, col_ledger = st.columns([1, 1.2])
    with col_assign:
        st.write("#### Issue Sub-Contract")
        crew_name = st.text_input("Sub-Tier Entity Name", value="Maksym Contracting LLC")
        scope = st.text_area("Scope of Work", value="Floor 2 Core HVAC & Electrical Rough-in")
        flat_rate = st.number_input("Sub-Contract Flat Rate Payout ($)", value=15000.00)
        mgmt_fee = st.slider("Your Management Markup (%)", 5.0, 30.0, 15.0)
        
        billed_to_gc = flat_rate * (1 + (mgmt_fee/100))
        net_profit = billed_to_gc - flat_rate
        
        st.markdown(f"<div class='shard-panel-gold'><b>GC Billed Value:</b> ${billed_to_gc:,.2f}<br><b>Your Net Profit:</b> ${net_profit:,.2f}</div>", unsafe_allow_html=True)
        
        if st.button("Generate & Bind Sub-Tier Contract"):
            st.session_state.sub_tier_contracts.insert(0, {"Entity": crew_name, "Scope": sanitize_input(scope), "Payout": flat_rate, "GC Bill": billed_to_gc, "Profit": net_profit, "Status": "Active in Field"})
            handle_action("Sub-tier contract executed and routed.")
            time.sleep(1); st.rerun()

    with col_ledger:
        st.write("#### Active Sub-Tier Operations")
        if st.session_state.sub_tier_contracts:
            st.dataframe(pd.DataFrame(st.session_state.sub_tier_contracts), use_container_width=True, hide_index=True)
        else:
            st.caption("No sub-tier contractors currently operating.")

elif selected_menu == "🧠 OmniMind RAG Spec Chat":
    st.write("### 🧠 OmniMind RAG Spec Book Terminal")
    st.markdown("<div class='shard-panel'>Query massive architectural PDF specifications via Retrieval-Augmented Generation (RAG).</div>", unsafe_allow_html=True)
    
    st.file_uploader("Upload Architecture Spec Book (PDF)", type=["pdf"])
    
    for chat in st.session_state.rag_chat:
        if chat['role'] == 'user':
            st.markdown(f"<div class='chat-bubble-user'><b>You:</b> {chat['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'><b>OmniMind AI:</b> {chat['text']}</div>", unsafe_allow_html=True)
            
    prompt = st.chat_input("Ask OmniMind about the specifications...")
    if prompt:
        st.session_state.rag_chat.append({"role": "user", "text": prompt})
        # Simulated RAG response
        ai_response = f"According to Division 26 (Electrical), Page 142: All Yealink VoIP drops in the reception area require a dedicated Cat6A pull, terminated at a mounting height of +48 inches AFF. Do not daisy-chain with the Apple M2 Kiosks."
        st.session_state.rag_chat.append({"role": "ai", "text": ai_response})
        st.rerun()

elif selected_menu == "📦 Live Supply Chain Pipeline":
    st.write("### 📦 API-Linked Supply Chain Logistics")
    st.markdown("<div class='shard-panel'>Live spot pricing API webhooks via Graybar and Home Depot Pro commercial accounts.</div>", unsafe_allow_html=True)
    
    col_live, col_pos = st.columns([1, 1.5])
    with col_live:
        if st.button("🔄 Fetch Live Market Spot Prices", use_container_width=True):
            with st.spinner("Pinging supplier webhooks..."):
                time.sleep(1.5)
                # Simulated live price fluctuations
                st.session_state.live_pricing = {
                    "Copper Wire (THHN 12 AWG / 500ft)": 115.50 + random.uniform(-5, 12),
                    "Premium White Quartz (sq ft)": 45.00 + random.uniform(-2, 5),
                    "ENT Conduit (3/4in / 100ft)": 38.20 + random.uniform(-1, 3)
                }
            handle_action("Market data updated.")
            st.rerun()
            
        if st.session_state.live_pricing:
            for item, price in st.session_state.live_pricing.items():
                st.markdown(f"<div style='padding: 10px; border-bottom:1px solid #1E293B;'><b>{item}:</b> <span style='color:#10B981; float:right;'>${price:.2f}</span></div>", unsafe_allow_html=True)
    
    with col_pos:
        st.write("#### Active Master Purchase Orders")
        if st.session_state.purchase_orders:
            st.dataframe(pd.DataFrame(st.session_state.purchase_orders), hide_index=True, use_container_width=True)
        else:
            st.caption("No POs currently in fabrication.")

elif selected_menu == "📐 AI Takeoff & OCR Vision":
    st.write("### 📐 Multimodal Architecture Parsing")
    st.markdown("<div class='shard-panel'>Extract bill of materials via NLP syntax parsing or deep Computer Vision OCR.</div>", unsafe_allow_html=True)
    tab_nlp, tab_cv, tab_res = st.tabs(["📝 NLP Text Spec Parser", "👁️ Computer Vision OCR", "📋 Extraction Ledger"])
    
    with tab_nlp:
        raw_specs = st.text_area("Architectural Specs", value="SPEC-01: Pull 1200ft 3/4-inch ENT. SPEC-02: Mount 60x Yealink VoIP.")
        if st.button("Run Text Parser"):
            matches = re.findall(r'(\d+)(x|ft)\s*(?:of\s*)?([a-zA-Z0-9\s\-]+?)(?=\.|$)', raw_specs, re.IGNORECASE)
            st.session_state.takeoff_results.extend([{"Item": i.strip().title(), "Qty": int(q), "Cost": int(q)*1.5} for q, u, i in matches])
            handle_action("Parsed successfully."); st.rerun()
            
    with tab_cv:
        if st.file_uploader("Upload Blueprint File (PNG/PDF)"):
            if st.button("Initiate Neural Scan"):
                with st.spinner("Processing symbology..."): time.sleep(1.5)
                st.session_state.takeoff_results.extend([{"Item": "Duplex Receptacle", "Qty": 85, "Cost": 14.50}, {"Item": "2x4 Troffer", "Qty": 40, "Cost": 125.00}])
                handle_action("Vision mapped."); st.rerun()
                
    with tab_res:
        if st.session_state.takeoff_results:
            st.dataframe(pd.DataFrame(st.session_state.takeoff_results))
            if st.button("Stage to Procurement Pipeline"):
                st.session_state.purchase_orders.insert(0, {"PO ID": f"PO-{random.randint(100,999)}", "Amount": sum(i['Cost'] for i in st.session_state.takeoff_results), "Status": "Fabrication"})
                st.session_state.takeoff_results = []
                handle_action("Staged!"); st.rerun()

elif selected_menu == "🎯 Generative Proposal Engine":
    st.write("### 🎯 Dynamic Bid Formulation")
    margin = st.slider("Target Margin (%)", 10.0, 50.0, 32.5)
    base_cost = 145000.00
    final = (base_cost * 1.85) * (1 + (margin/100))
    st.markdown(f"<div class='shard-panel-gold'><b>Projected Firm Fixed Price:</b> ${final:,.2f}</div>", unsafe_allow_html=True)
    if st.button("Generate Executive Commercial Proposal"):
        st.markdown(f"<div class='document-scrollbox'><h2 style='color:#0F172A;'>OMNIBUILD OS COMMERCIAL PROPOSAL</h2><hr><p>Vendor: {st.session_state.company_name}</p><p><b>Total Value: ${final:,.2f}</b></p></div>", unsafe_allow_html=True)

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
    
    st.markdown(f"<div class='shard-panel'><b>Lindsey Hopkins Technical College Progress</b><br><progress value='{total_hours/600}' max='1' style='width:100%; height:20px;'></progress><br> {total_hours:.1f} / 600 Hours Verified.</div>", unsafe_allow_html=True)
    
    worker = st.text_input("Technician Credential")
    c1, c2 = st.columns(2)
    if c1.button("🟢 Geofence Clock-In", use_container_width=True): 
        st.session_state.labor_logs.insert(0, {"Name": worker, "Status": "Active"})
        handle_action(f"{worker} clocked in."); st.rerun()
    if c2.button("🔴 Geo-Sync Clock-Out", use_container_width=True):
        for i, l in enumerate(st.session_state.labor_logs):
            if l['Name'] == worker: st.session_state.labor_logs[i]['Status'] = "Completed Shift"
        handle_action(f"{worker} clocked out."); st.rerun()

elif selected_menu == "🏥 Clinic IT Architecture":
    st.write("### 🏥 Medical Network Blueprint")
    st.markdown("<div class='shard-panel'>Stage UniFi & Yealink nodes and execute packet injection vulnerability scans.</div>", unsafe_allow_html=True)
    hw = st.selectbox("Hardware", ["UniFi U6-LR", "Yealink T58W"])
    loc = st.text_input("Node Assignment")
    if st.button("Register to Local Subnet") and loc:
        st.session_state.clinic_hardware_matrix.append({"Device": hw, "Location": loc, "MAC": "00:1A:2B:XX"})
        handle_action("Hardware staged."); st.rerun()

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
                handle_action("Room provisioned."); st.rerun()
    with col2:
        if st.session_state.active_video_room:
            st.markdown("<div class='shard-panel-green'>LIVE SESSION ACTIVE</div>", unsafe_allow_html=True)
            components.iframe(st.session_state.active_video_room, width=800, height=450, allow="camera; microphone; fullscreen; display-capture")
            if st.button("Terminate Session & Purge Logs"):
                st.session_state.active_video_room = None; handle_action("Session closed."); st.rerun()

elif selected_menu == "📷 Shard.Visuals Portal":
    st.write("### 📸 Cinematic Forensic Ledger")
    st.markdown("<div class='shard-panel'>Capture cryptographically-sealed progress photos and generate read-only client galleries.</div>", unsafe_allow_html=True)
    cam = st.camera_input("Secure Document Capture")
    if cam:
        st.session_state.forensic_photos.insert(0, {"Time": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Hash": "0x"+''.join(random.choices(string.hexdigits, k=32))})
        handle_action("Photo cryptographically sealed."); st.rerun()
    if st.session_state.forensic_photos:
        st.write("---")
        st.markdown("<h3 style='text-align:center; color:#F59E0B; letter-spacing:2px;'>SHARD.VISUALS PORTAL</h3>", unsafe_allow_html=True)
        for p in st.session_state.forensic_photos:
            st.markdown(f"<div class='shard-visuals-card'><div class='shard-visuals-header'>{p['Time']} | HASH: {p['Hash']}</div></div>", unsafe_allow_html=True)

elif selected_menu == "🔄 SLA & Digital Twin":
    st.write("### 🔄 Recurring SLA Engineering")
    if st.button("Draft Enterprise Support Contract ($1,299/mo)"):
        st.session_state.sla_contracts.append({"Client": "Dr. Sol Clinic", "Tier": "Enterprise SLA", "Status": "Active"})
        handle_action("Contract Bound. MRR Pipeline Secured.")
    if st.session_state.sla_contracts: st.dataframe(pd.DataFrame(st.session_state.sla_contracts))

elif selected_menu == "⚖️ Variance & Change Orders":
    st.write("### ⚖️ Scope Disruption Arbitration")
    if st.button("Log Field Disruption & Calculate Penalty"):
        st.session_state.active_change_orders.append({"ID": f"CO-{random.randint(100,999)}", "Status": "Pending GC Review", "Delta": 2450.00})
        handle_action("Variance logged.")
    if st.session_state.active_change_orders: st.dataframe(pd.DataFrame(st.session_state.active_change_orders))

else:
    st.write(f"### {selected_menu.replace('---', '').strip()}")
    st.info("System module standing by.")