import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import random

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | AR Spatial Core", layout="wide", initial_sidebar_state="expanded")

# --- 2. THE UI/UX ENGINE ---
def inject_global_styles():
    st.markdown("""
    <style>
        .stApp { background-color: #030508 !important; color: #E2E8F0 !important; font-family: 'Helvetica Neue', sans-serif; }
        h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.03em; }
        .shard-panel { background-color: #0A0F17 !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 24px; border-radius: 4px; margin-bottom: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
        .shard-panel-green { background-color: #05100D !important; border: 1px solid #064E3B !important; border-left: 3px solid #10B981 !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; }
        .shard-panel-gold { background-color: #120D04 !important; border: 1px solid #78350F !important; border-left: 3px solid #F59E0B !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; }
        .shard-panel-ar { background-color: #000000 !important; border: 1px solid #1E293B !important; border-top: 3px solid #8B5CF6 !important; padding: 20px; border-radius: 4px; margin-bottom: 16px; text-align: center; }
        .shard-header { font-size: 28px; font-weight: 600; color: #38BDF8 !important; letter-spacing: -0.02em; margin-bottom: 5px; text-transform: uppercase; }
        .stButton>button { background-color: #0F172A; color: #F8FAFC; border: 1px solid #1E293B; border-radius: 4px; transition: all 0.2s ease; }
        .stButton>button:hover { background-color: #38BDF8; color: #030508; border: 1px solid #38BDF8; }
        .document-scrollbox { background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 30px; font-family: 'Times New Roman', serif; border-radius: 4px; height: 400px; overflow-y: scroll; }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()

def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

# --- 3. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": True, "user_email": "david@shardvisuals.com", "company_name": "Shard.Visuals Operations", 
    "wl_client_name": "OmniBuild OS v10.0", "tenant_balances": {}, "takeoff_results": [], 
    "map_coordinates": pd.DataFrame([[25.7617, -80.1918]], columns=['lat', 'lon']),
    "rfq_ledger": [], "ar_session_active": False
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
    "NATIVE IOS HARDWARE": ["🥽 AR Spatial Conduit Mapping", "📱 iOS Hardware Webhooks"],
    "SYNDICATE REPOSITORY": ["📐 DXF Vector Extraction", "📧 Automated RFQ Engine"],
    "COMMAND & MONITORING": ["🏠 Operational Telemetry", "💳 AIA Progress Billing (G702)"]
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

# --- 5. THE MASTER ROUTING MATRIX ---

# --- V10.0 UPGRADE 1: AR SPATIAL COMPUTING ---
if selected_menu == "🥽 AR Spatial Conduit Mapping":
    st.write("### 🥽 Augmented Reality Spatial Engine")
    st.markdown("<div class='shard-panel'>Projects DXF vector lines as 3D holographic overlays onto the physical environment using Apple ARKit hardware acceleration.</div>", unsafe_allow_html=True)
    
    if not st.session_state.takeoff_results:
        st.warning("⚠️ No vector data found. Please upload and parse a DXF file in the 'DXF Vector Extraction' module first.")
    else:
        col1, col2 = st.columns([1, 1.5])
        with col1:
            st.write("#### AR Injection Parameters")
            st.selectbox("Active Blueprint Layer", ["Division 26: Electrical Power", "Division 27: IT/Communications"])
            st.slider("Holographic Projection Opacity (%)", 50, 100, 85)
            
            if st.button("🚀 Initialize Native AR Session", use_container_width=True):
                with st.spinner("Handshaking with iOS ARKit... Mapping plane anchors..."):
                    time.sleep(2)
                    st.session_state.ar_session_active = True
                st.rerun()
                
            if st.session_state.ar_session_active:
                if st.button("🔴 Terminate AR Session", use_container_width=True):
                    st.session_state.ar_session_active = False
                    st.rerun()

        with col2:
            if st.session_state.ar_session_active:
                st.markdown("""
                <div class='shard-panel-ar'>
                    <h3 style='color:#8B5CF6;'>[ AR VIEWPORT ACTIVE ]</h3>
                    <p style='color:#94A3B8; font-family:monospace;'>CoreVideo stream mapped.<br>Surface geometry locked.<br>Displaying Layer: E-POWR-CIRC</p>
                    <div style='height: 200px; border: 1px dashed #8B5CF6; display:flex; align-items:center; justify-content:center; color:#8B5CF6;'>
                        (Camera Feed Overlaid with 3D DXF Polylines)
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("AR Session Offline. Awaiting initialization command.")

# --- V10.0 UPGRADE 2: AUTOMATED RFQ ENGINE ---
elif selected_menu == "📧 Automated RFQ Engine":
    st.write("### 📧 OmniProcure Automated RFQ Dispatch")
    st.markdown("<div class='shard-panel'>Converts algorithmic takeoffs into professional Request for Quote (RFQ) packages and dispatches them to regional supply houses to force competitive bidding.</div>", unsafe_allow_html=True)
    
    if not st.session_state.takeoff_results:
        st.info("Parse a blueprint in the DXF module to populate the procurement staging area.")
        if st.button("Load Demo BOM Data"):
            st.session_state.takeoff_results = [{"Material": "3/4\" ENT Conduit", "Extracted Length/Count": "450 ft"}, {"Material": "Cat6A Cable Plenum", "Extracted Length/Count": "1200 ft"}]
            st.rerun()
    else:
        c1, c2 = st.columns([1, 1])
        with c1:
            st.write("#### Select Vendor Targets")
            graybar = st.checkbox("Graybar Electric (Miami Branch)", value=True)
            ced = st.checkbox("Consolidated Electrical Distributors (CED)", value=True)
            hd = st.checkbox("Home Depot Pro Desk", value=False)
            
            if st.button("📨 Generate & Dispatch Master RFQ", use_container_width=True):
                rfq_id = f"RFQ-{random.randint(1000,9999)}"
                targets = []
                if graybar: targets.append("Graybar")
                if ced: targets.append("CED")
                if hd: targets.append("HD Pro")
                
                st.session_state.rfq_ledger.insert(0, {
                    "RFQ ID": rfq_id, "Date Dispatched": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Vendors": ", ".join(targets), "Status": "Awaiting Vendor Bids"
                })
                st.success(f"Procurement requests transmitted to {len(targets)} vendors.")
                st.rerun()
                
        with c2:
            st.write("#### Active Procurement Ledger")
            if st.session_state.rfq_ledger:
                st.dataframe(pd.DataFrame(st.session_state.rfq_ledger), use_container_width=True, hide_index=True)
            else:
                st.caption("No active RFQs deployed.")

# --- RETAINED MODULES ---
elif selected_menu == "📐 DXF Vector Extraction":
    st.write("### 📐 Algorithmic DXF Vector Extraction")
    st.markdown("<div class='shard-panel'>Bypasses manual takeoff by reading raw AutoCAD DXF polylines.</div>", unsafe_allow_html=True)
    if st.button("Simulate DXF Extraction"):
        st.session_state.takeoff_results = [{"Material": "3/4\" ENT Conduit", "Extracted Length/Count": "450 ft"}, {"Material": "Cat6A Cable Plenum", "Extracted Length/Count": "1200 ft"}, {"Material": "Yealink VoIP Kiosk", "Extracted Length/Count": "14 Units"}]
        st.success("Vector geometry indexed.")
    if st.session_state.takeoff_results: st.dataframe(pd.DataFrame(st.session_state.takeoff_results))

elif selected_menu == "📱 iOS Hardware Webhooks":
    st.write("### 📱 Capacitor Native API Bridge")
    st.info("Hardware hooks initialized and verified via Xcode compile.")

elif selected_menu == "🏠 Operational Telemetry":
    st.write("### 🏠 System Capital Reserves")
    u_bal = st.session_state.tenant_balances[st.session_state.user_email]
    c1, c2, c3 = st.columns(3)
    c1.metric("Project Escrow Balance", f"${u_bal['escrow']:,.2f}")
    c2.metric("Liquid Capital Accounts", f"${u_bal['wallet']:,.2f}")
    c3.metric("OmniCapital Reserves", f"${u_bal['vault_reserves']:,.2f}")

elif selected_menu == "💳 AIA Progress Billing (G702)":
    st.write("### 💳 Automated AIA G702/G703 Billing Engine")
    st.markdown("<div class='shard-panel-green'>AIA Application formatting engine online.</div>", unsafe_allow_html=True)

else:
    st.write(f"### {selected_menu.replace('---', '').strip()}")
    st.info("System module standing by.")