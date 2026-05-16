import streamlit as st
import pandas as pd
import random
import time
import datetime
import json
import os
import math
from io import BytesIO

st.set_page_config(page_title="SparkyTakeoff OS", layout="wide", initial_sidebar_state="expanded")

# --- ACCESSIBILITY & STATE MANAGEMENT ---
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False

# --- DYNAMIC CSS INJECTION (PRO VS ACCESSIBLE) ---
if not st.session_state.accessibility_mode:
    # HARDCORE STEALTH ENGINEERING THEME
    st.markdown("""
    <style>
        .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
        h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
        div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
        div[data-testid="stMetricLabel"] { font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 1px !important; color: #64748B !important; }
        .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
        .unifi-stealth-alert { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
        .unifi-stealth-danger { background-color: #1E1014 !important; border: 1px solid #3B1E22 !important; border-left: 3px solid #EF4444 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
        .panel-breaker-even { background-color: #0F172A; border: 1px solid #1E293B; padding: 10px; text-align: center; border-radius: 4px; font-family: monospace; font-size: 12px; }
        .panel-bus-bar { background-color: #1E293B; height: 100%; min-height: 50px; border-radius: 2px; display: flex; align-items: center; justify-content: center; color: #64748B; font-weight: bold; }
        div[data-testid="stDataEditor"] { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-radius: 4px; }
        .cyber-terminal-output { background-color: #030712 !important; border: 1px solid #1E293B !important; border-radius: 4px; padding: 12px; font-family: 'Courier New', monospace !important; font-size: 12px !important; color: #34D399 !important; line-height: 1.6 !important; height: 150px; overflow-y: auto; margin-bottom: 10px; box-shadow: inset 0 0 10px rgba(0,0,0,0.8); }
        .terminal-timestamp { color: #64748B; } .terminal-kernel { color: #38BDF8; } .terminal-success { color: #10B981; } .terminal-warning { color: #F59E0B; } .terminal-danger { color: #EF4444; }
    </style>
    """, unsafe_allow_html=True)
