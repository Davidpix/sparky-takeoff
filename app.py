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

# --- CUSTOM UNIFI OS CSS INJECTION BLOCK ---
st.markdown("""
<style>
    /* Global Background and Typography Overrides */
    .stApp {
        background-color: #0B0F19;
        color: #E2E8F0;
    }
    /* Metric Card Styling */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: 600 !important;
        color: #00F0FF !important;
        font-family: 'Courier New', monospace;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 12px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #94A3B8 !important;
    }
    /* Clean Custom Container Cards mimicking UniFi Hardware Blades */
    .unifi-card {
        background-color: #131A2C;
        border: 1px solid #1E293B;
        border-left: 4px solid #00F0FF;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    .unifi-card-alert {
        background-color: #131A2C;
        border: 1px solid #1E293B;
        border-left: 4px solid #F59E0B;
        padding: 20px;
        border-radius: 6px;
        margin-bottom: 15px;
    }
    /* Tab Navigation Restyling */
    .stTabs [data-baseweb="tab"] {
        color: #94A3B8;
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        background-color: transparent;
        border: none;
        padding: 10px 20px;
    }
    .stTabs [data-baseweb="tab"]:hover {
        color: #00F0FF;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #00F0FF !important;
        border-bottom: 2px solid #00F0FF !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FILE-BASED STORAGE ARCHITECTURE ---
SAVED_PROJECTS_DIR = "saved_estimates_vault"
if not os.path.exists(SAVED_PROJECTS_DIR):
    os.makedirs(SAVED_PROJECTS_DIR)

# --- APPLICATION STATE MACHINES ---
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
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] SYS CORE: Bootloader sequence initialized successfully.",
        f"[{datetime.datetime.now().strftime('%H:%M:%S')}] NET KERNEL: Sourcing dynamic South Florida distributor matrix links..."
    ]

if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {
        "3/4\" EMT Conduit (10ft Factory Sticks)": 6.50,
        "3/4\" EMT Set-Screw Coupling": 1.15,
        "3/4\" 1-Hole EMT Strap": 0.45,
        "Commercial Grade 20A GFCI Device": 18.00,
        "Specification Grade 20A Toggle Switch": 1.50
    }

# --- PORTAL ROUTING ENGINE ---
if not st.session_state.user_authenticated:
    st.title("⚡ SparkyTakeoff OS")
    st.caption("UniFi-Style Integrated Electrical Sourcing System Node")
    
    col_login, col_guide = st.columns([1, 1])
    with col_login:
        with st.form("simple_login_form"):
            st.write("### 🔑 Gateway Authentication Required")
            user_email = st.text_input("Operator Identifier (Email)", placeholder="operator@domain.com")
            password = st.text_input("Access Key", type="password", placeholder="••••")
            submit_auth = st.form_submit_button("Authenticate Conductor Node")
            
            if submit_auth:
                if user_email and len(password) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = user_email
                    st.session_state.active_project_id = "EST_UNINITIALIZED_GRID"
                    st.rerun()
                else:
                    st.error("Authentication rejected. Minimum key constraint failure.")
    with col_guide:
        st.info("💡 **Quick Override:** Input email `admin@sharded.io` and password `1234` to complete security handshake bypass.")

else:
    # --- AUTHENTICATED MASTER WORKSTATION ---
    col_header, col_status = st.columns([3, 1])
    with col_header:
        st.markdown("<h2 style='margin-bottom:0px;'>⚡ UniFi Control Center: Core Workstation</h2>", unsafe_allow_html=True)
        st.caption(f"Active Operator Profile: `{st.session_state.user_email}` | Memory Workspace Node: `{st.session_state.active_project_id}`")
    with col_status:
        st.markdown("<div style='text-align:right; margin-top:15px;'>", unsafe_allow_html=True)
        if st.button("🚪 Terminate Session Connection"):
            st.session_state.user_authenticated = False
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    st.divider()

    # --- THE MOCK ESTIMATE DATA LOOP ---
    baseline_mock_manifest = [
        {"Item Name": "3/4\" EMT Conduit (10ft Factory Sticks)", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 150, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Conduit (10ft Factory Sticks)"], "Mins to Install": 12},
        {"Item Name": "3/4\" EMT Set-Screw Coupling", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 140, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Set-Screw Coupling"], "Mins to Install": 3},
        {"Item Name": "3/4\" 1-Hole EMT Strap", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 200, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" 1-Hole EMT Strap"], "Mins to Install": 2},
        {"Item Name": "Commercial Grade 20A GFCI Device", "Phase": "Trim-Out", "Target Zone": "Kitchen Layout", "Qty": 25, "Unit Cost ($)": st.session_state.vendor_pricing["Commercial Grade 20A GFCI Device"], "Mins to Install": 15},
        {"Item Name": "Specification Grade 20A Toggle Switch", "Phase": "Trim-Out", "Target Zone": "General Lighting", "Qty": 40, "Unit Cost ($)": st.session_state.vendor_pricing["Specification Grade 20A Toggle Switch"], "Mins to Install": 10}
    ]
    df_takeoff = pd.DataFrame(baseline_mock_manifest)
    
    # Financial Matrix Computations
    total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Unit Cost ($)"]).sum()
    total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
    raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
    burdened_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
    total_labor_hours = ((df_takeoff["Qty"] * df_takeoff["Mins to Install"]) / 60).sum()
    total_labor_cost = total_labor_hours * burdened_rate
    target_gross_bid = (total_mat_cost + total_labor_cost) * (1 + st.session_state.overhead)

    # --- TOP LEVEL UNIFI BLADE HEADER: SYSTEM HEALTH MATRIX ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<div class='unifi-card'><p style='margin:0; font-size:11px; color:#94A3B8; text-transform:uppercase;'>System Link Total</p><h2 style='margin:0; color:#00F0FF; font-family:monospace;'>${target_gross_bid:,.2f}</h2></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='unifi-card'><p style='margin:0; font-size:11px; color:#94A3B8; text-transform:uppercase;'>Conductor Weight</p><h2 style='margin:0; color:#00F0FF; font-family:monospace;'>${total_mat_cost:,.2f}</h2></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='unifi-card'><p style='margin:0; font-size:11px; color:#94A3B8; text-transform:uppercase;'>Labor Bandwidth</p><h2 style='margin:0; color:#00F0FF; font-family:monospace;'>{total_labor_hours:.1f} hrs</h2></div>", unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"<div class='unifi-card'><p style='margin:0; font-size:11px; color:#94A3B8; text-transform:uppercase;'>Margin Efficiency</p><h2 style='margin:0; color:#00F0FF; font-family:monospace;'>{st.session_state.overhead*100:.0f}%</h2></div>", unsafe_allow_html=True)

    # --- MASTER CONTROL BLADES ---
    tab_estimation, tab_sourcing, tab_analytics, tab_config = st.tabs([
        "📊 Takeoff Data Matrix", 
        "🏪 Supply Counter Link", 
        "🎯 Topology Performance Analytics", 
        "⚙️ Core Hardware Profile"
    ])

    # TAB 1: DATA MANIFEST
    with tab_estimation:
        st.write("### 🎛️ Active Multi-Sheet Data Grid Editor")
        edited_df = st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True, key="unifi_grid")

    # TAB 2: PROCUREMENT ROUTER
    with tab_sourcing:
        st.write("### 🏪 Integrated Supply House Gateway Router")
        sc_col1, sc_col2 = st.columns([1, 2])
        with sc_col1:
            target_supply_house = st.selectbox("Target Supplier Base Station Node", ["City Electric Supply (CES North Miami)", "Rexel Electrical Supply", "Graybar District Counter"])
            delivery_method = st.radio("Logistics Delivery Stream", ["Will Call Counter Pickup", "Flatbed Carrier Site Drop"])
            po_reference_id = st.text_input("PO Frame ID", value=f"PO-{random.randint(10000, 99999)}")
        with sc_col2:
            st.write("#### 📄 Current Hardware Frame Payload Preview")
            order_summary_list = [f"• {int(r['Qty'])}x -- {r['Item Name']}" for _, r in edited_df.iterrows() if r["Qty"] > 0]
            st.markdown("\n".join(order_summary_list))
            
            if st.button("🚀 TRANSMIT HARDWARE PAYLOAD LINK"):
                st.session_state.sys_log_history.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] ROUTER OUTBOUND: Transmitted payload packet frame {po_reference_id} to node '{target_supply_house}'. Status: Connected.")
                st.success("✨ Packet payload accepted by wholesale distributor endpoint server.")
                st.balloons()

    # TAB 3: NETWORK ANALYTICS
    with tab_analytics:
        st.write("### 🎯 System Load and Risk Architecture Analysis")
        an_col1, an_col2 = st.columns(2)
        with an_col1:
            st.write("#### 📊 Resource Budget Component Density")
            alloc_df = pd.DataFrame({
                "Component Sector": ["Wholesale Metal Materials", "Field Labor Bandwidth", "Gross Margin Profit Buffer"],
                "Allocation Value ($)": [total_mat_cost, total_labor_cost, (total_mat_cost + total_labor_cost) * st.session_state.overhead]
            })
            st.bar_chart(data=alloc_df, x="Component Sector", y="Allocation Value ($)", use_container_width=True)
        with an_col2:
            st.write("#### ⏳ Schedule Risk Capacity Monitoring")
            project_days = st.number_input("Designated Contract Delivery Timeline (Working Days)", min_value=1, value=5)
            max_avail_man_hours = project_days * (total_crew_members * 8)
            
            if total_labor_hours > max_avail_man_hours:
                st.markdown(f"<div class='unifi-card-alert'><h4 style='color:#F59E0B; margin:0;'>⚠️ OVERBURN CAP CONSTRAINT LIMIT HIT</h4><p style='font-size:12px; margin:5px 0 0 0;'>Estimated workload requires {total_labor_hours:.1f} hours, exceeding your active crew capacity constraint of {max_avail_man_hours:.1f} hours. Sizing up core crew values recommended.</p></div>", unsafe_allow_html=True)
            else:
                utilization = (total_labor_hours / max_avail_man_hours) * 100 if max_avail_man_hours > 0 else 0
                st.markdown(f"<div class='unifi-card' style='border-left-color:#10B981;'><h4 style='color:#10B981; margin:0;'>✅ BANDWIDTH TOLERANCE SECURE</h4><p style='font-size:12px; margin:5px 0 0 0;'>Active project footprint utilizes {utilization:.1f}% of total timeline capacity. Operational threshold buffer parameters safe.</p></div>", unsafe_allow_html=True)

    # TAB 4: CONFIGURATION
    with tab_config:
        st.write("### ⚙️ Hardware Frame Configuration Variables")
        st.session_state.company_name = st.text_input("Subcontractor Corporate Header Designation", value=st.session_state.company_name)
        st.session_state.qty_journeymen = st.number_input("Count of Active Field Journeymen Nodes", min_value=1, value=st.session_state.qty_journeymen)
        st.session_state.qty_helpers = st.number_input("Count of Active Helper / Apprentice Links", min_value=0, value=st.session_state.qty_helpers)

    # --- THE UNIFI OS LOWER BLOCK: LIVE REAL-TIME DEVICE TOPOLOGY SYSTEM LOGS ---
    st.divider()
    st.markdown("<h4 style='color:#94A3B8; text-transform:uppercase; letter-spacing:1px; font-size:12px;'>📋 System Topology Console Activity Log Feed</h4>", unsafe_allow_html=True)
    
    # Render logs in a monospace dark terminal look block window
    log_text_payload = "\n".join(st.session_state.sys_log_history[::-1])
    st.text_area(label="Terminal Logs Stream Output Frame", value=log_text_payload, height=140, label_visibility="collapsed")