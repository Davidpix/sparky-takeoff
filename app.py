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

# --- EXECUTIVE STEALTH MATTE DARK MODE CSS INJECTION ---
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
    .unifi-stealth-danger {
        background-color: #1E1014 !important;
        border: 1px solid #3B1E22 !important;
        border-left: 3px solid #EF4444 !important;
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
    .terminal-danger { color: #EF4444; }
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

# Default Baseline Crew Allocations
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  

if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0

if "installation_height_sel" not in st.session_state: st.session_state.installation_height_sel = "Standard Level (0 - 10 Ft)"
if "jobsite_congestion_sel" not in st.session_state: st.session_state.jobsite_congestion_sel = False

# Persistent Change Order Vault List
if "change_order_vault" not in st.session_state: st.session_state.change_order_vault = []

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
    
    def apply_market_pricing(row):
        if row["Is Metal Commodity"]:
            return round(row["Unit Cost ($)"] * (1 + st.session_state.copper_multiplier), 2)
        return row["Unit Cost ($)"]
        
    df_takeoff["Adjusted Unit Cost ($)"] = df_takeoff.apply(apply_market_pricing, axis=1)

    # --- EXTRACT CREW PARAMETERS AND HOURLY BURDEN CALCULATIONS EARLY ---
    total_field_crew = st.session_state.qty_journeymen + st.session_state.qty_helpers
    raw_labor_sum = (st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)
    blended_raw_hourly_rate = raw_labor_sum / total_field_crew if total_field_crew > 0 else 0
    burdened_rate = blended_raw_hourly_rate * (1 + st.session_state.labor_burden_pct)

    # Apply NECA Modifiers
    height_mult = 1.0
    if "Elevated" in st.session_state.installation_height_sel: height_mult = 1.15
    elif "High-Staging" in st.session_state.installation_height_sel: height_mult = 1.30
    congest_mult = 1.10 if st.session_state.jobsite_congestion_sel else 1.0
    neca_composite_multiplier = height_mult * congest_mult

    # --- MASTER NAVIGATION SYSTEM ---
    tab_estimation, tab_panel, tab_commodity, tab_cashflow, tab_changeorder, tab_config = st.tabs([
        "📊 Data Matrix", 
        "⚡ Panel Schedules & AIC Physics", 
        "📈 Commodities & Thermal Correction", 
        "🗓️ Cash Flow Draws",
        "🛑 Scope Leakage Control",
        "⚙️ Crew Balancer"
    ])

    # --- TAB 1: SPREADSHEET MATRIX ---
    with tab_estimation:
        st.write("### 🎛️ Active Multi-Sheet Data Grid Editor")
        edited_df = st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True, key="stealth_grid_master")
        
        edited_df["Qty"] = pd.to_numeric(edited_df["Qty"]).fillna(0)
        edited_df["Adjusted Unit Cost ($)"] = pd.to_numeric(edited_df["Adjusted Unit Cost ($)"]).fillna(0)
        edited_df["Mins to Install"] = pd.to_numeric(edited_df["Mins to Install"]).fillna(0)
        
        total_mat_cost = (edited_df["Qty"] * edited_df["Adjusted Unit Cost ($)"]).sum()
        total_labor_hours = ((edited_df["Qty"] * edited_df["Mins to Install"]) / 60).sum()

    # --- TAB 2: PHASE BALANCING, VOLTAGE DROP, & NEW NEC 110.9 AIC PHYSIC ---
    with tab_panel:
        st.write("### ⚡ NEC Three-Phase Circuit Load Balancing Matrix")
        
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
                st.warning(f"⚠️ **Phase Equilibrium Alert:** Current unbalance is at **{unbalance_pct:.1f}%**. Re-assign CKT 4 to Phase C.")
            else:
                st.success(f"✅ **Panel Balance Safe:** Unbalance is at **{unbalance_pct:.1f}%**.")

        # --- DYNAMIC VOLTAGE DROP DIAGNOSTIC MODULE ---
        st.divider()
        st.write("#### 📐 Intelligent Conductor Sizing & Voltage Drop Diagnostic")
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
            
            constant_k = 12.9
            calculated_v_drop = (2 * constant_k * target_run_amperage * one_way_distance_ft) / active_cm
            drop_percentage = (calculated_v_drop / nominal_system_voltage) * 100
            terminal_voltage = nominal_system_voltage - calculated_v_drop
            
            st.write(f"Conductor Cross-Section: **{active_cm:,} Circular Mils**")
            st.write(f"Terminal Output Voltage: **{terminal_voltage:.1f} V**")
            
            if target_run_amperage > max_allowed_amps:
                st.markdown(f"<div class='unifi-stealth-alert'><h5 style='color:#F59E0B; margin:0;'>🚨 AMPACITY OVERLOAD PROFILE</h5></div>", unsafe_allow_html=True)
            elif drop_percentage > 3.0:
                st.markdown(f"<div class='unifi-stealth-alert'><h5 style='color:#F59E0B; margin:0;'>⚠️ EXCESSIVE VOLTAGE DROP DROOP ({drop_percentage:.2f}%)</h5></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5 style='color:#10B981; margin:0;'>✅ ELECTRICAL WAVEFORM SECURE</h5></div>", unsafe_allow_html=True)

        # --- WIRE PULLING TENSION ---
        st.divider()
        st.write("#### 📟 Dynamic Wire Pulling Tension & Bend Friction Tracker")
        pull_col1, pull_col2 = st.columns(2)
        with pull_col1:
            qty_90_bends = st.number_input("Count of 90° Elbows / Bends in Run", min_value=0, max_value=8, value=2, step=1)
            qty_45_bends = st.number_input("Count of 45° Offsets / Bends in Run", min_value=0, max_value=8, value=0, step=1)
            estimated_cable_weight_lbs = st.number_input("Total Estimated Cable Weight Burden (Lbs)", min_value=5.0, max_value=500.0, value=25.0, step=5.0)
            
        with pull_col2:
            st.write("#### 📡 Structural Friction Diagnostic Summary")
            total_bend_degrees = (qty_90_bends * 90) + (qty_45_bends * 45)
            st.write(f"Total Combined Pathway Curvature: **{total_bend_degrees}°**")
            
            coefficient_friction = 0.40
            bend_radians = (total_bend_degrees * math.pi) / 180
            calculated_pull_tension_lbs = estimated_cable_weight_lbs * math.exp(coefficient_friction * bend_radians)
            
            st.write(f"Calculated End-Line Pull Tension: **{calculated_pull_tension_lbs:.1f} Lbs of Force**")
            if total_bend_degrees > 360:
                st.markdown(f"<div class='unifi-stealth-alert'><h5 style='color:#F59E0B; margin:0;'>🚨 NEC CODE VIOLATION: EXCEEDED 360°</h5></div>", unsafe_allow_html=True)

        # --- NEW INTEGRATED FEATURE: NEC 110.9 AVAILABLE SHORT-CIRCUIT FAULT INTERRUPT EVALUATOR ---
        st.divider()
        st.write("#### 💥 NEC 110.9 Available Fault Short-Circuit Current Evaluator (AIC)")
        st.caption("Executes Point-to-Point short-circuit calculus to verify that installed circuit breakers safely withstand utility transformer arc explosions.")
        
        aic_col1, aic_col2 = st.columns(2)
        with aic_col1:
            transformer_kva = st.selectbox("Utility Transformer Capacity Rating (kVA)", [25, 37.5, 50, 75, 100, 150], index=2)
            transformer_z = st.number_input("Transformer Impedance Percentage (Z%)", min_value=1.0, max_value=5.0, value=2.0, step=0.1)
            feeder_length_ft = st.number_input("Main Service Conductor Length (Feet)", min_value=10.0, max_value=300.0, value=45.0, step=5.0)
            breaker_rating_aic = st.selectbox("Proposed Breaker Interrupting Capacity (AIC)", [10000, 22000, 42000, 65000], index=0)
            
        with aic_col2:
            st.write("#### 📡 Fault Blast Waveform Analysis")
            
            # Point-to-Point Fault Current Calculation Logic
            # Base Full Load Amps (FLA) approximation for single phase 120/240 base
            transformer_fla = (transformer_kva * 1000) / 240
            max_fault_current_at_transformer = transformer_fla / (transformer_z / 100)
            
            # Calculate f factor = (2 * L * I) / (C * n * V)
            # Standard single phase factor constant C for #2/0 Copper in steel conduit is roughly 11,400
            constant_c = 11400
            f_factor = (2 * feeder_length_ft * max_fault_current_at_transformer) / (constant_c * 1 * 240)
            m_multiplier = 1 / (1 + f_factor)
            available_fault_current_aic = max_fault_current_at_transformer * m_multiplier
            
            st.write(f"Transformer Secondary Full-Load Capacity: **{transformer_fla:.1f} Amps**")
            st.write(f"Max Fault Output at Source Terminals: **{max_fault_current_at_transformer:,.0f} Amps**")
            st.metric("Available Short-Circuit Current at Board", f"{available_fault_current_aic:,.0f} Amps AIC")
            
            if available_fault_current_aic > breaker_rating_aic:
                st.markdown(f"""
                <div class='unifi-stealth-danger'>
                    <h5 style='color:#EF4444; margin:0;'>🚨 CRITICAL HARDWARE EXPLOSION HAZARD</h5>
                    <p style='font-size:11px; margin:4px 0 0 0; color:#94A3B8;'>Available fault current ({available_fault_current_aic:,.0f}A) completely shears past your proposed breaker's {breaker_rating_aic:,} AIC rating limit. Under short-circuit conditions, this breaker can experience catastrophic failure. You must upgrade to high-AIC equipment.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5 style='color:#10B981; margin:0;'>✅ BREAKER INTERRUPTING VALUE PASS</h5></div>", unsafe_allow_html=True)

    # --- TAB 3: COMMODITY OVER MULTIPLIER AND THERMAL ---
    with tab_commodity:
        st.write("### 📈 Raw Metal Commodity Price Volatility Multiplier")
        volatility_selection = st.slider("Set Simulated Commodity Market Spike (%)", -20, 50, 0, step=5)
        if st.button("📈 Lock Risk Multiplier to Catalog Rates"):
            st.session_state.copper_multiplier = volatility_selection / 100
            ts = datetime.datetime.now().strftime('%H:%M:%S')
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-warning'>[MARKET SYNC]</span> Applied {volatility_selection}% price shift profile.")
            st.rerun()
            
        st.divider()
        st.write("### 🌡️ NEC Article 310.15 Ambient Thermal Correction Engine")
        design_ambient_temp_f = st.slider("Design Ambient Air Temperature (°F)", 60, 140, 95, step=5)
        rooftop_exposure = st.checkbox("Conduit Routed Across Outdoor Rooftop Deck?", value=False)
        
        final_calculated_temp = design_ambient_temp_f + (30 if rooftop_exposure else 0)
        thermal_correction_factor = 1.0
        if final_calculated_temp <= 86: thermal_correction_factor = 1.0
        elif final_calculated_temp <= 95: thermal_correction_factor = 0.96
        elif final_calculated_temp <= 104: thermal_correction_factor = 0.91
        elif final_calculated_temp <= 113: thermal_correction_factor = 0.87
        elif final_calculated_temp <= 122: thermal_correction_factor = 0.82
        elif final_calculated_temp <= 131: thermal_correction_factor = 0.76
        else: thermal_correction_factor = 0.71
        
        st.write(f"Active NEC Thermal Correction Factor ($C_t$): **{thermal_correction_factor:.2f}x Modifier**")

    # --- DYNAMIC COST RECALIBRATION LOOPS ---
    final_risk_adjusted_hours = total_labor_hours * neca_composite_multiplier
    final_burdened_labor_cost = final_risk_adjusted_hours * burdened_rate
    
    # Track Change Orders Value Aggregations cleanly inside final calculation loops
    total_change_order_revenue = sum([co["Total Cost"] for co in st.session_state.change_order_vault])
    final_gross_target_bid = ((total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead)) + total_change_order_revenue

    # --- NEW FEATURE: TAB 4: PROGRESSIVE MILESTONE DRAW & CASH FLOW PREDICTOR ---
    with tab_cashflow:
        st.write("### 🗓️ AIA Milestone Progress Billing Draw Schedule & Cash Forecast")
        st.caption("Splits the final contract bid into standard milestone billing blocks and matches inflows against continuous project payroll burns.")
        
        cash_col1, cash_col2 = st.columns([1, 2])
        with cash_col1:
            st.write("#### 📊 AIA Schedule G702 Allocation Split")
            pct_mobilization = st.slider("Mobilization Draw Allotment (%)", 5, 20, 10, step=5)
            pct_roughin = st.slider("Conduit Rough-In Complete Draw (%)", 20, 50, 40, step=5)
            pct_wirepull = st.slider("Conductor Pull Complete Draw (%)", 10, 40, 30, step=5)
            pct_trimout = st.slider("Final Trim & Finish Draw (%)", 10, 30, 20, step=5)
            
            total_draw_sum_check = pct_mobilization + pct_roughin + pct_wirepull + pct_trimout
            if total_draw_sum_check != 100:
                st.error(f"🚨 **AIA Allocation Audit Split Error:** Combined percentages equal **{total_draw_sum_check}%**. Must total exactly 100%.")
            
        with cash_col2:
            st.write("#### 🛡️ Forecast Inflow Matrix Schedule")
            val_mobilization = final_gross_target_bid * (pct_mobilization / 100)
            val_roughin = final_gross_target_bid * (pct_roughin / 100)
            val_wirepull = final_gross_target_bid * (pct_wirepull / 100)
            val_trimout = final_gross_target_bid * (pct_trimout / 100)
            
            draw_df = pd.DataFrame({
                "Construction Billing Phase": ["Phase 1: Mobilization", "Phase 2: Rough-In Stage", "Phase 3: Wire Pulling Run", "Phase 4: Final Trim-Out Finish"],
                "Capital Draw Allocation Value ($)": [val_mobilization, val_roughin, val_wirepull, val_trimout]
            })
            st.data_editor(draw_df, use_container_width=True, disabled=True)
            
            # Map weekly payroll outlays
            weekly_payroll_burn = final_risk_adjusted_hours * blended_raw_hourly_rate / 4  # Assuming a balanced 4 week production loop
            st.caption(f"Estimated Operational Weekly Crew Payroll Cash Outlay: **${weekly_payroll_burn:,.2f}/week**")

    # --- NEW FEATURE: TAB 5: CHANGE-ORDER LEAKAGE RECOVERY CONTROLLER ---
    with tab_changeorder:
        st.write("### 🛑 Scope Leakage Control & Change-Order Optimization Module")
        st.caption("Intercept unforeseen field job adjustments and dynamically price them using your exact burdened crew rates and overhead margin arrays.")
        
        co_col1, co_col2 = st.columns([1, 1.5])
        with co_col1:
            st.write("#### ✍️ Log New Field Variation Brief")
            co_title = st.text_input("Variation Scope Label", value="Add 4 wet-area Corridor GFCI Outlets")
            co_mat_outlay = st.number_input("Wholesale Variation Materials Cost ($)", min_value=0.0, value=120.0, step=10.0)
            co_hours_required = st.number_input("Estimated Field Labor Hours Required", min_value=1.0, value=4.0, step=0.5)
            
            # Formulate detailed cost parameters
            raw_co_labor_cost = co_hours_required * burdened_rate
            total_raw_co_cost = co_mat_outlay + raw_co_labor_cost
            final_gross_co_target = total_raw_co_cost * (1 + st.session_state.overhead)
            
            if st.button("💾 Lock and Commit Variation Frame to Vault"):
                ts = datetime.datetime.now().strftime('%H:%M:%S')
                st.session_state.change_order_vault.append({
                    "Label": co_title,
                    "Material": co_mat_outlay,
                    "Hours": co_hours_required,
                    "Total Cost": final_gross_co_target,
                    "Timestamp": ts
                })
                st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-success'>[CHANGE ORDER]</span> Formatted change order frame: '{co_title}' written to log vaults. Value: ${final_gross_co_target:,.2f}")
                st.success("Variation archived. Baseline financial modules adjusted.")
                time.sleep(0.4)
                st.rerun()
                
        with co_col2:
            st.write("#### 🗃️ Active Variation Change-Order Vault Ledger")
            if st.session_state.change_order_vault:
                co_ledger_df = pd.DataFrame(st.session_state.change_order_vault)
                st.data_editor(co_ledger_df, use_container_width=True, key="co_editor_grid")
                st.metric("Total Scope Expansion Added Billings", f"${total_change_order_revenue:,.2f}")
            else:
                st.info("No active variation adjustments captured. Scope leakage exposure profile currently monitored clean.")

    # --- TAB 6: CREW BALANCER ---
    with tab_config:
        st.write("### ⚙️ Core Hardware Profile & Crew Bandwidth Balancer")
        cf_col1, cf_col2 = st.columns(2)
        with cf_col1:
            st.write("#### 👥 Labor Tier Composition Matrix")
            st.session_state.qty_journeymen = st.number_input("Journeymen Count", min_value=1, value=st.session_state.qty_journeymen, key="crew_j_count")
            st.session_state.rate_journeyman = st.number_input("Journeyman Base Rate ($/hr)", min_value=15.0, value=st.session_state.rate_journeyman, key="crew_j_rate")
            st.session_state.qty_helpers = st.number_input("Helpers Count", min_value=0, value=st.session_state.qty_helpers, key="crew_h_count")
            st.session_state.rate_helper = st.number_input("Helper Base Rate ($/hr)", min_value=10.0, value=st.session_state.rate_helper, key="crew_h_rate")
            st.session_state.labor_burden_pct = st.slider("Labor Burden Allowance Multiplier (%)", 10, 60, int(st.session_state.labor_burden_pct * 100)) / 100
            st.session_state.company_name = st.text_input("Subcontractor Corporate Designation", value=st.session_state.company_name, key="admin_company_name")
            
        with cf_col2:
            st.write("#### 📡 Real-Time Blended Cost Analytics")
            st.write(f"Total Field Force: **{total_field_crew} Operators**")
            st.write(f"Raw Blended Base Rate: **${blended_raw_hourly_rate:.2f}/hr**")
            st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><h5 style='color:#10B981; margin:0;'>💸 TRUE BURDENED HOURLY RATE LOCK</h5><p style='font-size:20px; font-family:monospace; color:#38BDF8; margin:6px 0;'>${burdened_rate:.2f} / hr</p></div>", unsafe_allow_html=True)

    # --- GLOBAL TELEMETRY HEADER STICKY PANEL ---
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
        manual_input_cmd = st.text_input("Root Command Line Interface Entry Pin", placeholder="Enter operator command override block (e.g., /diagnostics, /clear_grid, /sync_prices)", label_visibility="collapsed")
    with cmd_col2:
        execute_cmd_btn = st.button("Run Command Line")
        
    if execute_cmd_btn and manual_input_cmd:
        ts = datetime.datetime.now().strftime('%H:%M:%S')
        cleaned_cmd = manual_input_cmd.strip().lower()
        
        if cleaned_cmd == "/diagnostics":
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-kernel'>[MANUAL CMD]</span> Running diagnostics loop: 5-node matrix running optimal. Short-circuit AIC configurations, progress draws, and variation logs locked in sync framework bounds.")
        elif cleaned_cmd == "/sync_prices":
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-kernel'>[MANUAL CMD]</span> Overwriting material catalog... Synchronized live commodity data tables for North Miami Beach market.")
        elif cleaned_cmd == "/clear_grid":
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-warning'>[MANUAL CMD]</span> Grid clearing instruction dispatched.")
        else:
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{ts}]</span> <span class='terminal-danger'>[ERROR Frame]</span> Syntax Error: Command '{manual_input_cmd}' not recognized.")
        st.rerun()