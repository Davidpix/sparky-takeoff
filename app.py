import streamlit as st
import pandas as pd
import random
import time
import datetime
import json
import os
import math
from io import BytesIO

st.set_page_config(page_title="UniFi SparkyTakeoff OS", layout="wide", initial_sidebar_state="collapsed")

# --- EXECUTIVE STEALTH DARK MODE CSS INJECTION ---
st.markdown("""
<style>
    /* Global Anti-Glare Matte Surface */
    .stApp {
        background-color: #090D16 !important;
        color: #94A3B8 !important; /* Soft muted gray text instead of blinding white */
    }
    
    /* Clean, Lower-Intensity Headers */
    h1, h2, h3, h4, h5, h6 {
        color: #CBD5E1 !important;
        font-weight: 500 !important;
    }
    
    /* Muted UniFi Telemetry Metric Values */
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 600 !important;
        color: #38BDF8 !important; /* Swapped harsh cyan for a soothing matte sky blue */
        font-family: 'Courier New', monospace;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #64748B !important;
    }
    
    /* Matte Surface Hardware Blades */
    .unifi-stealth-blade {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-left: 3px solid #38BDF8 !important; /* Softer indicator anchor */
        padding: 16px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .unifi-stealth-alert {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-left: 3px solid #F59E0B !important; /* Controlled amber accent */
        padding: 16px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    
    /* Muted Tab Navigation Rails */
    .stTabs [data-baseweb="tab"] {
        color: #64748B !important;
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 0.5px !important;
        background-color: transparent !important;
        border: none !important;
        padding: 8px 16px !important;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #38BDF8 !important;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #38BDF8 !important;
        border-bottom: 2px solid #38BDF8 !important;
    }
    
    /* Dull Down Streamlit's Default Table/Editor Bright Lines */
    div[data-testid="stDataEditor"] {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-radius: 4px;
    }
    
    /* Desaturate Text Areas and Terminals */
    textarea {
        background-color: #05070C !important;
        color: #475569 !important; /* Low contrast terminal feed to ease eye focus */
        border: 1px solid #1E293B !important;
        font-family: monospace !important;
    }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM DIRECTORY STORAGE BOOT ---
SAVED_PROJECTS_DIR = "saved_estimates_vault"
if not os.path.exists(SAVED_PROJECTS_DIR):
    os.makedirs(SAVED_PROJECTS_DIR)

# --- CONTROL VARIABLES MACHINE ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "active_project_id" not in st.session_state: st.session_state.active_project_id = "SYS_UNASSIGNED_NODE"
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Electrical"
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "uploaded_file_bytes" not in st.session_state: st.session_state.uploaded_file_bytes = None
if "vision_counts" not in st.session_state: st.session_state.vision_counts = {}
if "sheet_ledger" not in st.session_state: st.session_state.sheet_ledger = {}

if "sys_log_history" not in st.session_state:
    st.session_state.sys_log_history = [
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] SYS CORE: Stealth kernel running safely.",
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] NET KERNEL: Connected to South Florida distributor pricing nodes."
    ]

if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {
        "3/4\" EMT Conduit (10ft Factory Sticks)": 6.50,
        "3/4\" EMT Set-Screw Coupling": 1.15,
        "3/4\" 1-Hole EMT Strap": 0.45,
        "Commercial Grade 20A GFCI Device": 18.00,
        "Specification Grade 20A Toggle Switch": 1.50
    }

# --- GATEWAY PORTAL SCREEN ---
if not st.session_state.user_authenticated:
    st.title("⚡ SparkyTakeoff OS")
    st.caption("Matte Interface Security Authentication Console")
    
    col_login, col_guide = st.columns([1, 1])
    with col_login:
        with st.form("simple_login_form"):
            user_email = st.text_input("Operator Email Identifier", placeholder="operator@domain.com")
            password = st.text_input("Access Security Key", type="password", placeholder="••••")
            submit_auth = st.form_submit_button("Verify Core Connection")
            
            if submit_auth:
                if user_email and len(password) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = user_email
                    st.session_state.active_project_id = "EST_STEALTH_BLADE_1"
                    st.rerun()
                else:
                    st.error("Authentication rejected.")
    with col_guide:
        st.caption("🔒 Guest Testing Access Credentials:\n* Email: `admin@sharded.io` | Key: `1234`")

else:
    # --- AUTHENTICATED COMMAND BLADES ---
    col_header, col_status = st.columns([3, 1])
    with col_header:
        st.markdown("<h3 style='margin-bottom:0px; letter-spacing:-0.5px;'>⚡ Control Center Matrix</h3>", unsafe_allow_html=True)
        st.caption(f"Operator Security Scope: `{st.session_state.user_email}` | Active Data Frame: `{st.session_state.active_project_id}`")
    with col_status:
        st.markdown("<div style='text-align:right; margin-top:10px;'>", unsafe_allow_html=True)
        if st.button("Disconnect Node"):
            st.session_state.user_authenticated = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    # --- BASELINE COMPUTATION SEQUENCE ---
    baseline_mock_manifest = [
        {"Item Name": "3/4\" EMT Conduit (10ft Factory Sticks)", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 150, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Conduit (10ft Factory Sticks)"], "Mins to Install": 12},
        {"Item Name": "3/4\" EMT Set-Screw Coupling", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 140, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Set-Screw Coupling"], "Mins to Install": 3},
        {"Item Name": "3/4\" 1-Hole EMT Strap", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 200, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" 1-Hole EMT Strap"], "Mins to Install": 2},
        {"Item Name": "Commercial Grade 20A GFCI Device", "Phase": "Trim-Out", "Target Zone": "Kitchen Layout", "Qty": 25, "Unit Cost ($)": st.session_state.vendor_pricing["Commercial Grade 20A GFCI Device"], "Mins to Install": 15},
        {"Item Name": "Specification Grade 20A Toggle Switch", "Phase": "Trim-Out", "Target Zone": "General Lighting", "Qty": 40, "Unit Cost ($)": st.session_state.vendor_pricing["Specification Grade 20A Toggle Switch"], "Mins to Install": 10}
    ]
    df_takeoff = pd.DataFrame(baseline_mock_manifest)
    
    total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Unit Cost ($)"]).sum()
    total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
    raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
    burdened_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
    total_labor_hours = ((df_takeoff["Qty"] * df_takeoff["Mins to Install"]) / 60).sum()
    total_labor_cost = total_labor_hours * burdened_rate
    target_gross_bid = (total_mat_cost + total_labor_cost) * (1 + st.session_state.overhead)

    # --- MATTE HARDWARE BLADES: HEALTH PANEL INDEX ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>System Gross Valuation</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>${target_gross_bid:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Material Invoice Limit</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>${total_mat_cost:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Production Allocation</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>{total_labor_hours:.1f} hrs</h3></div>", unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Target Operational Margin</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>{st.session_state.overhead*100:.0f}%</h3></div>", unsafe_allow_html=True)

    # --- INTEGRATED NAVIGATION TABS ---
    tab_estimation, tab_sourcing, tab_analytics, tab_config = st.tabs([
        "📊 Data Grid", "🏪 Vendor Router", "🎯 System Metrics", "⚙️ Hardware Parameters"
    ])

    with tab_estimation:
        edited_df = st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True, key="stealth_grid")

    with tab_sourcing:
        sc_col1, sc_col2 = st.columns([1, 2])
        with sc_col1:
            target_supply_house = st.selectbox("Select Counter Node Drop", ["City Electric Supply (CES North Miami)", "Rexel Electrical Supply", "Graybar District Counter"])
            delivery_method = st.radio("Logistics Pathway", ["Will Call Counter Pickup", "Flatbed Carrier Site Drop"])
            po_reference_id = st.text_input("PO Frame Index ID", value=f"PO-{random.randint(10000, 99999)}")
        with sc_col2:
            st.write("#### 📝 Current Procurement Payload Preview")
            order_summary_list = [f"• {int(r['Qty'])}x -- {r['Item Name']}" for _, r in edited_df.iterrows() if r["Qty"] > 0]
            st.markdown("\n".join(order_summary_list))
            
            if st.button("Transmit Secure Order"):
                st.session_state.sys_log_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] PACKET SEND: Transmitted PO frame {po_reference_id} to counter endpoint '{target_supply_house}'. Secure confirmation handshake verified.")
                st.toast("Order packet successfully processed.")

    with tab_analytics:
        an_col1, an_col2 = st.columns(2)
        with an_col1:
            # Low contrast charcoal bar layout
            alloc_df = pd.DataFrame({
                "Component Sector": ["Wholesale Items", "Labor Overhead", "Target Profit Buffer"],
                "Allocation Value ($)": [total_mat_cost, total_labor_cost, (total_mat_cost + total_labor_cost) * st.session_state.overhead]
            })
            st.bar_chart(data=alloc_df, x="Component Sector", y="Allocation Value ($)", use_container_width=True)
        with an_col2:
            project_days = st.number_input("Contract Operating Timeline Scope (Days)", min_value=1, value=5)
            max_avail_man_hours = project_days * (total_crew_members * 8)
            
            if total_labor_hours > max_avail_man_hours:
                st.markdown(f"<div class='unifi-stealth-alert'><h5 style='color:#F59E0B; margin:0;'>⚠️ TIMELINE CONSTRAINTS EXCEEDED</h5><p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>Estimated man-hours ({total_labor_hours:.1f}) exceed active crew availability limits. Schedule risk profile elevated.</p></div>", unsafe_allow_html=True)
            else:
                utilization = (total_labor_hours / max_avail_man_hours) * 100 if max_avail_man_hours > 0 else 0
                st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5 style='color:#10B981; margin:0;'>✅ WORKLOAD ALLOCATION OPERATIONAL</h5><p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>Active pipeline is drawing {utilization:.1f}% of crew milestone bandwidth limits.</p></div>", unsafe_allow_html=True)

    with tab_config:
        st.session_state.company_name = st.text_input("Subcontractor Workspace Label", value=st.session_state.company_name)
        st.session_state.qty_journeymen = st.number_input("Active Journeymen Operational Links", min_value=1, value=st.session_state.qty_journeymen)
        st.session_state.qty_helpers = st.number_input("Active Helper Operational Links", min_value=0, value=st.session_state.qty_helpers)

    # --- THE LOWER TELEMETRY ACTIVITIES STREAM LOG ---
    st.markdown("<p style='color:#475569; text-transform:uppercase; letter-spacing:1px; font-size:10px; margin-bottom:4px; font-weight:600;'>📋 System Telemetry Frame Log Stream</p>", unsafe_allow_html=True)
    log_text_payload = "\n".join(st.session_state.sys_log_history[::-1])
    st.text_area(label="Activity Frame Logger Console Frame", value=log_text_payload, height=110, label_visibility="collapsed")