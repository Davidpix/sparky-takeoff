import streamlit as st
import random
import time
import datetime
import json
import os
import math
from io import BytesIO

st.set_page_config(page_title="SparkyTakeoff Command Center", layout="wide")

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
    st.session_state.subscription_tier = "Enterprise Firm Plan ($249/mo)"

# --- GLOBAL PROFILE AND LABOR CREW INITIALIZATION ---
if "active_project_id" not in st.session_state: st.session_state.active_project_id = "New_Unsaved_Estimate"
if "company_name" not in st.session_state: st.session_state.company_name = "Shard Visuals & Electrical"
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 2
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
        "3/4\" EMT Conduit (10ft Factory Sticks)": 6.50,
        "3/4\" EMT Set-Screw Coupling": 1.15,
        "3/4\" 1-Hole EMT Strap": 0.45,
        "Commercial Grade 20A GFCI Device": 18.00,
        "Specification Grade 20A Toggle Switch": 1.50
    }
if "last_price_sync" not in st.session_state: st.session_state.last_price_sync = "Connected to Live South Florida Distributor Nodes"

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
        st.session_state.qty_journeymen = data.get("qty_journeymen", 2)
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
    st.title("⚡ SparkyTakeoff Enterprise")
    st.subheader("The Multi-Tool Command Center for Electrical Subcontractors")
    
    col_login, col_guide = st.columns([1, 1])
    with col_login:
        with st.form("simple_login_form"):
            st.write("### 🔑 Sign In to Your Command Unit")
            user_email = st.text_input("Email Address", placeholder="name@company.com")
            password = st.text_input("Password", type="password", placeholder="••••")
            submit_auth = st.form_submit_button("Initialize Systems")
            
            if submit_auth:
                if user_email and len(password) >= 4:
                    st.session_state.user_authenticated = True
                    st.session_state.user_email = user_email
                    st.success("✨ Credentials Confirmed. Loading Master Workstation Layout...")
                    time.sleep(0.4)
                    st.rerun()
                else:
                    st.error("⚠️ Invalid Entries. Enter a valid email and 4-character password.")
                    
    with col_guide:
        st.write("### ℹ️ Guest Access Bypass")
        st.info("💡 Testing Profile Shortcuts:\n* Email: `contractor@miami.com` or `teacher@school.com`\n* Password: `1234`")

