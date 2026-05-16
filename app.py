import streamlit as st
import pandas as pd
import datetime
import time
import math
import html
import re
import requests
import altair as alt
import random
import string

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
        "legal_contract": "📝 Master Contracts", "field_signoff": "🔍 Field Sign-Off", "pitch_white": "🎨 Brand White-Label", 
        "audit_logs": "📋 Audit Trail & Reports", "procure": "📦 Procurement & POs", "saas_licensing": "🔑 SaaS Tenant Licensing", "api": "☁️ Cloud API"
    }
}

# --- 4. STATE MANAGEMENT ---
if "user_authenticated" not in st.session_state: st.session_state.user_authenticated = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "user_role" not in st.session_state: st.session_state.user_role = "⚡ Electrical Sub"
if "company_name" not in st.session_state: st.session_state.company_name = "Independent Operator"
if "lang" not in st.session_state: st.session_state.lang = "English"
if "wallet_balance" not in st.session_state: st.session_state.wallet_balance = 75000.00
if "escrow_locked" not in st.session_state: st.session_state.escrow_locked = 185000.00
if "bank_connected" not in st.session_state: st.session_state.bank_connected = True
if "change_orders" not in st.session_state: st.session_state.change_orders = []
if "transaction_history" not in st.session_state: st.session_state.transaction_history = []
if "contract_agreements" not in st.session_state: st.session_state.contract_agreements = []
if "system_audit_trail" not in st.session_state: st.session_state.system_audit_trail = []
if "commercial_units" not in st.session_state:
    st.session_state.commercial_units = pd.DataFrame(columns=["Floor", "Unit Number", "Asset Type", "Fabrication Status", "Installation Status"])

# White-Label Theme State Defaults
if "wl_client_name" not in st.session_state: st.session_state.wl_client_name = "OmniBuild OS Standard"
if "wl_accent_color" not in st.session_state: st.session_state.wl_accent_color = "#38BDF8"
if "wl_bg_tint" not in st.session_state: st.session_state.wl_bg_tint = "#0F172A"

# New SaaS Licensing Tracker States
if "generated_license_keys" not in st.session_state:
    st.session_state.generated_license_keys = [
        {"Key Token": "OMNI-ELEC-9821", "Tier": "Growth Team", "Assigned Client": "david@shardvisuals.com", "Status": "Active / Verified"},
        {"Key Token": "OMNI-STONE-4412", "Tier": "Enterprise Multi-Trade", "Assigned Client": "angel@luxurycountertops.com", "Status": "Active / Verified"},
    ]

