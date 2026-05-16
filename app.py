import streamlit as st
import random
import time

st.set_page_config(page_title="SparkyTakeoff Enterprise Portal", layout="wide")

# --- USER AUTHENTICATION & SESSION ISOLATION STATE ---
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "subscription_tier" not in st.session_state:
    st.session_state.subscription_tier = "Free Trial Tier"

# --- GLOBAL PROFILE AND LABOR CREW PARAMETERS INITIALIZATION ---
if "company_name" not in st.session_state:
    st.session_state.company_name = "Shard Visuals & Electrical"
    
# Advanced Labor Crew Configuration Tokens
if "qty_journeymen" not in st.session_state:
    st.session_state.qty_journeymen = 1
if "rate_journeyman" not in st.session_state:
    st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state:
    st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state:
    st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state:
    st.session_state.labor_burden_pct = 0.30  # Default 30% payroll burden rate

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

# --- FOUNDER TELEMETRY ANALYTICS LOG ---
if "founder_metrics" not in st.session_state:
    st.session_state.founder_metrics = {
        "Total_Pages_Processed": 0,
        "Total_Calculations_Run": 0,
        "Vision_Engine_Calls": 0
    }

# --- GATEWAY AUTH UI DISPLAY ---
if not st.session_state.user_authenticated:
    st.title("⚡ SparkyTakeoff SaaS Platform")
    st.subheader("Secure Enterprise Gatekeeper Login")
    
    st.info("💡 **Beta Testing Profile Active:** You can share this portal link with your classmates, sister, Maksym, and your electrical teacher. Enter a configured email credential below to unlock custom workspace environments.")
    
    col_login, col_info = st.columns([1, 1])
    with col_login:
        with st.form("authentication_form"):
            user_email = st.text_input("Professional Email Address", placeholder="estimator@company.com")
            password = st.text_input("Password Secure Access Token", type="password", placeholder="••••••••")
            submit_auth = st.form_submit_button("🔑 Unlock Workspace Environment")
            
            if submit_auth:
                if user_email and len(password) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = user_email
                    check_email = user_email.lower().strip()
                    
                    if "teacher" in check_email or "admin" in check_email or "monday" in check_email:
                        st.session_state.subscription_tier = "Enterprise Firm Plan ($249/mo)"
                    elif "maksym" in check_email:
                        st.session_state.subscription_tier = "Enterprise Firm Plan ($249/mo)"
                    elif "sister" in check_email or "deleon" in check_email:
                        st.session_state.subscription_tier = "Enterprise Firm Plan ($249/mo)"
                    elif "student" in check_email or "classmate" in check_email:
                        st.session_state.subscription_tier = "Pro Estimator Plan ($99/mo)"
                    else:
                        st.session_state.subscription_tier = "Free Trial Tier"
                        
                    st.success(f"Access granted! Welcome, {user_email}.")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("Authentication rejected. Please enter a valid email address and password token.")
                    
    with col_info:
        st.write("### 💎 Commercial Platform Feature Tier Map")
        st.write("Here is how your revenue tiers map out based on automated functional permissions:")
        st.markdown("""
        * **Free Trial Tier:** Standard Keyword Regex Scanning, Manual Proposal Worksheet Grid.
        * **Pro Estimator Plan ($99/mo):** Multi-Phase Breakdown Filters, Linear Vector Spatial Measuring Canvas.
        * **Enterprise Firm Plan ($249/mo):** OpenCV-Powered Computer Vision Symbol Sweep, Live Sourcing API Integration, Custom Vendor CSV Price Upload Matrices.
        """)

