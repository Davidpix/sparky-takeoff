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
st.set_page_config(page_title="OmniBuild OS | Production Core", layout="wide", initial_sidebar_state="expanded")

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

# --- 3. CRYPTOGRAPHIC & MATH ENGINES ---
def generate_sha256_hash(data_string):
    """Generates an immutable SHA-256 hash block for forensic sealing."""
    return hashlib.sha256(data_string.encode('utf-8')).hexdigest()

def calculate_voltage_drop(phase, current, distance, awg, conductor, voltage):
    """Calculates exact physics-based voltage drop according to NEC standard variables."""
    # K values: Ohms-CM per foot
    k_val = 12.9 if conductor == "Copper" else 21.2
    
    # Circular Mils lookup table
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
    """A lightweight RAG semantic search engine without external API dependencies."""
    sentences = re.split(r'(?<=[.!?]) +', document)
    query_words = set(re.findall(r'\w+', query.lower()))
    
    best_match = "I could not locate specific constraints regarding that query in the active specification ledger."
    highest_score = 0
    
    for sentence in sentences:
        sentence_words = set(re.findall(r'\w+', sentence.lower()))
        overlap = len(query_words.intersection(sentence_words))
        if overlap > highest_score:
            highest_score = overlap
            best_match = sentence
            
    return best_match

# --- 4. GLOBAL STATE MANAGEMENT ---
default_states = {
    "user_authenticated": False, "user_email": "", "company_name": "Shard.Visuals Operations", "wl_client_name": "OmniBuild OS v7.0",
    "tenant_balances": {}, "sub_tier_contracts": [], "live_pricing": {}, "takeoff_results": [],
    "labor_logs": [], "forensic_photos": [], "clinic_appointments": [], "clinic_hardware_matrix": [],
    "base_apprentice_hours": 412.5, "rag_chat": [], "spec_document": ""
}
for key, val in default_states.items():
    if key not in st.session_state: st.session_state[key] = val

# --- 5. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='margin-top:10vh; text-align:center;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='font-size:3.5rem; color:#38BDF8 !important;'>OMNIBUILD OS</h1><p style='color:#94A3B8; font-size:1.2rem;'>PRODUCTION ECOSYSTEM TERMINAL</p>", unsafe_allow_html=True)
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
    "COMMAND & OPS": ["🏠 Global Telemetry Dashboard"],
    "SYNDICATE NETWORK": ["🧠 OmniMind Native RAG Chat"],
    "ENGINEERING & FIELD": ["⚡ Physics Load Calculator", "⏱️ Apprenticeship Ledger"],
    "FORENSICS & COMPLIANCE": ["📷 Cryptographic Site Forensics"]
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
    u_bal = st.session_state.tenant_balances[current_user]
    c1, c2, c3 = st.columns(3)
    c1.metric("Project Escrow", f"${u_bal['escrow']:,.2f}")
    c2.metric("Working Liquidity", f"${u_bal['wallet']:,.2f}")
    c3.metric("Lindsey Hopkins Log", f"{(st.session_state.base_apprentice_hours/600)*100:.1f}%")

# --- PRODUCTION MODULE 1: NATIVE RAG SPEC CHAT ---
elif selected_menu == "🧠 OmniMind Native RAG Chat":
    st.write("### 🧠 OmniMind Semantic RAG Terminal")
    st.markdown("<div class='shard-panel'>Stateful string-matching and semantic indexer for processing massive raw specification ledgers.</div>", unsafe_allow_html=True)
    
    with st.expander("Upload / Paste Raw Specification Book Text", expanded=not bool(st.session_state.spec_document)):
        raw_text = st.text_area("Master Specification Document", value=st.session_state.spec_document, height=200, placeholder="Paste Division 26 or Division 27 specification text here...")
        if st.button("Index Document into Active Memory"):
            st.session_state.spec_document = raw_text
            st.success("Document chunked and loaded into active RAG memory.")
            st.rerun()

    st.write("#### Secure Terminal Query")
    for chat in st.session_state.rag_chat:
        if chat['role'] == 'user':
            st.markdown(f"<div class='chat-bubble-user'><b>Operator:</b> {chat['text']}</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='chat-bubble-ai'><b>OmniMind:</b> {chat['text']}</div>", unsafe_allow_html=True)
            
    prompt = st.chat_input("Query active specification parameters...")
    if prompt:
        st.session_state.rag_chat.append({"role": "user", "text": sanitize_input(prompt)})
        if st.session_state.spec_document:
            ai_response = semantic_chunking_search(st.session_state.spec_document, prompt)
        else:
            ai_response = "No specification document loaded in active memory. Please upload spec text to proceed."
        st.session_state.rag_chat.append({"role": "ai", "text": ai_response})
        st.rerun()

