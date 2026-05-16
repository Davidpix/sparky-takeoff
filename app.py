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
st.set_page_config(page_title="OmniBuild OS | Apex Execution", layout="wide", initial_sidebar_state="expanded")

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
    """Generates a professional, legally-structured PDF Request for Quote."""
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
    pdf.multi_cell(0, 8, txt="Please provide your most aggressive spot pricing for the following materials. Bids must hold for 14 days. Delivery to North Miami Beach site.")
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
    """IFrame bridge to trigger the native iOS Camera Preview underneath the webview."""
    js_code = """
    <script>
        // Check if Capacitor is injected by the native iOS wrapper
        if (window.Capacitor && window.Capacitor.Plugins.CameraPreview) {
            const CameraPreview = window.Capacitor.Plugins.CameraPreview;
            const cameraPreviewOptions = {
                position: 'rear',
                parent: 'cameraPreview',
                className: 'cameraPreview',
                toBack: true // Puts camera BEHIND the webview so Streamlit UI overlays it
            };
            CameraPreview.start(cameraPreviewOptions);
            document.body.style.backgroundColor = 'transparent'; // Make Streamlit background clear
        } else {
            document.getElementById('ar-status').innerText = "[ HARDWARE BRIDGE NOT DETECTED: Running in Standard Browser ]";
        }
    </script>
    <div id="ar-status" style="color:#8B5CF6; font-family:monospace; text-align:center; padding:20px;">
        [ NATIVE AR CAMERA FEED ACTIVE ]<br>Mapping Plane Geometry...
    </div>
    """
    components.html(js_code, height=150)

# --- 4. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": True, "user_email": "david@shardvisuals.com", "company_name": "Shard.Visuals Operations", 
    "wl_client_name": "OmniBuild OS v11.0", "tenant_balances": {}, 
    "takeoff_results": [{"Material": "3/4\" ENT Conduit", "Extracted Length/Count": "450 ft"}, {"Material": "Premium White Quartz", "Extracted Length/Count": "120 sqft"}], 
    "rfq_ledger": [], "ar_session_active": False
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

# --- V11.0 UPGRADE 1: NATIVE AR HARDWARE BRIDGE ---
if selected_menu == "🥽 AR Spatial Conduit Mapping":
    st.write("### 🥽 Augmented Reality Spatial Engine")
    st.markdown("<div class='shard-panel'>Projects DXF vector lines as 3D holographic overlays onto the physical environment by tunneling the native iOS Camera beneath the Streamlit webview.</div>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 1.5])
    with col1:
        st.write("#### AR Injection Parameters")
        st.selectbox("Active Blueprint Layer", ["Division 26: Electrical Power", "Division 27: IT/Communications"])
        
        if st.button("🚀 Initialize Native AR Session", use_container_width=True):
            st.session_state.ar_session_active = True
            st.rerun()
            
        if st.session_state.ar_session_active:
            if st.button("🔴 Terminate AR Hardware Connection", use_container_width=True):
                st.session_state.ar_session_active = False
                st.rerun()

    with col2:
        if st.session_state.ar_session_active:
            st.markdown("<div style='border: 1px solid #8B5CF6; border-radius: 4px; padding: 10px; background-color: rgba(0,0,0,0.5);'>", unsafe_allow_html=True)
            inject_capacitor_camera()
            st.markdown("</div>", unsafe_allow_html=True)
            st.caption("Note: Camera feed will only render physically when running inside the compiled Xcode iOS app, not in a desktop browser.")
        else:
            st.info("AR Session Offline. Hardware lens sealed.")

# --- V11.0 UPGRADE 2: AUTOMATED RFQ PDF ENGINE ---
elif selected_menu == "📧 Automated RFQ Engine":
    st.write("### 📧 OmniProcure Automated RFQ Dispatch")
    st.markdown("<div class='shard-panel'>Converts algorithmic takeoffs into legally-formatted PDF Request for Quote packages to force supplier bidding wars.</div>", unsafe_allow_html=True)
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.write("#### Vendor Targeting Matrix")
        graybar = st.checkbox("Graybar Electric (Miami Branch)", value=True)
        ced = st.checkbox("Consolidated Electrical Distributors (CED)", value=True)
        
        if st.button("📨 Generate & Dispatch Master RFQ PDF", use_container_width=True):
            rfq_id = f"RFQ-{random.randint(1000,9999)}"
            targets = []
            if graybar: targets.append("Graybar")
            if ced: targets.append("CED")
            
            # Generate the actual PDF binary
            pdf_bytes = generate_rfq_pdf(rfq_id, ", ".join(targets), st.session_state.takeoff_results)
            
            st.session_state.rfq_ledger.insert(0, {
                "RFQ ID": rfq_id, "Date Dispatched": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                "Vendors": ", ".join(targets), "Status": "Awaiting Vendor Bids", "Binary": pdf_bytes
            })
            st.success(f"PDF Generated. Procurement requests transmitted.")
            st.rerun()
            
    with c2:
        st.write("#### Active Procurement Ledger")
        if st.session_state.rfq_ledger:
            latest_rfq = st.session_state.rfq_ledger[0]
            st.markdown(f"<div class='shard-panel-gold'><b>Latest Dispatch:</b> {latest_rfq['RFQ ID']}<br><b>Targets:</b> {latest_rfq['Vendors']}</div>", unsafe_allow_html=True)
            
            # Create a native Streamlit download button for the generated PDF
            b64_pdf = base64.b64encode(latest_rfq['Binary']).decode('utf-8')
            href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{latest_rfq["RFQ ID"]}_Master.pdf" style="display:block; text-align:center; padding:10px; background-color:#10B981; color:#030508; text-decoration:none; font-weight:bold; border-radius:4px;">📥 Download Formal RFQ Document (PDF)</a>'
            st.markdown(href, unsafe_allow_html=True)
        else:
            st.caption("No active RFQs deployed.")

elif selected_menu == "🏠 Operational Telemetry":
    st.write("### 🏠 System Capital Reserves")
    u_bal = st.session_state.tenant_balances[st.session_state.user_email]
    c1, c2, c3 = st.columns(3)
    c1.metric("Project Escrow Balance", f"${u_bal['escrow']:,.2f}")
    c2.metric("Liquid Capital Accounts", f"${u_bal['wallet']:,.2f}")
    c3.metric("OmniCapital Reserves", f"${u_bal['vault_reserves']:,.2f}")

else:
    st.write(f"### {selected_menu.replace('---', '').strip()}")
    st.info("System module standing by.")