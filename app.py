import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests
import altair as alt

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="OmniBuild OS | Enterprise Platform", layout="wide", initial_sidebar_state="expanded")

# --- 2. SECURE CLOUD INITIALIZATION & API HELPERS ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "ENV_VAR_MISSING")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "ENV_VAR_MISSING")

def supabase_api_call(endpoint="materials", method="GET", payload=None, params=None):
    if SUPABASE_URL == "ENV_VAR_MISSING" or SUPABASE_KEY == "ENV_VAR_MISSING":
        return None
    headers = {
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    try:
        if method == "GET": response = requests.get(url, headers=headers, params=params)
        elif method == "POST": response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return None

def sanitize_input(user_input):
    return html.escape(str(user_input)) if user_input else ""

# --- 3. LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Command Center", "matrix": "📊 Trade Matrix", "takeoff": "📐 Automated Takeoff", "gc_budg": "🏗️ GC Budget", 
        "fin": "💳 OmniPay & Escrow", "bank": "🏦 Bank Portal", "clinic": "🏥 Clinic Infra & Audit", 
        "co_lien": "📝 Change Orders & Liens", "bid": "🎯 AI Bid Optimizer", "sched": "📅 Trade Calendar", 
        "ai_core": "🧠 OmniMind AI Core", "dash": "📊 Telemetry Dashboard", "comm_rollout": "🏢 Commercial Rollout", 
        "legal_contract": "📝 Master Contracts", "field_signoff": "🔍 Field Sign-Off", "pitch_white": "🎨 Brand White-Label", 
        "audit_logs": "📋 Audit Trail & Reports", "procure": "📦 Procurement & POs", "api": "☁️ Cloud API"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 75000.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 185000.00
if "bank_connected" not in st.session_state: st.session_state.bank_connected = True
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []
if "system_audit_trail" not in st.session_state: st.session_state.system_audit_trail = []
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status"])

# White-Label Theme State Defaults
if "wl_client_name" not in st.session_state: st.session_state.wl_client_name = "OmniBuild OS Standard"
if "wl_accent_color" not in st.session_state: st.session_state.wl_accent_color = "#38BDF8"
if "wl_bg_tint" not in st.session_state: st.session_state.wl_bg_tint = "#0F172A"

# New persistent storage array tracking generated Purchase Orders
if "purchase_orders" not in st.session_state:
    st.session_state.purchase_orders = []

def log_system_event(user, phase, log_string):
    timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.system_audit_trail.insert(0, {
        "Timestamp": timestamp_str, "User Node": user, "Event Phase": phase, "Log Record String": log_string
    })

# --- 5. THEME STYLING INJECTION ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #070B12 !important; color: #94A3B8 !important; }}
    h1, h2, h3, h4, h5, h6 {{ color: #CBD5E1 !important; font-weight: 500 !important; }}
    .unifi-stealth-blade {{ background-color: {st.session_state.wl_bg_tint} !important; border: 1px solid #1E293B !important; border-left: 3px solid {st.session_state.wl_accent_color} !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .brand-hero-header {{ font-size: 28px; font-weight: bold; color: {st.session_state.wl_accent_color} !important; letter-spacing: -0.02em; margin-bottom: 5px; }}
    .po-document-box {{ background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 25px; font-family: monospace; font-size: 13px; line-height: 1.5; border-radius: 4px; }}
</style>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("auth_form"):
            input_email = st.text_input("Account Email").strip()
            input_password = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Verify Credentials", use_container_width=True):
                user_query = supabase_api_call(endpoint="user_registry", method="GET", params={"email": f"eq.{input_email}", "password_hash": f"eq.{input_password}"})
                if user_query and len(user_query) > 0:
                    profile = user_query[0]
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = profile["email"]
                    st.session_state.user_role = profile["assigned_role"]
                    st.session_state.company_name = profile["company_name"]
                    log_system_event(profile["email"], "Security Auth", "User cleared gateway access verification loops.")
                    st.success("Access Verified.")
                    time.sleep(0.5); st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

t = lang_dict[st.session_state.lang]

# --- 7. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["pitch_white"], t["audit_logs"], t["procure"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 8. GLOBAL TELEMETRY BAR HEADER ---
st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.markdown(f"<p style='font-size:12px; margin-top:-10px; color:#64748B;'>Enterprise Partner Network Interface Portal Node ∙ Managed by {st.session_state.company_name}</p>", unsafe_allow_html=True)
st.divider()

# --- 9. GLOBAL DATABASE CROSS-TABLE RECOVERY ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})
total_material_cost = 0.0
has_materials = False

if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0:
    full_df = pd.DataFrame(raw_cloud_data)
    df_elec_clean = full_df[full_df["trade_type"] == "Electrical"]
    total_material_cost = (df_elec_clean["quantity"] * df_elec_clean["cost_per_unit"]).sum()
    has_materials = True

# --- 10. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.bank_connected = True; st.session_state.escrow_locked = 220000.00; st.session_state.wallet_balance = 75000.00
        st.session_state.contract_agreements = [{"Doc ID": "SMA-DEMO", "GC Entity": "Global Development Corp", "Contract Value": 220000.00, "Execution Date": "Simulated Active", "Signatory": "Sandbox Admin", "Status": "Legally Executed"}]
        st.session_state.commercial_units = pd.DataFrame([
            {"Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00}
        ])
        log_system_event(st.session_state.user_email, "Sandbox Seed", "Injected full relational data science model array frames.")
        st.success("Sandbox populated!"); time.sleep(0.5); st.rerun()

elif selected_page == t["matrix"]: st.write(f"### {t['matrix']}")
elif selected_page == t["takeoff"]: st.write(f"### {t['takeoff']}")
elif selected_page == t["bid"]: st.write(f"### {t['bid']}")
elif selected_page == t["clinic"]: st.write(f"### {t['clinic']}")
elif selected_page == t["co_lien"]: st.write(f"### {t['co_lien']}")
elif selected_page == t["fin"]: st.write(f"### {t['fin']}")
elif selected_page == t["bank"]: st.write(f"### {t['bank']}")
elif selected_page == t["sched"]: st.write(f"### {t['sched']}")
elif selected_page == t["ai_core"]: st.write(f"### {t['ai_core']}")
elif selected_page == t["dash"]: st.write(f"### {t['dash']}")
elif selected_page == t["comm_rollout"]: st.write(f"### {t['comm_rollout']}")
elif selected_page == t["legal_contract"]: st.write(f"### {t['legal_contract']}")
elif selected_page == t["field_signoff"]: st.write(f"### {t['field_signoff']}")
elif selected_page == t["pitch_white"]: st.write(f"### {t['pitch_white']}")
elif selected_page == t["audit_logs"]: st.write(f"### {t['audit_logs']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# NEW ARCHITECTURE MODULE: AUTOMATED COMPONENT PROCUREMENT & PO GENERATOR
elif selected_page == t["procure"]:
    st.write(f"### {t['procure']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Intelligent Material Supply-Chain Buyout & Logistics Center</b><br>Compile wholesale vendor allocations, track material backorders, and execute automated secure corporate purchase orders.</div>", unsafe_allow_html=True)
    
    # Check if there are active materials to buyout
    active_buyout_value = total_material_cost if total_material_cost > 0 else (len(st.session_state.commercial_units) * 1150.00)
    
    if active_buyout_value == 0.0:
        st.warning("⚠️ Supply-chain matrix currently empty. Run a blueprint spec takeoff or populate your commercial unit grids to generate material buyout metrics.")
    else:
        col_po_actions, col_po_view = st.columns([1, 1.3])
        
        with col_po_actions:
            st.write("#### 📦 Supply Material Buyout Controls")
            selected_vendor = st.selectbox("Target Logistics Wholesaler", ["Stone Slabs Supply Distributor LLC", "Miami Electrical Wholesale Node", "Enterprise HVAC Manufacturing Hub"])
            shipping_address = sanitize_input(st.text_input("Project Delivery Destination Site", value="Miami Project Site, Grid-04"))
            payment_terms = st.selectbox("Vendor Funding Terms Matrix", ["Net 30 Days", "Due Immediately via OmniPay", "COD (Cash on Delivery)"])
            
            st.write("##### 📊 Dynamically Compiled Buyout Value")
            st.metric("Total Procurement Liability Amount", f"${active_buyout_value:,.2f}")
            
            st.write("---")
            if st.button("⚡ Execute Secure Purchase Order Authorization", use_container_width=True):
                if st.session_state.wallet_balance >= active_buyout_value:
                    # Deduct cost from active wallet ledger to reflect the liability buyout
                    st.session_state.wallet_balance -= active_buyout_value
                    
                    new_po = {
                        "PO ID": f"PO-{len(st.session_state.purchase_orders) + 1:03d}",
                        "Wholesaler": selected_vendor,
                        "Amount": active_buyout_value,
                        "Terms": payment_terms,
                        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "Logistics Status": "Dispatched / Processing Shop"
                    }
                    st.session_state.purchase_orders.insert(0, new_po)
                    log_system_event(st.session_state.user_email, "Procurement PO", f"Authorized secure purchase order {new_po['PO ID']} issued to {selected_vendor}.")
                    st.success(f"✅ Purchase Order {new_po['PO ID']} officially authorized and routed to vendor!")
                    time.sleep(0.5); st.rerun()
                else:
                    st.error("🚨 Order Blocked. Operational Liquid Wallet has insufficient funds to clear this procurement buyout line.")

        with col_po_view:
            st.write("#### 📑 Formal Document Output Frame")
            
            if not st.session_state.purchase_orders:
                # Preview draft before generation occurs
                st.markdown(f"""
                <div class='po-document-box'>
                    <p style='text-align: center; font-weight: bold; font-size: 15px; margin-bottom: 20px;'>PURCHASE ORDER DRAFT STATEMENT</p>
                    <b>PO TRACKING IDENTIFIER:</b> PO-DRAFT<br>
                    <b>ISSUANCE TIMESTAMP:</b> {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}<br>
                    <b>ISSUING SUBCONTRACTOR:</b> {st.session_state.company_name}<br>
                    <b>ROUTED WHOLESALER:</b> {selected_vendor}<br>
                    --------------------------------------------------<br>
                    <b>DELIVERY DESTINATION:</b> {shipping_address}<br>
                    <b>FUNDING PAYMENT TERMS:</b> {payment_terms}<br>
                    --------------------------------------------------<br>
                    <b>TOTAL PROCUREMENT VALUE COMPLED:</b> ${active_buyout_value:,.2f} USD<br>
                    --------------------------------------------------<br>
                    <p style='font-size: 11px; color: #64748B; font-style: italic; margin-top: 15px;'>This document acts as an unissued operational staging matrix.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                # View actively generated PO ledger elements
                st.write("##### 📋 Dispatched Corporate PO Ledger")
                po_df = pd.DataFrame(st.session_state.purchase_orders)
                st.dataframe(po_df, use_container_width=True, hide_index=True)
                
                with st.expander("🔍 View Latest Dispatched Document Details"):
                    latest_po = st.session_state.purchase_orders[0]
                    st.markdown(f"""
                    <div class='po-document-box'>
                        <p style='text-align: center; font-weight: bold; font-size: 15px; margin-bottom: 20px; color: #10B981;'>AUTHORIZED PURCHASE ORDER DISPATCHED</p>
                        <b>PURCHASE ORDER NUMBER:</b> {latest_po['PO ID']}<br>
                        <b>ISSUANCE TIMESTAMP:</b> {latest_po['Timestamp']}<br>
                        <b>ISSUING CLIENT LOG:</b> {st.session_state.company_name}<br>
                        <b>TARGET SUPPLY VENDOR:</b> {latest_po['Wholesaler']}<br>
                        --------------------------------------------------<br>
                        <b>FUNDING SETTLEMENT TERMS:</b> {latest_po['Terms']}<br>
                        --------------------------------------------------<br>
                        <b>LINE TOTAL PAYABLE VALUE:</b> ${latest_po['Amount']:,.2f} USD<br>
                        <b>LOGISTICS PIPELINE ROUTE:</b> {latest_po['Logistics Status']}<br>
                    </div>
                    """, unsafe_allow_html=True)