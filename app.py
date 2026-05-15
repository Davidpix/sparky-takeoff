import streamlit as st

st.set_page_config(page_title="SparkyTakeoff Enterprise Portal", layout="wide")

# --- INITIALIZE ALL COMPULSORY GLOBAL STATES ---
# This ensures that when users flip between different pages, their project data persists securely in memory
if "company_name" not in st.session_state:
    st.session_state.company_name = "Shard Visuals & Electrical"
if "labor_rate" not in st.session_state:
    st.session_state.labor_rate = 85.0
if "overhead" not in st.session_state:
    st.session_state.overhead = 0.20
if "uploaded_file_bytes" not in st.session_state:
    st.session_state.uploaded_file_bytes = None
if "click_history" not in st.session_state:
    st.session_state.click_history = []
if "scale_pixels_per_foot" not in st.session_state:
    st.session_state.scale_pixels_per_foot = None
if "conduit_runs" not in st.session_state:
    st.session_state.conduit_runs = 0.0
if "vision_counts" not in st.session_state:
    st.session_state.vision_counts = {}

st.title("⚡ SparkyTakeoff: Enterprise SaaS Command Center")
st.subheader("Welcome to the Next Generation of Electrical Estimation")

# --- EXECUTIVE SETUP PANEL ---
st.write("### 🏢 Corporate Environment Configuration")
st.caption("Configure your global workspace parameters below. These settings will dynamically lock across all active estimation sheets.")

col1, col2, col3 = st.columns(3)

with col1:
    st.session_state.company_name = st.text_input("Registered Company Name", value=st.session_state.company_name)
with col2:
    st.session_state.labor_rate = st.number_input("Blended Hourly Labor Rate ($/hr)", min_value=10.0, value=st.session_state.labor_rate, step=5.0)
with col3:
    # Overhead expressed as a fractional value
    overhead_pct = st.slider("Target Corporate Overhead / Profit Margin (%)", 10, 50, int(st.session_state.overhead * 100))
    st.session_state.overhead = overhead_pct / 100

st.divider()

# --- FILE INPUT PORTAL ---
st.write("### 📂 Project Blueprints File Portal")
uploaded_pdf = st.file_uploader("Upload Master Construction Blueprint Package (PDF Format)", type="pdf")

if uploaded_pdf is not None:
    uploaded_pdf.seek(0)
    st.session_state.uploaded_file_bytes = uploaded_pdf.read()
    st.success("🎉 Blueprint package uploaded successfully and locked into Global Session State! Use the navigation panel on the left to begin your multi-phase takeoff.")
else:
    if st.session_state.uploaded_file_bytes is not None:
        st.info("ℹ️ A blueprint package is currently active in memory. You can overwrite it by uploading a new file here.")
    else:
        st.warning("💡 To unlock full automation features, please drop your architectural PDF file here before proceeding to the worksheet pages.")

st.divider()
st.write("### 💸 Revenue-Ready SaaS Status Tracker")
c_a, c_b = st.columns(2)
c_a.info("🔒 **Secure Session Sandbox Active:** All parameters stored natively in isolated memory tokens.")
c_b.success("💳 **License Class:** Commercial Tier Unlimited Enterprise Access Profile Enabled.")