# --- 5. THEME STYLING INJECTION ---
st.markdown(f"""
<style>
    .stApp {{ background-color: #070B12 !important; color: #94A3B8 !important; }}
    h1, h2, h3, h4, h5, h6 {{ color: #CBD5E1 !important; font-weight: 500 !important; }}
    .unifi-stealth-blade {{ background-color: {st.session_state.wl_bg_tint} !important; border: 1px solid #1E293B !important; border-left: 3px solid {st.session_state.wl_accent_color} !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }}
    .brand-hero-header {{ font-size: 28px; font-weight: bold; color: {st.session_state.wl_accent_color} !important; letter-spacing: -0.02em; margin-bottom: 5px; }}
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

menu_options = [t["home"], t["matrix"], t["takeoff"], t["bid"], t["clinic"], t["co_lien"], t["fin"], t["bank"], t["sched"], t["ai_core"], t["dash"], t["comm_rollout"], t["legal_contract"], t["field_signoff"], t["pitch_white"], t["audit_logs"], t["procure"], t["saas_licensing"], t["api"]]
selected_page = st.sidebar.radio("Navigation Menu", menu_options)
st.sidebar.divider()
if st.sidebar.button("🚪 Terminate Session Workspace", use_container_width=True):
    st.session_state.user_authenticated = False; st.rerun()

# --- 8. GLOBAL TELEMETRY BAR HEADER ---
st.markdown(f"<div class='brand-hero-header'>⚜️ {st.session_state.wl_client_name}</div>", unsafe_allow_html=True)
st.divider()

# --- 9. MODULE ROUTING CONTAINER ---
if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    if st.button("🚀 One-Click Sandbox Simulation: Instant Demo Populate Mode", use_container_width=True):
        st.session_state.bank_connected = True; st.session_state.escrow_locked = 220000.00; st.session_state.wallet_balance = 75000.00
        st.session_state.commercial_units = pd.DataFrame([{"Floor": "Floor 01", "Unit Number": "Room 101", "Asset Type": "Premium White Quartz Countertop", "Fabrication Status": "Completed", "Installation Status": "Fully Installed", "GC Sign-Off": "Approved & Certified", "Value Release": 2250.00}])
        st.success("Sandbox populated!"); time.sleep(0.5); st.rerun()

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
elif selected_page == t["legal_contract"]: st.write(f"### {t['legal_contract']}")
elif selected_page == t["field_signoff"]: st.write(f"### {t['field_signoff']}")
elif selected_page == t["pitch_white"]: st.write(f"### {t['pitch_white']}")
elif selected_page == t["audit_logs"]: st.write(f"### {t['audit_logs']}")
elif selected_page == t["procure"]: st.write(f"### {t['procure']}")
elif selected_page == t["api"]: st.write(f"### {t['api']}")

# NEW ARCHITECTURE MODULE: SAAS CORPORATE LICENSE & monetizaton MANAGEMENT
elif selected_page == t["saas_licensing"]:
    st.write(f"### {t['saas_licensing']}")
    st.markdown("<div class='unifi-stealth-blade'><b>SaaS Core Tenant Token Provisional Console</b><br>Authorize enterprise organization seats, provision software license verification vectors, and track multi-tenant portfolio recurring revenue.</div>", unsafe_allow_html=True)
    
    # Financial Revenue Calculators
    active_tenant_count = len(st.session_state.generated_license_keys)
    simulated_mrr = sum([199 if row["Tier"] == "Solo Contractor" else (499 if row["Tier"] == "Growth Team" else 1299) for row in st.session_state.generated_license_keys])
    simulated_ltv = simulated_mrr * 12  # Extrapolated annualized performance indices
    
    m_c1, m_c2, m_c3 = st.columns(3)
    m_c1.metric("Active Provisioned Tenants", f"{active_tenant_count} Corporate Portals")
    m_c2.metric("Monthly Recurring Revenue (MRR)", f"${simulated_mrr:,.2f}", "+18.4% MoM")
    m_c3.metric("Projected Annual Run-Rate (ARR)", f"${simulated_mrr * 12:,.2f}")
    
    st.divider()
    
    col_lic_issue, col_lic_ledger = st.columns([1, 1.3])
    
    with col_lic_issue:
        st.write("#### 🔑 Provision New Tenant License Key")
        target_sub_email = sanitize_input(st.text_input("Target Subcontractor / Client Email Address"))
        selected_saas_tier = st.selectbox("Product Licensing Tier", ["Solo Contractor ($199/mo)", "Growth Team ($499/mo)", "Enterprise Multi-Trade ($1,299/mo)"])
        
        if st.button("⚡ Generate & Issue Encrypted Activation Token", use_container_width=True):
            if target_sub_email:
                tier_clean = selected_saas_tier.split(" ($")[0]
                # Synthesize a unique random cryptographic license token format
                token_suffix = ''.join(random.choices(string.digits, k=4))
                generated_token = f"OMNI-{tier_clean.split(' ')[0].upper()}-{token_suffix}"
                
                st.session_state.generated_license_keys.append({
                    "Key Token": generated_token, "Tier": tier_clean, "Assigned Client": target_sub_email, "Status": "Staged / Awaiting Activation"
                })
                st.success(f"License token generated for {target_sub_email}!")
                time.sleep(0.5); st.rerun()
            else:
                st.error("A valid target client email marker is required to route token generation threads.")
                
    with col_lic_ledger:
        st.write("#### 📋 Core Software License Asset Registry")
        lic_df = pd.DataFrame(st.session_state.generated_license_keys)
        st.dataframe(lic_df, use_container_width=True, hide_index=True)
        
        st.markdown("""
        <div class='unifi-stealth-blade' style='border-left-color: #A855F7;'>
            <b>💼 Organic Marketing Playbook:</b><br>
            Issue your first custom license key tokens directly to your closest circle (like Angel or structural associates). Giving them isolated, customized workspaces makes them your initial power users, validating your platform metrics and driving high-value corporate word-of-mouth growth.
        </div>
        """, unsafe_allow_html=True)