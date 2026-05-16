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
        "ai_core": "🧠 OmniMind AI Core", "dash": "📊 Telemetry Dashboard", "comm_rollout": "🏢 Commercial Rollout", 
        "legal_contract": "📝 Master Contracts", "api": "☁️ Cloud API"
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
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame([
        {"Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed"},
        {"Floor": "Floor 01", "Unit Number": "Room 102", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed"}
    ])

# New persistent array tracking legal binding agreement executions
if "contract_agreements" not in st.session_state:
    st.session_state.contract_agreements = []

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .legal-document-scrollbox { background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 30px; font-family: 'Times New Roman', Times, serif; font-size: 14px; line-height: 1.6; border-radius: 4px; height: 400px; overflow-y: scroll; box-shadow: inset 0 0 15px rgba(0,0,0,0.05); }
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
                    st.success("Access Verified.")
                    time.sleep(0.5); st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

t = lang_dict[st.session_state.lang]

# --- 7. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["api"]]

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
elif selected_page == t["comm_rollout"]: st.write(f"### {t['comm_rollout']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# NEW ARCHITECTURE MODULE: SUBCONTRACTOR MASTER AGREEMENT AND CONTRACT EXHIBIT GENERATOR
elif selected_page == t["legal_contract"]:
    st.write(f"### {t['legal_contract']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Enterprise Legal Binding Agreement & Scope Framework Portal</b><br>Compile statutory subcontractor contract agreements, bind scope riders, and track secure cloud digital signatures.</div>", unsafe_allow_html=True)
    
    col_con_form, col_con_view = st.columns([1, 1.3])
    
    # Calculate current scope quantities from Angel's commercial multi-unit rollout tab
    active_unit_count = len(st.session_state.commercial_units)
    estimated_cost_per_unit = 2250.00  # Baseline price target for commercial grade quartz finishes
    calculated_contract_value = active_unit_count * estimated_cost_per_unit
    
    with col_con_form:
        st.write("#### 📜 Standard Subcontract Agreement Parameters")
        prime_contractor = sanitize_input(st.text_input("General Contractor / Owner Entity Name", value="Miami Metro Builders Inc."))
        project_governing_law = st.selectbox("Governing Jurisdiction State", ["Florida", "California", "Texas", "New York"])
        allocated_retainage_pct = st.slider("Contract Retainage Retention Rate (%)", 0, 15, 10)
        
        st.write("##### 📊 Dynamically Amortized Contract Metrics")
        st.metric("Total Project Contract Value", f"${calculated_contract_value:,.2f}", f"Based on {active_unit_count} Active Rooms")
        
        st.write("---")
        authorized_sig_name = st.text_input("Authorized Signatory Corporate Name Label", placeholder="Type full name to digitally execute")
        
        if st.button("🔒 Finalize Document & Bind Contract Exhibit", use_container_width=True):
            if authorized_sig_name and calculated_contract_value > 0:
                new_agreement = {
                    "Doc ID": f"SMA-{len(st.session_state.contract_agreements) + 1:03d}",
                    "GC Entity": prime_contractor,
                    "Contract Value": calculated_contract_value,
                    "Execution Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Signatory": authorized_sig_name,
                    "Status": "Legally Executed & Bound"
                }
                st.session_state.contract_agreements.append(new_agreement)
                # Automatically fuel the locked project escrow pool based on signed commercial value
                st.session_state.escrow_locked += calculated_contract_value
                st.success(f"Contract {new_agreement['Doc ID']} successfully authorized and archived to legal ledger!")
                time.sleep(0.5); st.rerun()
            else:
                st.error("🚨 Signatory authorization validation and active room arrays are strictly required to compile document layers.")

    with col_con_view:
        st.write("#### 📑 Statutory Scope Rider Preview Panel (Exhibit 'A')")
        
        st.markdown(f"""
        <div class='legal-document-scrollbox'>
            <p style='text-align:center; font-weight:bold; font-size:16px; margin-bottom:5px;'>SUBCONTRACTOR MASTER AGREEMENT RIDER</p>
            <p style='text-align:center; font-weight:bold; font-size:12px; margin-bottom:20px;'>EXHIBIT "A" — SCOPE OF WORK ALLOCATION</p>
            
            <p><b>ARTICLE 1. PARTIES & PROJECT INGESTION</b><br>
            This agreement is entered into by and between the Subcontractor <b>({st.session_state.company_name})</b> and the Prime General Contractor Contractor <b>({prime_contractor})</b> regarding multi-unit structural finish integrations located at the Miami Medical Hub development grid.</p>
            
            <p><b>ARTICLE 2. SCOPE OF OPERATIONAL WORK</b><br>
            Subcontractor agrees to perform all technical procurement, fabrication tooling, transportation dispatch, and on-site physical installation mechanics for exactly <b>{active_unit_count} structural multi-unit high-density suites</b> as defined in the Commercial Multi-Unit Rollout Matrix Ledger. All materials utilized shall be premium commercial-grade stone matching architectural parameters perfectly.</p>
            
            <p><b>ARTICLE 3. FINANCIAL COMPENSATION STREAKS</b><br>
            As full compensation for complete performance of field actions, Prime Contractor agrees to compensate Subcontractor the sum total value of <b>${calculated_contract_value:,.2f} USD</b>. Payments shall be disbursed via the OmniPay digital liquidation framework inside progress application billing draws, subject to a fixed <b>{allocated_retainage_pct}% contractual retainage retention lock</b>.</p>
            
            <p><b>ARTICLE 4. GOVERNING COMPLIANCE LAWS</b><br>
            This corporate statutory instrument and all accompanying mechanics shall be governed strictly by the regulations and jurisdiction parameters of the State of <b>{project_governing_law}</b>.</p>
            
            <p style='margin-top:30px; text-transform:uppercase; font-size:11px; tracking-spacing:0.1em; color:#64748B;'>--- End of Active Scope Rider Draft Matrix ---</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.session_state.contract_agreements:
            st.write("---")
            st.write("#### 📋 Signed Legal Archive Ledger")
            contracts_df = pd.DataFrame(st.session_state.contract_agreements)
            st.dataframe(contracts_df, use_container_width=True, hide_index=True)