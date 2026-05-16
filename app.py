import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import datetime
import time
import math
import html
import random
import base64
from fpdf import FPDF

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | Acquisition Engine", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE UI/UX ENGINE ---
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

# --- 3. HARDWARE & PROCUREMENT ENGINES ---
def generate_rfq_pdf(rfq_id, vendors, materials):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="OMNIBUILD OS - MASTER REQUEST FOR QUOTE (RFQ)", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt=f"RFQ ID: {rfq_id} | DATE: {datetime.datetime.now().strftime('%Y-%m-%d')}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt=f"AUTHORIZED VENDORS: {vendors}", ln=True)
    pdf.set_font("Arial", size=11)
    pdf.multi_cell(0, 8, txt="Please provide your most aggressive spot pricing for the following materials. Bids must hold for 14 days.")
    pdf.ln(5)
    pdf.set_font("Arial", 'B', 12)
    pdf.cell(200, 10, txt="BILL OF MATERIALS:", ln=True)
    pdf.set_font("Arial", size=11)
    for item in materials:
        pdf.cell(200, 8, txt=f"- {item['Extracted Length/Count']} of {item['Material']}", ln=True)
    pdf.ln(15)
    pdf.cell(200, 10, txt="SUBMIT BIDS TO: david@shardvisuals.com", ln=True)
    return pdf.output(dest="S").encode("latin-1")

def inject_capacitor_camera():
    js_code = """
    <script>
        if (window.Capacitor && window.Capacitor.Plugins.CameraPreview) {
            const CameraPreview = window.Capacitor.Plugins.CameraPreview;
            CameraPreview.start({ position: 'rear', parent: 'cameraPreview', className: 'cameraPreview', toBack: true });
            document.body.style.backgroundColor = 'transparent'; 
        } else {
            document.getElementById('ar-status').innerText = "[ HARDWARE BRIDGE NOT DETECTED: Running in Standard Browser ]";
        }
    </script>
    <div id="ar-status" style="color:#8B5CF6; font-family:monospace; text-align:center; padding:20px;">[ NATIVE AR CAMERA FEED ACTIVE ]</div>
    """
    components.html(js_code, height=150)

# --- 4. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": True, "user_email": "david@shardvisuals.com", "company_name": "Shard.Visuals Operations", 
    "wl_client_name": "OmniBuild OS v12.0", "tenant_balances": {}, 
    "takeoff_results": [{"Material": "3/4\" ENT Conduit", "Extracted Length/Count": "450 ft"}], 
    "rfq_ledger": [], "ar_session_active": False, "property_defects": []
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

if st.session_state.user_email not in st.session_state.tenant_balances:
    st.session_state.tenant_balances[st.session_state.user_email] = {"wallet": 45000.00, "escrow": 250000.00, "vault_reserves": 100000.00}

# --- 5. UNIFIED SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color:#FFFFFF; text-transform:uppercase;'>{st.session_state.company_name}</h3>", unsafe_allow_html=True)
st.sidebar.caption(f"Operator: {st.session_state.user_email}")
st.sidebar.divider()

menu_categories = {
    "ESTATE & ACQUISITIONS": ["🏢 Due Diligence & ROI Engine"],
    "NATIVE IOS HARDWARE": ["🥽 AR Spatial Conduit Mapping"],
    "SYNDICATE REPOSITORY": ["📧 Automated RFQ Engine"],
    "COMMAND & MONITORING": ["🏠 Operational Telemetry"]
}

flat_options = []
for category, items in menu_categories.items():
    flat_options.append(f"--- {category} ---")
    flat_options.extend(items)

