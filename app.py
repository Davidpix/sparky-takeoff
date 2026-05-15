import streamlit as st
import PyPDF2
import pandas as pd
import re

st.set_page_config(page_title="SparkyTakeoff AI", layout="wide")

st.title("⚡ SparkyTakeoff: Elite Performance Edition")

# --- SIDEBAR: GLOBAL SETTINGS ---
with st.sidebar:
    st.header("Global Bid Settings")
    labor_rate = st.number_input("Hourly Labor Rate ($)", value=85.0)
    overhead = st.slider("Overhead/Profit Markup (%)", 10, 50, 20) / 100

# --- THE CACHING ENGINE (COMPLETE EXTRACTION & SCAN FIX) ---
@st.cache_data
def process_and_scan_blueprint(uploaded_file):
    """
    Reads the PDF AND runs the Regex scan ONCE. 
    Saves the resulting data structure in memory for instant re-runs.
    """
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    # Define rules inside the cached function
    electrical_manifest = {
        "Main Panel": {"pattern": r"(\d+)\s*(?:-|x)?\s*(?:amp)?\s*(?:panel|load center)", "cost": 450.00, "mins": 120},
        "GFCI Receptacle": {"pattern": r"(\d+)\s*(?:-|x)?\s*gfci", "cost": 18.00, "mins": 20},
        "Disconnect Switch": {"pattern": r"(\d+)\s*(?:-|x)?\s*(?:phase)?\s*disconnect", "cost": 85.00, "mins": 45},
        "Single Pole Switch": {"pattern": r"(\d+)\s*(?:-|x)?\s*single pole", "cost": 1.50, "mins": 15}
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
            "Detected Qty": total_qty,
            "Unit Cost ($)": info["cost"],
            "Mins to Install": info["mins"]
        })
    return scanned_results

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Blueprint PDF for Intelligent Scan", type="pdf")

# --- DATA INITIALIZATION ---
if uploaded_file is not None:
    # This execution runs instantly on table edits!
    scanned_data = process_and_scan_blueprint(uploaded_file)
else:
    # Default clean fallback state
    scanned_data = [
        {"Item Name": "Main Panel", "Detected Qty": 0, "Unit Cost ($)": 450.00, "Mins to Install": 120},
        {"Item Name": "GFCI Receptacle", "Detected Qty": 0, "Unit Cost ($)": 18.00, "Mins to Install": 20},
        {"Item Name": "Disconnect Switch", "Detected Qty": 0, "Unit Cost ($)": 85.00, "Mins to Install": 45},
        {"Item Name": "Single Pole Switch", "Detected Qty": 0, "Unit Cost ($)": 1.50, "Mins to Install": 15}
    ]

# --- RENDER THE CALCULATOR ---
st.write("### 📊 Material & Labor Takeoff Worksheet")
df = pd.DataFrame(scanned_data)

edited_df = st.data_editor(
    df, 
    num_rows="dynamic",
    column_config={
        "Detected Qty": st.column_config.NumberColumn("Detected Qty", min_value=0, step=1, format="%d"),
        "Unit Cost ($)": st.column_config.NumberColumn("Unit Cost ($)", format="$%.2f"),
        "Mins to Install": st.column_config.NumberColumn("Mins to Install", format="%d mins")
    }
)

# --- LIVE MATH ENGINE ---
edited_df["Detected Qty"] = pd.to_numeric(edited_df["Detected Qty"]).fillna(0)
edited_df["Unit Cost ($)"] = pd.to_numeric(edited_df["Unit Cost ($)"]).fillna(0)
edited_df["Mins to Install"] = pd.to_numeric(edited_df["Mins to Install"]).fillna(0)

total_mat = (edited_df["Detected Qty"] * edited_df["Unit Cost ($)"]).sum()
total_labor = ((edited_df["Detected Qty"] * edited_df["Mins to Install"] / 60) * labor_rate).sum()
final_bid = (total_mat + total_labor) * (1 + overhead)

# --- LIVE FINANCIAL DASHBOARD ---
st.divider()
col1, col2, col3 = st.columns(3)
col1.metric("Total Material Cost", f"${total_mat:,.2f}")
col2.metric("Total Labor Cost", f"${total_labor:,.2f}")
col3.metric("Total Suggested Bid", f"${final_bid:,.2f}", delta=f"{overhead*100:.0f}% Markup Included")