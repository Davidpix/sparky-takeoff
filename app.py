import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

# --- SUPABASE & API LIBRARIES (Simulated for Prototype) ---
# In production, you will run: pip install supabase requests
# from supabase import create_client, Client
# import requests

st.set_page_config(page_title="OmniBuild OS | Production Release", layout="wide", initial_sidebar_state="expanded")

# --- I18N LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Home Command", "elec": "⚡ Electrical", 
        "fin": "💳 OmniPay & Escrow", "api": "☁️ Cloud & QuickBooks API",
        "budget": "Total Build Budget", "sub": "Electrical Sub"
    },
    "Español": {
        "home": "🏠 Inicio", "elec": "⚡ Eléctrico",
        "fin": "💳 OmniPay y Fideicomiso", "api": "☁️ Nube y API QuickBooks",
        "budget": "Presupuesto Total", "sub": "Subcontrato Eléctrico"
    },
    "Українська": {
        "home": "🏠 Головна панель", "elec": "⚡ Електрика",
        "fin": "💳 Фінанси та Ескроу", "api": "☁️ Хмара та QuickBooks API",
        "budget": "Загальний бюджет", "sub": "Електрика"
    }
}

# --- STATE MANAGEMENT ---
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 12500.00
if "qb_connected" not in st.session_state: st.session_state.qb_connected = False
if "db_connected" not in st.session_state: st.session_state.db_connected = False
if "sync_logs" not in st.session_state: st.session_state.sync_logs = []

# --- DATABASES ---
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
master_build_cost = elec_total + 77500.0 # Arbitrary combined GC costs for demo

# --- STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-danger { background-color: #1E1014 !important; border: 1px solid #3B1E22 !important; border-left: 3px solid #EF4444 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .cyber-terminal { background-color: #030712; border: 1px solid #1E293B; padding: 15px; border-radius: 4px; font-family: monospace; color: #34D399; height: 200px; overflow-y: auto; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("🌍 OmniBuild OS")

selected_lang = st.sidebar.selectbox("🌐 System Language", ["English", "Español", "Українська"], index=["English", "Español", "Українська"].index(st.session_state.lang))
if selected_lang != st.session_state.lang: st.session_state.lang = selected_lang; st.rerun()
t = lang_dict[st.session_state.lang]

st.sidebar.divider()
menu_options = [t["home"], t["elec"], t["fin"], t["api"]]
selected_page = st.sidebar.radio("Navigation:", menu_options)
st.divider()

# --- TOP TELEMETRY ---
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>{t['budget']}</p><h3 style='margin:0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>⚡ {t['sub']}</p><h3 style='margin:0;'>${elec_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><p style='margin:0; font-size:10px;'>OmniPay Wallet</p><h3 style='margin:0; color:#10B981;'>${st.session_state.wallet_balance:,.2f}</h3></div>", unsafe_allow_html=True)

# --- ROUTING ENGINE ---

if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.success("All systems optimal. Welcome to OmniBuild Production.")

elif selected_page == t["elec"]:
    st.write(f"### {t['elec']}")
    st.session_state.df_elec = st.data_editor(st.session_state.df_elec, use_container_width=True, num_rows="dynamic")

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    st.write("#### ⚡ Instant Invoice Factoring")
    advance_pct = st.slider("Select Advance Amount (%)", 10, 100, 100, step=10)
    advance_amount = 24500.00 * (advance_pct / 100)
    net_payout = advance_amount - (advance_amount * 0.025)
    
    if st.button("💸 Advance Funds to Wallet Now"):
        st.session_state.wallet_balance += net_payout
        st.session_state.sync_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] OMNIPAY: Transferred ${net_payout:,.2f} to Wallet.")
        
        # TRIGGER QUICKBOOKS SYNC IF CONNECTED
        if st.session_state.qb_connected:
            st.session_state.sync_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] QUICKBOOKS API: Pushed Journal Entry - DEBIT Cash ${net_payout:,.2f}, CREDIT Accounts Receivable ${net_payout:,.2f}")
        
        st.success(f"✅ ${net_payout:,.2f} deposited to your OmniWallet.")
        st.rerun()

# --- THE NEW CLOUD & API PILLAR ---
elif selected_page == t["api"]:
    st.write(f"### {t['api']}")
    st.caption("Manage your production infrastructure. Connect to your Supabase PostgreSQL cluster and link your accounting software.")
    
    api_c1, api_c2 = st.columns(2)
    
    with api_c1:
        st.write("#### 🐘 Supabase Database Connection")
        st.text_input("Supabase Project URL", value="https://xyz123.supabase.co" if st.session_state.db_connected else "", type="password")
        st.text_input("Supabase API Key", value="ey..." if st.session_state.db_connected else "", type="password")
        
        if not st.session_state.db_connected:
            if st.button("🔌 Initialize Cloud Database"):
                with st.spinner("Connecting to PostgreSQL Cluster..."): time.sleep(1.5)
                st.session_state.db_connected = True
                st.session_state.sync_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] SUPABASE: Authenticated and connected to cluster.")
                st.rerun()
        else:
            st.markdown("<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><b>✅ Status: Online.</b> Real-time syncing active.</div>", unsafe_allow_html=True)
            
    with api_c2:
        st.write("#### 📗 QuickBooks Online API via OAuth 2.0")
        st.text_input("Intuit Client ID", value="ABcDeF..." if st.session_state.qb_connected else "", type="password")
        
        if not st.session_state.qb_connected:
            if st.button("🔗 Authenticate with QuickBooks"):
                with st.spinner("Executing OAuth 2.0 Handshake with Intuit Servers..."): time.sleep(2)
                st.session_state.qb_connected = True
                st.session_state.sync_logs.append(f"[{datetime.datetime.now().strftime('%H:%M:%S')}] QUICKBOOKS API: OAuth Token received. Ledger sync active.")
                st.rerun()
        else:
            st.markdown("<div class='unifi-stealth-blade' style='border-left-color:#10B981;'><b>✅ Status: Authenticated.</b> OmniPay transactions will automatically post to your General Ledger.</div>", unsafe_allow_html=True)

    st.divider()
    st.write("#### 🖥️ Live API Telemetry Stream")
    if len(st.session_state.sync_logs) == 0:
        st.markdown("<div class='cyber-terminal'>Awaiting system events...</div>", unsafe_allow_html=True)
    else:
        log_html = "<br>".join(st.session_state.sync_logs[::-1])
        st.markdown(f"<div class='cyber-terminal'>{log_html}</div>", unsafe_allow_html=True)