selected_menu = st.sidebar.radio("Navigation Protocol", flat_options, index=1)
st.sidebar.divider()
st.markdown(f"<div class='shard-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

if selected_menu.startswith("---"):
    st.info("Select an active processing module from the control list.")
    st.stop()

# --- 6. THE MASTER ROUTING MATRIX ---

# --- V12.0 UPGRADE 1: REAL ESTATE ACQUISITION MATRIX ---
if selected_menu == "🏢 Due Diligence & ROI Engine":
    st.write("### 🏢 North Miami Beach Acquisition Engine")
    st.markdown("<div class='shard-panel'>Compute exact commercial yields and log structural field defects using native camera forensics.</div>", unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["💰 ROI & Cap Rate Calculator", "📸 Structural Defect Ledger"])
    
    with t1:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write("#### Capital Allocation")
            purchase_price = st.number_input("Target Purchase Price ($)", value=450000.00, step=10000.0)
            rehab_cost = st.number_input("Estimated MEP/Structural Rehab ($)", value=65000.00, step=5000.0)
            down_payment_pct = st.slider("Down Payment Capital (%)", 10, 100, 20)
            
            st.write("#### Income Generation")
            monthly_rent = st.number_input("Projected Gross Monthly Rent ($)", value=4200.00, step=100.0)
            annual_opex = st.number_input("Annual Operating Expenses (Taxes, Ins, HOA) ($)", value=12500.00, step=500.0)
            
            # Mathematics
            total_investment = purchase_price + rehab_cost
            cash_invested = (purchase_price * (down_payment_pct / 100)) + rehab_cost
            annual_gross_income = monthly_rent * 12
            noi = annual_gross_income - annual_opex
            cap_rate = (noi / total_investment) * 100
            cash_on_cash = (noi / cash_invested) * 100 if cash_invested > 0 else 0
            
        with c2:
            st.write("#### Yield Projections")
            st.markdown(f"""
            <div class='shard-panel-gold'>
                <b style='font-size:18px; color:#F59E0B;'>Capitalization Rate (Cap Rate): {cap_rate:.2f}%</b><br><br>
                <b>Net Operating Income (NOI):</b> ${noi:,.2f} / year<br>
                <b>Total Cash Required to Close:</b> ${cash_invested:,.2f}<br>
                <b style='color:#10B981;'>Cash-on-Cash Return: {cash_on_cash:.2f}%</b>
            </div>
            """, unsafe_allow_html=True)
            if cap_rate >= 7.0:
                st.markdown("<div class='shard-panel-green'>✅ YIELD APPROVED: Asset meets target criteria.</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='shard-panel-red'>🚨 YIELD DEFICIT: Negotiate lower purchase price to hit 7% threshold.</div>", unsafe_allow_html=True)

    with t2:
        st.write("#### Visual Forensics")
        defect_note = st.text_input("Defect Description", placeholder="e.g., Sub-panel exhibits double-tapped neutral bus...")
        cam = st.camera_input("📸 Capture Defect")
        if cam and defect_note:
            st.session_state.property_defects.append({
                "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Defect": sanitize_input(defect_note)
            })
            st.success("Defect logged to ledger.")
            
        if st.session_state.property_defects:
            st.dataframe(pd.DataFrame(st.session_state.property_defects), use_container_width=True)

# --- RETAINED MODULES ---
elif selected_menu == "🥽 AR Spatial Conduit Mapping":
    st.write("### 🥽 Augmented Reality Spatial Engine")
    st.markdown("<div class='shard-panel'>Projects 3D holographic overlays onto the physical environment.</div>", unsafe_allow_html=True)
    if st.button("🚀 Initialize Native AR Session", use_container_width=True): st.session_state.ar_session_active = True; st.rerun()
    if st.session_state.ar_session_active:
        if st.button("🔴 Terminate AR Hardware Connection", use_container_width=True): st.session_state.ar_session_active = False; st.rerun()
        inject_capacitor_camera()
    else: st.info("AR Session Offline.")

elif selected_menu == "📧 Automated RFQ Engine":
    st.write("### 📧 OmniProcure Automated RFQ Dispatch")
    if st.button("📨 Generate & Dispatch Master RFQ PDF"):
        pdf_bytes = generate_rfq_pdf("RFQ-8821", "Graybar, CED", st.session_state.takeoff_results)
        st.session_state.rfq_ledger.insert(0, {"RFQ ID": "RFQ-8821", "Vendors": "Graybar, CED", "Binary": pdf_bytes})
        st.success("PDF Generated.")
        st.rerun()
    if st.session_state.rfq_ledger:
        b64_pdf = base64.b64encode(st.session_state.rfq_ledger[0]['Binary']).decode('utf-8')
        st.markdown(f'<a href="data:application/pdf;base64,{b64_pdf}" download="Master_RFQ.pdf" style="display:block; text-align:center; padding:10px; background-color:#10B981; color:#030508; text-decoration:none; font-weight:bold; border-radius:4px;">📥 Download Formal RFQ Document (PDF)</a>', unsafe_allow_html=True)

elif selected_menu == "🏠 Operational Telemetry":
    st.write("### 🏠 System Capital Reserves")
    u_bal = st.session_state.tenant_balances[st.session_state.user_email]
    c1, c2, c3 = st.columns(3)
    c1.metric("Project Escrow Balance", f"${u_bal['escrow']:,.2f}")
    c2.metric("OmniCapital Vault", f"${u_bal['vault_reserves']:,.2f}")
    c3.metric("Pending Acquisitions", len(st.session_state.property_defects))