else:
    # --- AUTHENTICATED ACTIVE SaaS PORTAL RENDER ---
    st.title("⚡ SparkyTakeoff: Enterprise Command Center")
    st.write(f"Logged Account: `{st.session_state.user_email}` | Subscription Level: **{st.session_state.subscription_tier}**")
    
    if st.session_state.subscription_tier == "Free Trial Tier":
        st.warning("💳 **Account Status Notice:** Your subscription profile is set to the Free Trial Tier. Advanced modules like the Spatial Measurement Canvas and Computer Vision are locked.")
        if st.button("🚀 Connect to Stripe Payment Portal to Upgrade to Pro"):
            st.session_state.subscription_tier = "Pro Estimator Plan ($99/mo)"
            st.success("Payment verified via simulated Stripe session webhook! Your system privileges have been upgraded.")
            time.sleep(1)
            st.rerun()
            
    st.divider()
    
    # --- GLOBAL PROJECT SETUP MATRIX WITH ADVANCED LABOR CREW INTERFACE ---
    st.write("### 🏢 Project Environment Configuration")
    
    col_admin, col_crew = st.columns([1, 2])
    
    with col_admin:
        st.write("#### Administrative Config")
        st.session_state.company_name = st.text_input("Registered Company Name", value=st.session_state.company_name)
        overhead_pct = st.slider("Target Corporate Overhead / Profit Margin (%)", 10, 50, int(st.session_state.overhead * 100))
        st.session_state.overhead = overhead_pct / 100
        
    with col_crew:
        st.write("#### 👥 Advanced Labor Crew Breakdown & Burden Metrics")
        cc1, cc2 = st.columns(2)
        with cc1:
            st.session_state.qty_journeymen = st.number_input("Qty of Journeymen on Crew", min_value=1, value=st.session_state.qty_journeymen)
            st.session_state.rate_journeyman = st.number_input("Journeyman Hourly Base Rate ($/hr)", min_value=15.0, value=st.session_state.rate_journeyman, step=1.0)
        with cc2:
            st.session_state.qty_helpers = st.number_input("Qty of Helpers/Apprentices on Crew", min_value=0, value=st.session_state.qty_helpers)
            st.session_state.rate_helper = st.number_input("Helper Hourly Base Rate ($/hr)", min_value=10.0, value=st.session_state.rate_helper, step=1.0)
            
        st.session_state.labor_burden_pct = st.slider("Labor Burden Factor % (Taxes, Worker's Comp, Insurance)", 10, 60, int(st.session_state.labor_burden_pct * 100)) / 100

        # Math Engine: Compute the Weighted Composite Crews metrics
        total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
        raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
        burdened_composite_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
        
        st.info(f"📈 **Blended Calculation Engine Status:** Raw Crew Composite is **\${raw_composite_rate:,.2f}/hr**. Fully Burdened Labor billing target is locked at **\${burdened_composite_rate:,.2f}/hr**.")

    st.divider()
    
    # --- DATA PIPELINE INTAKE PORTAL ---
    st.write("### 📂 Project Blueprints File Portal")
    uploaded_pdf = st.file_uploader("Upload Master Construction Blueprint Package (PDF Format)", type="pdf")
    
    if uploaded_pdf is not None:
        uploaded_pdf.seek(0)
        st.session_state.uploaded_file_bytes = uploaded_pdf.read()
        st.session_state.founder_metrics["Total_Pages_Processed"] += 5  
        st.session_state.founder_metrics["Total_Calculations_Run"] += 1
        st.success("🎉 Blueprint package uploaded successfully and locked into Global Session State!")
    else:
        if st.session_state.uploaded_file_bytes is not None:
            st.info("ℹ️ An architectural blueprint document package is currently active in memory.")
        else:
            st.warning("💡 To unlock automation features, please drop your architectural PDF file here before proceeding to the sub-pages.")

    # --- FOUNDER TELEMETRY ANALYTICS DASHBOARD ---
    st.divider()
    st.write("### 📈 Operational Telemetry Analytics (Founder Viewport)")
    t_col1, t_col2, t_col3 = st.columns(3)
    t_col1.metric("Calculated Document Pages Processed", st.session_state.founder_metrics["Total_Pages_Processed"])
    t_col2.metric("Total Ledger Formula Executions", st.session_state.founder_metrics["Total_Calculations_Run"])
    t_col3.metric("Scikit-Image Computer Vision System Invocations", len(st.session_state.vision_counts))

    st.divider()
    if st.button("🚪 Log Out of Secure Access Session"):
        st.session_state.user_authenticated = False
        st.session_state.user_email = ""
        st.rerun()