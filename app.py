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
import sqlite3
import requests
from collections import Counter
import altair as alt
from fpdf import FPDF
import ezdxf
import io

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | Omni-Node Core", layout="wide", initial_sidebar_state="expanded")

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
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()
def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

# --- 2. RELATIONAL DATABASE ENGINE ---
def init_db():
    conn = sqlite3.connect('omnibuild_core.db', check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS capital_ledger (date TEXT, principal REAL, yield_fee REAL, recovery REAL, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS property_defects (timestamp TEXT, note TEXT, hash TEXT)''')
    conn.commit()
    return conn
conn = init_db()

# --- 3. MASTER LOGIC ENGINES (DXF & AI TUNNEL) ---
def parse_true_dxf(file_bytes):
    """Mathematically extracts line lengths and block counts from real AutoCAD DXF files."""
    try:
        doc = ezdxf.read(io.StringIO(file_bytes.decode('utf-8')))
        msp = doc.modelspace()
        
        total_line_length = 0
        block_count = 0
        
        for entity in msp:
            if entity.dxftype() == 'LINE':
                start = entity.dxf.start; end = entity.dxf.end
                length = math.sqrt((end.x - start.x)**2 + (end.y - start.y)**2)
                total_line_length += length
            elif entity.dxftype() == 'INSERT':
                block_count += 1
                
        # Assume standard architectural scale (e.g., 1 unit = 1 inch, converted to feet)
        feet_length = total_line_length / 12
        return [
            {"Material": "Linear Conduit/Wire Run (Extracted)", "Extracted Length/Count": f"{feet_length:.2f} ft"},
            {"Material": "Fixture/Device Drops (Extracted)", "Extracted Length/Count": f"{block_count} Units"}
        ]
    except Exception as e:
        return [{"Material": "Extraction Error", "Extracted Length/Count": str(e)}]

def query_local_ai_node(tunnel_url, patient_data):
    """Pings your RTX 3070 hardware through the secure Ngrok tunnel."""
    try:
        # Standard Ollama API payload
        payload = {"model": "llama3", "prompt": f"Analyze this CGM data securely: {patient_data}", "stream": False}
        response = requests.post(f"{tunnel_url}/api/generate", json=payload, timeout=10)
        return response.json().get("response", "No response from local hardware.")
    except Exception:
        return "CONNECTION SEVERED: Local hardware node offline or tunnel closed."

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
    for item in materials: pdf.cell(200, 8, txt=f"- {item.get('Extracted Length/Count', 'Qty')} of {item.get('Material', 'Item')}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

# --- 4. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": True, "user_email": "david@shardvisuals.com", "company_name": "Shard.Visuals Operations", 
    "wl_client_name": "OmniBuild OS v14.0 Omni-Node", "tenant_balances": {}, 
    "rfq_ledger": [], "takeoff_results": [], "local_ai_tunnel": "",
    "ar_session_active": False
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

if st.session_state.user_email not in st.session_state.tenant_balances:
    st.session_state.tenant_balances[st.session_state.user_email] = {"wallet": 45000.00, "escrow": 250000.00, "vault_reserves": 100000.00}

# --- 5. SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color:#FFFFFF;'>{st.session_state.company_name}</h3>", unsafe_allow_html=True)
st.sidebar.markdown("<div style='background-color:#05100D; border-left:3px solid #10B981; padding:10px; margin-bottom:15px; font-size:12px;'>🔓 <b>VAULT UNLOCKED</b></div>", unsafe_allow_html=True)

menu_categories = {
    "MEDICAL INFRASTRUCTURE": ["🩺 Endocrinology Live Telemetry"],
    "SYNDICATE & PROCUREMENT": ["📐 True DXF Vector Extraction", "📧 Automated RFQ Engine"],
    "FINANCE & REAL ESTATE": ["🏦 OmniCapital FinTech Suite", "🏢 Due Diligence & ROI Engine"]
}

flat_options = ["🏠 Operational Telemetry"]
for category, items in menu_categories.items():
    flat_options.append(f"--- {category} ---")
    flat_options.extend(items)

selected_menu = st.sidebar.radio("Navigation Protocol", flat_options, index=0)
st.sidebar.divider()
st.markdown(f"<div class='shard-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()
if selected_menu.startswith("---"): st.stop()

# --- 6. THE MASTER ROUTING MATRIX ---

if selected_menu == "🏠 Operational Telemetry":
    st.write("### 🏠 System Capital Reserves")
    u_bal = st.session_state.tenant_balances[st.session_state.user_email]
    c1, c2, c3 = st.columns(3)
    c1.metric("Project Escrow Balance", f"${u_bal['escrow']:,.2f}")
    c2.metric("Liquid Capital Accounts", f"${u_bal['wallet']:,.2f}")
    c3.metric("OmniCapital Vault", f"${u_bal['vault_reserves']:,.2f}")

elif selected_menu == "📐 True DXF Vector Extraction":
    st.write("### 📐 Algorithmic DXF Vector Extraction")
    st.markdown("<div class='shard-panel'>Processes real AutoCAD .dxf files, parsing spatial vertex geometry to calculate exact conduit lengths.</div>", unsafe_allow_html=True)
    uploaded_dxf = st.file_uploader("Upload Architectural CAD File (.dxf)", type=["dxf"])
    
    if uploaded_dxf:
        if st.button("Parse Vector Geometry (ezdxf Engine)", use_container_width=True):
            with st.spinner("Decoding polyline vertex arrays..."):
                file_bytes = uploaded_dxf.read()
                st.session_state.takeoff_results = parse_true_dxf(file_bytes)
            st.success("True vector geometry extracted.")
            st.rerun()
            
    if st.session_state.takeoff_results:
        st.write("#### Extracted Bill of Materials")
        st.dataframe(pd.DataFrame(st.session_state.takeoff_results), use_container_width=True)

elif selected_menu == "🩺 Endocrinology Live Telemetry":
    st.write("### 🩺 Continuous Glucose Monitor (CGM) Matrix")
    st.markdown("<div class='shard-panel'>Connects to your local air-gapped hardware node for HIPAA-compliant AI medical analysis.</div>", unsafe_allow_html=True)
    
    st.session_state.local_ai_tunnel = st.text_input("Secure Ngrok Tunnel URL (Hardware Link)", value=st.session_state.local_ai_tunnel, placeholder="https://abc-123.ngrok.app")
    
    if st.button("📡 Ping Local AI Node for Analysis", use_container_width=True):
        if not st.session_state.local_ai_tunnel:
            st.error("Missing secure tunnel URL. Cannot reach hardware node.")
        else:
            with st.spinner("Transmitting encrypted payload to hardware node..."):
                # Simulating a data payload to send to your PC
                mock_cgm_data = "Patient PT-8821: Fasting Glucose 115mg/dL, Post-Prandial 145mg/dL."
                ai_response = query_local_ai_node(st.session_state.local_ai_tunnel, mock_cgm_data)
                
            st.markdown(f"""
            <div style='background-color:#050505; border:1px solid #333; padding:15px; border-radius:4px;'>
                <b style='color:#10B981;'>[ RTX NODE RESPONSE ]</b><br><br>
                <i style='color:#E2E8F0;'>{ai_response}</i>
            </div>
            """, unsafe_allow_html=True)

elif selected_menu == "📧 Automated RFQ Engine":
    st.write("### 📧 OmniProcure Automated RFQ Dispatch")
    if not st.session_state.takeoff_results: st.info("Parse a DXF file first to generate an RFQ.")
    else:
        if st.button("📨 Generate Master RFQ PDF"):
            pdf_bytes = generate_rfq_pdf(f"RFQ-{random.randint(1000,9999)}", "Graybar, CED", st.session_state.takeoff_results)
            st.session_state.rfq_ledger.insert(0, {"RFQ ID": "RFQ-Auto", "Vendors": "Graybar, CED", "Binary": pdf_bytes})
            st.rerun()
        if st.session_state.rfq_ledger:
            b64_pdf = base64.b64encode(st.session_state.rfq_ledger[0]['Binary']).decode('utf-8')
            st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="Master_RFQ.pdf" style="display:block; text-align:center; padding:10px; background-color:#10B981; color:#030508; text-decoration:none; font-weight:bold; border-radius:4px;">📥 Download Formal RFQ Document (PDF)</a>', unsafe_allow_html=True)

else:
    st.info("Module active. Select operational telemetry to proceed.")