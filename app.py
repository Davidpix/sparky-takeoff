import streamlit as st
import PyPDF2
import pandas as pd
import re

st.set_page_config(page_title="SparkyTakeoff Pro", layout="wide")

st.title("⚡ SparkyTakeoff: Multi-Phase Enterprise Edition")

# --- SIDEBAR: GLOBAL FINANCIALS ---
with st.sidebar:
    st.header("⚙️ Global Bid Settings")
    labor_rate = st.number_input("Hourly Labor Rate ($)", value=85.0, step=5.0)
    overhead = st.slider("Overhead & Profit Markup (%)", 10, 50, 20) / 100
    st.divider()
    st.info("💡 **Enterprise Tip:** Filter your worksheet below by Phase or Zone to generate targeted supply house orders.")

# --- CACHING ENGINE ---
@st.cache_data
def process_and_scan_blueprint(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    # Advanced Manifest with Phase and Zone tagging built-in
    electrical_manifest = {
        "Main Panel Enclosure": {"pattern": r"(\d+)\s*(?:-|x)?\s*(?:amp)?\s*(?:panel|load center)", "cost": 450.00, "mins": 120, "phase": "Rough-In", "zone": "Service Room"},
        "GFCI Receptacle": {"pattern": r"(\d+)\s*(?:-|x)?\s*gfci", "cost": 18.00, "mins": 20, "phase": "Trim-Out", "zone": "Wet Areas (Kitchen/Bath)"},
        "Disconnect Switch": {"pattern": r"(\d+)\s*(?:-|x)?\s*(?:phase)?\s*disconnect", "cost": 85.00, "mins": 45, "phase": "Rough-In", "zone": "HVAC / Equipment"},
        "Single Pole Switch": {"pattern": r"(\d+)\s*(?:-|x)?\s*single pole", "cost": 1.50, "mins": 15, "phase": "Trim-Out", "zone": "General Lighting"},
        "12/2 Romex (250ft coil)": {"pattern": r"(\d+)\s*(?:-|x)?\s*12/2", "cost": 110.00, "mins": 60, "phase": "Rough-In", "zone": "Branch Wiring"}
    }
    
    scanned_results = []
    for item, info in electrical_manifest.items():
        matches = re.findall(info["pattern"], full_text, re.IGNORECASE)
        total_qty = 0
        for match in matches:
            try:
                total_qty += int(match)
            except ValueError:
                continue
        
        scanned_results.append({
            "Item Name": item,
            "Phase": info["phase"],
            "Zone/Location": info["zone"],
            "Detected Qty": total_qty,
            "Unit Cost ($)": info["cost"],
            "Mins to Install": info["mins"]
        })
    return scanned_results

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Blueprint PDF for Multi-Phase Scan", type="pdf")

if uploaded_file is not None:
    scanned_data = process_and_scan_blueprint(uploaded_file)
else:
    # Default comprehensive structural template
    scanned_data = [
        {"Item Name": "Main Panel Enclosure", "Phase": "Rough-In", "Zone/Location": "Service Room", "Detected Qty": 0, "Unit Cost ($)": 450.00, "Mins to Install": 120},
        {"Item Name": "12/2 Romex (250ft coil)", "Phase": "Rough-In", "Zone/Location": "Branch Wiring", "Detected Qty": 0, "Unit Cost ($)": 110.00, "Mins to Install": 60},
        {"Item Name": "Disconnect Switch", "Phase": "Rough-In", "Zone/Location": "HVAC / Equipment", "Detected Qty": 0, "Unit Cost ($)": 85.00, "Mins to Install": 45},
        {"Item Name": "GFCI Receptacle", "Phase": "Trim-Out", "Zone/Location": "Wet Areas (Kitchen/Bath)", "Detected Qty": 0, "Unit Cost ($)": 18.00, "Mins to Install": 20},
        {"Item Name": "Single Pole Switch", "Phase": "Trim-Out", "Zone/Location": "General Lighting", "Detected Qty": 0, "Unit Cost ($)": 1.50, "Mins to Install": 15}
    ]

# Convert dataset into master DataFrame
master_df = pd.DataFrame(scanned_data)

# --- FILTER CONTROLS ---
st.write("### 🔍 Live Project Filters")
col_f1, col_f2 = st.columns(2)

with col_f1:
    phase_filter = st.selectbox("Select Project Phase", ["All Phases", "Rough-In", "Trim-Out"])
with col_f2:
    all_zones = ["All Zones"] + list(master_df["Zone/Location"].unique())
    zone_filter = st.selectbox("Select Physical Zone/Location", all_zones)

# Apply dynamic filters to our dataframe view
filtered_df = master_df.copy()
if phase_filter != "All Phases":
    filtered_df = filtered_df[filtered_df["Phase"] == phase_filter]
if zone_filter != "All Zones":
    filtered_df = filtered_df[filtered_df["Zone/Location"] == zone_filter]

# --- INTERACTIVE WORKSHEET ---
st.write(r"### 📊 Work Breakdown Structure (WBS)")
edited_df = st.data_editor(
    filtered_df, 
    num_rows="dynamic",
    column_config={
        "Phase": st.column_config.SelectboxColumn("Phase", options=["Rough-In", "Trim-Out"], required=True),
        "Detected Qty": st.column_config.NumberColumn("Qty", min_value=0, step=1),
        "Unit Cost ($)": st.column_config.NumberColumn("Unit Cost", format="$%.2f"),
        "Mins to Install": st.column_config.NumberColumn("Labor Mins", format="%d mins")
    },
    use_container_width=True
)

# --- REAL-TIME CALCULATION PIPELINE ---
# Sync adjustments back to master dataset to maintain aggregate project integrity
master_df.set_index("Item Name", inplace=True)
edited_df.set_index("Item Name", inplace=True)
master_df.update(edited_df)
master_df.reset_index(inplace=True)

# Compute raw numbers across whole project
master_df["Detected Qty"] = pd.to_numeric(master_df["Detected Qty"]).fillna(0)
master_df["Unit Cost ($)"] = pd.to_numeric(master_df["Unit Cost ($)"]).fillna(0)
master_df["Mins to Install"] = pd.to_numeric(master_df["Mins to Install"]).fillna(0)

total_mat = (master_df["Detected Qty"] * master_df["Unit Cost ($)"]).sum()
total_labor = ((master_df["Detected Qty"] * master_df["Mins to Install"] / 60) * labor_rate).sum()
final_bid = (total_mat + total_labor) * (1 + overhead)

# --- EXECUTIVE SUMMARY DASHBOARD ---
st.divider()
st.write("### 📈 Project Financial Summary (Total Estimate)")
c1, c2, c3 = st.columns(3)
c1.metric("Gross Material Allocation", f"${total_mat:,.2f}")
c2.metric("Gross Labor Allocation", f"${total_labor:,.2f}")
c3.metric("Target Contract Price", f"${final_bid:,.2f}", delta=f"{overhead*100:.0f}% Gross Margin")