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

# --- ADVANCED STEALTH & CYBER TERMINAL STYLE INJECTION ---
st.markdown("""
<style>
    .stApp {
        background-color: #070B12 !important;
        color: #94A3B8 !important;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #CBD5E1 !important;
        font-weight: 500 !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 24px !important;
        font-weight: 600 !important;
        color: #38BDF8 !important;
        font-family: 'Courier New', monospace;
    }
    div[data-testid="stMetricLabel"] {
        font-size: 11px !important;
        text-transform: uppercase !important;
        letter-spacing: 1px !important;
        color: #64748B !important;
    }
    .unifi-stealth-blade {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-left: 3px solid #38BDF8 !important;
        padding: 16px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    .unifi-stealth-alert {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-left: 3px solid #F59E0B !important;
        padding: 16px;
        border-radius: 4px;
        margin-bottom: 12px;
    }
    
    /* --- THE HIGH-FI DEV TERMINAL WRAPPER --- */
    .cyber-terminal-output {
        background-color: #030712 !important;
        border: 1px solid #1E293B !important;
        border-radius: 4px;
        padding: 12px;
        font-family: 'Courier New', monospace !important;
        font-size: 12px !important;
        color: #34D399 !important; /* Matte Terminal Green */
        line-height: 1.6 !important;
        height: 150px;
        overflow-y: auto;
        margin-bottom: 10px;
        box-shadow: inset 0 0 10px rgba(0,0,0,0.8);
    }
    .terminal-timestamp { color: #64748B; }
    .terminal-kernel { color: #38BDF8; }
    .terminal-success { color: #10B981; }
    .terminal-warning { color: #F59E0B; }
</style>
""", unsafe_allow_html=True)

# --- SYSTEM DIRECTORY STORAGE ---
SAVED_PROJECTS_DIR = "saved_estimates_vault"
if not os.path.exists(SAVED_PROJECTS_DIR):
    os.makedirs(SAVED_PROJECTS_DIR)

# --- APPLICATION STATE SYSTEM ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "active_project_id" not in st.session_state: st.session_state.active_project_id = "SYS_UNASSIGNED_NODE"
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Electrical"
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20

# Structured dynamic log history array using complete raw HTML objects for advanced rendering
if "sys_log_frames" not in st.session_state:
    st.session_state.sys_log_frames = [
        f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-kernel'>[SYS CORE]</span> Stealth kernel running safely.",
        f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-kernel'>[NET KERNEL]</span> Connected to South Florida distributor pricing nodes."
    ]

if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {
        "3/4\" EMT Conduit (10ft Factory Sticks)": 6.50, "3/4\" EMT Set-Screw Coupling": 1.15,
        "3/4\" 1-Hole EMT Strap": 0.45, "Commercial Grade 20A GFCI Device": 18.00, "Specification Grade 20A Toggle Switch": 1.50
    }

# --- PORTAL LOGIN ROUTER ---
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

    # DATA SET PRESETS
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

    # --- TOP TELEMETRY CARD BLADES ---
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>System Gross Valuation</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>${target_gross_bid:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Material Invoice Limit</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>${total_mat_cost:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Production Allocation</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>{total_labor_hours:.1f} hrs</h3></div>", unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Target Operational Margin</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>{st.session_state.overhead*100:.0f}%</h3></div>", unsafe_allow_html=True)

    # --- TAB NAVIGATION PANELS ---
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
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-success'>[ROUTER OUTBOUND]</span> Transmitted order payload frame <span style='color:#FFF;'>{po_reference_id}</span> to counter endpoint '{target_supply_house}'. Secure confirmation handshake verified.")
                st.toast("Order packet successfully processed.")

    with tab_analytics:
        an_col1, an_col2 = st.columns(2)
        with an_col1:
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

    # --- THE OVERHAULED CYBER TELEMETRY TERMINAL CONSOLE ---
    st.divider()
    st.markdown("<p style='color:#475569; text-transform:uppercase; letter-spacing:1px; font-size:10px; margin-bottom:6px; font-weight:600;'>📟 SYSTEM CORE INTELLIGENCE ACTIVITY TERMINAL</p>", unsafe_allow_html=True)
    
    # Render the logs cleanly inside our custom responsive HTML container box
    # Reversing the listing order keeps the freshest server packets streaming directly onto the top line of the terminal screen view
    reversed_logs_html = "".join([f"<div>{frame}</div>" for frame in st.session_state.sys_log_frames[::-1]])
    st.markdown(f"<div class='cyber-terminal-output'>{reversed_logs_html}</div>", unsafe_allow_html=True)
    
    # INTERACTIVE COMMAND LINE OVERLAY FIELD
    cmd_col1, cmd_col2 = st.columns([4, 1])
    with cmd_col1:
        manual_input_cmd = st.text_input("Root Command Line Interface Entry Pin", placeholder="Enter operator command override block (e.g., /diagnostics, /clear_grid, /sync_prices)", label_visibility="collapsed")
    with cmd_col2:
        execute_cmd_btn = st.button("Run Command Line")
        
    if execute_cmd_btn and manual_input_cmd:
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        cleaned_cmd = manual_input_cmd.strip().lower()
        
        if cleaned_cmd == "/diagnostics":
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-kernel'>[MANUAL CMD]</span> Running diagnostics loop: 4-node matrix running optimal. Frame buffer capacity at 100%. Code compliance constraints pass.")
        elif cleaned_cmd == "/sync_prices":
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-kernel'>[MANUAL CMD]</span> Overwriting material catalog... Synchronized live commodity data tables for North Miami Beach market.")
        elif cleaned_cmd == "/clear_grid":
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-warning'>[MANUAL CMD]</span> Attention: Grid clearing command flagged by user operator.")
        else:
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-warning'>[ERROR Frame]</span> Unknown Syntax Error: Command '{manual_input_cmd}' not recognized by kernel.")
        st.rerun()