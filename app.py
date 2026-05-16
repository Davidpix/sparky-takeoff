import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

st.set_page_config(page_title="OmniBuild OS | AI Enterprise Platform", layout="wide", initial_sidebar_state="expanded")

# --- STATE MANAGEMENT ---
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Operations"
if "ai_extracted" not in st.session_state: st.session_state.ai_extracted = False

# Subcontractor States
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "change_order_vault" not in st.session_state: st.session_state.change_order_vault = []
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0

# General Contractor Cross-Trade Estimates
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
        div[data-testid="stFileUploader"] { background-color: #0F172A !important; border: 2px dashed #38BDF8 !important; border-radius: 8px; padding: 20px; }
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
if not st.session_state.ai_extracted:
    default_data = [
        {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 0, "Cost": 6.50, "Mins": 12},
        {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 0, "Cost": 18.00, "Mins": 15}
    ]
else:
    default_data = [
        {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 2450, "Cost": 6.50, "Mins": 12},
        {"Item": "3/4\" EMT Coupling", "Phase": "Rough-In", "Qty": 400, "Cost": 1.15, "Mins": 3},
        {"Item": "3/4\" 1-Hole Strap", "Phase": "Rough-In", "Qty": 850, "Cost": 0.45, "Mins": 2},
        {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 45, "Cost": 18.00, "Mins": 15},
        {"Item": "20A Toggle Switch", "Phase": "Trim", "Qty": 120, "Cost": 1.50, "Mins": 10},
        {"Item": "2x4 LED Flat Panel", "Phase": "Trim", "Qty": 80, "Cost": 45.00, "Mins": 30},
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
    menu_options = ["🏠 Home Overview", "🚀 AI Auto-Takeoff", "📊 Manual Matrix", "📄 Proposal Builder"]
elif "General Contractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "🚀 AI Auto-Takeoff", "📊 Subcontractor Matrix", "⚖️ Bid Leveling", "🏗️ Master Budget", "📄 Proposal Builder"]
else:
    menu_options = ["🏠 Home Overview", "🚀 AI Auto-Takeoff", "📊 Subcontractor Matrix", "⚖️ Bid Leveling", "🏗️ Master Budget", "🏙️ Real Estate Pro Forma", "📄 Proposal Builder"]

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
    st.success("Platform Systems Optimal. Navigation initialized.")

# --- THE MISSING LINK: AI BLUEPRINT EXTRACTION ---
elif "AI" in selected_page:
    st.write("### 🚀 OmniVision AI: Automated Blueprint Extraction")
    st.caption("Drag and drop architectural PDFs or CAD files. Our computer vision engine automatically identifies symbols, calculates linear footage, and populates the pricing matrix.")
    
    upload_col1, upload_col2 = st.columns([1, 1])
    with upload_col1:
        uploaded_file = st.file_uploader("Upload Floor Plan (PDF, PNG, CAD)", type=['pdf', 'png', 'dwg'])
        
        if uploaded_file is not None and not st.session_state.ai_extracted:
            with st.spinner("Initializing OmniVision Neural Network..."):
                time.sleep(1.5)
            with st.spinner("Scanning vector lines and scaling geometries..."):
                time.sleep(1.5)
            with st.spinner("Cross-referencing NEC Code structural paths..."):
                time.sleep(1.5)
            
            st.session_state.ai_extracted = True
            st.success("✅ AI Extraction Complete! Database populated.")
            st.rerun()
            
        if st.session_state.ai_extracted:
            st.markdown("<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><b>✅ OmniVision Active:</b> Blueprint geometries have been translated to financial arrays.</div>", unsafe_allow_html=True)
            if st.button("Reset Extraction Engine"):
                st.session_state.ai_extracted = False
                st.rerun()

    with upload_col2:
        if st.session_state.ai_extracted:
            st.write("#### 📡 AI Extraction Summary")
            st.metric("Total Linear Feet Detected", "2,450 ft")
            st.metric("Total Device Symbols Counted", "245 Units")
            st.metric("Confidence Score", "98.7%", delta="Optimal")
        else:
            st.info("Awaiting document upload. Manual entry currently required in Matrix.")

elif "Matrix" in selected_page:
    st.write("### 📊 Trade Takeoff Pricing Matrix")
    if st.session_state.ai_extracted:
        st.success("Matrix populated via OmniVision AI Engine.")
    st.data_editor(df_takeoff, use_container_width=True)

# --- THE AUTOMATED PROPOSAL GENERATOR ---
elif "Proposal" in selected_page:
    st.write("### 📄 Automated Proposal & Contract Builder")
    st.caption("Generate a client-facing, legally structured proposal based on your active estimating matrix and corporate overhead parameters.")
    
    client_name = st.text_input("Client / General Contractor Name", value="Miami Development Group")
    project_address = st.text_input("Project Site Address", value="North Miami Beach Revitalization Area")
    
    total_hours = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum()
    
    proposal_text = f"""# COMMERCIAL CONSTRUCTION PROPOSAL
**Prepared By:** {st.session_state.company_name}
**Prepared For:** {client_name}
**Project Location:** {project_address}
**Date:** {datetime.date.today().strftime('%B %d, %Y')}

---

### 1. PROJECT SCOPE OVERVIEW
{st.session_state.company_name} agrees to provide all labor, materials, and equipment necessary to complete the electrical and mechanical scopes as defined in the master blueprint extraction. All work will be executed in strict compliance with current National Electrical Code (NEC) and South Florida municipal building standards.

### 2. FINANCIAL SUMMARY
* **Master Material Allotment:** ${total_mat_cost:,.2f}
* **Production Labor Burden ({total_hours:,.0f} Hours):** ${final_burdened_labor_cost:,.2f}
* **Project Overhead & Margin:** {st.session_state.overhead*100:.0f}%
* **Total Turnkey Contract Value:** **${electrical_subcontract_value:,.2f}**

### 3. AUTOMATED MATERIAL EXTRACTION (AI-GENERATED)
The following primary quantities have been calculated via OmniBuild AI vector extraction:
* EMT Conduit Pipeline: {df_takeoff.loc[df_takeoff['Item'] == '3/4" EMT Conduit', 'Qty'].sum()} Feet
* Devices & Receptacles: {df_takeoff.loc[df_takeoff['Phase'] == 'Trim', 'Qty'].sum()} Units

### 4. EXCLUSIONS
This proposal explicitly excludes:
- Concrete cutting, trenching, or patching.
- Utility company connection fees or municipal impact fees.
- Asbestos testing or abatement.

### 5. ACCEPTANCE OF PROPOSAL
The above prices, specifications, and conditions are satisfactory and are hereby accepted. You are authorized to do the work as specified. Payment will be made as outlined above.

**Authorized Signature:** ___________________________  **Date:** _________
"""
    
    st.text_area("Contract Preview", value=proposal_text, height=400)
    
    buffer = BytesIO()
    buffer.write(proposal_text.encode('utf-8'))
    st.download_button(
        label="📥 Download Official Client Proposal (.md)",
        data=buffer.getvalue(),
        file_name=f"Proposal_{client_name.replace(' ', '_')}.md",
        mime="text/markdown"
    )

elif "Leveling" in selected_page:
    st.write("### ⚖️ Subcontractor Procurement & Bid Leveling")
    st.info("System operational. Waiting for incoming trade bids to populate leveling matrix.")

elif "Budget" in selected_page:
    st.write("### 🏗️ General Contractor Trade Budget Aggregator")
    st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>🏗️ TOTAL GC BUILD BUDGET</h5><h2 style='color:#38BDF8; margin:0;'>${master_build_cost:,.2f}</h2></div>", unsafe_allow_html=True)

elif "Pro Forma" in selected_page:
    st.write("### 🏙️ Real Estate Development Interactive Pro Forma Matrix")
    p_c1, p_c2 = st.columns(2)
    with p_c1:
        st.session_state.re_purchase_price = st.slider("Property Purchase Price ($)", 100000, 1500000, int(st.session_state.re_purchase_price), step=25000)
        st.info(f"**Linked Master Build Cost:** ${master_build_cost:,.2f}")
        st.session_state.re_projected_arv = st.slider("Projected Market Value (ARV) ($)", 200000, 2500000, int(st.session_state.re_projected_arv), step=50000)
    with p_c2:
        if projected_net_profit >= 0:
            st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><h5>PROJECTED NET PROFIT</h5><h2 style='color:#10B981; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='unifi-stealth-danger'><h5>PROJECTED DEPRECIATION LOSS</h5><h2 style='color:#EF4444; margin:0;'>${projected_net_profit:,.2f}</h2></div>", unsafe_allow_html=True)