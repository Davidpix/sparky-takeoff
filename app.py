import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt

st.set_page_config(page_title="SparkyTakeoff OS | Master Builder", layout="wide", initial_sidebar_state="expanded")

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
    </style>
    """, unsafe_allow_html=True)

# --- DIRECTORY & STATE CONFIG ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Operations"
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0
if "change_order_vault" not in st.session_state: st.session_state.change_order_vault = []
if "sys_log_frames" not in st.session_state: st.session_state.sys_log_frames = [f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-kernel'>[SYS CORE]</span> Omni-Trade Platform initialized."]

# GC & Real Estate States
if "gc_plumbing_budget" not in st.session_state: st.session_state.gc_plumbing_budget = 18500.0
if "gc_hvac_budget" not in st.session_state: st.session_state.gc_hvac_budget = 24000.0
if "gc_framing_drywall" not in st.session_state: st.session_state.gc_framing_drywall = 32000.0
if "gc_finishes" not in st.session_state: st.session_state.gc_finishes = 45000.0

# --- GATEWAY LOGIN ---
if not st.session_state.user_authenticated:
    st.title("⚡ SparkyTakeoff OS | Master Builder")
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

    total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Cost"]).sum()
    total_labor_hours = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum()
    final_burdened_labor_cost = total_labor_hours * burdened_rate
    total_change_order_revenue = sum([co["Total Cost"] for co in st.session_state.change_order_vault])
    
    # Core Electrical Subcontract Value
    electrical_subcontract_value = ((total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead)) + total_change_order_revenue
    
    # GC Master Build Cost Calculation
    master_build_cost = electrical_subcontract_value + st.session_state.gc_plumbing_budget + st.session_state.gc_hvac_budget + st.session_state.gc_framing_drywall + st.session_state.gc_finishes

    # --- THE NEW UNIFIED SIDEBAR NAVIGATION ---
    st.sidebar.title("🧭 Navigation Menu")
    st.session_state.accessibility_mode = st.sidebar.toggle("🟢 Plain-English / Easy Mode", value=st.session_state.accessibility_mode)
    st.sidebar.divider()
    
    menu_options = [
        "🏠 Home Dashboard",
        "🎛️ Trade Takeoff Matrix", 
        "⚡ Engineering & Physics", 
        "🏗️ GC Master Budget", 
        "🏙️ Real Estate ROI Pro Forma",
        "🗓️ Draw Schedules",
        "💼 C-Suite EVM",
        "⚙️ Operation Settings"
    ]
    
    selected_page = st.sidebar.radio("Select View:", menu_options)
    
    st.sidebar.divider()
    if st.sidebar.button("🚪 Logout"):
        st.session_state.user_authenticated = False; st.rerun()

    # --- GLOBAL HEADER METRICS (OMNI-TRADE VIEW) ---
    title_gross = "Electrical Contract" if st.session_state.accessibility_mode else "MEP Electrical Subcontract"
    title_mat = "Total Build Cost" if st.session_state.accessibility_mode else "GC Master Budget"

    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    with m_col1: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:11px; text-transform:uppercase;'>{title_gross}</p><h3 style='margin:4px 0 0 0;'>${electrical_subcontract_value:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col2: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#F59E0B;'><p style='margin:0; font-size:11px; text-transform:uppercase;'>{title_mat}</p><h3 style='margin:4px 0 0 0; color:#F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col3: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:11px; text-transform:uppercase;'>Elec. Material Invoice</p><h3 style='margin:4px 0 0 0;'>${total_mat_cost:,.2f}</h3></div>", unsafe_allow_html=True)
    with m_col4: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:11px; text-transform:uppercase;'>Elec. Target Margin</p><h3 style='margin:4px 0 0 0;'>{st.session_state.overhead*100:.0f}%</h3></div>", unsafe_allow_html=True)

    st.divider()

    # --- ROUTING ENGINE ---
    if "Home" in selected_page:
        st.write("### 🏠 Omni-Trade Command Center")
        home_col1, home_col2 = st.columns([1.5, 1])
        with home_col1:
            st.write("#### 📅 Master Execution Schedule")
            crew_daily_capacity = total_field_crew * 8
            rough_in_hours = ((df_takeoff[df_takeoff['Phase'] == 'Rough-In']["Qty"] * df_takeoff[df_takeoff['Phase'] == 'Rough-In']["Mins"]) / 60).sum()
            trim_hours = ((df_takeoff[df_takeoff['Phase'] == 'Trim']["Qty"] * df_takeoff[df_takeoff['Phase'] == 'Trim']["Mins"]) / 60).sum()
            
            rough_in_days = math.ceil(rough_in_hours / crew_daily_capacity) if crew_daily_capacity > 0 else 1
            trim_days = math.ceil(trim_hours / crew_daily_capacity) if crew_daily_capacity > 0 else 1
            
            start_date = datetime.date.today() + datetime.timedelta(days=7)
            rough_in_end = start_date + datetime.timedelta(days=rough_in_days)
            trim_start = rough_in_end + datetime.timedelta(days=2)
            trim_end = trim_start + datetime.timedelta(days=trim_days)
            
            gantt_data = pd.DataFrame([
                {"Task": "Phase 1: Rough-In", "Start": start_date, "End": rough_in_end, "Duration": rough_in_days},
                {"Task": "Phase 2: Trim-Out", "Start": trim_start, "End": trim_end, "Duration": trim_days}
            ])
            
            chart = alt.Chart(gantt_data).mark_bar(cornerRadius=4, height=30).encode(
                x=alt.X('Start:T', title='Timeline', axis=alt.Axis(format='%b %d', grid=True, gridColor="#1E293B" if not st.session_state.accessibility_mode else "#E2E8F0")),
                x2='End:T',
                y=alt.Y('Task:N', title='', sort=None, axis=alt.Axis(labelColor="#94A3B8" if not st.session_state.accessibility_mode else "#1E293B", labelFontSize=12)),
                color=alt.Color('Task:N', legend=None, scale=alt.Scale(range=["#38BDF8", "#10B981"]))
            ).properties(height=180).configure_view(strokeWidth=0).configure_axis(domain=False)
            st.altair_chart(chart, use_container_width=True)
            
        with home_col2:
            st.write("#### 🚨 Central Alert Scanner")
            st.markdown("<div class='unifi-stealth-blade' style='padding:10px; border-left-color:#10B981;'><b>✅ Subcontractor Feeds:</b> Trade bids integrated.</div>", unsafe_allow_html=True)
            st.markdown("<div class='unifi-stealth-blade' style='padding:10px; border-left-color:#10B981;'><b>✅ Engineering Physics:</b> NEC variables optimal.</div>", unsafe_allow_html=True)

    elif "Matrix" in selected_page:
        st.write("### 🎛️ Active Subcontractor Estimating Matrix")
        st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True)

    elif "Physics" in selected_page:
        st.write("### ⚡ Engineering Physics & Safety Code Limits")
        p_col1, p_col2 = st.columns([1, 2])
        with p_col1:
            circuit_label = st.text_input("Appliance Name", value="Walk-in Shower Heater")
            volt_amps_load = st.number_input("Power Required (Watts/VA)", value=3100, step=100)
            st.selectbox("Assign to Phase", ["Phase A", "Phase B", "Phase C"])
        with p_col2:
            st.success("✅ Power is evenly distributed across the panel busbars. Structure safe.")

        st.divider()
        st.write("#### Conduit Fill Optimizer (NEC Chapter 9)")
        fill_col1, fill_col2 = st.columns(2)
        with fill_col1:
            qty_12 = st.number_input("Count of #12 AWG Wires", min_value=0, value=4, step=1)
            qty_10 = st.number_input("Count of #10 AWG Wires", min_value=0, value=1, step=1)
            qty_8 = st.number_input("Count of #8 AWG Wires", min_value=0, value=0, step=1)
        with fill_col2:
            total_bundle_area = (qty_12 * 0.0133) + (qty_10 * 0.0211) + (qty_8 * 0.0366)
            emt_caps = {"1/2\" EMT": 0.122, "3/4\" EMT": 0.213, "1\" EMT": 0.346}
            recommended_pipe = "Exceeds standard limits"
            for pipe_size, cap in emt_caps.items():
                if total_bundle_area <= cap:
                    recommended_pipe = pipe_size; break
            if (qty_12 + qty_10 + qty_8) > 0:
                st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #38BDF8;'><h5 style='color:#38BDF8; margin:0;'>🛠️ MINIMUM PIPE REQUIRED</h5><p style='font-size:24px; font-weight:bold; margin:4px 0;'>{recommended_pipe}</p></div>", unsafe_allow_html=True)

    # --- NEW FEATURE: GC MASTER BUDGET AGGREGATOR ---
    elif "GC" in selected_page:
        st.write("### 🏗️ General Contractor Master Budget Aggregator")
        st.caption("Level subcontractor bids and aggregate all Mechanical, Electrical, and Plumbing (MEP) and finishing costs to establish the total property build requirement.")
        
        gc_col1, gc_col2 = st.columns([1, 1.5])
        with gc_col1:
            st.write("#### 📋 Trade Estimates Input")
            st.info(f"**Electrical & Low-Voltage:** ${electrical_subcontract_value:,.2f} *(Auto-linked to active Matrix)*")
            st.session_state.gc_plumbing_budget = st.number_input("Plumbing Subcontract ($)", min_value=0.0, value=st.session_state.gc_plumbing_budget, step=1000.0)
            st.session_state.gc_hvac_budget = st.number_input("HVAC / Mechanical Subcontract ($)", min_value=0.0, value=st.session_state.gc_hvac_budget, step=1000.0)
            st.session_state.gc_framing_drywall = st.number_input("Framing & Drywall (inc. 8ft Ceilings) ($)", min_value=0.0, value=st.session_state.gc_framing_drywall, step=1000.0)
            st.session_state.gc_finishes = st.number_input("High-End Finishes (Quartz, Cabinetry, Gold Hardware) ($)", min_value=0.0, value=st.session_state.gc_finishes, step=1000.0)
            
        with gc_col2:
            st.write("#### 📊 Master Build Allocation")
            st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>🏗️ TOTAL GC BUILD BUDGET</h5><p style='font-size:32px; font-family:monospace; color:#38BDF8; margin:6px 0;'>${master_build_cost:,.2f}</p></div>", unsafe_allow_html=True)
            
            # Trade Distribution Visualization
            trade_df = pd.DataFrame({
                "Trade": ["Electrical", "Plumbing", "HVAC", "Framing/Drywall", "Finishes"],
                "Budget": [electrical_subcontract_value, st.session_state.gc_plumbing_budget, st.session_state.gc_hvac_budget, st.session_state.gc_framing_drywall, st.session_state.gc_finishes]
            })
            pie_chart = alt.Chart(trade_df).mark_arc(innerRadius=50).encode(
                theta=alt.Theta(field="Budget", type="quantitative"),
                color=alt.Color(field="Trade", type="nominal", legend=alt.Legend(title="Disciplines", labelColor="#94A3B8" if not st.session_state.accessibility_mode else "#1E293B")),
                tooltip=["Trade", alt.Tooltip("Budget:Q", format="$,.2f")]
            ).properties(height=250).configure_view(strokeWidth=0)
            st.altair_chart(pie_chart, use_container_width=True)

    # --- NEW FEATURE: REAL ESTATE ROI PRO FORMA ---
    elif "Real Estate" in selected_page:
        st.write("### 🏙️ Real Estate Development Pro Forma & ROI Matrix")
        st.caption("Cross-reference total master build costs against acquisition and projected After Repair Value (ARV) to lock in investment viability.")
        
        re_col1, re_col2 = st.columns(2)
        with re_col1:
            st.write("#### 🏢 Deal Capital Structure")
            purchase_price = st.number_input("Property Acquisition / Purchase Price ($)", min_value=0.0, value=450000.0, step=10000.0)
            holding_costs = st.number_input("Holding Costs (Taxes, Insurance, HOA, Financing) ($)", min_value=0.0, value=25000.0, step=1000.0)
            st.info(f"**Total Renovation Scope:** ${master_build_cost:,.2f} *(Auto-linked to GC Master Budget)*")
            projected_arv = st.number_input("Projected After Repair Value (ARV) ($)", min_value=0.0, value=750000.0, step=25000.0)
            
        with re_col2:
            st.write("#### 📈 Investment Returns Profile")
            total_cash_basis = purchase_price + holding_costs + master_build_cost
            net_profit = projected_arv - total_cash_basis
            roi_pct = (net_profit / total_cash_basis) * 100 if total_cash_basis > 0 else 0
            
            st.write(f"Total Capital Deployed (Cost Basis): **${total_cash_basis:,.2f}**")
            
            if net_profit > 0:
                st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><h5 style='color:#10B981; margin:0;'>💰 PROJECTED NET PROFIT</h5><p style='font-size:32px; font-family:monospace; color:#38BDF8; margin:6px 0;'>${net_profit:,.2f}</p></div>", unsafe_allow_html=True)
                st.metric("Cash-on-Cash ROI", f"{roi_pct:.1f}%", delta="Profitable Deal")
            else:
                st.markdown(f"<div class='unifi-stealth-danger'><h5 style='color:#EF4444; margin:0;'>🚨 DEAL OPERATING AT A LOSS</h5><p style='font-size:32px; font-family:monospace; margin:6px 0;'>${net_profit:,.2f}</p></div>", unsafe_allow_html=True)
                st.metric("Cash-on-Cash ROI", f"{roi_pct:.1f}%", delta="Capital Burn", delta_color="inverse")

    elif "Draws" in selected_page:
        st.write("### 🗓️ Capital Draw & Disbursement Schedule")
        pct_mobilization = st.slider("Upfront Deposit / Mobilization (%)", 5, 30, 15, step=5)
        pct_roughin = st.slider("Completion of Wall Phases (%)", 20, 50, 35, step=5)
        pct_trimout = st.slider("Final Trim & Sign-off (%)", 10, 50, 50, step=5)
        
        draw_df = pd.DataFrame({
            "Construction Phase": ["Phase 1: Mobilization", "Phase 2: Rough-In", "Phase 3: Final Trim"],
            "Capital Draw Value ($)": [master_build_cost*(pct_mobilization/100), master_build_cost*(pct_roughin/100), master_build_cost*(pct_trimout/100)]
        })
        st.data_editor(draw_df, use_container_width=True, disabled=True)

    elif "C-Suite" in selected_page:
        st.write("### 💼 C-Suite EVM (Earned Value Management)")
        evm_col1, evm_col2 = st.columns(2)
        with evm_col1:
            actual_cost_to_date = st.number_input("Actual Project Money Deployed ($)", value=float(master_build_cost * 0.40))
            actual_pct = st.slider("Actual Physical Progress (%)", 0, 100, 45)
        with evm_col2:
            earned = master_build_cost * (actual_pct/100)
            cpi = earned / actual_cost_to_date if actual_cost_to_date else 1
            if cpi < 1.0:
                st.markdown(f"<div class='unifi-stealth-danger'><h5>📉 BLEEDING CASH</h5><p>Construction execution is trailing budget burns.</p></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div class='unifi-stealth-blade'><h5>✅ MARGIN SECURE</h5></div>", unsafe_allow_html=True)

    elif "Settings" in selected_page:
        st.write("### ⚙️ Operating Cost Settings")
        st.session_state.qty_journeymen = st.number_input("Lead Techs / PMs", value=st.session_state.qty_journeymen)
        st.session_state.rate_journeyman = st.number_input("Lead Base Pay ($/hr)", value=st.session_state.rate_journeyman)
        st.session_state.labor_burden_pct = st.slider("Taxes & Insurance Burden (%)", 10, 60, int(st.session_state.labor_burden_pct*100)) / 100
        st.markdown(f"<div class='unifi-stealth-blade'><h5 style='color:#10B981;'>💸 TRUE HOURLY COST</h5><p style='font-size:24px;'>${burdened_rate:.2f} / hr</p></div>", unsafe_allow_html=True)

    # --- FOOTER TERMINAL ---
    if not st.session_state.accessibility_mode:
        st.divider()
        st.markdown("<p style='color:#475569; font-size:10px; font-weight:600;'>📋 SYSTEM CORE TERMINAL</p>", unsafe_allow_html=True)
        st.markdown(f"<div class='cyber-terminal-output'>{''.join([f'<div>{f}</div>' for f in st.session_state.sys_log_frames[::-1]])}</div>", unsafe_allow_html=True)
        manual_input_cmd = st.text_input("Root Command", placeholder="/diagnostics", label_visibility="collapsed")
        if st.button("Run Command") and manual_input_cmd:
            st.session_state.sys_log_frames.append(f"<span class='terminal-timestamp'>[{datetime.datetime.now().strftime('%H:%M:%S')}]</span> <span class='terminal-success'>[CMD EXECUTED]</span> {manual_input_cmd} processed.")
            st.rerun()