import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

# --- MONETIZATION & CORE ENGINE PLATFORM CONFIG ---
st.set_page_config(
    page_title="OmniBuild OS | Enterprise Construction & RE SaaS", 
    layout="wide", 
    initial_sidebar_state="expanded"
)

# --- RE-INITIALIZE INTERACTIVE APP STATES ---
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = True # Bypass login for rapid dev loop
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Operations"

# Subcontractor States
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0
if "change_order_vault" not in st.session_state: st.session_state.change_order_vault = []

# General Contractor Cross-Trade Estimates
if "gc_plumbing_budget" not in st.session_state: st.session_state.gc_plumbing_budget = 18500.0
if "gc_hvac_budget" not in st.session_state: st.session_state.gc_hvac_budget = 24000.0
if "gc_framing_drywall" not in st.session_state: st.session_state.gc_framing_drywall = 32000.0
if "gc_finishes" not in st.session_state: st.session_state.gc_finishes = 45000.0

# Real Estate Capital Structure States
if "re_purchase_price" not in st.session_state: st.session_state.re_purchase_price = 450000.0
if "re_holding_costs" not in st.session_state: st.session_state.re_holding_costs = 25000.0
if "re_projected_arv" not in st.session_state: st.session_state.re_projected_arv = 750000.0

# --- DYNAMIC INTERFACE CSS MARKDOWN INJECTION ---
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
        div[data-testid="stDataEditor"] { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-radius: 4px; }
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
        .unifi-stealth-alert { background-color: #FFFBEB !important; border: 1px solid #FEF3C7 !important; border-left: 5px solid #D97706 !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; color: #92400E !important; }
        .unifi-stealth-danger { background-color: #FEF2F2 !important; border: 1px solid #FEE2E2 !important; border-left: 5px solid #DC2626 !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; color: #991B1B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE INTERLOCKING MATH PIPELINE ---
df_takeoff = pd.DataFrame([
    {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 150, "Cost": 6.50, "Mins": 12, "Metal": True},
    {"Item": "3/4\" EMT Coupling", "Phase": "Rough-In", "Qty": 140, "Cost": 1.15, "Mins": 3, "Metal": True},
    {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 25, "Cost": 18.00, "Mins": 15, "Metal": False}
])
df_takeoff["Cost"] = df_takeoff.apply(lambda r: round(r["Cost"] * (1 + st.session_state.copper_multiplier), 2) if r["Metal"] else r["Cost"], axis=1)

total_field_crew = st.session_state.qty_journeymen + st.session_state.qty_helpers
raw_labor_sum = (st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)
burdened_rate = (raw_labor_sum / total_field_crew if total_field_crew > 0 else 0) * (1 + st.session_state.labor_burden_pct)

total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Cost"]).sum()
total_labor_hours = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum()
final_burdened_labor_cost = total_labor_hours * burdened_rate
total_change_order_revenue = sum([co["Total Cost"] for co in st.session_state.change_order_vault])

# Core Linked Financial Metrics
electrical_subcontract_value = ((total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead)) + total_change_order_revenue
master_build_cost = electrical_subcontract_value + st.session_state.gc_plumbing_budget + st.session_state.gc_hvac_budget + st.session_state.gc_framing_drywall + st.session_state.gc_finishes

# RE Pro Forma Math Formulas
total_capital_deployed = st.session_state.re_purchase_price + st.session_state.re_holding_costs + master_build_cost
projected_net_profit = st.session_state.re_projected_arv - total_capital_deployed
cash_on_cash_roi = (projected_net_profit / total_capital_deployed) * 100 if total_capital_deployed > 0 else 0

# --- THE ENTERPRISE SIDEBAR DESPATCH CONTROL ---
st.sidebar.title("🏙️ OmniBuild OS")
st.session_state.accessibility_mode = st.sidebar.toggle("🟢 Plain-English / Client Mode", value=st.session_state.accessibility_mode)

st.sidebar.divider()
st.sidebar.subheader("👑 Active Account Workspace")
user_market_tier = st.sidebar.selectbox("Simulate SaaS Account Tier Access", [
    "⚡ Subcontractor Operational Tier ($49/mo)",
    "🏗️ General Contractor Pro Tier ($199/mo)",
    "🏙️ Institutional Developer Executive Tier ($599/mo)"
], index=2)

st.sidebar.divider()
st.sidebar.subheader("📌 Workstations Navigation")

# Dynamic Menu Rendering based on User Scope Tiers
if "Subcontractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "📊 Electrical Takeoff Matrix", "⚡ NEC Sizing & Physics"]
elif "General Contractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "📊 Electrical Takeoff Matrix", "⚡ NEC Sizing & Physics", "🏗️ GC Multi-Trade Budget", "🛑 Change Order Tracker"]
else:
    menu_options = ["🏠 Home Overview", "📊 Electrical Takeoff Matrix", "⚡ NEC Sizing & Physics", "🏗️ GC Multi-Trade Budget", "🛑 Change Order Tracker", "🏙️ Real Estate Pro Forma", "⚙️ Global Cost Matrix"]

selected_page = st.sidebar.radio("Select Active Console Block:", menu_options)

# --- TOP TELESCOPIC TELEMETRY METRIC FLAGS ---
st.markdown("### 📊 Live Enterprise Telemetry Stream")
h_col1, h_col2, h_col3, h_col4 = st.columns(4)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; text-transform:uppercase;'>Project Cost Basis</p><h3 style='margin:4px 0 0 0;'>${total_capital_deployed:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px; text-transform:uppercase;'>Master Renovation Cost</p><h3 style='margin:4px 0 0 0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px; text-transform:uppercase;'>Electrical Subcontract</p><h3 style='margin:4px 0 0 0;'>${electrical_subcontract_value:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col4: 
    if projected_net_profit >= 0:
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><p style='margin:0; font-size:10px; text-transform:uppercase;'>Projected Yield (ROI)</p><h3 style='margin:4px 0 0 0; color: #10B981;'>{cash_on_cash_roi:.1f}%</h3></div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='unifi-stealth-danger'><p style='margin:0; font-size:10px; text-transform:uppercase;'>Projected Yield (ROI)</p><h3 style='margin:4px 0 0 0;'>{cash_on_cash_roi:.1f}%</h3></div>", unsafe_allow_html=True)

st.divider()

# --- WORKSTATION ROUTING PORT ---
if "Home" in selected_page:
    st.write("### 🏠 System Aggregated Command Screen")
    col_g1, col_g2 = st.columns([1.5, 1])
    with col_g1:
        st.write("#### 📅 Automated Trade Milestone Gantt Chart")
        crew_daily_capacity = total_field_crew * 8
        rough_days = max(1, math.ceil(total_labor_hours / crew_daily_capacity)) if crew_daily_capacity > 0 else 1
        
        gantt_df = pd.DataFrame([
            {"Phase": "1. Core Trades Rough-In", "Start": datetime.date.today(), "End": datetime.date.today() + datetime.timedelta(days=rough_days)},
            {"Phase": "2. High-End Finish / Trim", "Start": datetime.date.today() + datetime.timedelta(days=rough_days+1), "End": datetime.date.today() + datetime.timedelta(days=rough_days+6)}
        ])
        
        chart = alt.Chart(gantt_df).mark_bar(cornerRadius=4, height=30).encode(
            x=alt.X('Start:T', title='Project Timeline Frame'), x2='End:T',
            y=alt.Y('Phase:N', title='', sort=None),
            color=alt.Color('Phase:N', legend=None, scale=alt.Scale(range=["#38BDF8", "#10B981"]))
        ).properties(height=180)
        st.altair_chart(chart, use_container_width=True)
    with col_g2:
        st.write("#### 🚨 Central Risk Scanner")
        if projected_net_profit < 0:
            st.markdown("<div class='unifi-stealth-danger'><b>⚠️ Deficit Warning:</b> Total development outlays breach current ARV valuation boundaries.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><b>✅ Financial Integrity Optimal:</b> Deployed capital basis fits safe return brackets.</div>", unsafe_allow_html=True)

elif "Takeoff" in selected_page:
    st.write("### 📊 Subcontractor Trade Takeoff Matrix")
    st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True)

elif "Physics" in selected_page:
    st.write("### ⚡ NEC Engineering Physics & Code Compliance Rules")
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        st.write("#### Conduit Fill Sizing Calculator (NEC Chapter 9)")
        w_12 = st.number_input("Count of #12 AWG Copper THHN Wires", min_value=0, value=6)
        w_10 = st.number_input("Count of #10 AWG Copper THHN Wires", min_value=0, value=2)
        total_area = (w_12 * 0.0133) + (w_10 * 0.0211)
        st.write(f"Conductor Cross-Sectional Bundle Footprint Area: **{total_area:.4f} sq. in.**")
    with f_c2:
        st.write("#### Required Raceway Diameter Size")
        if total_area <= 0.122: req_pipe = "1/2\" EMT Conduit"
        elif total_area <= 0.213: req_pipe = "3/4\" EMT Conduit"
        else: req_pipe = "1\" EMT Conduit"
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#38BDF8;'><h5>MINIMUM CODE LEGAL CONDUIT</h5><p style='font-size:28px; font-weight:bold; margin:0;'>{req_pipe}</p></div>", unsafe_allow_html=True)

elif "Budget" in selected_page:
    st.write("### 🏗️ General Contractor Trade Budget Aggregator")
    b_col1, b_col2 = st.columns([1, 1.5])
    with b_col1:
        st.info(f"**Linked MEP Electrical Subcontract Bid:** ${electrical_subcontract_value:,.2f}")
        st.session_state.gc_plumbing_budget = st.number_input("Plumbing Division Budget ($)", value=st.session_state.gc_plumbing_budget)
        st.session_state.gc_hvac_budget = st.number_input("HVAC Division Budget ($)", value=st.session_state.gc_hvac_budget)
        st.session_state.gc_framing_drywall = st.number_input("Framing & Structural Drywall ($)", value=st.session_state.gc_framing_drywall)
        st.session_state.gc_finishes = st.number_input("Finishes Allowance (Quartz, Gold Fittings) ($)", value=st.session_state.gc_finishes)
    with b_col2:
        st.write("#### Visual Construction Allotment Mix")
        chart_data = pd.DataFrame({
            "Division": ["Electrical", "Plumbing", "HVAC", "Framing", "Finishes"],
            "Value ($)": [electrical_subcontract_value, st.session_state.gc_plumbing_budget, st.session_state.gc_hvac_budget, st.session_state.gc_framing_drywall, st.session_state.gc_finishes]
        })
        pie = alt.Chart(chart_data).mark_arc(innerRadius=40).encode(
            theta='Value ($):Q', color=alt.Color('Division:N')
        ).properties(height=260)
        st.altair_chart(pie, use_container_width=True)

elif "Tracker" in selected_page:
    st.write("### 🛑 Scope Change Order Revenue Leakage Log")
    co_title = st.text_input("Variation Scope Label Description", value="Client request: Extra quartz edge profile finishes")
    co_cost = st.number_input("Calculated Material + Labor Cost ($)", value=1450.0)
    if st.button("💾 Lock Variation Record to Vault"):
        st.session_state.change_order_vault.append({"Label": co_title, "Total Cost": co_cost})
        st.rerun()
    if st.session_state.change_order_vault:
        st.write("#### Active Authorized Change Orders")
        st.data_editor(pd.DataFrame(st.session_state.change_order_vault), use_container_width=True)

elif "Pro Forma" in selected_page:
    st.write("### 🏙️ Real Estate Development Interactive Pro Forma Matrix")
    p_c1, p_c2 = st.columns(2)
    with p_c1:
        st.write("#### 💸 Asset Capital Acquisition Structure")
        st.session_state.re_purchase_price = st.slider("Property Purchase Price ($)", 100000, 1500000, int(st.session_state.re_purchase_price), step=25000)
        st.session_state.re_holding_costs = st.slider("Holding & Financing Capital Outlays ($)", 5000, 100000, int(st.session_state.re_holding_costs), step=5000)
        st.info(f"**Linked Dynamic Hard Build Costs:** ${master_build_cost:,.2f}")
        st.session_state.re_projected_arv = st.slider("Projected Post-Renovation Asset Market Value (ARV) ($)", 200000, 2500000, int(st.session_state.re_projected_arv), step=50000)
    with p_c2:
        st.write("#### 📊 Investment Return Diagnostic Analytics")
        st.write(f"Total Combined Cost Basis Deployed: **${total_capital_deployed:,.2f}**")
        if projected_net_profit >= 0:
            st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5>PROJECTED DEVELOMENT NET PROFIT Margin</h5><h2 style='color:#10B981; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='unifi-stealth-danger'><h5>PROJECTED DEVELOPMENT DEPRECIATION LOSS</h5><h2 style='color:#EF4444; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)

elif "Global Cost" in selected_page:
    st.write("### ⚙️ SaaS Platform Variables Configurations Matrix")
    st.session_state.qty_journeymen = st.number_input("Active Journeymen Personnel Count", value=st.session_state.qty_journeymen)
    st.session_state.rate_journeyman = st.number_input("Journeyman Standard Hourly Rate ($)", value=st.session_state.rate_journeyman)
    st.session_state.labor_burden_pct = st.slider("Corporate Labor Burden Factor (%)", 10, 60, int(st.session_state.labor_burden_pct*100)) / 100