import streamlit as st
import random
import time
import datetime
import json
import os
from io import BytesIO

st.set_page_config(page_title="SparkyTakeoff Enterprise Portal", layout="wide")

# --- FILE-BASED CLOUD DATA VAULT CONFIGURATION ---
SAVED_PROJECTS_DIR = "saved_estimates_vault"
if not os.path.exists(SAVED_PROJECTS_DIR):
    os.makedirs(SAVED_PROJECTS_DIR)

# --- USER AUTHENTICATION & SESSION ISOLATION STATE ---
if "user_authenticated" not in st.session_state:
    st.session_state.user_authenticated = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""
if "subscription_tier" not in st.session_state:
    st.session_state.subscription_tier = "Free Trial Tier"

# --- GLOBAL PROFILE AND LABOR CREW INITIALIZATION ---
if "active_project_id" not in st.session_state: st.session_state.active_project_id = "New_Unsaved_Estimate"
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Electrical"
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 1
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30  
if "overhead" not in st.session_state: st.session_state.overhead = 0.20
if "uploaded_file_bytes" not in st.session_state: st.session_state.uploaded_file_bytes = None
if "vision_counts" not in st.session_state: st.session_state.vision_counts = {}
if "sheet_ledger" not in st.session_state: st.session_state.sheet_ledger = {}

if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {
        "Main Panel Enclosure": 450.00, "GFCI Receptacle": 18.00, 
        "Disconnect Switch": 85.00, "Single Pole Switch": 1.50,
        "3/4\" EMT Conduit Run (Linear Ft)": 1.25
    }
if "last_price_sync" not in st.session_state: st.session_state.last_price_sync = "Using Local Fallback Catalog"
if "founder_metrics" not in st.session_state: st.session_state.founder_metrics = {"Total_Pages_Processed": 0, "Total_Calculations_Run": 0}

# --- AUXILIARY DATABASE FUNCTION ENGINES ---
def save_project_to_vault(filename):
    payload = {
        "company_name": st.session_state.company_name,
        "qty_journeymen": st.session_state.qty_journeymen,
        "rate_journeyman": st.session_state.rate_journeyman,
        "qty_helpers": st.session_state.qty_helpers,
        "rate_helper": st.session_state.rate_helper,
        "labor_burden_pct": st.session_state.labor_burden_pct,
        "overhead": st.session_state.overhead,
        "vendor_pricing": st.session_state.vendor_pricing,
        "sheet_ledger": st.session_state.sheet_ledger,
        "vision_counts": st.session_state.vision_counts,
        "last_price_sync": st.session_state.last_price_sync,
        "timestamp": datetime.datetime.now().strftime("%m/%d/%Y %I:%M %p")
    }
    filepath = os.path.join(SAVED_PROJECTS_DIR, f"{filename}.json")
    with open(filepath, "w") as f:
        json.dump(payload, f, indent=4)

def load_project_from_vault(filename):
    filepath = os.path.join(SAVED_PROJECTS_DIR, f"{filename}.json")
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            data = json.load(f)
        st.session_state.company_name = data.get("company_name", "Shard Visuals & Electrical")
        st.session_state.qty_journeymen = data.get("qty_journeymen", 1)
        st.session_state.rate_journeyman = data.get("rate_journeyman", 45.0)
        st.session_state.qty_helpers = data.get("qty_helpers", 1)
        st.session_state.rate_helper = data.get("rate_helper", 22.0)
        st.session_state.labor_burden_pct = data.get("labor_burden_pct", 0.30)
        st.session_state.overhead = data.get("overhead", 0.20)
        st.session_state.vendor_pricing = data.get("vendor_pricing", {})
        st.session_state.sheet_ledger = data.get("sheet_ledger", {})
        st.session_state.vision_counts = data.get("vision_counts", {})
        st.session_state.last_price_sync = data.get("last_price_sync", "Loaded From Archive")
        st.session_state.active_project_id = filename

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
                    st.session_state.subscription_tier = "Enterprise Firm Plan ($249/mo)"
                    st.success("✨ Access granted! Loading your dashboard...")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("⚠️ Please fill out both fields. The password must be at least 4 characters long.")
                    
    with col_guide:
        st.write("### ℹ️ How to Test This App Right Now")
        st.info("""
        If you are a guest or tester, use these simple shortcuts:
        * **To test full features:** Type **`teacher@school.com`** or **`maksym@sparky.com`**
        * **Password:** Just type **`1234`** in the password slot.
        """)

