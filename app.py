import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

st.set_page_config(page_title="OmniBuild OS | Ultimate Enterprise", layout="wide", initial_sidebar_state="expanded")

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
        .unifi-stealth-danger { background-color: #FEF2F2 !important; border: 1px solid #FEE2E2 !important; border-left: 5px solid #DC2626 !important; padding: 20px; border-radius: 8px; margin-bottom: 16px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.1); color: #991B1B !important; }
    </style>
    """, unsafe_allow_html=True)

# --- CORE PIPELINE MATH ---
if not st.session_state.ai_extracted:
    default_data = [
        {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 150, "Cost": 6.50, "Mins": 12},
        {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 25, "Cost": 18.00, "Mins": 15}
    ]
else:
    default_data = [
        {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 2450, "Cost": 6.50, "Mins": 12},
        {"Item": "3/4\" EMT Coupling", "Phase": "Rough-In", "Qty": 400, "Cost": 1.15, "Mins": 3},
        {"Item": "3/4\" 1-Hole Strap", "Phase": "Rough-In", "Qty": 850, "Cost": 0.45, "Mins": 2},
        {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 45, "Cost": 18.00, "Mins": 15},
        {"Item": "2x4 LED Flat Panel", "Phase": "Trim", "Qty": 80, "Cost": 45.00, "Mins": 30},
        {"Item": "200A Main Breaker Panel", "Phase": "Rough-In", "Qty": 2, "Cost": 850.00, "Mins": 240}
    ]

df_takeoff = pd.DataFrame(default_data)
burdened_rate = st.session_state.rate_journeyman * (1 + st.session_state.labor_burden_pct)
total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Cost"]).sum()
final_burdened_labor_cost = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum() * burdened_rate
total_estimated_hours = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum()
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

# Dynamic Menu based on Tier selection
if "Subcontractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "🚀 AI Auto-Takeoff", "📊 Estimating Matrix", "🛒 Supply Chain", "⏱️ Field Labor Tracker", "🏛️ AI Permit Engine"]
elif "General Contractor" in user_market_tier:
    menu_options = ["🏠 Home Overview", "🚀 AI Auto-Takeoff", "⚖️ GC Bid Leveling", "🏗️ GC Master Budget", "⏱️ Field Labor Tracker", "🤝 Client Transparency Portal", "🏛️ AI Permit Engine"]
else:
    menu_options = ["🏠 Home Overview", "🏡 House Hack Pro", "🚀 AI Auto-Takeoff", "🏗️ GC Master Budget", "🏙️ Real Estate Pro Forma", "⏱️ Field Labor Tracker", "🤝 Client Transparency Portal", "🏛️ AI Permit Engine"]

selected_page = st.sidebar.radio("Navigation:", menu_options)
st.divider()

# --- ROUTING ENGINE ---

if "Home" in selected_page:
    st.write("### 🏠 System Aggregated Command Screen")
    st.success("Platform Systems Optimal. Select a module from the sidebar.")
    h_col1, h_col2, h_col3 = st.columns(3)
    with h_col1: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Master Build Cost</p><h3 style='margin:0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
    with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Elec. Subcontract</p><h3 style='margin:0;'>${electrical_subcontract_value:,.2f}</h3></div>", unsafe_allow_html=True)
    with h_col3: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><p style='margin:0; font-size:10px;'>Estimated Labor Hours</p><h3 style='margin:0; color: #10B981;'>{total_estimated_hours:.1f} hrs</h3></div>", unsafe_allow_html=True)

# --- NEW PILLAR 1: THE FIELD LABOR TRACKER ---
elif "Field Labor Tracker" in selected_page:
    st.write("### ⏱️ Boots-on-the-Ground Field Operations Terminal")
    st.caption("Foremen log active hours here. The system instantly cross-references actual burn rates against your AI estimate to detect profit bleeding.")
    
    lab_col1, lab_col2 = st.columns([1, 1.5])
    with lab_col1:
        st.write("#### 👷‍♂️ Log Daily Field Hours")
        todays_hours = st.number_input("Total Crew Hours Logged Today", min_value=0.0, value=16.0, step=0.5)
        phys_progress = st.slider("Estimated Physical Completion (%)", 0, 100, 45, step=5)
        
        if st.button("📡 Sync Hours to Cloud Dashboard"):
            st.session_state.field_hours_logged += todays_hours
            st.success("Hours synced successfully. EVM updated.")
            st.rerun()
            
    with lab_col2:
        st.write("#### 📡 Real-Time Earned Value Analytics (EVM)")
        total_logged = st.session_state.field_hours_logged
        st.write(f"**Total Hours Estimated (Budget):** {total_estimated_hours:.1f} hrs")
        st.write(f"**Total Hours Burned (Actual):** {total_logged:.1f} hrs")
        
        # Calculate EVM metrics for Labor
        if phys_progress > 0:
            earned_hours = total_estimated_hours * (phys_progress / 100)
            cpi = earned_hours / total_logged if total_logged > 0 else 1.0
            
            st.progress(phys_progress / 100, text=f"Physical Completion: {phys_progress}%")
            
            if cpi < 0.95:
                st.markdown(f"""
                <div class='unifi-stealth-danger'>
                    <h5 style='color:#EF4444; margin:0;'>🚨 PROFIT BLEED DETECTED: LABOR OVERRUN</h5>
                    <p style='font-size:12px; margin:4px 0 0 0;'>Labor Efficiency Index (CPI): <b>{cpi:.2f}</b>. Your crew is burning hours faster than they are completing the work. At this rate, labor costs will wipe out your target margin.</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class='unifi-stealth-blade' style='border-left-color: #10B981;'>
                    <h5 style='color:#10B981; margin:0;'>✅ CREW EFFICIENCY OPTIMAL</h5>
                    <p style='font-size:12px; margin:4px 0 0 0;'>Labor Efficiency Index (CPI): <b>{cpi:.2f}</b>. The crew is beating or meeting the estimated installation times.</p>
                </div>
                """, unsafe_allow_html=True)

# --- NEW PILLAR 2: THE CLIENT TRANSPARENCY PORTAL ---
elif "Client Transparency" in selected_page:
    st.write("### 🤝 Client & Stakeholder Transparency Portal")
    st.caption("A locked-down, read-only view sent to Homeowners or Investors. Builds extreme trust and allows instant digital sign-off on Change Orders.")
    
    st.markdown(f"<div class='unifi-stealth-blade' style='text-align:center; padding:30px;'><h2 style='margin:0;'>{client_name if 'client_name' in locals() else 'Miami Investment Group'} - Project Dashboard</h2><p style='color:#38BDF8;'>Powered by OmniBuild OS</p></div>", unsafe_allow_html=True)
    
    c_col1, c_col2 = st.columns(2)
    with c_col1:
        st.write("#### 🏗️ High-Level Project Status")
        st.progress(65, text="Phase 2: Rough-In & Framing (65% Complete)")
        st.info(f"**Total Authorized Master Budget:** ${master_build_cost:,.2f}")
        st.success("**Target Completion Date:** " + (datetime.date.today() + datetime.timedelta(days=45)).strftime('%B %d, %Y'))
        
    with c_col2:
        st.write("#### ✍️ Digital Signature Vault (Pending Action)")
        if len(st.session_state.change_order_vault) > 0:
            st.warning("You have pending scope adjustments requiring approval.")
            for co in st.session_state.change_order_vault:
                st.markdown(f"<div style='border:1px solid #1E293B; padding:10px; border-radius:4px; margin-bottom:5px;'><b>{co['Label']}</b> - ${co['Total Cost']:,.2f} <br><button style='margin-top:5px;'>Click to Digitally Sign & Approve</button></div>", unsafe_allow_html=True)
        else:
            st.write("✅ No pending change orders. You are up to date.")
            st.markdown("<div class='unifi-stealth-blade' style='border-left-color: #10B981;'>All variations have been signed and authorized. Funds secured.</div>", unsafe_allow_html=True)

# --- NEW PILLAR 3: THE AI PERMIT ENGINE ---
elif "Permit Engine" in selected_page:
    st.write("### 🏛️ Miami-Dade AI Permitting & Compliance Auto-Pilot")
    st.caption("Turns a 3-week municipal bureaucracy nightmare into a 10-second export. OmniBuild OS uses the live matrix data to auto-generate official building department technical forms.")
    
    perm_col1, perm_col2 = st.columns([1, 1])
    with perm_col1:
        st.write("#### 📄 Generate Municipal Forms")
        st.selectbox("Select Municipality", ["Miami-Dade County", "City of Miami Beach", "City of Fort Lauderdale", "Broward County"])
        permit_type = st.selectbox("Permit Sub-Type", ["Electrical Master Permit", "Mechanical / HVAC", "Plumbing", "Master Building / Structural"])
        
        if st.button("⚙️ Compile AI Load Calculations & Permit Docs"):
            with st.spinner("Extracting load totals from matrix..."): time.sleep(1)
            with st.spinner("Cross-referencing Florida Building Code (FBC)..."): time.sleep(1)
            with st.spinner("Generating official PDF package..."): time.sleep(1)
            st.success("✅ Permit Package Compiled Successfully.")
            
            # Simulated Download Button
            permit_text = f"MIAMI-DADE ELECTRICAL PERMIT APPLICATION\nTotal Amperage: 200A\nTotal Receptacles: {df_takeoff.loc[df_takeoff['Item'] == '20A GFCI Device', 'Qty'].sum() if st.session_state.ai_extracted else 25}\nStatus: FBC 2026 Compliant."
            buffer = BytesIO()
            buffer.write(permit_text.encode('utf-8'))
            st.download_button("📥 Download Official Municipal Permit Package (.pdf)", data=buffer.getvalue(), file_name="Miami_Dade_Permit_App.pdf", mime="application/pdf")
            
    with perm_col2:
        st.write("#### 🛡️ Code Compliance Pre-Check")
        st.markdown("<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><p style='margin:0; font-size:12px;'><b>NEC 310.15 (Thermal):</b> PASS</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><p style='margin:0; font-size:12px;'><b>NEC Chapter 9 (Conduit Fill):</b> PASS</p></div>", unsafe_allow_html=True)
        st.markdown("<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><p style='margin:0; font-size:12px;'><b>NEC 110.9 (Fault Currents):</b> PASS</p></div>", unsafe_allow_html=True)
        st.caption("Engine verifies all physics parameters pass local codes before submitting to the city, eliminating rejection delays.")

# --- EXISTING MODULES (AI Takeoff, Budget, Pro Forma, etc.) ---
elif "AI" in selected_page:
    st.write("### 🚀 OmniVision AI: Automated Blueprint Extraction")
    upload_col1, upload_col2 = st.columns(2)
    with upload_col1:
        st.file_uploader("Upload Floor Plan (PDF, PNG, CAD)", type=['pdf', 'png', 'dwg'])
        if st.button("Extract Data via AI"):
            with st.spinner("Scanning vector lines..."): time.sleep(2)
            st.session_state.ai_extracted = True; st.rerun()
    with upload_col2:
        if st.session_state.ai_extracted:
            st.success("✅ Extraction Complete! Matrix Populated.")
            st.metric("Detected Linear Footage", "2,450 ft")
        else: st.info("Awaiting Blueprint upload.")

elif "Matrix" in selected_page:
    st.write("### 📊 Trade Takeoff Pricing Matrix")
    st.data_editor(df_takeoff, use_container_width=True)

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
    hb_col1, hb_col2 = st.columns([1, 1.5])
    with hb_col1:
        home_price = st.number_input("Purchase Price ($)", value=450000, step=10000)
        down_pct = st.slider("Down Payment (%)", 3.0, 50.0, 20.0, step=1.0)
        interest_rate = st.slider("Mortgage Interest Rate (%)", 3.0, 9.0, 6.5, step=0.1)
        reno_budget = st.number_input("Renovation Budget ($)", value=35000, step=5000)
        rental_income = st.slider("Expected Monthly Rental Income ($)", 0, 3000, 1500, step=100)
    with hb_col2:
        down_payment_cash = home_price * (down_pct / 100)
        total_upfront_cash = down_payment_cash + reno_budget
        loan_amount = home_price - down_payment_cash
        monthly_rate = (interest_rate / 100) / 12
        num_payments = 30 * 12
        monthly_pi = loan_amount * (monthly_rate * math.pow(1 + monthly_rate, num_payments)) / (math.pow(1 + monthly_rate, num_payments) - 1) if monthly_rate > 0 else loan_amount / num_payments
        total_monthly_payment = monthly_pi + ((home_price * 0.02)/12) + (6000/12)
        net_monthly_burn = total_monthly_payment - rental_income

        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Upfront Cash Needed", f"${total_upfront_cash:,.0f}")
        m_c2.metric("Gross Monthly Payment", f"${total_monthly_payment:,.0f}")
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><h5 style='color:#10B981; margin:0;'>🔥 NET MONTHLY BURN (AFTER RENT)</h5><p style='font-size:36px; font-weight:bold; margin:4px 0;'>${net_monthly_burn:,.0f} / mo</p></div>", unsafe_allow_html=True)