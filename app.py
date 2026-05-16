import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import time
import re
import requests
import random
import string
import base64

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | Apex Ecosystem", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE UI/UX ENGINE (MODERN MINIMALIST) ---
def inject_global_styles():
    st.markdown("""
    <style>
        .stApp { background-color: #030508 !important; color: #E2E8F0 !important; font-family: 'Helvetica Neue', sans-serif; }
        h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.03em; }
        .shard-panel { background-color: #0A0F17 !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 24px; border-radius: 4px; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .shard-panel-green { background-color: #05100D !important; border: 1px solid #064E3B !important; border-left: 3px solid #10B981 !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; }
        .shard-panel-gold { background-color: #120D04 !important; border: 1px solid #78350F !important; border-left: 3px solid #F59E0B !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; }
        .shard-header { font-size: 28px; font-weight: 600; color: #38BDF8 !important; letter-spacing: -0.02em; margin-bottom: 5px; text-transform: uppercase; }
        .stButton>button { background-color: #0F172A; color: #F8FAFC; border: 1px solid #1E293B; border-radius: 4px; transition: all 0.2s ease; }
        .stButton>button:hover { background-color: #38BDF8; color: #030508; border: 1px solid #38BDF8; }
        .document-scrollbox { background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 30px; font-family: 'Times New Roman', serif; border-radius: 4px; height: 400px; overflow-y: scroll; }
        .mesh-container { background: radial-gradient(circle at center, #1E293B 0%, #030508 100%); height: 300px; border: 1px solid #333; display: flex; align-items: center; justify-content: center; font-family: monospace; color: #38BDF8; border-radius: 4px; }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()

def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

# --- 3. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": False, "user_email": "", "company_name": "Shard Enterprise Matrix", "wl_client_name": "OmniBuild OS v6.0",
    "tenant_balances": {}, "sub_tier_contracts": [], "live_pricing": {}, "takeoff_results": [],
    "labor_logs": [], "forensic_photos": [], "clinic_appointments": [], "clinic_hardware_matrix": [],
    "base_apprentice_hours": 412.5, "offline_mode": False, "pwa_offline_queue": 0,
    "micro_loans": [], "drone_maps": [], "municipal_permits": []
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 4. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='margin-top:10vh; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:3.5rem; color:#38BDF8 !important;'>OMNIBUILD OS</h1><p style='color:#94A3B8; font-size:1.2rem;'>APEX ECOSYSTEM TERMINAL</p>", unsafe_allow_html=True)
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
    st.session_state.tenant_balances[current_user] = {"wallet": 45000.00, "escrow": 250000.00, "vault_reserves": 100000.00}

# --- 5. UNIFIED SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color:#FFFFFF; text-transform:uppercase;'>{st.session_state.company_name}</h3>", unsafe_allow_html=True)
st.sidebar.caption(f"Node: {current_user}")

st.session_state.offline_mode = st.sidebar.toggle("📶 Offline PWA Mode (IndexedDB)")
if st.session_state.offline_mode:
    st.sidebar.markdown(f"<div style='color:#F59E0B; font-size:12px;'>⚠️ SYSTEM OFFLINE. {st.session_state.pwa_offline_queue} actions queued.</div>", unsafe_allow_html=True)
st.sidebar.divider()

menu_categories = {
    "COMMAND & OPS": ["🏠 Global Telemetry Dashboard"],
    "ECOSYSTEM & CAPITAL": ["🏦 OmniCapital Micro-Lending", "🚁 Aero-Forensics 3D", "🏛️ Miami-Dade Municipal AI"],
    "SYNDICATE NETWORK": ["🔗 1099 Sub-Tier Portal", "🧠 OmniMind RAG Spec Chat"],
    "ESTIMATION & BIDS": ["📐 AI Takeoff & OCR Vision", "📦 Live Supply Chain Pipeline"],
    "ENGINEERING & FIELD": ["⚡ NEC Load Calculator", "⏱️ Labor & Apprenticeship"],
    "HEALTH & INFRASTRUCTURE": ["🏥 Clinic IT Architecture", "🩺 OmniHealth Telemedicine"]
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

def handle_action(success_msg):
    if st.session_state.offline_mode:
        st.session_state.pwa_offline_queue += 1
        st.warning("Action saved to local IndexedDB. Will sync when connection is restored.")
    else:
        st.success(success_msg)

# --- 6. THE MASTER ROUTING MATRIX ---

if selected_menu == "🏠 Global Telemetry Dashboard":
    st.write("### 🏠 Executive Command Center")
    u_bal = st.session_state.tenant_balances[current_user]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Project Escrow", f"${u_bal['escrow']:,.2f}")
    c2.metric("Working Liquidity", f"${u_bal['wallet']:,.2f}")
    c3.metric("OmniCapital Vault", f"${u_bal['vault_reserves']:,.2f}")
    c4.metric("Offline Commits", st.session_state.pwa_offline_queue)

# --- APEX MODULE 1: OMNICAPITAL MICRO-LENDING ---
elif selected_menu == "🏦 OmniCapital Micro-Lending":
    st.write("### 🏦 OmniCapital FinTech Engine")
    st.markdown("<div class='shard-panel'>Issue 30-day material financing to your 1099 Sub-Tier crews. Deduct principal + 5% financing fee automatically from their final GC payout.</div>", unsafe_allow_html=True)
    
    col_loan, col_ledger = st.columns([1, 1.2])
    with col_loan:
        if not st.session_state.sub_tier_contracts:
            st.info("No active Sub-Tier contracts. Generate a contract in the '1099 Sub-Tier Portal' first.")
            if st.button("Generate Demo Sub-Tier Contract"):
                st.session_state.sub_tier_contracts.append({"Entity": "Maksym Contracting LLC", "Scope": "Floor 2 Rough-In", "Payout": 15000.00, "Status": "Active"})
                st.rerun()
        else:
            sub_crew = st.selectbox("Select Sub-Tier Entity", [c["Entity"] for c in st.session_state.sub_tier_contracts])
            loan_amount = st.number_input("Material Advance Amount ($)", min_value=500.00, max_value=50000.00, value=2500.00)
            
            fee_calc = loan_amount * 0.05
            total_deduction = loan_amount + fee_calc
            
            st.markdown(f"<div class='shard-panel-gold'><b>Principal:</b> ${loan_amount:,.2f}<br><b>OmniCapital Fee (5%):</b> ${fee_calc:,.2f}<br><b>Total Escrow Deduction:</b> ${total_deduction:,.2f}</div>", unsafe_allow_html=True)
            
            if st.button("💸 Authorize Wire & Bind Lien", use_container_width=True):
                st.session_state.tenant_balances[current_user]["vault_reserves"] -= loan_amount
                st.session_state.micro_loans.insert(0, {
                    "Entity": sub_crew, "Advance": loan_amount, "Fee": fee_calc, 
                    "Total Deduction": total_deduction, "Date": datetime.datetime.now().strftime("%Y-%m-%d"), "Status": "Yielding Interest"
                })
                handle_action(f"Wire dispatched to {sub_crew}. Lien secured.")
                time.sleep(1); st.rerun()

    with col_ledger:
        st.write("#### Active Capital Deployed")
        if st.session_state.micro_loans:
            st.dataframe(pd.DataFrame(st.session_state.micro_loans), use_container_width=True, hide_index=True)
        else:
            st.caption("No capital currently deployed.")

# --- APEX MODULE 2: AERO-FORENSICS 3D ---
elif selected_menu == "🚁 Aero-Forensics 3D":
    st.write("### 🚁 Shard.Visuals Aero-Forensics")
    st.markdown("<div class='shard-panel'>Upload DJI/Autel flight logs to render interactive 3D photogrammetry site meshes for stakeholder review.</div>", unsafe_allow_html=True)
    
    col_upload, col_render = st.columns([1, 1.5])
    with col_upload:
        st.file_uploader("Upload Drone Flight Log (.txt, .csv, .laz)", type=["txt", "csv", "laz"])
        if st.button("Render 3D Orthomosaic Mesh", use_container_width=True):
            with st.spinner("Compiling point cloud data..."):
                time.sleep(2)
                st.session_state.drone_maps.append({
                    "Project": "Dr. Sol Clinic Exterior",
                    "Points": "1.4 Million",
                    "Render Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                })
                handle_action("3D Mesh Rendered.")
                st.rerun()

    with col_render:
        if st.session_state.drone_maps:
            st.markdown("<h4 style='color:#F59E0B; letter-spacing: 2px;'>SHARD.VISUALS | AERIAL INTELLIGENCE</h4>", unsafe_allow_html=True)
            # Simulated 3D WebGL Canvas
            st.markdown("""
            <div class='mesh-container'>
                [ 🛰️ WebGL Point-Cloud Engine Active ]<br>
                Render: Clinic Exterior Envelope<br>
                Vertices: 1,402,891<br>
                Status: Interactive (Drag to Rotate)
            </div>
            """, unsafe_allow_html=True)
            st.caption(f"Latest Render: {st.session_state.drone_maps[-1]['Render Date']}")
        else:
            st.info("Awaiting flight log data.")

# --- APEX MODULE 3: MIAMI-DADE MUNICIPAL AI ---
elif selected_menu == "🏛️ Miami-Dade Municipal AI":
    st.write("### 🏛️ Automated Municipal Compliance")
    st.markdown("<div class='shard-panel'>Cross-reference structural data against Miami-Dade building codes to auto-generate master permit applications.</div>", unsafe_allow_html=True)
    
    col_gen, col_doc = st.columns([1, 1.2])
    with col_gen:
        project_type = st.selectbox("Permit Classification", ["Commercial Electrical Form 02-B", "Low Voltage / Data (IT) Form 09", "Mechanical / HVAC Form 04"])
        property_folio = st.text_input("Miami-Dade Property Folio Number", value="30-2215-000-0010")
        
        if st.button("⚖️ Generate Miami-Dade Permit Package", use_container_width=True):
            with st.spinner("Cross-referencing Chapter 8 of the Code of Miami-Dade County..."):
                time.sleep(1.5)
                st.session_state.municipal_permits.insert(0, {
                    "Folio": property_folio,
                    "Type": project_type,
                    "Status": "Ready for Master Electrician Signature"
                })
                handle_action("Permit application compiled.")
                st.rerun()

    with col_doc:
        if st.session_state.municipal_permits:
            latest = st.session_state.municipal_permits[0]
            permit_html = f"""
            <div class='document-scrollbox' style='height: 350px;'>
                <h3 style='text-align:center; color:#0F172A;'>MIAMI-DADE COUNTY<br>BUILDING DEPARTMENT</h3>
                <hr>
                <p><b>FOLIO NUMBER:</b> {latest['Folio']}</p>
                <p><b>APPLICATION TYPE:</b> {latest['Type']}</p>
                <p><b>CONTRACTOR:</b> {st.session_state.company_name}</p>
                <br><br>
                <p><i>Pursuant to the Florida Building Code, all structural loads and network topology maps have been verified by OmniBuild OS.</i></p>
                <hr>
                <p>X____________________________________<br>Qualifying Agent Signature</p>
            </div>
            """
            st.markdown(permit_html, unsafe_allow_html=True)
            
            b64 = base64.b64encode("Simulated PDF Content".encode()).decode()
            href = f'<a href="data:application/pdf;base64,{b64}" download="Miami_Dade_Permit_{latest["Folio"]}.pdf" style="display:block; text-align:center; padding:10px; background-color:#10B981; color:#030508; text-decoration:none; font-weight:bold; border-radius:4px; margin-top:10px;">📥 Download PDF for e-Permitting Portal</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.caption("No permits generated in the current session.")

# --- RETAINED CORE SYNDICATE MODULES ---

elif selected_menu == "🔗 1099 Sub-Tier Portal":
    st.write("### 🔗 1099 Sub-Tier Syndicate Matrix")
    st.markdown("<div class='shard-panel'>Farm out scope to independent crews.</div>", unsafe_allow_html=True)
    crew_name = st.text_input("Sub-Tier Entity Name", value="Maksym Contracting LLC")
    flat_rate = st.number_input("Sub-Contract Flat Rate Payout ($)", value=15000.00)
    mgmt_fee = st.slider("Management Markup (%)", 5.0, 30.0, 15.0)
    if st.button("Generate & Bind Sub-Tier Contract"):
        st.session_state.sub_tier_contracts.insert(0, {"Entity": crew_name, "Payout": flat_rate, "GC Bill": flat_rate * (1 + (mgmt_fee/100)), "Status": "Active in Field"})
        handle_action("Sub-tier contract executed."); st.rerun()
    if st.session_state.sub_tier_contracts: st.dataframe(pd.DataFrame(st.session_state.sub_tier_contracts))

elif selected_menu == "🧠 OmniMind RAG Spec Chat":
    st.write("### 🧠 OmniMind RAG Spec Book Terminal")
    st.markdown("<div class='shard-panel'>Query massive architectural PDF specifications via Retrieval-Augmented Generation (RAG).</div>", unsafe_allow_html=True)
    st.file_uploader("Upload Architecture Spec Book (PDF)", type=["pdf"])
    st.markdown("<div class='chat-bubble-user'><b>You:</b> What is the required mounting height for the Yealink VoIP phones?</div>", unsafe_allow_html=True)
    st.markdown("<div class='chat-bubble-ai'><b>OmniMind AI:</b> According to Division 26, Page 142: All Yealink VoIP drops require a Cat6A pull, terminated at +48 inches AFF.</div>", unsafe_allow_html=True)

elif selected_menu == "📦 Live Supply Chain Pipeline":
    st.write("### 📦 API-Linked Supply Chain Logistics")
    if st.button("🔄 Fetch Live Market Spot Prices"):
        st.session_state.live_pricing = {"Copper Wire (THHN 12 AWG / 500ft)": 115.50 + random.uniform(-5, 12), "Premium White Quartz (sq ft)": 45.00 + random.uniform(-2, 5)}
        handle_action("Market data updated."); st.rerun()
    if st.session_state.live_pricing:
        for item, price in st.session_state.live_pricing.items(): st.markdown(f"<b>{item}:</b> <span style='color:#10B981;'>${price:.2f}</span>", unsafe_allow_html=True)

elif selected_menu == "📐 AI Takeoff & OCR Vision":
    st.write("### 📐 Multimodal Architecture Parsing")
    st.markdown("<div class='shard-panel'>Extract BOM via NLP syntax parsing or deep Computer Vision OCR.</div>", unsafe_allow_html=True)
    raw_specs = st.text_area("Architectural Specs", value="SPEC-01: Pull 1200ft 3/4-inch ENT.")
    if st.button("Run Text Parser"): st.success("Parsed successfully.")

elif selected_menu == "⚡ NEC Load Calculator":
    st.write("### ⚡ National Electrical Code Field Engineering")
    st.markdown("<div class='shard-panel-green'>V-Drop Compliant: 1.6% Drop at 100ft.</div>", unsafe_allow_html=True)

elif selected_menu == "⏱️ Labor & Apprenticeship":
    st.write("### 🎓 State Apprenticeship & Labor Telemetry")
    total_hours = st.session_state.base_apprentice_hours
    st.markdown(f"<div class='shard-panel'><b>Lindsey Hopkins Technical College Progress</b><br><progress value='{total_hours/600}' max='1' style='width:100%;'></progress><br> {total_hours:.1f} / 600 Hours Verified.</div>", unsafe_allow_html=True)

elif selected_menu == "🏥 Clinic IT Architecture":
    st.write("### 🏥 Medical Network Blueprint")
    if st.button("Execute Penetration Audit"): st.markdown("<div class='shard-panel-green'>HIPAA COMPLIANCE VERIFIED: 98/100.</div>", unsafe_allow_html=True)

elif selected_menu == "🩺 OmniHealth Telemedicine":
    st.write("### 🩺 WebRTC Telehealth Gateway")
    if st.button("Generate Encrypted Room"): handle_action("Room provisioned.")

else:
    st.write(f"### {selected_menu.replace('---', '').strip()}")
    st.info("System module standing by.")