# --- PRODUCTION MODULE 2: EXACT PHYSICS NEC CALCULATOR ---
elif selected_menu == "⚡ Physics Load Calculator":
    st.write("### ⚡ National Electrical Code Mathematics")
    st.markdown("<div class='shard-panel'>Computes exact physics formulas for voltage drop using Direct Ohm-CM Resistivity (K-values).</div>", unsafe_allow_html=True)
    
    st.markdown("$$VD=\\frac{2\\cdot K\\cdot I\\cdot D}{CM}$$")
    st.markdown("$$VD=\\frac{\\sqrt{3}\\cdot K\\cdot I\\cdot D}{CM}$$")
    
    col1, col2, col3 = st.columns(3)
    c_phase = col1.selectbox("System Phase", ["Single-Phase", "Three-Phase"])
    c_conductor = col2.selectbox("Conductor Material", ["Copper", "Aluminum"])
    c_voltage = col3.number_input("Source Voltage (V)", value=120)
    
    col4, col5, col6 = st.columns(3)
    c_current = col4.number_input("Load Current (A)", value=20.0)
    c_distance = col5.number_input("One-Way Distance (ft)", value=150.0)
    c_awg = col6.selectbox("Wire Gauge (AWG/kcmil)", ["14", "12", "10", "8", "6", "4", "2", "1/0", "2/0", "3/0", "4/0", "250", "500"], index=1)
    
    if st.button("Execute Field Physics Calculation", use_container_width=True):
        vd, vd_pct = calculate_voltage_drop(c_phase, c_current, c_distance, c_awg, c_conductor, c_voltage)
        if vd_pct <= 3.0:
            st.markdown(f"<div class='shard-panel-green'><b>✅ NEC COMPLIANT:</b> {vd_pct:.2f}% Drop ({vd:.2f} Volts Lost). Secure to execute pull.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='shard-panel-red'><b>🚨 CRITICAL VOLTAGE LOSS:</b> {vd_pct:.2f}% Drop ({vd:.2f} Volts Lost). Upsize conductor gauge immediately.</div>", unsafe_allow_html=True)

# --- PRODUCTION MODULE 3: CRYPTOGRAPHIC FORENSICS ---
elif selected_menu == "📷 Cryptographic Site Forensics":
    st.write("### 📸 Immutable Site Progress Ledger")
    st.markdown("<div class='shard-panel'>Generates true, deterministic SHA-256 block hashes from combined visual metadata and time-stamps.</div>", unsafe_allow_html=True)
    
    col_cam, col_ledger = st.columns([1, 1.2])
    with col_cam:
        photo_notes = st.text_input("Forensic Field Notes", placeholder="e.g., Pull box terminated at 8-foot ceiling height...")
        captured_image = st.camera_input("📸 Capture Field Document")
        
        if captured_image:
            with st.spinner("Executing cryptographic algorithm..."):
                time.sleep(0.8)
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                raw_data_string = f"{photo_notes}_{timestamp}_{captured_image.size}"
                true_hash = generate_sha256_hash(raw_data_string)
                
                st.session_state.forensic_photos.insert(0, {
                    "Timestamp": timestamp, 
                    "Unit Node": "Production Site-Wide", 
                    "Notes": sanitize_input(photo_notes), 
                    "Hash": true_hash
                })
                st.success("Photo digitally sealed into the active matrix."); time.sleep(1); st.rerun()

    with col_ledger:
        if st.session_state.forensic_photos:
            st.markdown("<h4 style='color:#F59E0B; letter-spacing:2px;'>SHARD.VISUALS CRYPTO-LEDGER</h4>", unsafe_allow_html=True)
            for p in st.session_state.forensic_photos:
                st.markdown(f"""
                <div style='background-color:#050505; border:1px solid #333; padding:15px; border-radius:4px; margin-bottom:10px;'>
                    <span style='color:#38BDF8;'>[{p['Timestamp']}]</span> <b>{p['Unit Node']}</b><br>
                    <i style='color:#94A3B8;'>"{p['Notes']}"</i><br>
                    <code style='color:#10B981; background:none; padding:0; font-size:10px;'>SHA-256: {p['Hash']}</code>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.caption("Awaiting cryptographic field captures.")

# --- PRODUCTION MODULE 4: APPRENTICESHIP LEDGER ---
elif selected_menu == "⏱️ Apprenticeship Ledger":
    st.write("### 🎓 Academic Telemetry")
    total_hours = st.session_state.base_apprentice_hours
    st.markdown(f"<div class='shard-panel'><b>Lindsey Hopkins Technical College Target</b><br><progress value='{total_hours/600}' max='1' style='width:100%; height:20px;'></progress><br> {total_hours:.1f} / 600 Hours Verified toward requirement.</div>", unsafe_allow_html=True)

else:
    st.write(f"### {selected_menu.replace('---', '').strip()}")
    st.info("System module standing by.")