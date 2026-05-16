import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

st.set_page_config(page_title="OmniBuild OS | FinTech Enterprise", layout="wide", initial_sidebar_state="expanded")

# --- STATE MANAGEMENT ---
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Operations"
if "ai_extracted" not in st.session_state: st.session_state.ai_extracted = False

# Core App States
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0
if "change_order_vault" not in st.session_state: st.session_state.change_order_vault = []
if "field_hours_logged" not in st.session_state: st.session_state.field_hours_logged = 0.0
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 12500.00

# GC & Real Estate States
if "gc_plumbing_budget" not in st.session_state: st.session_state.gc_plumbing_budget = 18500.0
if "gc_hvac_budget" not in st.session_state: st.session_state.gc_hvac_budget = 24000.0
if "gc_framing_drywall" not in st.session_state: st.session_state.gc_framing_drywall = 32000.0
if "gc_finishes" not in st.session_state: st.session_state.gc_finishes = 45000.0
if "re_purchase_price" not in st.session_state: st.session_state.re_purchase_price = 500000.0
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
        .unifi-stealth-alert { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
        .unifi-stealth-danger { background-color: #1E1014 !important; border: 1px solid #3B1E22 !important; border-left: 3px solid #EF4444 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
        .unifi-stealth-gold { background-color: #1A170F !important; border: 1px solid #3B321E !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    </style>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
    <style>
        .stApp { background-color: #F8FAFC !important; color: #1E293B !important; font-size: 18px !important; }
        .unifi-stealth-blade { background-color: #FFFFFF !important; border: 1px solid #E2E8F0 !important; border-left: 5px solid #0284C7 !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); }
        .unifi-stealth-gold { background-color: #FFFBEB !important; border: 1px solid #FEF3C7 !important; border-left: 5px solid #F59E0B !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE PIPELINE MATH ---
default_data = [
    {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 2450, "Cost": 6.50, "Mins": 12},
    {"Item": "3/4\" EMT Coupling", "Phase": "Rough-In", "Qty": 400, "Cost": 1.15, "Mins": 3},
    {"Item": "3/4\" 1-Hole Strap", "Phase": "Rough-In", "Qty": 850, "Cost": 0.45, "Mins": 2},
    {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 45, "Cost": 18.00, "Mins": 15},
    {"Item": "200A Main Breaker Panel", "Phase": "Rough-In", "Qty": 2, "Cost": 850.00, "Mins": 240}
]

df_takeoff = pd.DataFrame(default_data)
burdened_rate = st.session_state.rate_journeyman * (1 + st.session_state.labor_burden_pct)
total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Cost"]).sum()
final_burdened_labor_cost = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum() * burdened_rate
electrical_subcontract_value = ((total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead)) + sum([co["Total Cost"] for co in st.session_state.change_order_vault])
master_build_cost = electrical_subcontract_value + st.session_state.gc_plumbing_budget + st.session_state.gc_hvac_budget + st.session_state.gc_framing_drywall + st.session_state.gc_finishes
total_capital_deployed = st.session_state.re_purchase_price + st.session_state.re_holding_costs + master_build_cost
projected_net_profit = st.session_state.re_projected_arv - total_capital_deployed

# --- SIDEBAR NAVIGATION ---
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
    menu_options = ["🏠 Home Overview", "🚀 AI Auto-Takeoff", "📊 Estimating Matrix", "🛒 Supply Chain", "💳 OmniPay & Capital", "⏱️ Field Labor Tracker"]
elif "General Contractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "🚀 AI Auto-Takeoff", "🏗️ GC Master Budget", "🛒 Supply Chain", "💳 OmniPay & Capital", "🤝 Client Portal", "🏛️ AI Permit Engine"]
else:
    menu_options = ["🏠 Home Overview", "🏡 House Hack Pro", "🏙️ Investor Pro Forma", "🏗️ GC Master Budget", "💳 OmniPay & Capital", "🤝 Client Portal", "🏛️ AI Permit Engine"]

selected_page = st.sidebar.radio("Navigation:", menu_options)
st.divider()

# --- TOP TELEMETRY ---
h_col1, h_col2, h_col3, h_col4 = st.columns(4)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Master Build Cost</p><h3 style='margin:0;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Elec. Subcontract</p><h3 style='margin:0;'>${electrical_subcontract_value:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-gold'><p style='margin:0; font-size:10px; color:#F59E0B;'>OmniPay Wallet Balance</p><h3 style='margin:0; color:#F59E0B;'>${st.session_state.wallet_balance:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col4: 
    if projected_net_profit >= 0: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><p style='margin:0; font-size:10px;'>Projected Yield (ROI)</p><h3 style='margin:0; color: #10B981;'>{(projected_net_profit / total_capital_deployed)*100 if total_capital_deployed > 0 else 0:.1f}%</h3></div>", unsafe_allow_html=True)
    else: st.markdown(f"<div class='unifi-stealth-danger'><p style='margin:0; font-size:10px;'>Projected Yield (ROI)</p><h3 style='margin:0; color:#EF4444;'>0.0%</h3></div>", unsafe_allow_html=True)

# --- ROUTING ENGINE ---

if "Home" in selected_page:
    st.write("### 🏠 System Aggregated Command Screen")
    st.success("Platform Systems Optimal. Select a module from the sidebar.")

# --- THE BILLION DOLLAR FINTECH PILLAR: OMNIPAY ---
elif "OmniPay" in selected_page:
    st.write("### 💳 OmniPay & Capital Float Engine")
    st.caption("Construction is choked by 60-day payment delays. OmniPay eliminates the wait. Instantly finance your material orders or cash out your approved invoices immediately.")
    
    pay_col1, pay_col2 = st.columns([1, 1])
    
    with pay_col1:
        st.write("#### ⚡ Instant Invoice Factoring (Cash Out)")
        st.markdown("<div class='unifi-stealth-blade' style='padding:15px;'><p style='margin:0; color:#94A3B8;'>Approved Draw: <b>Phase 1 Rough-In</b></p><h2 style='margin:0; color:#38BDF8;'>$24,500.00</h2><p style='margin:0; font-size:11px;'>Status: Awaiting GC Payment (Expected in 45 Days)</p></div>", unsafe_allow_html=True)
        
        advance_pct = st.slider("Select Advance Amount (%)", 10, 100, 100, step=10)
        advance_amount = 24500.00 * (advance_pct / 100)
        factoring_fee = advance_amount * 0.025 # 2.5% fee
        net_payout = advance_amount - factoring_fee
        
        st.write(f"OmniPay Fee (2.5%): **-${factoring_fee:,.2f}**")
        st.write(f"Net Instant Deposit: **${net_payout:,.2f}**")
        
        if st.button("💸 Advance Funds to Wallet Now"):
            st.session_state.wallet_balance += net_payout
            with st.spinner("Processing ACH transfer..."):
                time.sleep(1.5)
            st.success(f"✅ ${net_payout:,.2f} deposited to your OmniWallet. You can now make payroll.")
            st.rerun()

    with pay_col2:
        st.write("#### 🏗️ Material Net-60 Financing (Float)")
        st.markdown(f"<div class='unifi-stealth-blade' style='padding:15px;'><p style='margin:0; color:#94A3B8;'>Pending Material Order (Miami Elec Supply)</p><h2 style='margin:0; color:#F59E0B;'>${total_mat_cost:,.2f}</h2><p style='margin:0; font-size:11px;'>Status: Awaiting Payment to Ship</p></div>", unsafe_allow_html=True)
        
        st.write("Don't pay out of pocket before the job starts. OmniBuild will pay the supplier today. You pay us back in 60 days when the job is done.")
        
        float_fee = total_mat_cost * 0.015 # 1.5% fee
        
        st.write(f"Supplier Receives Today: **${total_mat_cost:,.2f}**")
        st.write(f"Your Balance Due in 60 Days: **${total_mat_cost + float_fee:,.2f}** (Includes 1.5% Fee)")
        
        if st.button("🚚 Float Materials & Ship to Site"):
            with st.spinner("Authorizing Supplier Payment via OmniPay..."):
                time.sleep(1.5)
            st.success("✅ Materials paid for. Delivery scheduled for tomorrow morning.")

# --- EXISTING MODULES RETAINED FOR SEAMLESS EXPERIENCE ---
elif "AI" in selected_page:
    st.write("### 🚀 OmniVision AI: Automated Blueprint Extraction")
    st.file_uploader("Upload Floor Plan (PDF, PNG, CAD)", type=['pdf', 'png', 'dwg'])

elif "Matrix" in selected_page:
    st.write("### 📊 Trade Takeoff Pricing Matrix")
    st.data_editor(df_takeoff, use_container_width=True)

elif "Supply Chain" in selected_page:
    st.write("### 🛒 Automated Material Procurement & API Supply Chain Router")
    st.info("Split-ticket purchasing active. Routes mapped to lowest local vendor prices.")

elif "Budget" in selected_page:
    st.write("### 🏗️ General Contractor Trade Budget Aggregator")
    st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>🏗️ TOTAL GC BUILD BUDGET</h5><h2 style='color:#38BDF8; margin:0;'>${master_build_cost:,.2f}</h2></div>", unsafe_allow_html=True)

elif "Pro Forma" in selected_page:
    st.write("### 🏙️ Real Estate Development Interactive Pro Forma Matrix")
    p_c1, p_c2 = st.columns(2)
    with p_c1:
        st.session_state.re_purchase_price = st.slider("Purchase Price ($)", 100000, 1500000, int(st.session_state.re_purchase_price), step=25000)
        st.info(f"**Linked Master Build Cost:** ${master_build_cost:,.2f}")
        st.session_state.re_projected_arv = st.slider("Projected Market Value (ARV) ($)", 200000, 2500000, int(st.session_state.re_projected_arv), step=50000)
    with p_c2:
        if projected_net_profit >= 0:
            st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5>PROJECTED NET PROFIT</h5><h2 style='color:#10B981; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='unifi-stealth-danger'><h5>PROJECTED LOSS</h5><h2 style='color:#EF4444; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)

elif "House Hack" in selected_page:
    st.write("### 🏡 Homebuyer Financial & House Hack Analyzer")
    st.info("Interactive Mortgage & Renovation visualizer active.")

elif "Field Labor" in selected_page:
    st.write("### ⏱️ Boots-on-the-Ground Field Operations Terminal")
    st.info("Time tracking and EVM monitoring active.")

elif "Client Portal" in selected_page:
    st.write("### 🤝 Client & Stakeholder Transparency Portal")
    st.info("Stakeholder portal online. Awaiting digital signatures.")

elif "Permit Engine" in selected_page:
    st.write("### 🏛️ Miami-Dade AI Permitting & Compliance Auto-Pilot")
    st.info("Compliance engine standing by. NEC limits verified.")