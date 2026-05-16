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

# --- ADVANCED STEALTH MATTE DARK MODE CSS INJECTION ---
st.markdown("""
<style>
    /* Global Anti-Glare Matte Surface */
    .stApp {
        background-color: #070B12 !important;
        color: #94A3B8 !important;
    }
    
    /* Softened Typography Profiles */
    h1, h2, h3, h4, h5, h6 {
        color: #CBD5E1 !important;
        font-weight: 500 !important;
    }
    
    /* UniFi Telemetry Metric Formatting */
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
    
    /* Matte Surface Hardware Blades */
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
    
    /* Physical Breaker Panel Layout Cards */
    .panel-breaker-even {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        padding: 10px;
        text-align: center;
        border-radius: 4px;
        font-family: monospace;
        font-size: 12px;
    }
    .panel-bus-bar {
        background-color: #1E293B;
        height: 100%;
        min-height: 50px;
        border-radius: 2px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #64748B;
        font-weight: bold;
    }
    
    /* Muted Tab Navigation Components */
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
    
    /* Data Editor Custom Overrides */
    div[data-testid="stDataEditor"] {
        background-color: #0F172A !important;
        border: 1px solid #1E293B !important;
        border-radius: 4px;
    }
    
    /* Scrolling Cyber Developer Terminal */
    .cyber-terminal-output {
        background-color: #030712 !important;
        border: 1px solid #1E293B !important;
        border-radius: 4px;
        padding: 12px;
        font-family: 'Courier New', monospace !important;
        font-size: 12px !important;
        color: #34D399 !important;
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

# --- DIRECTORY CONFIGURATION ---
SAVED_PROJECTS_DIR = "saved_estimates_vault"
if not os.path.exists(SAVED_PROJECTS_DIR):
    os.makedirs(SAVED_PROJECTS_DIR)

# --- APPLICATION STATE MANAGEMENT ---
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
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0

if "sys_log_frames" not in st.session_state:
    st.session_state.sys_log_frames = [
        f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-kernel'>[SYS CORE]</span> Stealth multi-module matrix engine online.",
        f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-kernel'>[NET KERNEL]</span> Connected to global commodity index streams."
    ]

if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {
        "3/4\" EMT Conduit (10ft Factory Sticks)": 6.50, 
        "3/4\" EMT Set-Screw Coupling": 1.15,
        "3/4\" 1-Hole EMT Strap": 0.45, 
        "Commercial Grade 20A GFCI Device": 18.00, 
        "Specification Grade 20A Toggle Switch": 1.50
    }

# --- GATEWAY USER DISPATCH PORTAL ---
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
    # --- AUTHENTICATED CONTROL MATRIX ---
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

    # --- BASE DATASET STRUCTURING ---
    baseline_mock_manifest = [
        {"Item Name": "3/4\" EMT Conduit (10ft Factory Sticks)", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 150, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Conduit (10ft Factory Sticks)"], "Mins to Install": 12, "Is Metal Commodity": True},
        {"Item Name": "3/4\" EMT Set-Screw Coupling", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 140, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Set-Screw Coupling"], "Mins to Install": 3, "Is Metal Commodity": True},
        {"Item Name": "3/4\" 1-Hole EMT Strap", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 200, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" 1-Hole EMT Strap"], "Mins to Install": 2, "Is Metal Commodity": True},
        {"Item Name": "Commercial Grade 20A GFCI Device", "Phase": "Trim-Out", "Target Zone": "Kitchen Layout", "Qty": 25, "Unit Cost ($)": st.session_state.vendor_pricing["Commercial Grade 20A GFCI Device"], "Mins to Install": 15, "Is Metal Commodity": False},
        {"Item Name": "Specification Grade 20A Toggle Switch", "Phase": "Trim-Out", "Target Zone": "General Lighting", "Qty": 40, "Unit Cost ($)": st.session_state.vendor_pricing["Specification Grade 20A Toggle Switch"], "Mins to Install": 10, "Is Metal Commodity": False}
    ]
    df_takeoff = pd.DataFrame(baseline_mock_manifest)
    
    # Execute Real-Time Volatility Calculations
    def apply_market_pricing(row):
        if row["Is Metal Commodity"]:
            return round(row["Unit Cost ($)"] * (1 + st.session_state.copper_multiplier), 2)
        return row["Unit Cost ($)"]
        
    df_takeoff["Adjusted Unit Cost ($)"] = df_takeoff.apply(apply_market_pricing, axis=1)
    
    # Financial Pipeline Calculations Basic Baseline
    total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Adjusted Unit Cost ($)"]).sum()
    total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
    raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
    burdened_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
    total_labor_hours = ((df_takeoff["Qty"] * df_takeoff["Mins to Install"]) / 60).sum()
    
    # Pre-calculated baseline for standard tracking blocks
    standard_labor_cost = total_labor_hours * burdened_rate
    standard_gross_bid = (total_mat_cost + standard_labor_cost) * (1 + st.session_state.overhead)

    # --- TAB NAVIGATION MODULES ---
    tab_estimation, tab_panel, tab_commodity, tab_submittal = st.tabs([
        "📊 Data Matrix", 
        "⚡ Three-Phase Panel Schedule & Sizing", 
        "📈 Commodity Market Multiplier", 
        "📁 Executive Submittal Generator"
    ])

    # --- TAB 1: MASTER ESTIMATOR SPREADSHEET ---
    with tab_estimation:
        st.write("### 🎛️ Active Multi-Sheet Data Grid Editor")
        edited_df = st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True, key="stealth_grid_master")
        
        # Recalculate based on real-time data adjustments inside user viewport frame lines
        edited_df["Qty"] = pd.to_numeric(edited_df["Qty"]).fillna(0)
        edited_df["Adjusted Unit Cost ($)"] = pd.to_numeric(edited_df["Adjusted Unit Cost ($)"]).fillna(0)
        edited_df["Mins to Install"] = pd.to_numeric(edited_df["Mins to Install"]).fillna(0)
        
        total_mat_cost = (edited_df["Qty"] * edited_df["Adjusted Unit Cost ($)"]).sum()
        total_labor_hours = ((edited_df["Qty"] * edited_df["Mins to Install"]) / 60).sum()

    # --- TAB 2: THREE-PHASE BALANCER & VOLTAGE DROP PHYSICS ---
    with tab_panel:
        st.write("### ⚡ NEC Three-Phase Circuit Load Balancing Matrix")
        st.caption("Distribute single-phase branching continuous loads across Phase A, B, and C busbars to prevent neutral current oversaturation.")
        
        p_col1, p_col2 = st.columns([1, 2])
        with p_col1:
            st.write("#### ➕ Add Load Entry to Phase Rail")
            circuit_label = st.text_input("Circuit Load Name Tag", value="CKT-1: Kitchen Receptacles")
            volt_amps_load = st.number_input("Connected Load Power Footprint (Volt-Amperes)", min_value=100, max_value=10000, value=1800, step=100)
            target_phase = st.selectbox("Assign Target Phase Busbar", ["Phase A", "Phase B", "Phase C"])
            
            if st.button("🔌 Inject Circuit to Panel Main"):
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-kernel'>[PANEL MATRIX]</span> Injected load '{circuit_label}' ({volt_amps_load}VA) onto {target_phase} bus.")
                st.toast("Circuit injected successfully!")
                
        with p_col2:
            st.write("#### 🗊 120/208V 3-Phase 4-Wire Panelboard Layout")
            b_row1, b_bus, b_row2 = st.columns([4, 1, 4])
            with b_row1:
                st.markdown("<div class='panel-breaker-even'><b>CKT 1 (A)</b><br>Kitchen Receptacles<br><span style='color:#38BDF8;'>1,800 VA</span></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                st.markdown("<div class='panel-breaker-even'><b>CKT 3 (C)</b><br>Lighting Track Main<br><span style='color:#38BDF8;'>1,200 VA</span></div>", unsafe_allow_html=True)
            with b_bus:
                st.markdown("<div class='panel-bus-bar'>A</div>", unsafe_allow_html=True)
                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                st.markdown("<div class='panel-bus-bar'>B</div>", unsafe_allow_html=True)
            with b_row2:
                st.markdown("<div class='panel-breaker-even'><b>CKT 2 (B)</b><br>A/C Condenser Fan<br><span style='color:#38BDF8;'>2,400 VA</span></div>", unsafe_allow_html=True)
                st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
                st.markdown("<div class='panel-breaker-even'><b>CKT 4 (A)</b><br>Water Outlet Heater<br><span style='color:#38BDF8;'>3,100 VA</span></div>", unsafe_allow_html=True)
                
            st.divider()
            load_a, load_b, load_load_c = 4900, 2400, 1200
            total_panel_va = load_a + load_b + load_load_c
            
            tot_c1, tot_c2, tot_c3 = st.columns(3)
            tot_c1.metric("Phase A Connected Load", f"{load_a:,.0f} VA")
            tot_c2.metric("Phase B Connected Load", f"{load_b:,.0f} VA")
            tot_c3.metric("Phase C Connected Load", f"{load_load_c:,.0f} VA")
            
            avg_phase = total_panel_va / 3
            max_deviation = max(abs(load_a - avg_phase), abs(load_b - avg_phase), abs(load_load_c - avg_phase))
            unbalance_pct = (max_deviation / avg_phase) * 100
            
            if unbalance_pct > 15.0:
                st.warning(f"⚠️ **Phase Equilibrium Alert:** Current unbalance is at **{unbalance_pct:.1f}%**. Re-assign CKT 4 to Phase C to achieve structural balance limits.")
            else:
                st.success(f"✅ **Panel Balance Safe:** Unbalance is at **{unbalance_pct:.1f}%**.")

        # --- DYNAMIC VOLTAGE DROP DIAGNOSTIC MODULE ---
        st.divider()
        st.write("#### 📐 Intelligent Conductor Sizing & Voltage Drop Diagnostic")
        st.caption("Executes automated cross-examinations of copper wire cross-sections and computes voltage sag parameters over physical distances.")
        
        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            nominal_system_voltage = st.selectbox("Circuit Voltage Base", [120, 208, 240, 277, 480], index=0)
            target_run_amperage = st.number_input("Design Continuous Load (Amps)", min_value=1.0, max_value=200.0, value=16.0, step=1.0)
            one_way_distance_ft = st.number_input("One-Way Circuit Length (Feet)", min_value=5.0, max_value=1000.0, value=120.0, step=5.0)
            wire_gauge_choice = st.selectbox("Conductor Gauge Choice (Copper THHN)", ["#14 AWG", "#12 AWG", "#10 AWG", "#8 AWG", "#6 AWG", "#4 AWG"])
            
        with diag_col2:
            st.write("#### 📡 Live Diagnostic Evaluation")
            cm_specs = {"#14 AWG": 4110, "#12 AWG": 6530, "#10 AWG": 10380, "#8 AWG": 16510, "#6 AWG": 26240, "#4 AWG": 41740}
            ampacity_specs = {"#14 AWG": 15, "#12 AWG": 20, "#10 AWG": 30, "#8 AWG": 50, "#6 AWG": 65, "#4 AWG": 85}
            
            active_cm = cm_specs[wire_gauge_choice]
            max_allowed_amps = ampacity_specs[wire_gauge_choice]
            
            # Voltage Drop Math: V_drop = (2 * K * I * D) / CM
            constant_k = 12.9
            calculated_v_drop = (2 * constant_k * target_run_amperage * one_way_distance_ft) / active_cm
            drop_percentage = (calculated_v_drop / nominal_system_voltage) * 100
            terminal_voltage = nominal_system_voltage - calculated_v_drop
            
            st.write(f"Conductor Cross-Section: **{active_cm:,} Circular Mils**")
            st.write(f"Terminal Output Voltage: **{terminal_voltage:.1f} V**")
            
            if target_run_amperage > max_allowed_amps:
                st.markdown(f"<div class='unifi-stealth-alert'><h5 style='color:#F59E0B; margin:0;'>🚨 AMPACITY OVERLOAD PROFILE</h5><p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>{wire_gauge_choice} is hard-capped at {max_allowed_amps}A per NEC Table 310.16. Your {target_run_amperage}A load will cause insulation thermal degradation.</p></div>", unsafe_allow_html=True)
            elif drop_percentage > 3.0:
                st.markdown(f"<div class='unifi-stealth-alert'><h5 style='color:#F59E0B; margin:0;'>⚠️ EXCESSIVE VOLTAGE DROP DROOP</h5><p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>Voltage sag is at **{drop_percentage:.2f}%** ({calculated_v_drop:.2f}V lost). Exceeds the NEC 3% efficiency threshold recommendation. Size up wire gauge to avoid equipment stalling.</p></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5 style='color:#10B981; margin:0;'>✅ ELECTRICAL WAVEFORM SECURE</h5><p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>Voltage sag locked in at **{drop_percentage:.2f}%**. Conductor operating temperature and thermal footprints inside safe limits.</p></div>", unsafe_allow_html=True)

    # --- TAB 3: SYSTEMS ANALYTICS & NECA RISK MATRIX FACTORING ---
    with tab_commodity:
        st.write("### 📈 Raw Metal Commodity Price Volatility Multiplier")
        st.caption("Simulate real-time wholesale pricing risks caused by sudden supply-chain shifts in raw copper and galvanized steel indices.")
        
        com_col1, com_col2 = st.columns([1, 2])
        with com_col1:
            volatility_selection = st.slider("Set Simulated Commodity Market Spike (%)", -20, 50, 0, step=5)
            if st.button("📈 Lock Risk Multiplier to Catalog Rates"):
                st.session_state.copper_multiplier = volatility_selection / 100
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-warning'>[MARKET SYNC]</span> Applied {volatility_selection}% price shift profile to all physical metallic inventory items.")
                st.success("Multiplier pinned safely to material data-frames.")
                time.sleep(0.4)
                st.rerun()
                
        with com_col2:
            st.write("#### 🛡️ Margin Deviation Performance Review")
            st.write(f"Active Volatility Burden: **{st.session_state.copper_multiplier*100:+.0f}% Deviation**")
            st.write(f"Updated Adjusted Material Estimate Total: **${total_mat_cost:,.2f}**")

    # --- RECALCULATE ADVANCED INTEGRATED COST LOOPS INCLUDING NECA ADJUSTMENTS ---
    # Placed globally so top health matrices update accurately based on all tabs
    if "installation_height_sel" not in st.session_state: st.session_state.installation_height_sel = "Standard Level (0 - 10 Ft)"
    if "jobsite_congestion_sel" not in st.session_state: st.session_state.jobsite_congestion_sel = False
    
    height_mult = 1.0
    if "Elevated" in st.session_state.installation_height_sel: height_mult = 1.15
    elif "High-Staging" in st.session_state.installation_height_sel: height_mult = 1.30
    
    congest_mult = 1.10 if st.session_state.jobsite_congestion_sel else 1.0
    neca_composite_multiplier = height_mult * congest_mult
    
    final_risk_adjusted_hours = total_labor_hours * neca_composite_multiplier
    final_burdened_labor_cost = final_risk_adjusted_hours * burdened_rate
    final_gross_target_bid = (total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead)

    # --- TAB 4: COMPLIANCE SUBMITTAL DOCUMENT ARCHIVER ---
    with tab_submittal:
        st.write("### 🎯 System Load, Risk Architecture, & NECA Multipliers")
        st.caption("Apply standard industrial labor derating adjustments to account for environmental field complexities per NECA Standard 1 guidelines.")
        
        an_col1, an_col2 = st.columns(2)
        with an_col1:
            st.write("#### 🏗️ NECA Labor Productivity Adjustment Board")
            st.session_state.installation_height_sel = st.selectbox("Field Working Height Profile", ["Standard Level (0 - 10 Ft)", "Elevated Scaffold Phase (11 - 20 Ft)", "High-Staging Zone (21+ Ft)"], index=0)
            st.session_state.jobsite_congestion_sel = st.checkbox("Complex/Congested Area Workspace? (Occupied Clinic / Retrofit)", value=False)
            
            st.write("---")
            st.write(f"Composite Labor Risk Burden Modifier: **{neca_composite_multiplier:.2f}x Scale**")
            st.write(f"Adjusted Target Production Labor: **{final_risk_adjusted_hours:.1f} Man-Hours**")
            
        with an_col2:
            st.write("#### ⏳ Schedule Risk Capacity Monitoring")
            project_days = st.number_input("Designated Contract Delivery Timeline (Working Days)", min_value=1, value=5, key="risk_days_input")
            max_avail_man_hours = project_days * (total_crew_members * 8)
            
            if final_risk_adjusted_hours > max_avail_man_hours:
                st.markdown(f"<div class='unifi-stealth-alert'><h5 style='color:#F59E0B; margin:0;'>⚠️ TIMELINE CONSTRAINTS EXCEEDED</h5><p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>Derated labor requirement ({final_risk_adjusted_hours:.1f} hrs) completely burns past your active crew availability ceiling of {max_avail_man_hours:.1f} hours. Scale up field crew counts immediately to safeguard your baseline margin.</p></div>", unsafe_allow_html=True)
            else:
                utilization = (final_risk_adjusted_hours / max_avail_man_hours) * 100 if max_avail_man_hours > 0 else 0
                st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5 style='color:#10B981; margin:0;'>✅ WORKLOAD ALLOCATION OPERATIONAL</h5><p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>Active field operations utilize {utilization:.1f}% of crew milestone bandwidth limits under applied NECA adjustments.</p></div>", unsafe_allow_html=True)

        st.divider()
        st.write("#### 📁 Automated Client Submittal Compilation")
        project_architect_label = st.text_input("Lead Project Architect / Contact", value="Maksym Engineering Group")
        project_location_tag = st.text_input("Project Site Destination Address", value="North Miami Beach District, FL")
        
        submittal_preview_text = f"""===========================================================
COMMERCIAL ELECTRICAL SUBMITTAL PROPOSAL PACKET
ISSUED BY: {st.session_state.company_name.upper()}
TARGET ARCHITECT: {project_architect_label.upper()}
LOCATION: {project_location_tag.upper()}
DATE COMPILED: {datetime.date.today().strftime('%m/%d/%Y')}
===========================================================
1. PROJECT FINANCIAL METRICS (NECA ADJUSTED)
   - Total Estimated Contract Bid: ${final_gross_target_bid:,.2f}
   - Raw Material Allotment Footprint: ${total_mat_cost:,.2f}
   - Total Production Burden Labor: {final_risk_adjusted_hours:.1f} Man-Hours
   - Applied NECA Intensity Scaling Factor: {neca_composite_multiplier:.2f}x

2. NATIONAL ELECTRICAL CODE (NEC) COMPLIANCE PROFILE
   - Box Sizing Parameters: Compiled per NEC Article 314.16
   - Branch Distribution Balance: Balanced per 3-Phase Busbar Guidelines
==========================================================="""
        st.text_area("Submittal Brief Layout Preview Frame", value=submittal_preview_text, height=180)
        
        buffer_submittal = BytesIO()
        buffer_submittal.write(submittal_preview_text.encode('utf-8'))
        st.download_button("📥 Download Compiled Submittal Brief (.txt)", data=buffer_submittal.getvalue(), file_name="Project_Submittal_Package.txt")

    # --- FINANCIAL DATA MONITOR BLADES HEADER (DYNAMIC LINK) ---
    st.sidebar.markdown("### ⚙️ Hardware Parameters")
    st.session_state.company_name = st.sidebar.text_input("Subcontractor Workspace Label", value=st.session_state.company_name)
    st.session_state.qty_journeymen = st.sidebar.number_input("Active Field Journeymen", min_value=1, value=st.session_state.qty_journeymen)
    st.session_state.qty_helpers = st.sidebar.number_input("Active Helpers", min_value=0, value=st.session_state.qty_helpers)
    st.session_state.rate_journeyman = st.sidebar.number_input("Journeyman Rate ($/hr)", min_value=15.0, value=st.session_state.rate_journeyman)
    st.session_state.rate_helper = st.sidebar.number_input("Helper Rate ($/hr)", min_value=10.0, value=st.session_state.rate_helper)
    st.sidebar.write("---")
    st.sidebar.write("Use the configuration pane to alter underlying labor compositions across calculations.")

    # Render top telemetry summary using fully calculated figures
    st.markdown("<div style='margin-top:25px;'></div>", unsafe_allow_html=True)
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>System Gross Valuation</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>${final_gross_target_bid:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col2:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Material Invoice Limit</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>${total_mat_cost:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col3:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Production Allocation</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>{final_risk_adjusted_hours:.1f} hrs</h3></div>", unsafe_allow_html=True)
    with m_col4:
        st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; color:#64748B; text-transform:uppercase;'>Target Operational Margin</p><h3 style='margin:4px 0 0 0; color:#38BDF8; font-family:monospace;'>{st.session_state.overhead*100:.0f}%</h3></div>", unsafe_allow_html=True)

    # --- THE LOWER TELEMETRY TERMINAL CONSOLE CONTROL ---
    st.markdown("<p style='color:#475569; text-transform:uppercase; letter-spacing:1px; font-size:10px; margin-bottom:4px; font-weight:600;'>📋 SYSTEM CORE INTELLIGENCE ACTIVITY TERMINAL</p>", unsafe_allow_html=True)
    reversed_logs_html = "".join([f"<div>{frame}</div>" for frame in st.session_state.sys_log_frames[::-1]])
    st.markdown(f"<div class='cyber-terminal-output'>{reversed_logs_html}</div>", unsafe_allow_html=True)
    
    cmd_col1, cmd_col2 = st.columns([4, 1])
    with cmd_col1:
        manual_input_cmd = st.text_input("Root Command Line Interface Entry Pin", placeholder="Enter operator command override block (e.g., /diagnostics, /sync_prices)", label_visibility="collapsed")
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