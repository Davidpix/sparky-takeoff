import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

st.set_page_config(page_title="OmniBuild OS | Real Estate Platform", layout="wide", initial_sidebar_state="expanded")

# --- STATE MANAGEMENT ---
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = True # Defaulted to True for your sister!
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Operations"
if "ai_extracted" not in st.session_state: st.session_state.ai_extracted = False

# Core App States
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "copper_multiplier" not in st.session_state: st.session_state.copper_multiplier = 0.0

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

# --- PIPELINE MATH ---
df_takeoff = pd.DataFrame([
    {"Item": "3/4\" EMT Conduit", "Phase": "Rough-In", "Qty": 150, "Cost": 6.50, "Mins": 12},
    {"Item": "20A GFCI Device", "Phase": "Trim", "Qty": 25, "Cost": 18.00, "Mins": 15}
])
burdened_rate = st.session_state.rate_journeyman * (1 + st.session_state.labor_burden_pct)
total_mat_cost = (df_takeoff["Qty"] * df_takeoff["Cost"]).sum()
final_burdened_labor_cost = ((df_takeoff["Qty"] * df_takeoff["Mins"]) / 60).sum() * burdened_rate
electrical_subcontract_value = ((total_mat_cost + final_burdened_labor_cost) * (1 + st.session_state.overhead))
master_build_cost = electrical_subcontract_value + st.session_state.gc_plumbing_budget + st.session_state.gc_hvac_budget + st.session_state.gc_framing_drywall + st.session_state.gc_finishes

total_capital_deployed = st.session_state.re_purchase_price + st.session_state.re_holding_costs + master_build_cost
projected_net_profit = st.session_state.re_projected_arv - total_capital_deployed
cash_on_cash_roi = (projected_net_profit / total_capital_deployed) * 100 if total_capital_deployed > 0 else 0

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🏙️ OmniBuild OS")
st.session_state.accessibility_mode = st.sidebar.toggle("🟢 Plain-English Mode", value=st.session_state.accessibility_mode)
st.sidebar.divider()

if st.session_state.accessibility_mode:
    menu_options = ["🏠 Home Overview", "🏡 Homebuyer & House Hack", "📊 Estimate Database", "🏗️ Renovation Budget", "📄 Proposal Builder"]
else:
    menu_options = ["🏠 Home Overview", "🏡 Homebuyer & House Hack", "🚀 AI Auto-Takeoff", "📊 Estimating Matrix", "⚖️ Bid Leveling", "🏗️ GC Master Budget", "🏙️ Investor Pro Forma", "📄 Proposal Builder"]

selected_page = st.sidebar.radio("Navigation:", menu_options)

st.divider()

# --- ROUTING ENGINE ---

if "Home" in selected_page:
    st.write("### 🏠 System Aggregated Command Screen")
    st.success("Platform Systems Optimal. Choose a module from the sidebar to begin.")

elif "Takeoff" in selected_page or "Estimate" in selected_page:
    st.write("### 📊 Trade Takeoff Pricing Matrix")
    st.data_editor(df_takeoff, use_container_width=True)

