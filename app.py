import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt

st.set_page_config(page_title="OmniBuild OS | Enterprise Construction", layout="wide", initial_sidebar_state="expanded")

# --- STATE MANAGEMENT ---
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Operations"

# Subcontractor States
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "change_order_vault" not in st.session_state: st.session_state.change_order_vault = []

# General Contractor Cross-Trade Estimates (Linked to Bid Leveler)
if "gc_plumbing_budget" not in st.session_state: st.session_state.gc_plumbing_budget = 18500.0
if "gc_hvac_budget" not in st.session_state: st.session_state.gc_hvac_budget = 24000.0
if "gc_framing_drywall" not in st.session_state: st.session_state.gc_framing_drywall = 32000.0
if "gc_finishes" not in st.session_state: st.session_state.gc_finishes = 45000.0

# Real Estate Capital Structure States
if "re_purchase_price" not in st.session_state: st.session_state.re_purchase_price = 450000.0
if "re_holding_costs" not in st.session_state: st.session_state.re_holding_costs = 25000.0
if "re_projected_arv" not in st.session_state: st.session_state.re_projected_arv = 750000.0

# --- STYLING INJECTION ---
if not st.session_state.accessibility_mode:
    st.markdown("""
    <style>
        .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
        h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
        div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
        div[data-testid="stMetricLabel"] { font-size: 11px !important; text-transform: uppercase !important; letter-spacing: 1px !important; color: #64748B !important; }
        .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
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
    </style>
    """, unsafe_allow_html=True)

# --- CORE PIPELINE MATH ---
df_takeoff = pd.DataFrame([
    {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 150, "Cost": 6.50, "Mins": 12},
    {"Item": "3/4\" EMT Coupling", "Phase": "Rough-In", "Qty": 140, "Cost": 1.15, "Mins": 3},
    {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 25, "Cost": 18.00, "Mins": 15}
])

burdened_rate = st.session_state.rate_journeyman * (1 + st.session_state.labor_burden_pct)
total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Cost"]).sum()
final_burdened_labor_cost = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum() * burdened_rate

electrical_subcontract_value = ((total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead)) + sum([co["Total Cost"] for co in st.session_state.change_order_vault])
master_build_cost = electrical_subcontract_value + st.session_state.gc_plumbing_budget + st.session_state.gc_hvac_budget + st.session_state.gc_framing_drywall + st.session_state.gc_finishes

total_capital_deployed = st.session_state.re_purchase_price + st.session_state.re_holding_costs + master_build_cost
projected_net_profit = st.session_state.re_projected_arv - total_capital_deployed
cash_on_cash_roi = (projected_net_profit / total_capital_deployed) * 100 if total_capital_deployed > 0 else 0

# --- THE ENTERPRISE SIDEBAR ---
st.sidebar.title("🏙️ OmniBuild OS")
st.session_state.accessibility_mode = st.sidebar.toggle("🟢 Plain-English Mode", value=st.session_state.accessibility_mode)
st.sidebar.divider()

user_market_tier = st.sidebar.selectbox("Simulate SaaS Tier", [
    "⚡ Subcontractor Tier ($49/mo)",
    "🏗️ General Contractor Pro ($199/mo)",
    "🏙️ Executive Developer ($599/mo)"
], index=2)

st.sidebar.divider()

if "Subcontractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "📊 Electrical Takeoff"]
elif "General Contractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "📊 Electrical Takeoff", "⚖️ Bid Leveling & Procurement", "🏗️ GC Master Budget", "🛑 Change Orders"]
else:
    menu_options = ["🏠 Home Overview", "📊 Electrical Takeoff", "⚖️ Bid Leveling & Procurement", "🏗️ GC Master Budget", "🏙️ Real Estate Pro Forma", "💼 C-Suite EVM"]

selected_page = st.sidebar.radio("Navigation:", menu_options)

