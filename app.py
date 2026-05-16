import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

st.set_page_config(page_title="OmniBuild OS | Unicorn Enterprise", layout="wide", initial_sidebar_state="expanded")

# --- I18N LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Home Command", "elec": "⚡ Electrical", "plumb": "💧 Plumbing", 
        "gc_budg": "🏗️ GC Master Budget", "fin": "💳 OmniPay & Escrow", "sched": "📅 Trade Calendar", 
        "inv": "🧾 AIA Invoicing", "bid": "🎯 AI Bid Optimizer",
        "budget": "Total Build Budget", "sub": "Electrical Sub"
    },
    "Español": {
        "home": "🏠 Inicio", "elec": "⚡ Eléctrico", "plumb": "💧 Plomería",
        "gc_budg": "🏗️ Presupuesto GC", "fin": "💳 OmniPay y Fideicomiso", "sched": "📅 Calendario", 
        "inv": "🧾 Facturación", "bid": "🎯 Optimizador de IA",
        "budget": "Presupuesto Total", "sub": "Subcontrato Eléctrico"
    },
    "Українська": {
        "home": "🏠 Головна панель", "elec": "⚡ Електрика", "plumb": "💧 Сантехніка",
        "gc_budg": "🏗️ Бюджет GC", "fin": "💳 Фінанси та Ескроу", "sched": "📅 Графік робіт", 
        "inv": "🧾 Фактурування", "bid": "🎯 AI Оптимізатор",
        "budget": "Загальний бюджет", "sub": "Електрика"
    }
}

# --- STATE MANAGEMENT ---
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 12500.00
if "escrow_balance" not in st.session_state: st.session_state.escrow_balance = 0.00
if "lien_signed" not in st.session_state: st.session_state.lien_signed = False

# --- MULTI-TRADE DATABASES ---
if "df_elec" not in st.session_state:
    st.session_state.df_elec = pd.DataFrame([
        {"Item": "3/4\" EMT Conduit", "Qty": 2450, "Cost": 6.50, "Mins": 12},
        {"Item": "20A GFCI Device", "Qty": 45, "Cost": 18.00, "Mins": 15},
        {"Item": "200A Breaker Panel", "Qty": 2, "Cost": 850.00, "Mins": 240}
    ])

if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 

# --- CORE MATH ENGINE ---
def calc_trade(df):
    mat = (df["Qty"] * df["Cost"]).sum()
    lab = ((df["Qty"] * df["Mins"]) / 60).sum() * st.session_state.labor_rate
    return mat, lab

elec_mat, elec_lab = calc_trade(st.session_state.df_elec)
elec_raw_cost = elec_mat + elec_lab
elec_total = elec_raw_cost * (1 + st.session_state.overhead)
master_build_cost = elec_total + 18500.0 + 24000.0 + 35000.0 # Plumbing, HVAC, Finishes

# --- STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-danger { background-color: #1E1014 !important; border: 1px solid #3B1E22 !important; border-left: 3px solid #EF4444 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-gold { background-color: #1A170F !important; border: 1px solid #3B321E !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & LOCALIZATION ---
st.sidebar.title("🌍 OmniBuild OS")

selected_lang = st.sidebar.selectbox("🌐 System Language / Мова", ["English", "Español", "Українська"], index=["English", "Español", "Українська"].index(st.session_state.lang))
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang; st.rerun()

t = lang_dict[st.session_state.lang]

st.sidebar.divider()
user_market_tier = st.sidebar.selectbox("Simulate Workspace Profile", [
    "🏗️ General Contractor (Admin)",
    "⚡ Electrical Sub"
], index=0)
st.sidebar.divider()

if "General Contractor" in user_market_tier:
    menu_options = [t["home"], t["gc_budg"], t["sched"], t["inv"], t["fin"]]
else:
    menu_options = [t["home"], t["elec"], t["bid"], t["fin"]]

selected_page = st.sidebar.radio("Navigation:", menu_options)
st.divider()

# --- TOP TELEMETRY ---
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>{t['budget']}</p><h3 style='margin:0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>⚡ {t['sub']}</p><h3 style='margin:0;'>${elec_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-gold'><p style='margin:0; font-size:10px; color:#F59E0B;'>OmniPay Wallet</p><h3 style='margin:0; color:#F59E0B;'>${st.session_state.wallet_balance:,.2f}</h3></div>", unsafe_allow_html=True)

# --- ROUTING ENGINE ---

if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.success("All systems optimal. Navigation loaded.")

elif selected_page == t["elec"]:
    st.write(f"### {t['elec']}")
    st.session_state.df_elec = st.data_editor(st.session_state.df_elec, use_container_width=True, num_rows="dynamic")