# --- THE SISTER'S NEW MODULE: HOMEBUYER & HOUSE HACK ---
elif "Homebuyer" in selected_page:
    st.write("### 🏡 Homebuyer Financial & House Hack Analyzer")
    st.caption("Calculate your true upfront cash, monthly mortgage burn, and see how adding an 'Efficiency/ADU' rental offsets your costs in Miami.")
    
    hb_col1, hb_col2 = st.columns([1, 1.5])
    
    with hb_col1:
        st.write("#### 💸 Property & Loan Details")
        home_price = st.number_input("Purchase Price ($)", value=450000, step=10000)
        down_pct = st.slider("Down Payment (%)", 3.0, 50.0, 20.0, step=1.0)
        interest_rate = st.slider("Mortgage Interest Rate (%)", 3.0, 9.0, 6.5, step=0.1)
        
        st.write("#### 🏗️ Renovation & Tax Estimates")
        reno_budget = st.number_input("Renovation Budget (Kitchen/Floors/ADU) ($)", value=35000, step=5000)
        tax_rate = st.slider("Miami Annual Property Tax Rate (%)", 1.5, 2.5, 2.0, step=0.1)
        annual_insurance = st.number_input("Annual Homeowners/Wind Insurance ($)", value=6000, step=500)
        
        st.write("#### 🔑 The 'House Hack' Offset")
        rental_income = st.slider("Expected Monthly Rental Income from ADU/Efficiency ($)", 0, 3000, 1500, step=100)

    with hb_col2:
        # Math Engine
        down_payment_cash = home_price * (down_pct / 100)
        total_upfront_cash = down_payment_cash + reno_budget
        loan_amount = home_price - down_payment_cash
        
        # Standard Amortization Formula: M = P [ r(1 + r)^n ] / [ (1 + r)^n - 1]
        monthly_rate = (interest_rate / 100) / 12
        num_payments = 30 * 12
        if monthly_rate > 0:
            monthly_pi = loan_amount * (monthly_rate * math.pow(1 + monthly_rate, num_payments)) / (math.pow(1 + monthly_rate, num_payments) - 1)
        else:
            monthly_pi = loan_amount / num_payments
            
        monthly_tax = (home_price * (tax_rate / 100)) / 12
        monthly_ins = annual_insurance / 12
        total_monthly_payment = monthly_pi + monthly_tax + monthly_ins
        net_monthly_burn = total_monthly_payment - rental_income

        # Output Metrics
        st.write("#### 💰 Financial Breakdown")
        m_c1, m_c2 = st.columns(2)
        m_c1.metric("Total Upfront Cash Needed", f"${total_upfront_cash:,.0f}", "Down Payment + Reno Cash", delta_color="off")
        m_c2.metric("Total Gross Monthly Payment", f"${total_monthly_payment:,.0f}", "P&I + Taxes + Insurance", delta_color="off")
        
        st.markdown(f"""
        <div class='unifi-stealth-blade' style='border-left-color: #10B981;'>
            <h5 style='color:#10B981; margin:0;'>🔥 NET MONTHLY BURN (AFTER RENTAL INCOME)</h5>
            <p style='font-size:36px; font-weight:bold; margin:4px 0;'>${net_monthly_burn:,.0f} / mo</p>
            <p style='font-size:12px; margin:0;'>By renting the efficiency for ${rental_income}/mo, you are effectively cutting your housing cost dramatically.</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("#### 📈 10-Year Wealth & Equity Projection")
        st.caption("Assumes a conservative 4% annual Miami appreciation rate and standard loan paydown.")
        
        # 10 Year Equity Math Array
        years = list(range(1, 11))
        appreciation_rate = 0.04
        property_values = [home_price * math.pow(1 + appreciation_rate, y) for y in years]
        
        # Calculate remaining balance year by year
        loan_balances = []
        balance = loan_amount
        for y in years:
            for _ in range(12):
                interest_payment = balance * monthly_rate
                principal_payment = monthly_pi - interest_payment
                balance -= principal_payment
            loan_balances.append(balance)
            
        equity_values = [pv - lb for pv, lb in zip(property_values, loan_balances)]
        
        equity_df = pd.DataFrame({
            "Year": years,
            "Property Value": property_values,
            "Remaining Mortgage": loan_balances,
            "Total Equity": equity_values
        })
        
        chart = alt.Chart(equity_df).mark_area(opacity=0.6).encode(
            x=alt.X('Year:O', title='Years Owned'),
            y=alt.Y('Total Equity:Q', title='Net Wealth ($)', axis=alt.Axis(format='$,.0f')),
            tooltip=['Year', alt.Tooltip('Total Equity', format='$,.0f')]
        ).properties(height=200).configure_mark(color='#38BDF8')
        
        st.altair_chart(chart, use_container_width=True)

elif "Budget" in selected_page:
    st.write("### 🏗️ Master Renovation Budget")
    st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>🏗️ TOTAL ESTIMATED RENOVATION BUDGET</h5><h2 style='color:#38BDF8; margin:0;'>${master_build_cost:,.2f}</h2></div>", unsafe_allow_html=True)

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