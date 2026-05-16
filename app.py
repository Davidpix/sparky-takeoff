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
        "ai_core": "🧠 OmniMind AI Core", "dash": "📊 Telemetry Dashboard", "comm_rollout": "🏢 Commercial Rollout", "api": "☁️ Cloud API"
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

# Persistent state arrays for Commercial Multi-Unit Simulator (Angel's scaling engine)
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame([
        {"Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed"},
        {"Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed"},
        {"Floor": "Floor 02", "Unit Number": "Room 201", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "In Shop Progress", "Installation Status": "Staged On-Site"},
        {"Floor": "Floor 02", "Unit Number": "Room 202", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "In Shop Progress", "Installation Status": "Pending Delivery"},
        {"Floor": "Floor 03", "Unit Number": "Room 301", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Raw Slab Inventory", "Installation Status": "Unscheduled"},
        {"Floor": "Floor 03", "Unit Number": "Room 302", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Raw Slab Inventory", "Installation Status": "Unscheduled"}
    ])

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-green { background-color: #0B1C16 !important; border: 1px solid #143A2E !important; border-left: 3px solid #10B981 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
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

# --- 7. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

# Dynmically adjust menus to include the brand new Commercial Scaling module
menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["api"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 8. MODULE ROUTING CONTAINER ---
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
elif selected_page == t["dash"]: st.write(f"### {t['dash']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# NEW ARCHITECTURE MODULE: COMMERCIAL MULTI-UNIT ROLLOUT TARGET ENGINE
elif selected_page == t["comm_rollout"]:
    st.write(f"### {t['comm_rollout']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Multi-Unit High-Density Real Estate Scaling Portal</b><br>Track room-by-room fabrication streams, floor allocation statuses, and high-volume commercial production velocity metrics.</div>", unsafe_allow_html=True)
    
    # Calculate commercial production telemetry dynamically
    total_units = len(st.session_state.commercial_units)
    installed_units = (st.session_state.commercial_units["Installation Status"] == "Fully Installed").sum()
    rollout_percentage = (installed_units / total_units * 100) if total_units > 0 else 0.0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Project Contract Units", f"{total_units} High-End Suites")
    c2.metric("Handed-Over Fully Installed Rooms", f"{installed_units} / {total_units} Units")
    c3.metric("Project Total Completion Velocity", f"{rollout_percentage:.1f}%")
    
    st.divider()
    
    col_grid, col_visual = st.columns([1.5, 1])
    
    with col_grid:
        st.write("#### 🧱 Multi-Unit Floor Plan Ledger Matrix")
        st.caption("Double-click fields to update stone fabrication pipeline or installation states for hotel tower rollouts:")
        
        updated_comm_df = st.data_editor(st.session_state.commercial_units, use_container_width=True, num_rows="dynamic")
        
        if st.button("💾 Synchronize Commercial Ledger State", use_container_width=True):
            st.session_state.commercial_units = updated_comm_df
            st.success("Commercial multi-unit status matrix cleanly synced!")
            time.sleep(0.5); st.rerun()
            
    with col_visual:
        st.write("#### 📊 Logistics Pipeline Allocation")
        
        # Build an interactive chart breaking down inventory stages for commercial developers
        chart_data = st.session_state.commercial_units.groupby("Fabrication Status").size().reset_name_params = pd.DataFrame(st.session_state.commercial_units["Fabrication Status"].value_counts()).reset_index()
        chart_data.columns = ["Status Phase", "Total Units Count"]
        
        status_chart = alt.Chart(chart_data).mark_bar(cornerRadiusTopRight=3, cornerRadiusBottomRight=3, size=24).encode(
            x=alt.X('Total Units Count:Q', title="Number of High-End Suites"),
            y=alt.Y('Status Phase:N', sort='-x', title=None),
            color=alt.Color('Status Phase:N', scale=alt.Scale(range=['#10B981', '#38BDF8', '#475569']))
        ).properties(height=200, width='container')
        
        st.altair_chart(status_chart, use_container_width=True)
        
        st.markdown("""
        <div class='unifi-stealth-blade' style='border-left-color: #A855F7;'>
            <b>💡 Commercial Scaler Directive:</b><br>
            Export this dashboard view directly to your proposal deck when pitching hotel GCs. Showing an active room-by-room structural delivery matrix instantly proves your 3-man operation possesses enterprise management capability.
        </div>
        """, unsafe_allow_html=True)