# --- NEW PILLAR 1: AI BID OPTIMIZER ---
elif selected_page == t["bid"]:
    st.write(f"### {t['bid']} & Probability Engine")
    st.caption("Don't guess your margins. The AI analyzes historical market data to show you exactly how much profit you can add before you start losing jobs to competitors.")
    
    bid_c1, bid_c2 = st.columns([1, 1.5])
    with bid_c1:
        st.write("#### 📊 Target Constraints")
        st.info(f"**Calculated Raw Hard Cost (Materials + Labor):** ${elec_raw_cost:,.2f}")
        market_comp = st.selectbox("Market Competition Level", ["High (Residential / Bidding Wars)", "Medium (Commercial Construction)", "Low (Government / Highly Specialized)"], index=1)
        test_margin = st.slider("Simulate Profit Margin (%)", 5, 60, int(st.session_state.overhead * 100))
        
    with bid_c2:
        # Dynamic Probability Math
        margins = list(range(5, 65, 5))
        if "High" in market_comp: drop_factor = 0.08
        elif "Medium" in market_comp: drop_factor = 0.05
        else: drop_factor = 0.03
        
        probabilities = [max(5, 100 * math.exp(-drop_factor * (m - 5))) for m in margins]
        expected_values = [(elec_raw_cost * (m/100)) * (p/100) for m, p in zip(margins, probabilities)]
        
        # Calculate for selected slider
        selected_prob = max(5, 100 * math.exp(-drop_factor * (test_margin - 5)))
        selected_profit = elec_raw_cost * (test_margin / 100)
        selected_ev = selected_profit * (selected_prob / 100)
        
        st.write("#### 🤖 Predictive Intelligence")
        mc1, mc2, mc3 = st.columns(3)
        mc1.metric("Final Bid Price", f"${elec_raw_cost + selected_profit:,.0f}")
        mc2.metric("Win Probability", f"{selected_prob:.1f}%")
        mc3.metric("Expected Value (Sweet Spot)", f"${selected_ev:,.0f}")
        
        df_bid = pd.DataFrame({"Profit Margin (%)": margins, "Expected Value ($)": expected_values})
        chart = alt.Chart(df_bid).mark_area(color="#38BDF8", opacity=0.4).encode(
            x=alt.X('Profit Margin (%):Q', title='Margin Markup'),
            y=alt.Y('Expected Value ($):Q', title='Statistical Value (Profit × Win Rate)'),
            tooltip=['Profit Margin (%)', alt.Tooltip('Expected Value ($)', format='$,.0f')]
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)
        
        if st.button("💾 Lock Margin to Project"):
            st.session_state.overhead = test_margin / 100
            st.success(f"Margin updated to {test_margin}%. Matrix re-calculated.")
            st.rerun()

# --- NEW PILLAR 2: AUTOMATED ESCROW & LIEN WAIVERS ---
elif selected_page == t["fin"]:
    st.write(f"### {t['fin']} & Compliance Vault")
    st.caption("Secure funds in transit. General Contractors deposit funds into Escrow; OmniPay releases the cash to Subcontractors ONLY when digital Lien Waivers are signed.")
    
    fin_c1, fin_c2 = st.columns(2)
    
    with fin_c1:
        st.write("#### 🏗️ General Contractor Controls")
        payment_amt = st.number_input("Amount to pay Electrical Subcontractor ($)", value=25000.0)
        if st.button("🔒 Deposit Funds to Subcontractor Escrow"):
            st.session_state.escrow_balance += payment_amt
            st.session_state.lien_signed = False
            st.success(f"${payment_amt:,.2f} locked in OmniPay Escrow. Awaiting Subcontractor Lien Signature.")
            st.rerun()
            
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #64748B;'><p style='margin:0; font-size:12px;'>Funds Currently in Escrow Vault:</p><h2 style='margin:0; color:#CBD5E1;'>${st.session_state.escrow_balance:,.2f}</h2></div>", unsafe_allow_html=True)

    with fin_c2:
        st.write("#### ⚡ Subcontractor Receivables & Compliance")
        if st.session_state.escrow_balance > 0:
            if not st.session_state.lien_signed:
                st.warning("⚠️ You have funds waiting in Escrow. You must sign the Conditional Lien Waiver to release payment to your OmniWallet.")
                st.markdown("""
                <div style='border:1px dashed #38BDF8; padding:15px; border-radius:4px;'>
                <p style='font-size:12px;'><i>"The undersigned does hereby waive and release any and all lien or claim of, or right to, mechanic's lien on the referenced project."</i></p>
                </div>
                """, unsafe_allow_html=True)
                if st.button("✍️ Digitally Sign Lien Waiver & Release Funds"):
                    st.session_state.lien_signed = True
                    st.session_state.wallet_balance += st.session_state.escrow_balance
                    st.session_state.escrow_balance = 0.0
                    st.success("✅ Lien Waiver Executed. Funds instantly deposited to OmniWallet!")
                    st.rerun()
            else:
                st.success("✅ All Lien Waivers signed. No pending Escrow actions.")
        else:
            st.info("No funds currently waiting in Escrow.")

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")
    st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>🏗️ TOTAL GC BUILD BUDGET</h5><h2 style='color:#38BDF8; margin:0;'>${master_build_cost:,.2f}</h2></div>", unsafe_allow_html=True)

elif selected_page in [t["sched"], t["inv"]]:
    st.write(f"### {selected_page}")
    st.info("System operational. Waiting for schedule data inputs.")