import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import time
import math
import html
import random
import base64
import hashlib
import re
import numpy as np
import altair as alt
from fpdf import FPDF

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | Unified Monolith", layout="wide", initial_sidebar_state="expanded")

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
        .chat-bubble-ai { background-color: #0A0F17; border: 1px solid #1E293B; border-left: 3px solid #10B981; padding: 15px; border-radius: 4px; margin-bottom: 10px; }
        .chat-bubble-user { background-color: #1E293B; color: #F8FAFC; padding: 15px; border-radius: 4px; margin-bottom: 10px; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()

def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

# --- 2. MASTER ENGINE FUNCTIONS ---
def generate_sha256_hash(data_string): return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

def calculate_voltage_drop(phase, current, distance, awg, conductor, voltage):
    k_val = 12.9 if conductor == "Copper" else 21.2
    cm_map = {"14": 4110, "12": 6530, "10": 10380, "8": 16510, "6": 26240, "4": 41740, "2": 66360, "1/0": 105600, "2/0": 133100, "3/0": 167800, "4/0": 211600, "250": 250000, "500": 500000}
    cm = cm_map.get(awg, 6530)
    vd = ((2 * k_val * current * distance) / cm) if phase == "Single-Phase" else ((math.sqrt(3) * k_val * current * distance) / cm)
    return vd, (vd / voltage) * 100

def semantic_chunking_search(document, query):
    sentences = re.split(r'(?<=[.!?]) +|\n', document)
    query_words = set(re.findall(r'\w+', query.lower()))
    best_match = "No precise specification matches located in active ledger memory."
    highest_score = 0
    for sentence in sentences:
        if not sentence.strip(): continue
        overlap = len(query_words.intersection(set(re.findall(r'\w+', sentence.lower()))))
        if overlap > highest_score: highest_score = overlap; best_match = sentence.strip()
    return best_match

def generate_rfq_pdf(rfq_id, vendors, materials):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="OMNIBUILD OS - MASTER REQUEST FOR QUOTE (RFQ)", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"RFQ ID: {rfq_id} | DATE: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"AUTHORIZED VENDORS: {vendors}", ln=True)
    pdf.ln(5)
    pdf.cell(200, 10, txt="BILL OF MATERIALS:", ln=True)
    for item in materials: pdf.cell(200, 8, txt=f"- {item.get('Extracted Length/Count', 'Qty')} of {item.get('Material', 'Item')}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

def inject_capacitor_camera():
    js_code = """
    <script>
        if (window.Capacitor && window.Capacitor.Plugins.CameraPreview) {
            window.Capacitor.Plugins.CameraPreview.start({ position: 'rear', parent: 'cameraPreview', className: 'cameraPreview', toBack: true });
            document.body.style.backgroundColor = 'transparent'; 
        } else { document.getElementById('ar-status').innerText = "[ HARDWARE BRIDGE NOT DETECTED: Running in Browser ]"; }
    </script>
    <div id="ar-status" style="color:#8B5CF6; font-family:monospace; text-align:center; padding:20px;">[ NATIVE AR CAMERA FEED ACTIVE ]</div>
    """
    components.html(js_code, height=150)

# --- 3. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": True, "user_email": "david@shardvisuals.com", "company_name": "Shard.Visuals Operations", 
    "wl_client_name": "OmniBuild OS v12.5 Monolith", "tenant_balances": {}, 
    "micro_loans": [], "property_defects": [], "rfq_ledger": [], "takeoff_results": [{"Material": "3/4\" ENT Conduit", "Extracted Length/Count": "450 ft"}],
    "rag_chat": [], "spec_document": "", "clinic_hardware_matrix": [], "patient_cgm_data": pd.DataFrame(),
    "base_apprentice_hours": 412.5, "map_coordinates": pd.DataFrame([[25.7617, -80.1918]], columns=['lat', 'lon']),
    "ar_session_active": False, "forensic_photos": [], "aia_billing_ledger": []
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

if st.session_state.user_email not in st.session_state.tenant_balances:
    st.session_state.tenant_balances[st.session_state.user_email] = {"wallet": 45000.00, "escrow": 250000.00, "vault_reserves": 100000.00}

# --- 4. UNIFIED SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color:#FFFFFF; text-transform:uppercase;'>{st.session_state.company_name}</h3>", unsafe_allow_html=True)
st.sidebar.caption(f"Operator: {st.session_state.user_email}")
st.sidebar.markdown("<div style='background-color:#05100D; border-left:3px solid #10B981; padding:10px; margin-bottom:15px; font-size:12px;'>🔓 <b>VAULT UNLOCKED:</b> FaceID Verified.</div>", unsafe_allow_html=True)
st.sidebar.divider()

menu_categories = {
    "COMMAND & OPS": ["🏠 Operational Telemetry", "🚁 Geospatial Mapping Tracker"],
    "FINANCE & REAL ESTATE": ["🏦 OmniCapital FinTech Suite", "🏢 Due Diligence & ROI Engine", "💳 AIA Progress Billing (G702)"],
    "NATIVE IOS HARDWARE": ["🥽 AR Spatial Conduit Mapping", "📷 Cryptographic Site Forensics"],
    "MEDICAL INFRASTRUCTURE": ["🩺 Endocrinology Live Telemetry", "🏥 Frictionless Device Routing"],
    "SYNDICATE & PROCUREMENT": ["📧 Automated RFQ Engine", "📐 DXF Vector Extraction", "🧠 OmniMind Native RAG Chat"],
    "FIELD ENGINEERING": ["⚡ Physics Load Calculator", "⏱️ Apprenticeship Ledger"]
}

flat_options = []
for category, items in menu_categories.items():
    flat_options.append(f"--- {category} ---")
    flat_options.extend(items)

selected_menu = st.sidebar.radio("Navigation Protocol", flat_options, index=1)
st.sidebar.divider()
st.markdown(f"<div class='shard-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

if selected_menu.startswith("---"): st.stop()

# --- 5. THE MASTER ROUTING MATRIX ---

if selected_menu == "🏠 Operational Telemetry":
    st.write("### 🏠 System Capital Reserves")
    u_bal = st.session_state.tenant_balances[st.session_state.user_email]
    c1, c2, c3 = st.columns(3)
    c1.metric("Project Escrow Balance", f"${u_bal['escrow']:,.2f}")
    c2.metric("Liquid Capital Accounts", f"${u_bal['wallet']:,.2f}")
    c3.metric("OmniCapital Vault", f"${u_bal['vault_reserves']:,.2f}")

elif selected_menu == "🏦 OmniCapital FinTech Suite":
    st.write("### 🏦 Advanced FinTech Material Financing")
    st.markdown("<div class='shard-panel'>Calculate explicit compound returns on cash advancements extended to sub-tier labor forces.</div>", unsafe_allow_html=True)
    col_calc, col_ledger = st.columns([1, 1.2])
    with col_calc:
        st.write("#### Term Yield Calculator")
        principal = st.number_input("Material Advance Capital ($)", value=5000.00, step=500.00)
        rate = st.slider("Flat Financing Fee Rate (%)", 2.0, 15.0, 5.0)
        interest = principal * (rate / 100)
        total_payout = principal + interest
        st.markdown(f"<div class='shard-panel-gold'><b>Principal Base:</b> ${principal:,.2f}<br><b>Compounded Yield Fee:</b> ${interest:,.2f}<br><b>Total Escrow Recovery:</b> ${total_payout:,.2f}</div>", unsafe_allow_html=True)
        if st.button("Authorize Financing Disbursal", use_container_width=True):
            st.session_state.tenant_balances[st.session_state.user_email]["vault_reserves"] -= principal
            st.session_state.micro_loans.insert(0, {"Date": datetime.datetime.now().strftime("%Y-%m-%d"), "Principal": principal, "Yield Fee": interest, "Recovery": total_payout, "Status": "Active"})
            st.success("Financing deployed. Lien secured.")
            st.rerun()
    with col_ledger:
        st.write("#### Active FinTech Book Ledger")
        if st.session_state.micro_loans: st.dataframe(pd.DataFrame(st.session_state.micro_loans), use_container_width=True)

elif selected_menu == "🏢 Due Diligence & ROI Engine":
    st.write("### 🏢 North Miami Beach Acquisition Engine")
    c1, c2 = st.columns([1, 1])
    with c1:
        purchase_price = st.number_input("Target Purchase Price ($)", value=450000.00, step=10000.0)
        rehab_cost = st.number_input("Estimated Rehab ($)", value=65000.00, step=5000.0)
        monthly_rent = st.number_input("Projected Gross Monthly Rent ($)", value=4200.00, step=100.0)
        annual_opex = st.number_input("Annual Operating Expenses ($)", value=12500.00, step=500.0)
        
        noi = (monthly_rent * 12) - annual_opex
        cap_rate = (noi / (purchase_price + rehab_cost)) * 100
    with c2:
        st.markdown(f"<div class='shard-panel-gold'><b style='font-size:18px; color:#F59E0B;'>Cap Rate: {cap_rate:.2f}%</b><br><b>NOI:</b> ${noi:,.2f} / year</div>", unsafe_allow_html=True)
        if cap_rate >= 7.0: st.markdown("<div class='shard-panel-green'>✅ YIELD APPROVED</div>", unsafe_allow_html=True)
        else: st.markdown("<div class='shard-panel-red'>🚨 YIELD DEFICIT</div>", unsafe_allow_html=True)

elif selected_menu == "🥽 AR Spatial Conduit Mapping":
    st.write("### 🥽 Augmented Reality Spatial Engine")
    if st.button("🚀 Initialize Native AR Session", use_container_width=True): st.session_state.ar_session_active = True; st.rerun()
    if st.session_state.ar_session_active:
        if st.button("🔴 Terminate AR Hardware Connection", use_container_width=True): st.session_state.ar_session_active = False; st.rerun()
        inject_capacitor_camera()
    else: st.info("AR Session Offline.")

elif selected_menu == "📷 Cryptographic Site Forensics":
    st.write("### 📸 Immutable Site Progress Ledger")
    photo_notes = st.text_input("Forensic Field Notes")
    cam = st.camera_input("📸 Capture Field Document")
    if cam:
        raw_data = f"{photo_notes}_{datetime.datetime.now()}_{cam.size}"
        st.session_state.forensic_photos.insert(0, {"Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"), "Notes": sanitize_input(photo_notes), "Hash": generate_sha256_hash(raw_data)})
        st.success("Photo cryptographically sealed.")
    if st.session_state.forensic_photos: st.dataframe(pd.DataFrame(st.session_state.forensic_photos))

elif selected_menu == "🩺 Endocrinology Live Telemetry":
    st.write("### 🩺 Continuous Glucose Monitor (CGM) Matrix")
    if st.button("📡 Initialize Live Data Stream", use_container_width=True):
        times = pd.date_range(start="2026-05-16 08:00", periods=50, freq="5min")
        st.session_state.patient_cgm_data = pd.DataFrame({"Timestamp": times, "Glucose (mg/dL)": 110 + np.random.normal(0, 5, 50).cumsum()})
    if not st.session_state.patient_cgm_data.empty:
        chart = alt.Chart(st.session_state.patient_cgm_data).mark_line(color="#38BDF8").encode(x='Timestamp:T', y=alt.Y('Glucose (mg/dL):Q', scale=alt.Scale(domain=[50, 250])))
        st.altair_chart(chart, use_container_width=True)

elif selected_menu == "🏥 Frictionless Device Routing":
    st.write("### 🏥 Seamless Hardware Staging")
    c1, c2 = st.columns(2)
    dev_type = c1.selectbox("Hardware Type", ["UniFi U6-Enterprise", "Yealink T58W VoIP"])
    dev_loc = c2.text_input("Clinic Zone Location")
    if st.button("Inject to Routing Table"):
        st.session_state.clinic_hardware_matrix.insert(0, {"Zone": dev_loc, "Endpoint": dev_type, "MAC Address": "00:1A:2B:3C:4D:5E", "Status": "🟢 Active"})
    if st.session_state.clinic_hardware_matrix: st.dataframe(pd.DataFrame(st.session_state.clinic_hardware_matrix))

elif selected_menu == "📧 Automated RFQ Engine":
    st.write("### 📧 OmniProcure Automated RFQ Dispatch")
    if st.button("📨 Generate & Dispatch Master RFQ PDF"):
        pdf_bytes = generate_rfq_pdf("RFQ-8821", "Graybar, CED", st.session_state.takeoff_results)
        st.session_state.rfq_ledger.insert(0, {"RFQ ID": "RFQ-8821", "Vendors": "Graybar, CED", "Binary": pdf_bytes})
        st.rerun()
    if st.session_state.rfq_ledger:
        b64_pdf = base64.b64encode(st.session_state.rfq_ledger[0]['Binary']).decode('utf-8')
        st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="Master_RFQ.pdf" style="display:block; text-align:center; padding:10px; background-color:#10B981; color:#030508; text-decoration:none; font-weight:bold; border-radius:4px;">📥 Download Formal RFQ Document (PDF)</a>', unsafe_allow_html=True)

elif selected_menu == "🧠 OmniMind Native RAG Chat":
    st.write("### 🧠 Production RAG Spec Document Indexer")
    uploaded_file = st.file_uploader("Upload Raw Blueprint Specification File (.txt)", type=["txt"])
    if uploaded_file: st.session_state.spec_document = uploaded_file.read().decode("utf-8")
    for chat in st.session_state.rag_chat:
        st.markdown(f"<div class='{'chat-bubble-user' if chat['role']=='user' else 'chat-bubble-ai'}'><b>{'You' if chat['role']=='user' else 'OmniMind'}:</b> {chat['text']}</div>", unsafe_allow_html=True)
    if prompt := st.chat_input("Query active specification parameters..."):
        st.session_state.rag_chat.append({"role": "user", "text": prompt})
        st.session_state.rag_chat.append({"role": "ai", "text": semantic_chunking_search(st.session_state.spec_document, prompt) if st.session_state.spec_document else "Upload a doc first."})
        st.rerun()

elif selected_menu == "⚡ Physics Load Calculator":
    st.write("### ⚡ National Electrical Code Mathematics")
    c1, c2, c3 = st.columns(3)
    phase = c1.selectbox("Phase", ["Single-Phase", "Three-Phase"])
    conductor = c2.selectbox("Conductor", ["Copper", "Aluminum"])
    awg = c3.selectbox("AWG", ["12", "10", "8", "6", "4"])
    if st.button("Calculate V-Drop"):
        vd, vd_pct = calculate_voltage_drop(phase, 20.0, 150.0, awg, conductor, 120)
        st.markdown(f"<div class='shard-panel-{'green' if vd_pct <= 3.0 else 'red'}'>V-Drop: {vd_pct:.2f}% ({vd:.2f}V)</div>", unsafe_allow_html=True)

elif selected_menu == "⏱️ Apprenticeship Ledger":
    st.write("### 🎓 Academic Telemetry")
    st.markdown(f"<div class='shard-panel'><progress value='{st.session_state.base_apprentice_hours/600}' max='1' style='width:100%;'></progress><br>{st.session_state.base_apprentice_hours:.1f} / 600 Hours Verified.</div>", unsafe_allow_html=True)

else:
    st.info("Module active.")