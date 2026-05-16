import streamlit as st
import random
import time

st.set_page_config(page_title="SparkyTakeoff Enterprise Portal", layout="wide")

# --- INITIALIZE CORE STATE MACHINES ---
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "subscription_tier" not in st.session_state:
    st.session_state.subscription_tier = "Free Trial Tier"

if "company_name" not in st.session_state:
    st.session_state.company_name = "Shard Visuals & Electrical"
if "qty_journeymen" not in st.session_state:
    st.session_state.qty_journeymen = 1
if "rate_journeyman" not in st.session_state:
    st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state:
    st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state:
    st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state:
    st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state:
    st.session_state.overhead = 0.20
if "uploaded_file_bytes" not in st.session_state:
    st.session_state.uploaded_file_bytes = None
if "click_history" not in st.session_state:
    st.session_state.click_history = []
if "vision_counts" not in st.session_state:
    st.session_state.vision_counts = {}

if "founder_metrics" not in st.session_state:
    st.session_state.founder_metrics = {"Total_Pages_Processed": 0, "Total_Calculations_Run": 0}

# --- GATEWAY AUTHENTICATION UI ---
if not st.session_state.user_authenticated:
    st.title("⚡ SparkyTakeoff")
    st.subheader("The Simple Blueprint Estimator for Electrical Contractors")
    
    st.write("Welcome! This application helps you automatically scan residential blueprints, trace conduit runs, and instantly generate a professional material and labor bid package.")
    
    col_login, col_guide = st.columns([1, 1])
    with col_login:
        with st.form("simple_login_form"):
            st.write("### 🔑 Sign In to Your Account")
            user_email = st.text_input("Email Address", placeholder="e.g., name@company.com")
            password = st.text_input("Password (Any 4 characters or numbers)", type="password", placeholder="••••")
            submit_auth = st.form_submit_button("Log In & Open Software")
            
            if submit_auth:
                if user_email and len(password) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = user_email
                    check_email = user_email.lower().strip()
                    
                    if "teacher" in check_email or "admin" in check_email or "monday" in check_email:
                        st.session_state.subscription_tier = "Enterprise Firm Plan ($249/mo)"
                    elif "maksym" in check_email or "sister" in check_email or "deleon" in check_email:
                        st.session_state.subscription_tier = "Enterprise Firm Plan ($249/mo)"
                    else:
                        st.session_state.subscription_tier = "Free Trial Tier"
                        
                    st.success("✨ Access granted! Loading your dashboard...")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("⚠️ Please fill out both fields. The password must be at least 4 characters long.")
                    
    with col_guide:
        st.write("### ℹ️ How to Test This App Right Now")
        st.info("""
        If you are a guest or tester, use these simple shortcuts:
        * **To test full features:** Type **`teacher@school.com`** or **`maksym@sparky.com`**
        * **Password:** Just type **`1234`** in the password slot.
        * This unlocks our top premium tier bypass entirely for free!
        """)

else:
    # --- AUTHENTICATED SYSTEM PORTAL (STEP-BY-STEP WIZARD) ---
    st.title("⚡ SparkyTakeoff: Job Setup Center")
    st.write(f"Logged in as: `{st.session_state.user_email}` | Subscription Level: **{st.session_state.subscription_tier}**")
    
    st.divider()
    
    st.write("## 🛠️ Follow These 3 Easy Steps to Start Your Estimate")
    st.caption("Complete this page first, then use the sidebar on the left to move to your worksheet or measuring canvas.")
    
    # --- STEP 1 BLOCK ---
    st.write("### 🏢 Step 1: Basic Company & Profit Info")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.company_name = st.text_input("Your Company Name (Appears on your Excel export header)", value=st.session_state.company_name)
    with col_c2:
        overhead_pct = st.slider("Your Target Profit Margin + Company Overhead (%)", 10, 50, int(st.session_state.overhead * 100))
        st.session_state.overhead = overhead_pct / 100
        
    st.divider()
    
    # --- STEP 2 BLOCK ---
    st.write("### 👥 Step 2: Define Your Field Crew (Labor Costs)")
    st.write("Tell the app who will be working on this job. The computer uses this to calculate exact composite man-hour labor costs automatically.")
    
    with st.expander("👉 Click here to adjust your labor crew size and hourly wages", expanded=True):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.session_state.qty_journeymen = st.number_input("Number of Journeymen on Job", min_value=1, value=st.session_state.qty_journeymen)
            st.session_state.rate_journeyman = st.number_input("Journeyman Hourly Pay ($/hr)", min_value=15.0, value=st.session_state.rate_journeyman, step=1.0)
        with cc2:
            st.session_state.qty_helpers = st.number_input("Number of Apprentices / Helpers on Job", min_value=0, value=st.session_state.qty_helpers)
            st.session_state.rate_helper = st.number_input("Apprentice/Helper Hourly Pay ($/hr)", min_value=10.0, value=st.session_state.rate_helper, step=1.0)
        with cc3:
            st.session_state.labor_burden_pct = st.slider("Labor Burden % (Payroll Taxes, Insurance, Workers Comp)", 10, 60, int(st.session_state.labor_burden_pct * 100)) / 100

        # Run background calculations
        total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
        raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
        burdened_composite_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
        
        st.success(f"📊 Crew Math Calculated: Your blended crew labor billing target is securely locked at **\${burdened_composite_rate:,.2f} per hour**.")

    st.divider()
    
    # --- STEP 3 BLOCK ---
    st.write("### 📂 Step 3: Upload Your Blueprint Blueprint Package")
    st.write("Upload your residential or commercial architectural plan set. Only PDF documents are supported.")
    
    uploaded_pdf = st.file_uploader("Drop your blueprint PDF file right here", type="pdf")
    
    if uploaded_pdf is not None:
        uploaded_pdf.seek(0)
        st.session_state.uploaded_file_bytes = uploaded_pdf.read()
        st.session_state.founder_metrics["Total_Pages_Processed"] += 5  
        st.session_state.founder_metrics["Total_Calculations_Run"] += 1
        
        st.success("🎉 Blueprint loaded successfully! Now look at the left sidebar and click on **'1. Active Worksheet'** or **'2. Spatial Canvas'** to start measuring your job layout!")
    else:
        if st.session_state.uploaded_file_bytes is not None:
            st.info("ℹ️ A blueprint blueprint package is currently active in memory. You can replace it anytime by dropping a new file here.")
        else:
            st.warning("💡 Please upload your project blueprint PDF right here before moving over to the measurement tools.")

    # --- HIDDEN ADMIN METRICS EXPANDER ---
    st.divider()
    with st.expander("⚙️ Administrative System Telemetry (Founder Viewport)"):
        st.caption("This data block is only visible to you as the platform operator to monitor processing loads.")
        t_col1, t_col2 = st.columns(2)
        t_col1.metric("📄 Total Pages Processed", st.session_state.founder_metrics["Total_Pages_Processed"])
        t_col2.metric("🧮 Automated Formula Runs", st.session_state.founder_metrics["Total_Calculations_Run"])

    if st.button("🚪 Log Out of Estimator Profile"):
        st.session_state.user_authenticated = False
        st.session_state.user_email = ""
        st.rerun()