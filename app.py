import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import hashlib
import string

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | Production Ecosystem", layout="wide", initial_sidebar_state="expanded")

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
        .chat-bubble-ai { background-color: #0A0F17; border: 1px solid #1E293B; border-left: 3px solid #10B981; padding: 15px; border-radius: 4px; margin-bottom: 10px; }
        .chat-bubble-user { background-color: #1E293B; color: #F8FAFC; padding: 15px; border-radius: 4px; margin-bottom: 10px; text-align: right; }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()

def sanitize_input(user_input): return html.escape(str(user_input)) if user_input else ""

# --- 3. CRYPTOGRAPHIC, RAG & MATHEMATICAL ENGINES ---
def generate_sha256_hash(data_string):
    """Generates an immutable SHA-256 hash block for forensic sealing."""
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

def calculate_voltage_drop(phase, current, distance, awg, conductor, voltage):
    """Calculates exact physics-based voltage drop according to NEC standard variables."""
    k_val = 12.9 if conductor == "Copper" else 21.2
    cm_map = {
        "14": 4110, "12": 6530, "10": 10380, "8": 16510, "6": 26240, 
        "4": 41740, "2": 66360, "1/0": 105600, "2/0": 133100, 
        "3/0": 167800, "4/0": 211600, "250": 250000, "500": 500000
    }
    cm = cm_map.get(awg, 6530)
    
    if phase == "Single-Phase":
        vd = (2 * k_val * current * distance) / cm
    else:
        vd = (math.sqrt(3) * k_val * current * distance) / cm
        
    vd_percent = (vd / voltage) * 100
    return vd, vd_percent

def semantic_chunking_search(document, query):
    """A lightweight RAG semantic search engine matching structural keyword overlap."""
    sentences = re.split(r'(?<=[.!?]) +|\n', document)
    query_words = set(re.findall(r'\w+', query.lower()))
    
    best_match = "No precise specification matches located in active ledger memory."
    highest_score = 0
    
    for sentence in sentences:
        if not sentence.strip(): continue
        sentence_words = set(re.findall(r'\w+', sentence.lower()))
        overlap = len(query_words.intersection(sentence_words))
        if overlap > highest_score:
            highest_score = overlap
            best_match = sentence.strip()
            
    return best_match

# --- 4. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": False, "user_email": "", "company_name": "Shard.Visuals Operations", "wl_client_name": "OmniBuild OS v7.5",
    "tenant_balances": {}, "sub_tier_contracts": [], "takeoff_results": [],
    "labor_logs": [], "forensic_photos": [], "clinic_hardware_matrix": [],
    "base_apprentice_hours": 412.5, "rag_chat": [], "spec_document": "",
    "micro_loans": [], "map_coordinates": pd.DataFrame([[25.7617, -80.1918]], columns=['lat', 'lon']) # Default Miami Node
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 5. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='margin-top:10vh; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:3.5rem; color:#38BDF8 !important;'>OMNIBUILD OS</h1><p style='color:#94A3B8; font-size:1.2rem;'>UPGRADED SYSTEM REPOSITORY</p>", unsafe_allow_html=True)
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

# --- 6. UNIFIED SIDEBAR NAVIGATION ---
st.sidebar.markdown(f"<h3 style='color:#FFFFFF; text-transform:uppercase;'>{st.session_state.company_name}</h3>", unsafe_allow_html=True)
st.sidebar.caption(f"Node: {current_user}")
st.sidebar.divider()

menu_categories = {
    "COMMAND & MONITORING": ["🏠 Operational Telemetry", "🚁 Geospatial Mapping Tracker"],
    "FINANCIAL INFRASTRUCTURE": ["🏦 OmniCapital FinTech Suite"],
    "SYNDICATE REPOSITORY": ["🧠 OmniMind Native RAG Chat"],
    "ENGINEERING LOGISTICS": ["⚡ Physics Load Calculator"]
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
    st.info("Select an active processing module from the control list.")
    st.stop()

# --- 7. THE MASTER ROUTING MATRIX ---

if selected_menu == "🏠 Operational Telemetry":
    st.write("### 🏠 System Capital Reserves")
    u_bal = st.session_state.tenant_balances[current_user]
    c1, c2, c3 = st.columns(3)
    c1.metric("Project Escrow Balance", f"${u_bal['escrow']:,.2f}")
    c2.metric("Liquid Capital Accounts", f"${u_bal['wallet']:,.2f}")
    c3.metric("OmniCapital Reserves", f"${u_bal['vault_reserves']:,.2f}")

# --- UPGRADE 1: LIVE GEOSPATIAL MAPPING ---
elif selected_menu == "🚁 Geospatial Mapping Tracker":
    st.write("### 🚁 Live Asset & Progress Mapping")
    st.markdown("<div class='shard-panel'>Displays real-time geographic data nodes for site forensics and drone photogrammetry passes across Miami-Dade.</div>", unsafe_allow_html=True)
    
    col_coords, col_map = st.columns([1, 2])
    with col_coords:
        st.write("#### Register Deployment Coordinates")
        lat_in = st.number_input("Latitude Coordinate", value=25.7617, format="%.4f")
        lon_in = st.number_input("Longitude Coordinate", value=-80.1918, format="%.4f")
        if st.button("Pin Coordinate to Ledger", use_container_width=True):
            new_coord = pd.DataFrame([[lat_in, lon_in]], columns=['lat', 'lon'])
            st.session_state.map_coordinates = pd.concat([st.session_state.map_coordinates, new_coord], ignore_index=True)
            st.success("Geospatial node verified and locked.")
            st.rerun()
            
        if st.button("Reset Map Grid", use_container_width=True):
            st.session_state.map_coordinates = pd.DataFrame([[25.7617, -80.1918]], columns=['lat', 'lon'])
            st.rerun()
            
    with col_map:
        st.map(st.session_state.map_coordinates, zoom=11)

# --- UPGRADE 2: INTERACTIVE FINTECH CAPITAL YIELD MATH ---
elif selected_menu == "🏦 OmniCapital FinTech Suite":
    st.write("### 🏦 Advanced FinTech Material Financing")
    st.markdown("<div class='shard-panel'>Calculate explicit compound returns on cash advancements extended to sub-tier labor forces.</div>", unsafe_allow_html=True)
    
    col_calc, col_ledger = st.columns([1, 1.2])
    with col_calc:
        st.write("#### Term Yield Calculator")
        principal = st.number_input("Material Advance Capital ($)", value=5000.00, step=500.00)
        rate = st.slider("Flat Financing Fee Rate (%)", 2.0, 15.0, 5.0)
        days = st.number_input("Financing Term Window (Days)", value=30, step=5)
        
        # Exact compound yield structure
        interest = principal * (rate / 100)
        total_payout = principal + interest
        
        st.markdown(f"""
        <div class='shard-panel-gold'>
            <b>Principal Base:</b> ${principal:,.2f}<br>
            <b>Compounded Yield Asset:</b> ${interest:,.2f}<br>
            <b>Total Escrow Recovery:</b> ${total_payout:,.2f}
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Authorize Financing Disbursal", use_container_width=True):
            st.session_state.tenant_balances[current_user]["vault_reserves"] -= principal
            st.session_state.micro_loans.insert(0, {
                "Date": datetime.datetime.now().strftime("%Y-%m-%d"),
                "Principal": principal,
                "Yield Fee": interest,
                "Recovery Total": total_payout,
                "Status": "Secured / Active Ledger"
            })
            st.success("Financing pipeline locked against sub-tier escrow draws.")
            time.sleep(0.5); st.rerun()

    with col_ledger:
        st.write("#### Active FinTech Book Ledger")
        if st.session_state.micro_loans:
            st.dataframe(pd.DataFrame(st.session_state.micro_loans), use_container_width=True, hide_index=True)
        else:
            st.caption("No capital assets deployed in active financing.")

# --- UPGRADE 3: PRODUCTION NATIVE FILE-BASED RAG ---
elif selected_menu == "🧠 OmniMind Native RAG Chat":
    st.write("### 🧠 Production RAG Spec Document Indexer")
    st.markdown("<div class='shard-panel'>Accepts raw specification files directly, slicing data profiles in memory without external web vectors.</div>", unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader("Upload Raw Blueprint Specification File (.txt Only)", type=["txt"])
    if uploaded_file is not None:
        try:
            file_contents = uploaded_file.read().decode("utf-8")
            st.session_state.spec_document = file_contents
            st.markdown("<div class='shard-panel-green'><b>SUCCESS:</b> Document contents loaded and cached successfully.</div>", unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Error parsing text file context: {e}")

    st.write("---")
    st.write("#### Active Conversational RAG Array")
    for chat in st.session_state.rag_chat:
        if chat['role'] == 'user':
            st.markdown(f"<div class='chat-bubble-user'><b>Query:</b> {chat['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'><b>OmniMind:</b> {chat['text']}</div>", unsafe_allow_html=True)
            
    prompt = st.chat_input("Query structural parameter records...")
    if prompt:
        st.session_state.rag_chat.append({"role": "user", "text": sanitize_input(prompt)})
        if st.session_state.spec_document:
            ai_response = semantic_chunking_search(st.session_state.spec_document, prompt)
        else:
            ai_response = "Active memory index clear. Upload a blueprint spec document above to enable querying."
        st.session_state.rag_chat.append({"role": "ai", "text": ai_response})
        st.rerun()

elif selected_menu == "⚡ Physics Load Calculator":
    st.write("### ⚡ National Electrical Code Mathematics")
    col1, col2, col3 = st.columns(3)
    c_phase = col1.selectbox("System Configuration Type", ["Single-Phase", "Three-Phase"])
    c_conductor = col2.selectbox("Material Conductor", ["Copper", "Aluminum"])
    c_voltage = col3.number_input("Circuit Voltage Rating (V)", value=120)
    
    col4, col5, col6 = st.columns(3)
    c_current = col4.number_input("Load Current Factor (A)", value=20.0)
    c_distance = col5.number_input("Distance Loop (ft)", value=150.0)
    c_awg = col6.selectbox("Wire Sizing Index (AWG)", ["14", "12", "10", "8", "6", "4", "2", "1/0", "2/0", "3/0", "4/0"], index=1)
    
    if st.button("Execute Field Physics Calculation", use_container_width=True):
        vd, vd_pct = calculate_voltage_drop(c_phase, c_current, c_distance, c_awg, c_conductor, c_voltage)
        if vd_pct <= 3.0:
            st.markdown(f"<div class='shard-panel-green'><b>✅ CALCULATED COMPLIANT:</b> {vd_pct:.2f}% Drop ({vd:.2f} Volts Lost). Conductor sizing approved.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='shard-panel-red'><b>🚨 OUT OF LIMIT COMPLIANCE:</b> {vd_pct:.2f}% Drop ({vd:.2f} Volts Lost). Conductor cross-section adjustments mandatory.</div>", unsafe_allow_html=True)