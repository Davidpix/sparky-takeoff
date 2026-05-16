import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests

# --- 1. SET PAGE CONFIG ---
st.set_page_config(page_title="OmniBuild OS | Enterprise Platform", layout="wide", initial_sidebar_state="expanded")

# --- 2. SECURE CLOUD INITIALIZATION & API HELPERS ---
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "ENV_VAR_MISSING")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "ENV_VAR_MISSING")

def supabase_api_call(endpoint="materials", method="GET", payload=None, params=None):
    if SUPABASE_URL == "ENV_VAR_MISSING" or SUPABASE_KEY == "ENV_VAR_MISSING":
        return None
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation" if method in ["POST", "PATCH"] else ""
    }
    url = f"{SUPABASE_URL}/rest/v1/{endpoint}"
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, params=params)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=payload)
        return response.json()
    except Exception as e:
        st.error(f"Cloud communication error: {e}")
        return None

def sanitize_input(user_input):
    return html.escape(str(user_input)) if user_input else ""

# --- 3. LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Command Center", "matrix": "📊 Trade Matrix", "takeoff": "📐 Automated Takeoff", "gc_budg": "🏗️ GC Budget", 
        "fin": "💳 OmniPay & Escrow", "sched": "📅 Trade Calendar", "inv": "🧾 Progress Billings", 
        "bid": "🎯 AI Bid Optimizer", "clinic": "🏥 Clinic Infra & Audit", "co_lien": "📝 Change Orders & Liens", "api": "☁️ Cloud API",
        "budget": "Master Budget", "wallet": "OmniWallet"
    },
    "Español": {
        "home": "🏠 Centro de Mando", "matrix": "📊 Matriz de Oficio", "takeoff": "📐 Despegue Automatizado", "gc_budg": "🏗️ Presupuesto GC",
        "fin": "💳 OmniPay y Fideicomiso", "sched": "📅 Calendario", "inv": "🧾 Facturación de Progreso",
        "bid": "🎯 Optimizador IA", "clinic": "🏥 Infraestructura Clínica", "co_lien": "📝 Órdenes de Cambio", "api": "☁️ API en la Nube",
        "budget": "Presupuesto Maestro", "wallet": "Billetera Omni"
    },
    "Українська": {
        "home": "🏠 Головна панель", "matrix": "📊 Кошторисна матриця", "takeoff": "📐 Авто-Кошторис", "gc_budg": "🏗️ Бюджет GC",
        "fin": "💳 Фінанси та Ескроу", "sched": "📅 Графік робіт", "inv": "🧾 Прогресивне виставлення рахунків",
        "bid": "🎯 AI Оптимізатор", "clinic": "🏥 Клінічна Інфраструктура", "co_lien": "📝 Зміни та Відмови від Прав", "api": "☁️ Хмарний API",
        "budget": "Головний бюджет", "wallet": "Гаманець Omni"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 12500.00
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 

# Persistent state for Change Orders
if "change_orders" not in st.session_state:
    st.session_state.change_orders = []

# --- 5. STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .legal-document-container { background-color: #F8FAFC !important; color: #0F172A !important; border: 1px solid #E2E8F0 !important; padding: 25px; font-family: 'Times New Roman', Times, serif; font-size: 14px; line-height: 1.5; border-radius: 4px; box-shadow: inset 0 0 10px rgba(0,0,0,0.05); }
</style>
""", unsafe_allow_html=True)

# --- 6. AUTHENTICATION GATEWAY ---
if not st.session_state.user_authenticated:
    st.markdown("<div style='text-align:center; padding:40px;'><h1>🔐 OmniBuild OS</h1><p>Enterprise Multi-User Authentication Gateway</p></div>", unsafe_allow_html=True)
    tab_login, tab_register = st.tabs(["🔒 Secure Login", "📝 Beta Account Registration"])
    with tab_login:
        with st.form("auth_form"):
            input_email = st.text_input("Account Email / Username").strip()
            input_password = st.text_input("Secure Password", type="password").strip()
            if st.form_submit_button("Verify Credentials", use_container_width=True):
                user_query = supabase_api_call(endpoint="user_registry", method="GET", params={"email": f"eq.{input_email}", "password_hash": f"eq.{input_password}"})
                if user_query and len(user_query) > 0:
                    profile = user_query[0]
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = profile["email"]
                    st.session_state.user_role = profile["assigned_role"]
                    st.session_state.company_name = profile["company_name"]
                    st.success("Authentication successful!")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Invalid credentials.")
    st.stop()

# --- 7. DYNAMIC CONTRACT CALCULATIONS ---
raw_cloud_data = supabase_api_call(endpoint="materials", method="GET", params={"user_email": f"eq.{st.session_state.user_email}"})
if raw_cloud_data and not isinstance(raw_cloud_data, dict) and len(raw_cloud_data) > 0:
    full_df = pd.DataFrame(raw_cloud_data)
    df_elec_clean = full_df[full_df["trade_type"] == "Electrical"]
    mat_sum = (df_elec_clean["quantity"] * df_elec_clean["cost_per_unit"]).sum()
    lab_sum = ((df_elec_clean["quantity"] * df_elec_clean["labor_minutes"]) / 60).sum() * st.session_state.labor_rate
    elec_base_total = (mat_sum + lab_sum) * (1 + st.session_state.overhead)
else:
    elec_base_total = 0.0

# Add approved change order totals dynamically to the base values
approved_co_total = sum(co["Cost Impact"] for co in st.session_state.change_orders if co["Status"] == "Approved & Signed")
current_contract_total = elec_base_total + approved_co_total

# --- 8. SIDEBAR CONTROL PANEL ---
st.sidebar.title("🌍 OmniBuild OS")
selected_lang = st.sidebar.selectbox("🌐 Language", ["English", "Español", "Українська"], index=0)
t = lang_dict[selected_lang]

st.sidebar.divider()
st.sidebar.write(f"👤 **User:** `{st.session_state.user_email}`")
st.sidebar.write(f"🏢 **Entity:** `{st.session_state.company_name}`")
st.sidebar.divider()

if "General Contractor" in st.session_state.user_role:
    menu_options = [t["home"], t["gc_budg"], t["clinic"], t["co_lien"], t["api"]]
else:
    menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["inv"], t["clinic"], t["co_lien"], t["api"]]

selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 9. TOP TELEMETRY MATRIX ---
h_col1, h_col2, h_col3 = st.columns(3)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>Active Contract Value</p><h3 style='margin:0; color: #F59E0B;'>${current_contract_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>Approved Scope Changes</p><h3 style='margin:0;'>${approved_co_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><p style='margin:0; font-size:10px;'>{t['wallet']}</p><h3 style='margin:0; color:#10B981;'>${st.session_state.wallet_balance:,.2f}</h3></div>", unsafe_allow_html=True)

# --- 10. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.markdown(f"<div class='unifi-stealth-blade'>Authorized Account Node: <b>{st.session_state.company_name}</b></div>", unsafe_allow_html=True)

elif selected_page == t["matrix"]:
    st.write(f"### {t['matrix']}")

elif selected_page == t["takeoff"]:
    st.write(f"### {t['takeoff']}")

elif selected_page == t["bid"]:
    st.write(f"### {t['bid']}")

elif selected_page == t["inv"]:
    st.write(f"### {t['inv']}")

elif selected_page == t["clinic"]:
    st.write(f"### {t['clinic']}")

# NEW ARCHITECTURE MODULE: CHANGE ORDERS & LEGAL LIEN WAIVERS
elif selected_page == t["co_lien"]:
    st.write(f"### {t['co_lien']}")
    st.markdown("<div class='unifi-stealth-blade'><b>Contract Variance Control & Compliance Dashboard</b><br>Authorize contract adjustments, track pricing changes, and issue corresponding statutory conditional lien releases.</div>", unsafe_allow_html=True)
    
    col_co_form, col_co_ledger = st.columns([1, 1.2])
    
    with col_co_form:
        st.write("#### 🛠️ Draft New Scope Variation")
        with st.form("change_order_form"):
            co_title = st.text_input("Change Order Description / Title", placeholder="e.g., Add 4 data drops in Consult Room 2")
            co_reason = st.text_area("Scope Justification", placeholder="Owner requested relocation of secure workstation nodes.")
            co_cost = st.number_input("Total Financial Impact ($)", min_value=0.0, value=1250.00)
            co_days = st.number_input("Project Schedule Extension Impact (Days)", min_value=0, value=1)
            
            if st.form_submit_button("Stage Change Order Document", use_container_width=True):
                if co_title and co_cost > 0:
                    new_co = {
                        "ID": f"PCO-{len(st.session_state.change_orders) + 1:03d}",
                        "Title": co_title,
                        "Reason": co_reason,
                        "Cost Impact": co_cost,
                        "Schedule Impact": f"+{co_days} Days",
                        "Status": "Pending Review"
                    }
                    st.session_state.change_orders.append(new_co)
                    st.success(f"Successfully staged contract modification {new_co['ID']}!")
                    st.rerun()
                else: st.error("A comprehensive description and cost analysis value are required.")

    with col_co_ledger:
        st.write("#### 🧾 Active Modification Ledger")
        if not st.session_state.change_orders:
            st.caption("No variance documents or change orders have been registered for this contract scope.")
        else:
            for idx, co in enumerate(st.session_state.change_orders):
                with st.expander(f"📄 {co['ID']}: {co['Title']} — **{co['Status']}**"):
                    st.write(f"**Justification:** {co['Reason']}")
                    st.write(f"**Financial Adjustment:** `${co['Cost Impact']:,.2f}`")
                    st.write(f"**Schedule Variation:** {co['Schedule Impact']}")
                    
                    if co["Status"] == "Pending Review":
                        st.write("---")
                        st.write("##### ⚖️ Accompanying Legal Document Generated:")
                        
                        # Legal Statutory Conditional Waiver Template Layout
                        st.markdown(f"""
                        <div class='legal-document-container'>
                            <p style='text-align:center; font-weight:bold; margin-bottom:15px;'>CONDITIONAL WAIVER AND RELEASE UPON PROGRESS PAYMENT</p>
                            <p><b>Project Name:</b> Miami Medical Hub Renovation<br>
                            <b>Subcontractor Entity:</b> {st.session_state.company_name}<br>
                            <b>Sum Value:</b> ${co['Cost Impact']:,.2f} USD</p>
                            <p style='text-indent: 30px; text-align: justify;'>Upon receipt by the undersigned of a check from the Prime Contractor in the sum of <b>${co['Cost Impact']:,.2f}</b> payable to <b>{st.session_state.company_name}</b> and when the check has been properly endorsed and has cleared the bank, this document shall become effective to release any mechanic's lien, stop notice, or bond right the undersigned has on the job of the owner to the extent of this scope modification variation.</p>
                            <p style='margin-top:20px; font-style:italic;'>Executed Digitally Secure via OmniBuild Compliance Engine System Stack.</p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🖋️ Execute Signature & Approve {co['ID']}", key=f"sig_{idx}", use_container_width=True):
                            st.session_state.change_orders[idx]["Status"] = "Approved & Signed"
                            st.toast(f"{co['ID']} approved! Contract parameters reallocated.", icon="✅")
                            time.sleep(0.5)
                            st.rerun()

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")

elif selected_page == t["api"]:
    st.write(f"### {t['api']}")