# --- TOP TELEMETRY ---
h_col1, h_col2, h_col3, h_col4 = st.columns(4)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Project Cost Basis</p><h3 style='margin:0;'>${total_capital_deployed:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>Master Build Cost</p><h3 style='margin:0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Elec. Subcontract</p><h3 style='margin:0;'>${electrical_subcontract_value:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col4: 
    if projected_net_profit >= 0: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><p style='margin:0; font-size:10px;'>Projected Yield (ROI)</p><h3 style='margin:0; color: #10B981;'>{cash_on_cash_roi:.1f}%</h3></div>", unsafe_allow_html=True)
    else: st.markdown(f"<div class='unifi-stealth-danger'><p style='margin:0; font-size:10px;'>Projected Yield (ROI)</p><h3 style='margin:0; color:#EF4444;'>{cash_on_cash_roi:.1f}%</h3></div>", unsafe_allow_html=True)
st.divider()

# --- ROUTING ENGINE ---
if "Home" in selected_page:
    st.write("### 🏠 System Aggregated Command Screen")
    st.success("Platform Systems Optimal. Real Estate variables mapped to active trades.")

elif "Takeoff" in selected_page:
    st.write("### 📊 Subcontractor Trade Takeoff Matrix")
    st.data_editor(df_takeoff, use_container_width=True)

# --- THE MISSING BILLION DOLLAR PILLAR: BID LEVELING ---
elif "Leveling" in selected_page:
    st.write("### ⚖️ Subcontractor Procurement & Bid Leveling (Procore/BuildingConnected Alternative)")
    st.caption("General Contractors solicit multiple bids for the same trade. Use this matrix to spot \"scope gaps\" (e.g., a plumber who forgot to include fixture costs) and Award the contract safely.")
    
    st.write("#### 💧 Division 22: Plumbing Bid Leveling Analysis")
    
    # Building the Bid Comparison Matrix
    leveling_data = pd.DataFrame({
        "Scope Item (Cost Breakdown)": ["Underground Rough-in", "Top-Out / Pipe Routing", "Fixtures & Trim", "Permits & Fees", "TOTAL BID PRICE"],
        "Joe's Plumbing (Local)": ["$4,500", "$7,000", "$5,000", "$800", "$17,300"],
        "Miami Pipe Pros (Commercial)": ["$5,000", "$6,500", "$4,500", "$1,000", "$17,000"],
        "Apex Mechanical (Incomplete)": ["$4,800", "$6,800", "⚠️ $0 (Excluded)", "$900", "$12,500"]
    })
    st.dataframe(leveling_data, use_container_width=True, hide_index=True)
    
    st.markdown("<div class='unifi-stealth-danger' style='padding:8px;'><p style='margin:0; font-size:12px;'><b>🚨 SCOPE GAP DETECTED:</b> Apex Mechanical appears cheaper, but they excluded Fixtures & Trim from their bid. If you award to them, you will have to pay out of pocket for toilets and sinks later.</p></div>", unsafe_allow_html=True)
    
    st.write("#### 🏆 Execute Subcontractor Award")
    col_award1, col_award2 = st.columns([1, 2])
    with col_award1:
        awarded_sub = st.selectbox("Select Winning Subcontractor:", ["Joe's Plumbing - $17,300", "Miami Pipe Pros - $17,000", "Apex Mechanical - $12,500 (RISK)"])
        if st.button("Contract Award & Sync to Master Budget"):
            if "Joe" in awarded_sub: st.session_state.gc_plumbing_budget = 17300.0
            elif "Miami" in awarded_sub: st.session_state.gc_plumbing_budget = 17000.0
            elif "Apex" in awarded_sub: st.session_state.gc_plumbing_budget = 12500.0
            st.rerun()
            
    with col_award2:
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #38BDF8;'><p style='margin:0; font-size:11px;'>ACTIVE PLUMBING BUDGET</p><h3 style='margin:0;'>${st.session_state.gc_plumbing_budget:,.2f}</h3></div>", unsafe_allow_html=True)

elif "Budget" in selected_page:
    st.write("### 🏗️ General Contractor Trade Budget Aggregator")
    b_col1, b_col2 = st.columns([1, 1.5])
    with b_col1:
        st.info(f"**Electrical Subcontract:** ${electrical_subcontract_value:,.2f}")
        st.info(f"**Plumbing Subcontract:** ${st.session_state.gc_plumbing_budget:,.2f} *(Synced from Procurement)*")
        st.session_state.gc_hvac_budget = st.number_input("HVAC Division Budget ($)", value=st.session_state.gc_hvac_budget)
        st.session_state.gc_framing_drywall = st.number_input("Framing & Structural Drywall ($)", value=st.session_state.gc_framing_drywall)
        st.session_state.gc_finishes = st.number_input("Finishes Allowance ($)", value=st.session_state.gc_finishes)
    with b_col2:
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>🏗️ TOTAL GC BUILD BUDGET</h5><h2 style='color:#38BDF8; margin:0;'>${master_build_cost:,.2f}</h2></div>", unsafe_allow_html=True)

elif "Pro Forma" in selected_page:
    st.write("### 🏙️ Real Estate Development Interactive Pro Forma Matrix")
    p_c1, p_c2 = st.columns(2)
    with p_c1:
        st.session_state.re_purchase_price = st.slider("Property Purchase Price ($)", 100000, 1500000, int(st.session_state.re_purchase_price), step=25000)
        st.session_state.re_holding_costs = st.slider("Holding Capital Outlays ($)", 5000, 100000, int(st.session_state.re_holding_costs), step=5000)
        st.info(f"**Linked Master Build Cost:** ${master_build_cost:,.2f}")
        st.session_state.re_projected_arv = st.slider("Projected Market Value (ARV) ($)", 200000, 2500000, int(st.session_state.re_projected_arv), step=50000)
    with p_c2:
        st.write(f"Total Combined Cost Basis Deployed: **${total_capital_deployed:,.2f}**")
        if projected_net_profit >= 0:
            st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5>PROJECTED NET PROFIT</h5><h2 style='color:#10B981; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='unifi-stealth-danger'><h5>PROJECTED DEPRECIATION LOSS</h5><h2 style='color:#EF4444; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)

elif "Tracker" in selected_page or "EVM" in selected_page:
    st.write("### 🛑 Additional Management Tools Available in Dashboard")