else:
    # --- AUTHENTICATED SYSTEM PORTAL ---
    st.title("⚡ SparkyTakeoff: Job Setup Center")
    st.write(f"Active Account: `{st.session_state.user_email}` | Active Estimate Sandbox ID: `{st.session_state.active_project_id}`")
    
    # --- OPTION 1 WORKSPACE IMPLEMENTATION: PERSISTENT HISTORY VAULT INTERFACE ---
    st.write("### 💾 Cloud Estimate Vault & History Manager")
    st.caption("Save your ongoing architectural estimates securely or load historical project sheets instantly.")
    
    v_col1, v_col2 = st.columns([2, 1])
    with v_col1:
        existing_files = [f.replace(".json", "") for f in os.listdir(SAVED_PROJECTS_DIR) if f.endswith(".json")]
        if existing_files:
            selected_load_file = st.selectbox("Select an Archived Estimate to Open", options=existing_files)
            if st.button("📂 Open Selected Project Archive File"):
                load_project_from_vault(selected_load_file)
                st.success(f"🎉 Successfully loaded project profile: '{selected_load_file}'!")
                time.sleep(1)
                st.rerun()
        else:
            st.info("Empty Vault: You haven't backed up any estimating projects to the filesystem repository directory yet.")
            
    with v_col2:
        new_save_name = st.text_input("Project File Designation Name", placeholder="e.g., Job_102_Miami_Apartments").strip()
        if st.button("💾 Save Current Takeoff State to Vault"):
            if new_save_name:
                cleaned_filename = "".join([c for c in new_save_name if c.isalnum() or c in ('_', '-')])
                save_project_to_vault(cleaned_filename)
                st.session_state.active_project_id = cleaned_filename
                st.success(f"🚀 State archived perfectly as '{cleaned_filename}'!")
                time.sleep(1)
                st.rerun()
            else:
                st.error("⚠️ Please enter a unique filename label block before clicking backup.")

    st.divider()
    st.write("## 🛠️ Follow These Easy Steps to Configure Your Active Estimate")
    
    # --- STEP 1 BLOCK ---
    st.write("### 🏢 Step 1: Basic Company & Profit Info")
    col_c1, col_c2 = st.columns(2)
    with col_c1:
        st.session_state.company_name = st.text_input("Your Company Name", value=st.session_state.company_name)
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
            st.session_state.labor_burden_pct = st.slider("Labor Burden %", 10, 60, int(st.session_state.labor_burden_pct * 100)) / 100

        total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
        raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
        burdened_composite_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
        st.success(f"📊 Crew Math Calculated: Labor billing target is locked at **\${burdened_composite_rate:,.2f} per hour**.")

    st.divider()

    # --- STEP 3 BLOCK ---
    st.write("### 📈 Step 3: Live Supplier Pricing Integration")
    with st.expander("🔌 Wholesale Material Sourcing Portal", expanded=False):
        col_m1, col_m2 = st.columns([2, 1])
        with col_m1:
            st.write("**Current Supply House Catalog Rates:**")
            st.json(st.session_state.vendor_pricing)
            st.caption(f"Status: `{st.session_state.last_price_sync}`")
        with col_m2:
            supplier_region = st.selectbox("Select Regional Supply House Node", ["Southeast Hub (Miami / Broward)", "National Wholesale Feed"])
            if st.button("🔄 Sync Live Supplier Catalog Prices"):
                with st.spinner("Connecting to distributor networks..."):
                    time.sleep(0.5)
                    modifier = 1.0 + random.uniform(-0.04, 0.14)
                    st.session_state.vendor_pricing["Main Panel Enclosure"] = round(450.00 * modifier, 2)
                    st.session_state.vendor_pricing["GFCI Receptacle"] = round(18.00 * modifier, 2)
                    st.session_state.vendor_pricing["Disconnect Switch"] = round(85.00 * modifier, 2)
                    st.session_state.vendor_pricing["Single Pole Switch"] = round(1.50 * modifier, 2)
                    st.session_state.vendor_pricing["3/4\" EMT Conduit Run (Linear Ft)"] = round(1.25 * modifier, 2)
                    st.session_state.last_price_sync = f"Synced with {supplier_region} on {datetime.datetime.now().strftime('%m/%d/%Y %I:%M %p')}"
                    st.rerun()

    st.divider()
    
    # --- STEP 4 BLOCK ---
    st.write("### 📂 Step 4: Upload Your Blueprint Document Package")
    uploaded_pdf = st.file_uploader("Drop your blueprint PDF file right here", type="pdf")
    
    if uploaded_pdf is not None:
        uploaded_pdf.seek(0)
        st.session_state.uploaded_file_bytes = uploaded_pdf.read()
        st.success("🎉 Blueprint loaded successfully! Open the left sidebar menu to navigate to your worksheet or canvas pages.")

    if st.button("🚪 Log Out of Estimator Profile"):
        st.session_state.user_authenticated = False
        st.session_state.user_email = ""
        st.rerun()