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
        "home": "🏠 Home Command", "elec": "⚡ Electrical Takeoff", "plumb": "💧 Plumbing Takeoff", "hvac": "❄️ HVAC Takeoff",
        "gc_budg": "🏗️ GC Master Budget", "fin": "💳 OmniPay FinTech", "ai": "🚀 AI Blueprint Scan",
        "welcome": "Platform Systems Optimal. Select a module.", "budget": "Total GC Build Budget", "sub": "Electrical Subcontract", "settings": "⚙️ Settings"
    },
    "Español": {
        "home": "🏠 Inicio (Comando)", "elec": "⚡ Presupuesto Eléctrico", "plumb": "💧 Presupuesto Plomería", "hvac": "❄️ Presupuesto HVAC",
        "gc_budg": "🏗️ Presupuesto Maestro GC", "fin": "💳 Finanzas OmniPay", "ai": "🚀 Escaneo Plano IA",
        "welcome": "Sistemas óptimos. Seleccione un módulo.", "budget": "Presupuesto Total de Construcción", "sub": "Subcontrato Eléctrico", "settings": "⚙️ Configuraciones"
    },
    "Українська": {
        "home": "🏠 Головна панель", "elec": "⚡ Електричний кошторис", "plumb": "💧 Сантехнічний кошторис", "hvac": "❄️ HVAC Кошторис",
        "gc_budg": "🏗️ Загальний бюджет підрядника", "fin": "💳 Фінанси OmniPay", "ai": "🚀 AI Сканування креслень",
        "welcome": "Системи працюють оптимально. Виберіть модуль.", "budget": "Загальний бюджет будівництва", "sub": "Електричний субпідряд", "settings": "⚙️ Налаштування"
    }
}

# --- STATE MANAGEMENT ---
if "lang" not in st.session_state: st.session_state.lang = "English"
if "accessibility_mode" not in st.session_state: st.session_state.accessibility_mode = False
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Operations"

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
        {"Item": "Carrier 3-Ton Condenser Unit", "Qty": 1, "Cost": 2100.00, "Mins": 180},
        {"Item": "R8 Flexible Duct (25ft)", "Qty": 10, "Cost": 55.00, "Mins": 45},
        {"Item": "Nest Smart Thermostat", "Qty": 1, "Cost": 199.00, "Mins": 30}
    ])

# Shared Globals
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "labor_rate" not in st.session_state: st.session_state.labor_rate = 60.00 # Blended burdened rate

# --- CORE MATH ENGINE ---
def calc_trade(df):
    mat = (df["Qty"] * df["Cost"]).sum()
    lab = ((df["Qty"] * df["Mins"]) / 60).sum() * st.session_state.labor_rate
    return (mat + lab) * (1 + st.session_state.overhead)

elec_total = calc_trade(st.session_state.df_elec)
plumb_total = calc_trade(st.session_state.df_plumb)
hvac_total = calc_trade(st.session_state.df_hvac)
master_build_cost = elec_total + plumb_total + hvac_total + 35000.0 # Adding 35k arbitrary for framing/finishes

# --- STYLING INJECTION ---
st.markdown("""
<style>
    .stApp { background-color: #070B12 !important; color: #94A3B8 !important; }
    h1, h2, h3, h4, h5, h6 { color: #CBD5E1 !important; font-weight: 500 !important; }
    div[data-testid="stMetricValue"] { font-size: 24px !important; font-weight: 600 !important; color: #38BDF8 !important; font-family: 'Courier New', monospace; }
    .unifi-stealth-blade { background-color: #0F172A !important; border: 1px solid #1E293B !important; border-left: 3px solid #38BDF8 !important; padding: 16px; border-radius: 4px; margin-bottom: 12px; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR & LOCALIZATION ---
st.sidebar.title("🌍 OmniBuild OS")

# Language Selector
selected_lang = st.sidebar.selectbox("🌐 System Language / Мова", ["English", "Español", "Українська"], index=["English", "Español", "Українська"].index(st.session_state.lang))
if selected_lang != st.session_state.lang:
    st.session_state.lang = selected_lang
    st.rerun()

t = lang_dict[st.session_state.lang]

st.sidebar.divider()
user_market_tier = st.sidebar.selectbox("Simulate Workspace Profile", [
    "🏗️ General Contractor (Admin)",
    "⚡ Electrical Subcontractor",
    "💧 Plumbing Subcontractor",
    "❄️ HVAC Subcontractor"
], index=0)
st.sidebar.divider()

# Dynamic Menu based on Trade Role
if "General Contractor" in user_market_tier:
    menu_options = [t["home"], t["elec"], t["plumb"], t["hvac"], t["gc_budg"], t["fin"]]
elif "Electrical" in user_market_tier:
    menu_options = [t["home"], t["elec"], t["ai"]]
elif "Plumbing" in user_market_tier:
    menu_options = [t["home"], t["plumb"], t["ai"]]
elif "HVAC" in user_market_tier:
    menu_options = [t["home"], t["hvac"], t["ai"]]

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
    st.caption("Isolated electrical workspace. Changes here automatically sync to the Master GC Budget.")
    st.session_state.df_elec = st.data_editor(st.session_state.df_elec, use_container_width=True, num_rows="dynamic")
    st.metric("Total Electrical Subcontract", f"${elec_total:,.2f}")

elif selected_page == t["plumb"]:
    st.write(f"### {t['plumb']}")
    st.caption("Isolated plumbing workspace. PVC, Copper, and Fixture takeoff matrix.")
    st.session_state.df_plumb = st.data_editor(st.session_state.df_plumb, use_container_width=True, num_rows="dynamic")
    st.metric("Total Plumbing Subcontract", f"${plumb_total:,.2f}")

elif selected_page == t["hvac"]:
    st.write(f"### {t['hvac']}")
    st.caption("Isolated HVAC workspace. Ductwork, Condensers, and Air Handler takeoff matrix.")
    st.session_state.df_hvac = st.data_editor(st.session_state.df_hvac, use_container_width=True, num_rows="dynamic")
    st.metric("Total HVAC Subcontract", f"${hvac_total:,.2f}")

elif selected_page == t["gc_budg"]:
    st.write(f"### {t['gc_budg']}")
    
    chart_data = pd.DataFrame({
        "Trade": ["Electrical", "Plumbing", "HVAC", "Framing/Finishes (Fixed)"],
        "Value ($)": [elec_total, plumb_total, hvac_total, 35000.0]
    })
    
    pie = alt.Chart(chart_data).mark_arc(innerRadius=50).encode(
        theta='Value ($):Q', color=alt.Color('Trade:N', scale=alt.Scale(range=["#38BDF8", "#3B82F6", "#8B5CF6", "#64748B"]))
    ).properties(height=300)
    
    gc_c1, gc_c2 = st.columns([1.5, 1])
    with gc_c1: st.altair_chart(pie, use_container_width=True)
    with gc_c2:
        st.markdown(f"<div class='unifi-stealth-blade' style='border-left-color: #F59E0B;'><h5 style='color:#F59E0B; margin:0;'>{t['budget']}</h5><h2 style='color:#38BDF8; margin:0;'>${master_build_cost:,.2f}</h2></div>", unsafe_allow_html=True)

elif selected_page == t["fin"]:
    st.write(f"### {t['fin']}")
    st.info("Embedded financial tools operational.")
    
elif selected_page == t["ai"]:
    st.write(f"### {t['ai']}")
    st.info("AI Upload portal online. Select Trade Blueprint.")