else:
    # CLEAN, HIGH-CONTRAST ACCESSIBILITY THEME
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC !important; color: #1E293B !important; font-size: 18px !important; }
        h1, h2, h3, h4, h5, h6 { color: #0F172A !important; font-weight: 700 !important; }
        div[data-testid="stMetricValue"] { font-size: 28px !important; font-weight: 800 !important; color: #0284C7 !important; }
        div[data-testid="stMetricLabel"] { font-size: 14px !important; font-weight: 600 !important; color: #475569 !important; }
        .unifi-stealth-blade { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-left: 5px solid #0284C7 !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .unifi-stealth-alert { background-color: #FFFBEB !important; border: 1px solid #FEF3C7 !important; border-left: 5px solid #D97706 !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); color: #92400E !important; }
        .unifi-stealth-danger { background-color: #FEF2F2 !important; border: 1px solid #FEE2E2 !important; border-left: 5px solid #DC2626 !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); color: #991B1B !important; }
        .panel-breaker-even { background-color: #F1F5F9; border: 1px solid #CBD5E1; padding: 12px; text-align: center; border-radius: 6px; font-weight: bold; font-size: 14px; color: #0F172A; }
        .panel-bus-bar { background-color: #94A3B8; height: 100%; min-height: 50px; border-radius: 4px; display: flex; align-items: center; justify-content: center; color: #FFFFFF; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- DIRECTORY & STATE CONFIG ---
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
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0
if "installation_height_sel" not in st.session_state: st.session_state.installation_height_sel = "Standard Level (0 - 10 Ft)"
if "jobsite_congestion_sel" not in st.session_state: st.session_state.jobsite_congestion_sel = False
if "change_order_vault" not in st.session_state: st.session_state.change_order_vault = []
if "sys_log_frames" not in st.session_state:
    st.session_state.sys_log_frames = [f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-kernel'>[SYS CORE]</span> System initialized."]
if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {"3/4\" EMT Conduit": 6.50, "3/4\" EMT Coupling": 1.15, "3/4\" 1-Hole Strap": 0.45, "20A GFCI Device": 18.00, "20A Toggle Switch": 1.50}

# --- GATEWAY LOGIN ---
if not st.session_state.user_authenticated:
    st.title("⚡ SparkyTakeoff OS")
    with st.form("simple_login_form"):
        user_email = st.text_input("Email", placeholder="admin@sharded.io")
        password = st.text_input("Password", type="password", placeholder="1234")
        if st.form_submit_button("Login"):
            if user_email and len(password) >= 4:
                st.session_state.user_authenticated = True; st.session_state.user_email = user_email; st.rerun()

else:
    # --- DYNAMIC DATA & MATH ENGINE ---
    df_takeoff = pd.DataFrame([
        {"Item": "3/4\" EMT Conduit", "Qty": 150, "Cost": 6.50, "Mins": 12, "Metal": True},
        {"Item": "3/4\" EMT Coupling", "Qty": 140, "Cost": 1.15, "Mins": 3, "Metal": True},
        {"Item": "20A GFCI Device", "Qty": 25, "Cost": 18.00, "Mins": 15, "Metal": False}
    ])
    df_takeoff["Cost"] = df_takeoff.apply(lambda r: round(r["Cost"] * (1 + st.session_state.copper_multiplier), 2) if r["Metal"] else r["Cost"], axis=1)
    
    total_field_crew = st.session_state.qty_journeymen + st.session_state.qty_helpers
    raw_labor_sum = (st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)
    burdened_rate = (raw_labor_sum / total_field_crew if total_field_crew > 0 else 0) * (1 + st.session_state.labor_burden_pct)

    height_mult = 1.15 if "Elevated" in st.session_state.installation_height_sel else (1.30 if "High" in st.session_state.installation_height_sel else 1.0)
    neca_multiplier = height_mult * (1.10 if st.session_state.jobsite_congestion_sel else 1.0)

    total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Cost"]).sum()
    total_labor_hours = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum()
    final_risk_adjusted_hours = total_labor_hours * neca_multiplier
    final_burdened_labor_cost = final_risk_adjusted_hours * burdened_rate
    total_change_order_revenue = sum([co["Total Cost"] for co in st.session_state.change_order_vault])
    final_gross_target_bid = ((total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead)) + total_change_order_revenue

    # --- THE NEW UNIFIED SIDEBAR NAVIGATION ---
    st.sidebar.title("🧭 Navigation Menu")
    st.session_state.accessibility_mode = st.sidebar.toggle("🟢 Plain-English / Easy Mode", value=st.session_state.accessibility_mode)
    st.sidebar.divider()
    
    # Adapt Menu Names based on mode
    if st.session_state.accessibility_mode:
        menu_options = [
            "1. Project Material List", 
            "2. Safety & Power Checks", 
            "3. Market Risk & Weather", 
            "4. Payment Schedule",
            "5. Extra Work Tracking",
            "6. Executive Summary",
            "7. Crew Cost Settings"
        ]
    else:
        menu_options = [
            "📊 Takeoff Data Matrix", 
            "⚡ Panel Balancing & AIC Physics", 
            "📈 Commodities & Thermal Limits", 
            "🗓️ AIA Cash Flow Forecast",
            "🛑 Scope Leakage / Change Orders",
            "💼 C-Suite War Room & EVM",
            "⚙️ Crew Architecture & Balancer"
        ]
    
    selected_page = st.sidebar.radio("Select Dashboard View:", menu_options)
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user_authenticated = False; st.rerun()

    # --- GLOBAL HEADER METRICS (Adapts to Plain English) ---
    title_gross = "Total Project Price" if st.session_state.accessibility_mode else "System Gross Valuation"
    title_mat = "Material Costs" if st.session_state.accessibility_mode else "Material Invoice Limit"
    title_lab = "Total Labor Hours" if st.session_state.accessibility_mode else "Production Allocation"
    title_marg = "Profit Margin" if st.session_state.accessibility_mode else "Target Operational Margin"

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:11px; text-transform:uppercase;'>{title_gross}</p><h3 style='margin:4px 0 0 0;'>${final_gross_target_bid:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:11px; text-transform:uppercase;'>{title_mat}</p><h3 style='margin:4px 0 0 0;'>${total_mat_cost:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col3: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:11px; text-transform:uppercase;'>{title_lab}</p><h3 style='margin:4px 0 0 0;'>{final_risk_adjusted_hours:.1f} hrs</h3></div>", unsafe_allow_html=True)
    with m_col4: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:11px; text-transform:uppercase;'>{title_marg}</p><h3 style='margin:4px 0 0 0;'>{st.session_state.overhead*100:.0f}%</h3></div>", unsafe_allow_html=True)

    st.divider()

    # --- ROUTING ENGINE ---
    if "Matrix" in selected_page or "Material" in selected_page:
        st.write("### 🎛️ Material Database & Quantities")
        if st.session_state.accessibility_mode: st.info("Review and edit the exact materials needed for this job. Costs automatically update based on your changes.")
        st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True)

    elif "Physics" in selected_page or "Safety" in selected_page:
        if st.session_state.accessibility_mode:
            st.write("### 🛡️ Electrical Safety & Power Checks")
            st.info("This section ensures the electrical design is safe, won't cause fires, and passes city inspections.")
        else:
            st.write("### ⚡ NEC Engineering Physics & Code Compliance")

        st.write("#### 1. Power Panel Balance Check")
        p_col1, p_col2 = st.columns([1, 2])
        with p_col1:
            if st.session_state.accessibility_mode: st.caption("If too much power is on one side of a breaker box, wires can overheat. This tool balances the power.")
            circuit_label = st.text_input("Appliance Name", value="Kitchen Outlets")
            volt_amps_load = st.number_input("Power Required (Watts/VA)", value=1800, step=100)
            st.selectbox("Assign to Phase", ["Phase A", "Phase B", "Phase C"])
        with p_col2:
            st.success("✅ Power is evenly distributed across the panel. Safe to install.")

        st.divider()
        st.write("#### 2. Wire Safety & Fire Prevention" if st.session_state.accessibility_mode else "#### 2. Conductor Ampacity & Voltage Drop")
        if st.session_state.accessibility_mode: st.caption("If a wire is too long or too thin, it loses power and gets hot. We calculate the exact wire thickness you need.")
        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            target_run_amperage = st.number_input("Expected Power Load (Amps)", min_value=1.0, value=16.0)
            one_way_distance_ft = st.number_input("Wire Length (Feet)", min_value=5.0, value=120.0)
            wire_gauge_choice = st.selectbox("Wire Thickness Size", ["#14 AWG (Thinnest)", "#12 AWG", "#10 AWG", "#8 AWG (Thickest)"])
        with diag_col2:
            if "#14" in wire_gauge_choice and target_run_amperage > 15:
                st.markdown("<div class='unifi-stealth-danger'><h5>🚨 FIRE HAZARD: WIRE TOO THIN</h5><p>This wire will melt under 16 Amps. Upgrade to #12 AWG immediately.</p></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='unifi-stealth-blade'><h5>✅ WIRE SIZE IS SAFE</h5><p>No risk of overheating or power loss.</p></div>", unsafe_allow_html=True)

        st.divider()
        st.write("#### 3. Main Breaker Explosion Check" if st.session_state.accessibility_mode else "#### 3. NEC 110.9 Fault Current (AIC)")
        if st.session_state.accessibility_mode: st.caption("If a major power surge hits from the city utility line, standard breakers can explode. This checks if we need heavy-duty commercial breakers.")
        aic_col1, aic_col2 = st.columns(2)
        with aic_col1:
            transformer_kva = st.selectbox("City Transformer Size", [25, 50, 100, 150], index=2)
            breaker_rating_aic = st.selectbox("Your Breaker Strength", [10000, 22000, 65000], index=0)
        with aic_col2:
            if breaker_rating_aic == 10000 and transformer_kva >= 100:
                st.markdown("<div class='unifi-stealth-danger'><h5>🚨 CRITICAL: BREAKER WILL FAIL</h5><p>The city transformer is too powerful for standard breakers. Upgrade to 22,000 rating.</p></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='unifi-stealth-blade'><h5>✅ BREAKER STRENGTH APPROVED</h5></div>", unsafe_allow_html=True)

    elif "Market" in selected_page or "Commods" in selected_page:
        st.write("### 📈 Market Risk & Weather Constraints" if st.session_state.accessibility_mode else "### 📈 Commodity & Thermal Constraints")
        if st.session_state.accessibility_mode: st.info("Copper prices change daily, and extreme heat affects how much power wires can hold. Adjust parameters here to protect your budget.")
        
        st.write("#### 1. Copper Price Fluctuation")
        volatility_selection = st.slider("Simulate Copper Price Jump (%)", -20, 50, 0, step=5)
        if st.button("Apply New Price to Estimate"):
            st.session_state.copper_multiplier = volatility_selection / 100; st.rerun()
            
        st.divider()
        st.write("#### 2. Rooftop Heat Degradation" if st.session_state.accessibility_mode else "#### 2. Ambient Thermal Correction (NEC 310.15)")
        rooftop_exposure = st.checkbox("Are wires being installed on a hot outdoor roof?", value=False)
        if rooftop_exposure:
            st.markdown("<div class='unifi-stealth-alert'><h5>⚠️ EXTREME HEAT DETECTED</h5><p>Rooftops trap heat. The wire's capacity to carry power has been reduced by 24% for safety. We may need to buy thicker wire.</p></div>", unsafe_allow_html=True)

    elif "Draws" in selected_page or "Payment" in selected_page:
        st.write("### 🗓️ Payment Schedule & Cash Flow" if st.session_state.accessibility_mode else "### 🗓️ AIA Progress Billing Draw Schedule")
        if st.session_state.accessibility_mode: st.info("Construction takes time. This schedule breaks down exactly when you will get paid by the client to ensure you can cover weekly payroll.")
        pct_mobilization = st.slider("Upfront Deposit (%)", 5, 20, 10, step=5)
        pct_roughin = st.slider("Payment after placing pipes (%)", 20, 50, 40, step=5)
        pct_wirepull = st.slider("Payment after pulling wires (%)", 10, 40, 30, step=5)
        pct_trimout = st.slider("Final payment when finished (%)", 10, 30, 20, step=5)
        
        draw_df = pd.DataFrame({
            "Construction Phase": ["1: Upfront Deposit", "2: In-Wall Pipes Done", "3: Wires Installed", "4: Final Sign-off"],
            "Amount You Receive ($)": [final_gross_target_bid*(pct_mobilization/100), final_gross_target_bid*(pct_roughin/100), final_gross_target_bid*(pct_wirepull/100), final_gross_target_bid*(pct_trimout/100)]
        })
        st.data_editor(draw_df, use_container_width=True, disabled=True)

    elif "Leakage" in selected_page or "Extra" in selected_page:
        st.write("### 🛑 Extra Work Tracking (Change Orders)")
        if st.session_state.accessibility_mode: st.info("Clients often ask for extra work not in the original plan. Log those requests here to ensure you get paid for the extra labor and materials.")
        co_title = st.text_input("What extra work was requested?", value="Add 4 extra outlets in hallway")
        co_mat_outlay = st.number_input("Cost of extra materials ($)", value=120.0)
        co_hours_required = st.number_input("Extra labor hours needed", value=4.0)
        if st.button("Save Extra Work to Bill"):
            st.session_state.change_order_vault.append({"Label": co_title, "Total Cost": (co_mat_outlay + (co_hours_required * burdened_rate)) * (1 + st.session_state.overhead)})
            st.rerun()
        if st.session_state.change_order_vault:
            st.data_editor(pd.DataFrame(st.session_state.change_order_vault), use_container_width=True)

    elif "C-Suite" in selected_page or "Executive" in selected_page:
        st.write("### 💼 Executive Summary")
        if st.session_state.accessibility_mode: st.info("A high-level view for business owners to see if this project is losing money, and how much future work is in the pipeline.")
        evm_col1, evm_col2 = st.columns(2)
        with evm_col1:
            st.write("#### Project Health Tracker")
            actual_cost_to_date = st.number_input("Money spent so far ($)", value=float(final_gross_target_bid * 0.40))
            planned_pct = st.slider("Where we SHOULD be (%)", 0, 100, 50)
            actual_pct = st.slider("Where we ACTUALLY are (%)", 0, 100, 45)
        with evm_col2:
            st.write("#### Financial Warning System")
            earned = final_gross_target_bid * (actual_pct/100)
            cpi = earned / actual_cost_to_date if actual_cost_to_date else 1
            if cpi < 1.0:
                st.markdown(f"<div class='unifi-stealth-danger'><h5>📉 BLEEDING CASH</h5><p>You are spending money faster than you are completing the work. You are projected to lose your profit margin.</p></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='unifi-stealth-blade'><h5>✅ PROFIT ON TRACK</h5></div>", unsafe_allow_html=True)

    elif "Crew" in selected_page:
        st.write("### ⚙️ Crew Cost Settings")
        if st.session_state.accessibility_mode: st.info("Calculate exactly how much an hour of labor costs your company, including taxes, insurance, and base pay.")
        cf_col1, cf_col2 = st.columns(2)
        with cf_col1:
            st.session_state.qty_journeymen = st.number_input("Number of Expert Workers", value=st.session_state.qty_journeymen)
            st.session_state.rate_journeyman = st.number_input("Expert Base Pay ($/hr)", value=st.session_state.rate_journeyman)
            st.session_state.qty_helpers = st.number_input("Number of Helpers", value=st.session_state.qty_helpers)
            st.session_state.rate_helper = st.number_input("Helper Base Pay ($/hr)", value=st.session_state.rate_helper)
            st.session_state.labor_burden_pct = st.slider("Taxes & Insurance Burden (%)", 10, 60, int(st.session_state.labor_burden_pct*100)) / 100
        with cf_col2:
            st.write("#### True Company Cost")
            st.markdown(f"<div class='unifi-stealth-blade'><h5 style='color:#10B981;'>💸 TRUE COST PER HOUR</h5><p style='font-size:24px;'>${burdened_rate:.2f} / hr</p><p>This is what you must charge just to break even on labor.</p></div>", unsafe_allow_html=True)

    # --- FOOTER TERMINAL (HIDDEN IN ACCESSIBLE MODE) ---
    if not st.session_state.accessibility_mode:
        st.divider()
        st.markdown("<p style='color:#475569; font-size:10px; font-weight:600;'>📋 SYSTEM CORE TERMINAL</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='cyber-terminal-output'>{''.join([f'<div>{f}</div>' for f in st.session_state.sys_log_frames[::-1]])}</div>", unsafe_allow_html=True)
        manual_input_cmd = st.text_input("Root Command", placeholder="/diagnostics", label_visibility="collapsed")
        if st.button("Run Command") and manual_input_cmd:
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-success'>[CMD EXECUTED]</span> {manual_input_cmd} applied.")
            st.rerun()