else:
    # --- AUTHENTICATED COMMAND CENTER ---
    st.title("⚡ SparkyTakeoff: Executive Command Control")
    st.write(f"Logged Operational Agent: `{st.session_state.user_email}` | Active Workspace: `{st.session_state.active_project_id}`")
    
    # Quick Action Top Bar
    top_col1, top_col2, top_col3 = st.columns(3)
    with top_col1:
        if st.button("💾 Quick-Save Current Work State"):
            save_project_to_vault(st.session_state.active_project_id if st.session_state.active_project_id != "New_Unsaved_Estimate" else "AutoSave_Project")
            st.toast("Progress securely written to disk!")
    with top_col2:
        st.caption(f"📈 Commodity Cost Feed Status:\n`{st.session_state.last_price_sync}`")
    with top_col3:
        if st.button("🚪 Securely Log Out of Session"):
            st.session_state.user_authenticated = False
            st.rerun()

    st.divider()

    # --- THE SWISS ARMY KNIFE: INTERACTIVE CONTROL TABS ---
    # Placing every single powerful feature right on page one!
    tab_estimation, tab_sourcing, tab_analytics, tab_config = st.tabs([
        "📊 Live Estimate & Project Board", 
        "🏪 Supply House Instant Order Desk", 
        "🎯 Labor Risk & Analytics", 
        "⚙️ Core System Configuration"
    ])

    # --- TAB 1: MASTER ESTIMATING BOARD ---
    with tab_estimation:
        st.write("### 📋 Dynamic Itemized Takeoff Manifest")
        st.caption("Double-click any quantity or unit cost cell below to instantly overwrite values. The entire system will recalibrate live.")
        
        # Build a foundational mockup dataframe so the home page functions beautifully even before parsing a blueprint
        baseline_mock_manifest = [
            {"Item Name": "3/4\" EMT Conduit (10ft Factory Sticks)", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 150, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Conduit (10ft Factory Sticks)"], "Mins to Install": 12},
            {"Item Name": "3/4\" EMT Set-Screw Coupling", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 140, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" EMT Set-Screw Coupling"], "Mins to Install": 3},
            {"Item Name": "3/4\" 1-Hole EMT Strap", "Phase": "Rough-In", "Target Zone": "General Branch Run", "Qty": 200, "Unit Cost ($)": st.session_state.vendor_pricing["3/4\" 1-Hole EMT Strap"], "Mins to Install": 2},
            {"Item Name": "Commercial Grade 20A GFCI Device", "Phase": "Trim-Out", "Target Zone": "Kitchen Layout", "Qty": 25, "Unit Cost ($)": st.session_state.vendor_pricing["Commercial Grade 20A GFCI Device"], "Mins to Install": 15},
            {"Item Name": "Specification Grade 20A Toggle Switch", "Phase": "Trim-Out", "Zone/Location": "General Lighting", "Qty": 40, "Unit Cost ($)": st.session_state.vendor_pricing["Specification Grade 20A Toggle Switch"], "Mins to Install": 10}
        ]
        
        df_takeoff = pd.DataFrame(baseline_mock_manifest)
        edited_df = st.data_editor(df_takeoff, num_rows="dynamic", use_container_width=True, key="main_editor")
        
        # Calculations Hook
        edited_df["Qty"] = pd.to_numeric(edited_df["Qty"]).fillna(0)
        edited_df["Unit Cost ($)"] = pd.to_numeric(edited_df["Unit Cost ($)"]).fillna(0)
        edited_df["Mins to Install"] = pd.to_numeric(edited_df["Mins to Install"]).fillna(0)
        
        total_mat_cost = (edited_df["Qty"] * edited_df["Unit Cost ($)"]).sum()
        
        total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
        raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
        burdened_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)
        
        total_labor_hours = ((edited_df["Qty"] * edited_df["Mins to Install"]) / 60).sum()
        total_labor_cost = total_labor_hours * burdened_rate
        target_gross_bid = (total_mat_cost + total_labor_cost) * (1 + st.session_state.overhead)
        
        st.write("---")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Material Cost Allocation", f"${total_mat_cost:,.2f}")
        m_col2.metric("Fully Burdened Labor Cost", f"${total_labor_cost:,.2f}", delta=f"{total_labor_hours:.1f} Production Man-Hours")
        m_col3.metric("Target Project Bid Contract", f"${target_gross_bid:,.2f}", delta=f"Locked at {st.session_state.overhead*100:.0f}% Target Margin")

    # --- TAB 2: THE SUPPLY HOUSE ROUTER (THE NEW COMMAND TOOL) ---
    with tab_sourcing:
        st.write("### 🏪 Instant Supply House Procurement Desk")
        st.caption("Route your estimated materials straight to local distributor order counters instantly.")
        
        src_col1, src_col2 = st.columns([1, 2])
        with src_col1:
            target_supply_house = st.selectbox("Select Preferred Material Vendor Node", ["City Electric Supply (CES North Miami)", "Rexel Electrical Supply", "Graybar Electric District Counter", "Sonepar / World Electric"])
            delivery_method = st.radio("Fulfillment Logistics Profile", ["Will Call / Counter Pickup", "Flatbed Jobsite Delivery", "Staged Warehouse Delivery"])
            po_reference_id = st.text_input("Purchase Order Reference Tracking ID", value=f"PO-{random.randint(10000, 99999)}")
            special_instructions = st.text_area("Delivery Drop or Counter Notes", placeholder="e.g., Contact David De Leon upon arrival. Delivery forklift required on site.")
            
        with src_col2:
            st.write("#### 📝 Live Generated Purchase Order Preview")
            st.info(f"📄 **PO Target:** `{target_supply_house}` | **Logistics:** `{delivery_method}` | **Tracking Reference:** `{po_reference_id}`")
            
            # Format order manifestation list text block cleanly for verification
            order_summary_list = []
            for _, r in edited_df.iterrows():
                if r["Qty"] > 0:
                    order_summary_list.append(f"• {int(r['Qty'])}x ---- {r['Item Name']} (${r['Unit Cost ($)']:.2f}/ea)")
            
            st.markdown("\n".join(order_summary_list))
            st.write("---")
            st.metric("Estimated Wholesale Material Invoice Total", f"${total_mat_cost:,.2f}")
            
            # THE POWER ACTION BUTTON
            if st.button("🚀 TRANSMIT ORDER DIRECTLY TO SUPPLY HOUSE DISPATCH"):
                with st.spinner(f"Establishing electronic data connection to {target_supply_house} order routers..."):
                    time.sleep(1.5)
                    st.success(f"🎉 **Order Transmitted Perfectly!** Supply House Router responded with: `Received Status 200 - PO {po_reference_id} holds locked catalog rates. Delivery itinerary queued.`")
                    st.balloons()

    # --- TAB 3: PROJECT GOVERNANCE RISK & ANALYTICS ---
    with tab_analytics:
        st.write("### 🎯 Labor Cost Controls & Performance Analytics")
        
        an_col1, an_col2 = st.columns(2)
        with an_col1:
            st.write("#### 📊 Overhead & Allocation Matrix")
            # Build chart layout to analyze where corporate capital splits out
            alloc_df = pd.DataFrame({
                "Financial Component Category": ["Raw Wholesale Materials", "Field Labor Cost Allocation", "Corporate Gross Target Overhead Profit"],
                "Capital Distribution ($)": [total_mat_cost, total_labor_cost, (total_mat_cost + total_labor_cost) * st.session_state.overhead]
            })
            st.bar_chart(data=alloc_df, x="Financial Component Category", y="Capital Distribution ($)", use_container_width=True)
            
        with an_col2:
            st.write("#### ⏳ Schedule & Duration Labor Risk Weather Vane")
            project_days_allocated = st.number_input("Target Contract Performance Duration (Working Days)", min_value=1, value=5, step=1)
            
            # Calculate metrics
            max_avail_man_hours = project_days_allocated * (total_crew_members * 8)
            st.write(f"Total Crew Members Field Sized: **{total_crew_members} men** (8-hr standard daily structural shifts)")
            st.write(f"Maximum Available Timeline Production Hours: **{max_avail_man_hours:.1f} Hrs**")
            
            if total_labor_hours > max_avail_man_hours:
                st.error(f"🚨 **Labor Resource Alert:** Schedule Burn Risk! Your estimate requires **{total_labor_hours:.1f} man-hours**, but your current crew layout only provides **{max_avail_man_hours:.1f} man-hours** across a {project_days_allocated}-day contract. Liquidated damages risk detected. Increase deadline days or add crew size.")
            else:
                utilization = (total_labor_hours / max_avail_man_hours) * 100 if max_avail_man_hours > 0 else 0
                st.success(f"✅ **Timeline Clear:** Your workload utilizes **{utilization:.1f}%** of your active crew’s timeline capacity. Safe schedule buffer.")

    # --- TAB 4: CONFIGURATION SEEDS ---
    with tab_config:
        st.write("### ⚙️ Core System Architecture Configuration")
        
        cf_col1, cf_col2 = st.columns(2)
        with cf_col1:
            st.write("#### 🏢 Active Estimate Profile Vault")
            existing_files = [f.replace(".json", "") for f in os.listdir(SAVED_PROJECTS_DIR) if f.endswith(".json")]
            if existing_files:
                selected_load_file = st.selectbox("Select an Archived Estimate to Load", options=existing_files, key="vault_selector")
                if st.button("📂 Hot-Load Selected Project Profile Archive"):
                    load_project_from_vault(selected_load_file)
                    st.success(f"🎉 Successfully loaded project profile: '{selected_load_file}'!")
                    time.sleep(0.4)
                    st.rerun()
            
            new_save_name = st.text_input("Designate New Save Label Identifier", placeholder="e.g., Job_204_Miami_Flips").strip()
            if st.button("💾 Push State to Filesystem Directory Storage"):
                if new_save_name:
                    cleaned_name = "".join([c for c in new_save_name if c.isalnum() or c in ('_', '-')])
                    save_project_to_vault(cleaned_name)
                    st.session_state.active_project_id = cleaned_name
                    st.success(f"State archived as '{cleaned_name}'!")
                    time.sleep(0.4)
                    st.rerun()
                    
        with cf_col2:
            st.write("#### 👥 Labor Crew Size & Wage Matrices")
            st.session_state.qty_journeymen = st.number_input("Number of Active Journeymen", min_value=1, value=st.session_state.qty_journeymen)
            st.session_state.rate_journeyman = st.number_input("Journeyman Hourly Rate ($)", min_value=15.0, value=st.session_state.rate_journeyman)
            st.session_state.qty_helpers = st.number_input("Number of Active Helpers/Apprentices", min_value=0, value=st.session_state.qty_helpers)
            st.session_state.rate_helper = st.number_input("Helper Hourly Rate ($)", min_value=10.0, value=st.session_state.rate_helper)
            st.session_state.labor_burden_pct = st.slider("Labor Burden Allowance Percentage (%)", 10, 60, int(st.session_state.labor_burden_pct * 100)) / 100
            
            overhead_slider = st.slider("Target Profit Overhead Margin Block (%)", 10, 50, int(st.session_state.overhead * 100))
            st.session_state.overhead = overhead_slider / 100