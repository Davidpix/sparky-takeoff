import streamlit as st
import pandas as pd
import random
import time
import datetime
import math
import altair as alt
from io import BytesIO

st.set_page_config(page_title="OmniBuild OS | Global Enterprise", layout="wide", initial_sidebar_state="expanded")

# --- I18N LOCALIZATION DICTIONARY ---
lang_dict = {
    "English": {
        "home": "🏠 Home Command", "elec": "⚡ Electrical", "plumb": "💧 Plumbing", "hvac": "❄️ HVAC",
        "gc_budg": "🏗️ GC Master Budget", "fin": "💳 FinTech", "sched": "📅 Trade Calendar", "inv": "🧾 AIA Invoicing",
        "welcome": "Platform Systems Optimal. Select a module.", "budget": "Total Build Budget", "sub": "Electrical Sub"
    },
    "Español": {
        "home": "🏠 Inicio", "elec": "⚡ Eléctrico", "plumb": "💧 Plomería", "hvac": "❄️ HVAC",
        "gc_budg": "🏗️ Presupuesto GC", "fin": "💳 Finanzas", "sched": "📅 Calendario de Oficios", "inv": "🧾 Facturación AIA",
        "welcome": "Sistemas óptimos. Seleccione un módulo.", "budget": "Presupuesto Total", "sub": "Subcontrato Eléctrico"
    },
    "Українська": {
        "home": "🏠 Головна панель", "elec": "⚡ Електрика", "plumb": "💧 Сантехніка", "hvac": "❄️ Опалення/Вентиляція",
        "gc_budg": "🏗️ Бюджет GC", "fin": "💳 Фінанси", "sched": "📅 Графік робіт", "inv": "🧾 AIA Фактурування",
        "welcome": "Системи працюють оптимально. Виберіть модуль.", "budget": "Загальний бюджет", "sub": "Електрика"
    }
}

# --- STATE MANAGEMENT ---
if "lang" not in st.session_state: st.session_state.lang = "English"
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False

# --- MULTI-TRADE DATABASES ---
if "df_elec" not in st.session_state:
    st.session_state.df_elec = pd.DataFrame([
        {"Item": "3/4\" EMT Conduit", "Qty": 1500, "Cost": 6.50, "Mins": 12},
        {"Item": "20A GFCI Device", "Qty": 45, "Cost": 18.00, "Mins": 15},
        {"Item": "200A Breaker Panel", "Qty": 2, "Cost": 850.00, "Mins": 240}
    ])
if "df_plumb" not in st.session_state:
    st.session_state.df_plumb = pd.DataFrame([
        {"Item": "2\" Schedule 40 PVC Pipe", "Qty": 400, "Cost": 12.50, "Mins": 15},
        {"Item": "Kohler Elongated Toilet", "Qty": 4, "Cost": 225.00, "Mins": 45},
        {"Item": "50-Gal Rheem Water Heater", "Qty": 1, "Cost": 650.00, "Mins": 120}
    ])
if "df_hvac" not in st.session_state:
    st.session_state.df_hvac = pd.DataFrame([
        {"Item": "Carrier 3-Ton Condenser", "Qty": 1, "Cost": 2100.00, "Mins": 180},
        {"Item": "R8 Flexible Duct (25ft)", "Qty": 10, "Cost": 55.00, "Mins": 45},
        {"Item": "Nest Smart Thermostat", "Qty": 1, "Cost": 199.00, "Mins": 30}
    ])

# Shared Globals
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 
if "prev_billed" not in st.session_state: st.session_state.prev_billed = 25000.0

# --- CORE MATH ENGINE ---
def calc_trade(df):
    mat = (df["Qty"] * df["Cost"]).sum()
    lab = ((df["Qty"] * df["Mins"]) / 60).sum() * st.session_state.labor_rate
    return (mat + lab) * (1 + st.session_state.overhead)

elec_total = calc_trade(st.session_state.df_elec)
plumb_total = calc_trade(st.session_state.df_plumb)
hvac_total = calc_trade(st.session_state.df_hvac)
master_build_cost = elec_total + plumb_total + hvac_total + 35000.0

