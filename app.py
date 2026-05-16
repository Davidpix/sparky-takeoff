import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests
import altair as alt

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="OmniBuild OS | Enterprise Platform", layout="wide", initial_sidebar_state="expanded")

# --- 2. SECURE CLOUD INITIALIZATION & API HELPERS ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "ENV_VAR_MISSING")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "ENV_VAR_MISSING")

def supabase_api_call(endpoint="materials", method="GET", payload=None, params=None):
    if SUPABASE_URL == "ENV_VAR_MISSING" or SUPABASE_KEY == "ENV_VAR_MISSING":
        return None
    headers = {
        "apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"
    }
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    try:
        if method == "GET": response = requests.get(url, headers=headers, params=params)
        elif method == "POST": response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        return None

def sanitize_input(user_input):
    return html.escape(str(user_input)) if user_input else ""

# --- 3. LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Command Center", "matrix": "📊 Trade Matrix", "takeoff": "📐 Automated Takeoff", "gc_budg": "🏗️ GC Budget", 
        "fin": "💳 OmniPay & Escrow", "bank": "🏦 Bank Portal", "clinic": "🏥 Clinic Infra & Audit", 
        "co_lien": "📝 Change Orders & Liens", "bid": "🎯 AI Bid Optimizer", "sched": "📅 Trade Calendar", 
        "ai_core": "🧠 OmniMind AI Core", "dash": "📊 Telemetry Dashboard", "api": "☁️ Cloud API"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 35000.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 110000.00
if "bank_connected" not in st.session_state: st.session_state.bank_connected = True
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        with st.form("auth_form"):
            input_email = st.text_input("Account Email").strip()
            input_password = st.text_input("Password", type="password").strip()
            if st.form_submit_button("Verify Credentials", use_container_width=True):
                user_query = supabase_api_call(endpoint="user_registry", method="GET", params={"email": f"eq.{input_email}", "password_hash": f"eq.{input_password}"})
                if user_query and len(user_query) > 0:
                    profile = user_query[0]
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = profile["email"]
                    st.session_state.user_role = profile["assigned_role"]
                    st.session_state.company_name = profile["company_name"]
                    st.success("Access Granted.")
                    time.sleep(0.5); st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

t = lang_dict[st.session_state.lang]

# --- 7. CROSS-TABLE DATA EXTRACTIONS ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})
total_labor_hours = 0.0
total_material_cost = 0.0

if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0:
    full_df = pd.DataFrame(raw_cloud_data)
    df_elec_clean = full_df[full_df["trade_type"] == "Electrical"]
    total_material_cost = (df_elec_clean["quantity"] * df_elec_clean["cost_per_unit"]).sum()
    total_labor_hours = ((df_elec_clean["quantity"] * df_elec_clean["labor_minutes"]) / 60).sum()

calculated_duration_days = max(1, math.ceil(total_labor_hours / 8)) if total_labor_hours > 0 else 5

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

if "General Contractor" in st.session_state.user_role:
    menu_options = [t["home"], t["gc_budg"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["api"]]
else:
    menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["api"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]: st.write(f"### {t['home']}")
elif selected_page == t["matrix"]: st.write(f"### {t['matrix']}")
elif selected_page == t["takeoff"]: st.write(f"### {t['takeoff']}")
elif selected_page == t["bid"]: st.write(f"### {t['bid']}")
elif selected_page == t["clinic"]: st.write(f"### {t['clinic']}")
elif selected_page == t["co_lien"]: st.write(f"### {t['co_lien']}")
elif selected_page == t["fin"]: st.write(f"### {t['fin']}")
elif selected_page == t["bank"]: st.write(f"### {t['bank']}")
elif selected_page == t["sched"]: st.write(f"### {t['sched']}")
elif selected_page == t["ai_core"]: st.write(f"### {t['ai_core']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# NEW ARCHITECTURE MODULE: VISUAL TELEMETRY ANALYTICS DASHBOARD
elif selected_page == t["dash"]:
    st.write(f"### {t['dash']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Executive Telemetry Control Panel</b><br>High-fidelity dynamic charting mapping production burn rates and cash runway velocities.</div>", unsafe_allow_html=True)
    
    # Grid Row 1: Key Performance Metrics
    kpi1, kpi2, kpi3 = st.columns(3)
    kpi1.metric("Escrow Liquidation Runway", f"${st.session_state.escrow_locked:,.2f}", "+12.4%")
    kpi2.metric("Liquid Capital Density", f"${st.session_state.wallet_balance:,.2f}", "+5.2%")
    kpi3.metric("Project Production Velocity", f"{calculated_duration_days} Days", "On Target")
    
    st.divider()
    
    # Grid Row 2: Visual Chart Paneling
    col_chart_left, col_chart_right = st.columns(2)
    
    with col_chart_left:
        st.write("#### 📈 Financial Runway Variance (Weekly Projection)")
        # Simulated chronological trend line tracking funding depletion curves
        runway_data = pd.DataFrame({
            "Project Week": ["Week 1", "Week 2", "Week 3", "Week 4", "Week 5"],
            "Locked Escrow ($)": [st.session_state.escrow_locked + 20000, st.session_state.escrow_locked + 10000, st.session_state.escrow_locked, st.session_state.escrow_locked - 15000, st.session_state.escrow_locked - 30000],
            "Liquid Wallet ($)": [15000, 25000, st.session_state.wallet_balance, st.session_state.wallet_balance + 10000, st.session_state.wallet_balance + 25000]
        }).melt("Project Week", var_name="Financial Account", value_name="Balance ($)")
        
        line_chart = alt.Chart(runway_data).mark_line(point=True, strokeWidth=3).encode(
            x='Project Week:N',
            y='Balance ($):Q',
            color=alt.Color('Financial Account:N', scale=alt.Scale(range=['#F59E0B', '#10B981']))
        ).properties(height=300, width='container')
        
        st.altair_chart(line_chart, use_container_width=True)
        
    with col_chart_right:
        st.write("#### 📊 Labor Deployment Burn (Estimated vs Actual Hours)")
        # Simulated labor matrix values mapping operational metrics
        labor_burn_data = pd.DataFrame({
            "Trade Vector": ["Conduit Routing", "Device Install", "Panel Termination", "System Tuning"],
            "Estimated Hours": [total_labor_hours * 0.4, total_labor_hours * 0.3, total_labor_hours * 0.2, total_labor_hours * 0.1],
            "Actual Consumed": [total_labor_hours * 0.38, total_labor_hours * 0.25, 0.0, 0.0]
        }).melt("Trade Vector", var_name="Time Metric", value_name="Man-Hours")
        
        bar_chart = alt.Chart(labor_burn_data).mark_bar(cornerRadiusTopLeft=3, cornerRadiusTopRight=3).encode(
            x=alt.X('Time Metric:N', title=None),
            y=alt.Y('Man-Hours:Q', title="Hours Spent"),
            color=alt.Color('Time Metric:N', scale=alt.Scale(range=['#38BDF8', '#475569'])),
            column=alt.Column('Trade Vector:N', title=None)
        ).properties(height=280, width=100)
        
        st.altair_chart(bar_chart, use_container_width=True)