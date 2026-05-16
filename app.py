import streamlit as st
import pandas as pd
import random
import time
import datetime
import json
import os
import math
import altair as alt
from io import BytesIO

st.set_page_config(page_title="SparkyTakeoff OS", layout="wide", initial_sidebar_state="expanded")

# --- ACCESSIBILITY & STATE MANAGEMENT ---
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False

# --- DYNAMIC CSS INJECTION (PRO VS ACCESSIBLE) ---
if not st.session_state.accessibility_mode:
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
if "sys_log_frames" not in st.session_state: st.session_state.sys_log_frames = [f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-kernel'>[SYS CORE]</span> System initialized."]
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
                st.session_state.user_authenticated = True; st.rerun()

else:
    # --- DYNAMIC DATA & MATH ENGINE ---
    df_takeoff = pd.DataFrame([
        {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 150, "Cost": 6.50, "Mins": 12, "Metal": True},
        {"Item": "3/4\" EMT Coupling", "Phase": "Rough-In", "Qty": 140, "Cost": 1.15, "Mins": 3, "Metal": True},
        {"Item": "3/4\" 1-Hole Strap", "Phase": "Rough-In", "Qty": 200, "Cost": 0.45, "Mins": 2, "Metal": True},
        {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 25, "Cost": 18.00, "Mins": 15, "Metal": False},
        {"Item": "20A Toggle Switch", "Phase": "Trim", "Qty": 40, "Cost": 1.50, "Mins": 10, "Metal": False}
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
    
    if st.session_state.accessibility_mode:
        menu_options = [
            "🏠 1. Home Dashboard",
            "📋 2. Project Material List", 
            "🛡️ 3. Safety & Power Checks", 
            "🌡️ 4. Market Risk & Weather", 
            "🗓️ 5. Payment Schedule",
            "🛑 6. Extra Work Tracking",
            "💼 7. Executive Summary",
            "⚙️ 8. Crew Cost Settings"
        ]
    else:
        menu_options = [
            "🏠 Command Dashboard",
            "📊 Takeoff Data Matrix", 
            "⚡ Engineering & Code Physics", 
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

    # --- GLOBAL HEADER METRICS ---
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
    if "Home" in selected_page or "Command" in selected_page:
        st.write("### 🏠 Project Command Center" if st.session_state.accessibility_mode else "### 🏠 Master Command Dashboard")
        
        home_col1, home_col2 = st.columns([1.5, 1])
        with home_col1:
            st.write("#### 📅 Automated Construction Gantt Schedule")
            crew_daily_capacity = total_field_crew * 8
            rough_in_hours = ((df_takeoff[df_takeoff['Phase'] == 'Rough-In']["Qty"] * df_takeoff[df_takeoff['Phase'] == 'Rough-In']["Mins"]) / 60).sum() * neca_multiplier
            trim_hours = ((df_takeoff[df_takeoff['Phase'] == 'Trim']["Qty"] * df_takeoff[df_takeoff['Phase'] == 'Trim']["Mins"]) / 60).sum() * neca_multiplier
            
            rough_in_days = math.ceil(rough_in_hours / crew_daily_capacity) if crew_daily_capacity > 0 else 1
            trim_days = math.ceil(trim_hours / crew_daily_capacity) if crew_daily_capacity > 0 else 1
            
            start_date = datetime.date.today() + datetime.timedelta(days=7)
            rough_in_end = start_date + datetime.timedelta(days=rough_in_days)
            trim_start = rough_in_end + datetime.timedelta(days=2)
            trim_end = trim_start + datetime.timedelta(days=trim_days)
            
            gantt_data = pd.DataFrame([
                {"Task": "Phase 1: Rough-In (Pipes/Wires)", "Start": start_date, "End": rough_in_end, "Duration": rough_in_days},
                {"Task": "Phase 2: Trim-Out (Devices)", "Start": trim_start, "End": trim_end, "Duration": trim_days}
            ])
            
            chart = alt.Chart(gantt_data).mark_bar(cornerRadius=4, height=30).encode(
                x=alt.X('Start:T', title='Timeline', axis=alt.Axis(format='%b %d', grid=True, gridColor="#1E293B" if not st.session_state.accessibility_mode else "#E2E8F0")),
                x2='End:T',
                y=alt.Y('Task:N', title='', sort=None, axis=alt.Axis(labelColor="#94A3B8" if not st.session_state.accessibility_mode else "#1E293B", labelFontSize=12)),
                color=alt.Color('Task:N', legend=None, scale=alt.Scale(range=["#38BDF8", "#10B981"])),
                tooltip=[alt.Tooltip('Task:N'), alt.Tooltip('Start:T', format='%b %d'), alt.Tooltip('End:T', format='%b %d'), alt.Tooltip('Duration:Q', title='Work Days')]
            ).properties(height=180).configure_view(strokeWidth=0).configure_axis(domain=False)
            st.altair_chart(chart, use_container_width=True)
            
        with home_col2:
            st.write("#### 🚨 Central Alert Scanner")
            if final_risk_adjusted_hours > (10 * crew_daily_capacity): 
                st.markdown("<div class='unifi-stealth-alert' style='padding:10px; margin-bottom:8px;'><b>⚠️ Schedule Warning:</b> High labor hours. Consider expanding crew.</div>", unsafe_allow_html=True)
            if st.session_state.copper_multiplier > 0:
                st.markdown(f"<div class='unifi-stealth-alert' style='padding:10px; margin-bottom:8px;'><b>📈 Market Alert:</b> Copper materials marked up by {st.session_state.copper_multiplier*100:.0f}%.</div>", unsafe_allow_html=True)
            if len(st.session_state.change_order_vault) > 0:
                st.markdown(f"<div class='unifi-stealth-blade' style='padding:10px; border-left-color:#10B981; margin-bottom:8px;'><b>✅ Active Adjustments:</b> {len(st.session_state.change_order_vault)} Change Orders billed.</div>", unsafe_allow_html=True)
            if final_risk_adjusted_hours <= (10 * crew_daily_capacity) and st.session_state.copper_multiplier == 0:
                st.markdown("<div class='unifi-stealth-blade' style='padding:10px; border-left-color:#10B981;'><b>✅ System Optimal:</b> All physics and financial parameters are within safe bounds.</div>", unsafe_allow_html=True)

    elif "Matrix" in selected_page or "Material" in selected_page:
        st.write("### 🎛️ Material Database & Quantities")
        st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True)

    elif "Physics" in selected_page or "Safety" in selected_page or "Engineering" in selected_page:
        st.write("### 🛡️ Electrical Safety & Power Checks" if st.session_state.accessibility_mode else "### ⚡ NEC Engineering Physics & Code Compliance")

        st.write("#### 1. Power Panel Balance Check")
        p_col1, p_col2 = st.columns([1, 2])
        with p_col1:
            circuit_label = st.text_input("Appliance Name", value="Kitchen Outlets")
            volt_amps_load = st.number_input("Power Required (Watts/VA)", value=1800, step=100)
            st.selectbox("Assign to Phase", ["Phase A", "Phase B", "Phase C"])
        with p_col2:
            st.success("✅ Power is evenly distributed across the panel. Safe to install.")

        st.divider()
        st.write("#### 2. Wire Safety & Fire Prevention" if st.session_state.accessibility_mode else "#### 2. Conductor Ampacity & Voltage Drop")
        diag_col1, diag_col2 = st.columns(2)
        with diag_col1:
            target_run_amperage = st.number_input("Expected Power Load (Amps)", min_value=1.0, value=16.0)
            one_way_distance_ft = st.number_input("Wire Length (Feet)", min_value=5.0, value=120.0)
            wire_gauge_choice = st.selectbox("Wire Thickness Size", ["#14 AWG (Thinnest)", "#12 AWG", "#10 AWG", "#8 AWG (Thickest)"])
        with diag_col2:
            if "#14" in wire_gauge_choice and target_run_amperage > 15:
                st.markdown("<div class='unifi-stealth-danger'><h5>🚨 FIRE HAZARD: WIRE TOO THIN</h5><p>This wire will melt under your current load. Upgrade to #12 AWG immediately.</p></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='unifi-stealth-blade'><h5>✅ WIRE SIZE IS SAFE</h5></div>", unsafe_allow_html=True)

        # --- NEW PILLAR: CONDUIT FILL OPTIMIZER ---
        st.divider()
        st.write("#### 3. Pipe Size Calculator" if st.session_state.accessibility_mode else "#### 3. NEC Conduit Fill & Raceway Optimizer (Chapter 9)")
        if st.session_state.accessibility_mode: st.caption("Ensures we buy the right size pipe so the wires actually fit without getting jammed.")
        
        fill_col1, fill_col2 = st.columns(2)
        with fill_col1:
            st.write("**Build Your Wire Bundle:**")
            qty_12 = st.number_input("Count of #12 AWG Wires", min_value=0, value=4, step=1)
            qty_10 = st.number_input("Count of #10 AWG Wires", min_value=0, value=1, step=1)
            qty_8 = st.number_input("Count of #8 AWG Wires", min_value=0, value=0, step=1)
        
        with fill_col2:
            # Wire Area (sq in) THHN
            area_12 = 0.0133
            area_10 = 0.0211
            area_8 = 0.0366
            
            total_bundle_area = (qty_12 * area_12) + (qty_10 * area_10) + (qty_8 * area_8)
            total_wires = qty_12 + qty_10 + qty_8
            
            # EMT 40% Fill Capacities (sq in)
            emt_caps = {
                "1/2\" EMT": 0.122,
                "3/4\" EMT": 0.213,
                "1\" EMT": 0.346,
                "1-1/4\" EMT": 0.598
            }
            
            recommended_pipe = "Exceeds standard limits"
            for pipe_size, cap in emt_caps.items():
                if total_bundle_area <= cap:
                    recommended_pipe = pipe_size
                    break
            
            st.write(f"Total Wires in Pipe: **{total_wires}**")
            st.write(f"Bundle Cross-Sectional Area: **{total_bundle_area:.4f} sq. in.**")
            
            if total_wires > 0:
                st.markdown(f"""
                <div class='unifi-stealth-blade' style='border-left-color: #38BDF8;'>
                    <h5 style='color:#38BDF8; margin:0;'>🛠️ MINIMUM PIPE REQUIRED</h5>
                    <p style='font-size:24px; font-weight:bold; margin:4px 0;'>{recommended_pipe}</p>
                    <p style='font-size:11px; margin:0;'>Complies with NEC 40% maximum fill capacity limits.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.info("Add wires to calculate required pipe size.")

        st.divider()
        st.write("#### 4. Main Breaker Explosion Check" if st.session_state.accessibility_mode else "#### 4. NEC 110.9 Fault Current (AIC)")
        aic_col1, aic_col2 = st.columns(2)
        with aic_col1:
            transformer_kva = st.selectbox("City Transformer Size", [25, 50, 100, 150], index=2)
            breaker_rating_aic = st.selectbox("Your Breaker Strength", [10000, 22000, 65000], index=0)
        with aic_col2:
            if breaker_rating_aic == 10000 and transformer_kva >= 100:
                st.markdown("<div class='unifi-stealth-danger'><h5>🚨 CRITICAL: BREAKER WILL FAIL</h5><p>Upgrade to 22,000 AIC rating.</p></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='unifi-stealth-blade'><h5>✅ BREAKER STRENGTH APPROVED</h5></div>", unsafe_allow_html=True)

    elif "Market" in selected_page or "Commods" in selected_page:
        st.write("### 📈 Market Risk & Weather Constraints" if st.session_state.accessibility_mode else "### 📈 Commodity & Thermal Constraints")
        st.write("#### 1. Copper Price Fluctuation")
        volatility_selection = st.slider("Simulate Copper Price Jump (%)", -20, 50, 0, step=5)
        if st.button("Apply New Price to Estimate"):
            st.session_state.copper_multiplier = volatility_selection / 100; st.rerun()

    elif "Draws" in selected_page or "Payment" in selected_page:
        st.write("### 🗓️ Payment Schedule & Cash Flow" if st.session_state.accessibility_mode else "### 🗓️ AIA Progress Billing Draw Schedule")
        pct_mobilization = st.slider("Upfront Deposit (%)", 5, 20, 10, step=5)
        pct_roughin = st.slider("Payment after placing pipes (%)", 20, 50, 40, step=5)
        pct_wirepull = st.slider("Payment after pulling wires (%)", 10, 40, 30, step=5)
        pct_trimout = st.slider("Final payment when finished (%)", 10, 30, 20, step=5)
        
        draw_df = pd.DataFrame({
            "Construction Phase": ["1: Upfront", "2: Rough-In", "3: Wire Pull", "4: Final Sign-off"],
            "Amount You Receive ($)": [final_gross_target_bid*(pct_mobilization/100), final_gross_target_bid*(pct_roughin/100), final_gross_target_bid*(pct_wirepull/100), final_gross_target_bid*(pct_trimout/100)]
        })
        st.data_editor(draw_df, use_container_width=True, disabled=True)

    elif "Leakage" in selected_page or "Extra" in selected_page:
        st.write("### 🛑 Extra Work Tracking (Change Orders)")
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
        evm_col1, evm_col2 = st.columns(2)
        with evm_col1:
            st.write("#### Project Health Tracker")
            actual_cost_to_date = st.number_input("Money spent so far ($)", value=float(final_gross_target_bid * 0.40))
            actual_pct = st.slider("Where we ACTUALLY are (%)", 0, 100, 45)
        with evm_col2:
            st.write("#### Financial Warning System")
            earned = final_gross_target_bid * (actual_pct/100)
            cpi = earned / actual_cost_to_date if actual_cost_to_date else 1
            if cpi < 1.0:
                st.markdown(f"<div class='unifi-stealth-danger'><h5>📉 BLEEDING CASH</h5></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='unifi-stealth-blade'><h5>✅ PROFIT ON TRACK</h5></div>", unsafe_allow_html=True)

    elif "Crew" in selected_page:
        st.write("### ⚙️ Crew Cost Settings")
        cf_col1, cf_col2 = st.columns(2)
        with cf_col1:
            st.session_state.qty_journeymen = st.number_input("Number of Expert Workers", value=st.session_state.qty_journeymen)
            st.session_state.rate_journeyman = st.number_input("Expert Base Pay ($/hr)", value=st.session_state.rate_journeyman)
            st.session_state.qty_helpers = st.number_input("Number of Helpers", value=st.session_state.qty_helpers)
            st.session_state.rate_helper = st.number_input("Helper Base Pay ($/hr)", value=st.session_state.rate_helper)
            st.session_state.labor_burden_pct = st.slider("Taxes & Insurance Burden (%)", 10, 60, int(st.session_state.labor_burden_pct*100)) / 100
        with cf_col2:
            st.write("#### True Company Cost")
            st.markdown(f"<div class='unifi-stealth-blade'><h5 style='color:#10B981;'>💸 TRUE COST PER HOUR</h5><p style='font-size:24px;'>${burdened_rate:.2f} / hr</p></div>", unsafe_allow_html=True)

    # --- FOOTER TERMINAL ---
    if not st.session_state.accessibility_mode:
        st.divider()
        st.markdown("<p style='color:#475569; font-size:10px; font-weight:600;'>📋 SYSTEM CORE TERMINAL</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='cyber-terminal-output'>{''.join([f'<div>{f}</div>' for f in st.session_state.sys_log_frames[::-1]])}</div>", unsafe_allow_html=True)
        manual_input_cmd = st.text_input("Root Command", placeholder="/diagnostics", label_visibility="collapsed")
        if st.button("Run Command") and manual_input_cmd:
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-success'>[CMD EXECUTED]</span> {manual_input_cmd} applied.")
            st.rerun()