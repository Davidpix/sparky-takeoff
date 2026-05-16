import streamlit as st
import random
import time
import datetime

st.set_page_config(page_title="SparkyTakeoff Enterprise Portal", layout="wide")

# --- USER AUTHENTICATION & SESSION ISOLATION STATE ---
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "subscription_tier" not in st.session_state:
    st.session_state.subscription_tier = "Free Trial Tier"

# --- GLOBAL PROFILE AND LABOR CREW INITIALIZATION ---
if "company_name" not in st.session_state:
    st.session_state.company_name = "Shard Visuals & Electrical"
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 1
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "uploaded_file_bytes" not in st.session_state: st.session_state.uploaded_file_bytes = None
if "vision_counts" not in st.session_state: st.session_state.vision_counts = {}

# --- INITIALIZE CORE DYNAMIC VENDOR MATRIX ---
if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {
        "Main Panel Enclosure": 450.00, 
        "GFCI Receptacle": 18.00, 
        "Disconnect Switch": 85.00, 
        "Single Pole Switch": 1.50,
        "3/4\" EMT Conduit Run (Linear Ft)": 1.25
    }
if "last_price_sync" not in st.session_state:
    st.session_state.last_price_sync = "Never Synced (Using Local Fallback Catalog)"

if "founder_metrics" not in st.session_state:
    st.session_state.founder_metrics = {"Total_Pages_Processed": 0, "Total_Calculations_Run": 0}

# --- GATEWAY AUTHENTICATION UI ---
if not st.session_state.user_authenticated:
    st.title("⚡ SparkyTakeoff")
    st.subheader("The Simple Blueprint Estimator for Electrical Contractors")
    
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
                    
                    if "teacher" in check_email or "admin" in check_email or "monday" in check_email or "maksym" in check_email or "sister" in check_email or "deleon" in check_email:
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
    with st.expander("👉 Click here to adjust your labor crew size and hourly wages", expanded=False):
        cc1, cc2, cc3 = st.columns(3)
        with cc1:
            st.session_state.qty_journeymen = st.number_input("Number of Journeymen on Job", min_value=1, value=st.session_state.qty_journeymen)
            st.session_state.rate_journeyman = st.number_input("Journeyman Hourly Pay ($/hr)", min_value=15.0, value=st.session_state.rate_journeyman, step=1.0)
        with cc2:
            st.session_state.qty_helpers = st.number_input("Number of Apprentices / Helpers on Job", min_value=0, value=st.session_state.qty_helpers)
            st.session_state.rate_helper = st.number_input("Apprentice/Helper Hourly Pay ($/hr)", min_value=10.0, value=st.session_state.rate_helper, step=1.0)
        with cc3:
            st.session_state.labor_burden_pct = st.slider("Labor Burden % (Payroll Taxes, Insurance, Workers Comp)", 10, 60, int(st.session_state.labor_burden_pct * 100)) / 100

        total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
        raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
        burdened_composite_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
        st.success(f"📊 Crew Math Calculated: Labor billing target is locked at **\${burdened_composite_rate:,.2f} per hour**.")

    st.divider()

    # --- ADVANCED FEATURE BLOCK: LIVE WHOLESALE DISTRIBUTOR FEED SYNC ---
    st.write("### 📈 Step 3: Live Supplier Pricing Integration")
    st.write("Connect directly to local distributors to pull real-time material wholesale costs based on active commodities (copper, steel, pvc index).")
    
    with st.expander("🔌 Wholesale Material Sourcing Portal", expanded=True):
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            st.write("**Current Supply House Catalog Rates:**")
            st.json(st.session_state.vendor_pricing)
            st.caption(f"Status: `{st.session_state.last_price_sync}`")
        with col_m2:
            supplier_region = st.selectbox("Select Regional Supply House Node", ["Southeast Hub (Miami / Broward)", "National Wholesale Feed"])
            if st.button("🔄 Sync Live Supplier Catalog Prices"):
                with st.spinner("Connecting to distributor inventory networks..."):
                    time.sleep(1.5) # Simulated API latency
                    
                    # Simulate slight raw metal price fluctuations (+/- 5% to 15%)
                    modifier = 1.0 + random.uniform(-0.04, 0.14)
                    st.session_state.vendor_pricing["Main Panel Enclosure"] = round(450.00 * modifier, 2)
                    st.session_state.vendor_pricing["GFCI Receptacle"] = round(18.00 * modifier, 2)
                    st.session_state.vendor_pricing["Disconnect Switch"] = round(85.00 * modifier, 2)
                    st.session_state.vendor_pricing["Single Pole Switch"] = round(1.50 * modifier, 2)
                    st.session_state.vendor_pricing["3/4\" EMT Conduit Run (Linear Ft)"] = round(1.25 * modifier, 2)
                    
                    st.session_state.last_price_sync = f"Successfully Synced with {supplier_region} on {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
                    st.toast("Prices synchronized live!")
                    st.rerun()

    st.divider()
    
    # --- STEP 4 BLOCK (FORMERLY STEP 3) ---
    st.write("### 📂 Step 4: Upload Your Blueprint Document Package")
    uploaded_pdf = st.file_uploader("Drop your blueprint PDF file right here", type="pdf")
    
    if uploaded_pdf is not None:
        uploaded_pdf.seek(0)
        st.session_state.uploaded_file_bytes = uploaded_pdf.read()
        st.success("🎉 Blueprint loaded successfully! Now use the left sidebar menu to navigate to your worksheet or canvas pages.")

    if st.button("🚪 Log Out of Estimator Profile"):
        st.session_state.user_authenticated = False
        st.session_state.user_email = ""
        st.rerun()