# --- STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-danger { background-color: #1E1014 !important; border: 1px solid #3B1E22 !important; border-left: 3px solid #EF4444 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
    .unifi-stealth-alert { background-color: #1A1500 !important; border: 1px solid #332A00 !important; border-left: 3px solid #F59E0B !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & LOCALIZATION ---
st.sidebar.title("🌍 OmniBuild OS")

selected_lang = st.sidebar.selectbox("🌐 System Language / Мова", ["English", "Español", "Українська"], index=["English", "Español", "Українська"].index(st.session_state.lang))
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

t = lang_dict[st.session_state.lang]

st.sidebar.divider()
user_market_tier = st.sidebar.selectbox("Simulate Workspace Profile", [
    "🏗️ General Contractor (Admin)",
    "⚡ Electrical Sub",
    "💧 Plumbing Sub",
    "❄️ HVAC Sub"
], index=0)
st.sidebar.divider()

if "General Contractor" in user_market_tier:
    menu_options = [t["home"], t["sched"], t["gc_budg"], t["inv"], t["elec"], t["plumb"], t["hvac"]]
elif "Electrical" in user_market_tier:
    menu_options = [t["home"], t["elec"], t["sched"], t["inv"]]
elif "Plumbing" in user_market_tier:
    menu_options = [t["home"], t["plumb"], t["sched"]]
elif "HVAC" in user_market_tier:
    menu_options = [t["home"], t["hvac"], t["sched"]]

selected_page = st.sidebar.radio("Navigation:", menu_options)
st.divider()

# --- TOP TELEMETRY ---
h_col1, h_col2, h_col3, h_col4 = st.columns(4)
with h_col1: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><p style='margin:0; font-size:10px;'>{t['budget']}</p><h3 style='margin:0; color: #F59E0B;'>${master_build_cost:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col2: st.markdown(f"<div class='unifi-stealth-blade'><p style='margin:0; font-size:10px;'>⚡ {t['sub'] if st.session_state.lang != 'English' else 'Electrical Sub'}</p><h3 style='margin:0;'>${elec_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col3: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #3B82F6;'><p style='margin:0; font-size:10px;'>💧 Plumbing Sub</p><h3 style='margin:0;'>${plumb_total:,.2f}</h3></div>", unsafe_allow_html=True)
with h_col4: st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #8B5CF6;'><p style='margin:0; font-size:10px;'>❄️ HVAC Sub</p><h3 style='margin:0;'>${hvac_total:,.2f}</h3></div>", unsafe_allow_html=True)

# --- ROUTING ENGINE ---

if selected_page == t["home"]:
    st.write(f"### {t['home']}")
    st.success(t["welcome"])

elif selected_page == t["elec"]:
    st.write(f"### {t['elec']}")
    st.session_state.df_elec = st.data_editor(st.session_state.df_elec, use_container_width=True, num_rows="dynamic")

elif selected_page == t["plumb"]:
    st.write(f"### {t['plumb']}")
    st.session_state.df_plumb = st.data_editor(st.session_state.df_plumb, use_container_width=True, num_rows="dynamic")

elif selected_page == t["hvac"]:
    st.write(f"### {t['hvac']}")
    st.session_state.df_hvac = st.data_editor(st.session_state.df_hvac, use_container_width=True, num_rows="dynamic")

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")
    chart_data = pd.DataFrame({"Trade": ["Electrical", "Plumbing", "HVAC", "Framing/Finishes"], "Value ($)": [elec_total, plumb_total, hvac_total, 35000.0]})
    pie = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(theta='Value ($):Q', color=alt.Color('Trade:N', scale=alt.Scale(range=["#38BDF8", "#3B82F6", "#8B5CF6", "#64748B"]))).properties(height=300)
    st.altair_chart(pie, use_container_width=True)

# --- NEW PILLAR: TRADE DECONFLICTION SCHEDULER ---
elif selected_page == t["sched"]:
    st.write(f"### {t['sched']} & Clash Detection")
    st.caption("Visually map trade mobilizations. OmniBuild AI automatically flags scheduling overlaps in the same zone to prevent job site chaos.")
    
    # Simulating Trade Schedules (Intentional Overlap for Demo)
    today = datetime.date.today()
    sched_data = pd.DataFrame([
        {"Trade": "HVAC Rough-In", "Zone": "Zone A (Interior)", "Start": today, "End": today + datetime.timedelta(days=4)},
        {"Trade": "Plumbing Rough-In", "Zone": "Zone A (Interior)", "Start": today + datetime.timedelta(days=2), "End": today + datetime.timedelta(days=6)},
        {"Trade": "Electrical Wire Pull", "Zone": "Zone B (Exterior)", "Start": today + datetime.timedelta(days=5), "End": today + datetime.timedelta(days=8)}
    ])
    
    col_s1, col_s2 = st.columns([2, 1])
    with col_s1:
        chart = alt.Chart(sched_data).mark_bar(cornerRadius=4, height=20).encode(
            x=alt.X('Start:T', title='Timeline'), x2='End:T',
            y=alt.Y('Trade:N', title='', sort=None),
            color=alt.Color('Zone:N', scale=alt.Scale(range=["#EF4444", "#10B981"]))
        ).properties(height=200)
        st.altair_chart(chart, use_container_width=True)
        
    with col_s2:
        st.write("#### 🚨 Collision AI Scanner")
        st.markdown("""
        <div class='unifi-stealth-danger'>
            <h5 style='color:#EF4444; margin:0;'>⚠️ TRADE CLASH DETECTED</h5>
            <p style='font-size:12px; margin:4px 0 0 0;'><b>Plumbing</b> and <b>HVAC</b> are both scheduled to mobilize in <b>Zone A</b> between """ + (today + datetime.timedelta(days=2)).strftime('%b %d') + """ and """ + (today + datetime.timedelta(days=4)).strftime('%b %d') + """. Recommend shifting Plumbing start date to prevent physical interference.</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<div class='unifi-stealth-blade' style='border-left-color: #10B981;'><h5 style='color:#10B981; margin:0;'>✅ Zone B Clear</h5><p style='font-size:12px; margin:4px 0 0 0;'>Electrical path is unobstructed.</p></div>", unsafe_allow_html=True)

# --- NEW PILLAR: AIA PROGRESS INVOICING ---
elif selected_page == t["inv"]:
    st.write(f"### {t['inv']} (G702/G703 Application for Payment)")
    st.caption("Generate legally compliant, standard AIA construction billing applications. Calculates retainage, previous payments, and current amounts due automatically.")
    
    inv_col1, inv_col2 = st.columns([1, 1])
    with inv_col1:
        st.write("#### Billing Period Variables")
        pct_complete = st.slider("Total Project Completion to Date (%)", 0, 100, 60, step=5)
        retainage_pct = st.slider("Contract Retainage Held (%)", 0.0, 10.0, 10.0, step=5.0)
        st.session_state.prev_billed = st.number_input("Less Previous Certificates for Payment ($)", value=st.session_state.prev_billed, step=1000.0)
        
    with inv_col2:
        # Standard AIA Math
        contract_sum = master_build_cost
        total_completed = contract_sum * (pct_complete / 100)
        retainage_held = total_completed * (retainage_pct / 100)
        total_earned_less_ret = total_completed - retainage_held
        current_payment_due = total_earned_less_ret - st.session_state.prev_billed
        
        st.markdown(f"""
        <div style='background-color: #0F172A; padding: 20px; border-radius: 4px; border: 1px solid #1E293B; font-family: monospace;'>
            <h4 style='color:#CBD5E1; margin-top:0;'>APPLICATION FOR PAYMENT</h4>
            <hr style='border-color: #1E293B;'>
            <p>1. ORIGINAL CONTRACT SUM: <span style='float:right;'>${contract_sum:,.2f}</span></p>
            <p>2. TOTAL COMPLETED & STORED: <span style='float:right;'>${total_completed:,.2f}</span></p>
            <p>3. RETAINAGE ({retainage_pct}%): <span style='float:right; color:#EF4444;'>-${retainage_held:,.2f}</span></p>
            <p>4. TOTAL EARNED LESS RETAINAGE: <span style='float:right;'>${total_earned_less_ret:,.2f}</span></p>
            <p>5. LESS PREVIOUS CERTIFICATES: <span style='float:right; color:#EF4444;'>-${st.session_state.prev_billed:,.2f}</span></p>
            <hr style='border-color: #1E293B;'>
            <h3 style='color:#38BDF8; margin-bottom:0;'>6. CURRENT PAYMENT DUE: <span style='float:right;'>${current_payment_due:,.2f}</span></h3>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📥 Generate Official PDF Invoice"):
            st.success("Invoice generated and locked into project ledger.")