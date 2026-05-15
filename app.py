import streamlit as st
import PyPDF2
import pandas as pd
import re
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

st.set_page_config(page_title="SparkyTakeoff Pro", layout="wide")

st.title("⚡ SparkyTakeoff: Enterprise Export Edition")

# --- SIDEBAR: GLOBAL FINANCIALS ---
with st.sidebar:
    st.header("⚙️ Global Bid Settings")
    labor_rate = st.number_input("Hourly Labor Rate ($)", value=85.0, step=5.0)
    overhead = st.slider("Overhead & Profit Markup (%)", 10, 50, 20) / 100
    st.divider()

# --- CACHING ENGINE ---
@st.cache_data
def process_and_scan_blueprint(uploaded_file):
    reader = PyPDF2.PdfReader(uploaded_file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
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
    scanned_data = [
        {"Item Name": "Main Panel Enclosure", "Phase": "Rough-In", "Zone/Location": "Service Room", "Detected Qty": 0, "Unit Cost ($)": 450.00, "Mins to Install": 120},
        {"Item Name": "12/2 Romex (250ft coil)", "Phase": "Rough-In", "Zone/Location": "Branch Wiring", "Detected Qty": 0, "Unit Cost ($)": 110.00, "Mins to Install": 60},
        {"Item Name": "Disconnect Switch", "Phase": "Rough-In", "Zone/Location": "HVAC / Equipment", "Detected Qty": 0, "Unit Cost ($)": 85.00, "Mins to Install": 45},
        {"Item Name": "GFCI Receptacle", "Phase": "Trim-Out", "Zone/Location": "Wet Areas (Kitchen/Bath)", "Detected Qty": 0, "Unit Cost ($)": 18.00, "Mins to Install": 20},
        {"Item Name": "Single Pole Switch", "Phase": "Trim-Out", "Zone/Location": "General Lighting", "Detected Qty": 0, "Unit Cost ($)": 1.50, "Mins to Install": 15}
    ]

master_df = pd.DataFrame(scanned_data)

# --- FILTER CONTROLS ---
st.write("### 🔍 Live Project Filters")
col_f1, col_f2 = st.columns(2)
with col_f1:
    phase_filter = st.selectbox("Select Project Phase", ["All Phases", "Rough-In", "Trim-Out"])
with col_f2:
    all_zones = ["All Zones"] + list(master_df["Zone/Location"].unique())
    zone_filter = st.selectbox("Select Physical Zone/Location", all_zones)

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

# --- SYNC DATA BACK TO MASTER ---
master_df.set_index("Item Name", inplace=True)
edited_df.set_index("Item Name", inplace=True)
master_df.update(edited_df)
master_df.reset_index(inplace=True)

master_df["Detected Qty"] = pd.to_numeric(master_df["Detected Qty"]).fillna(0)
master_df["Unit Cost ($)"] = pd.to_numeric(master_df["Unit Cost ($)"]).fillna(0)
master_df["Mins to Install"] = pd.to_numeric(master_df["Mins to Install"]).fillna(0)

# Calculations
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

# --- HIGH-FIDELITY EXCEL GENERATION ENGINE ---
def generate_excel_package(df_data, mat_cost, labor_cost, total_bid, overhead_pct, rate):
    output = BytesIO()
    wb = openpyxl.Workbook()
    
    # Setup Styles
    font_family = "Segoe UI"
    header_fill = PatternFill(start_color="1F4E78", end_color="1F4E78", fill_type="solid") # Dark Blue
    accent_fill = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid") # Light Slate Tint
    
    title_font = Font(name=font_family, size=16, bold=True, color="1F4E78")
    header_font = Font(name=font_family, size=11, bold=True, color="FFFFFF")
    bold_font = Font(name=font_family, size=11, bold=True)
    regular_font = Font(name=font_family, size=11)
    
    thin_border = Border(
        left=Side(style='thin', color='BFBFBF'),
        right=Side(style='thin', color='BFBFBF'),
        top=Side(style='thin', color='BFBFBF'),
        bottom=Side(style='thin', color='BFBFBF')
    )
    
    # --- TAB 1: SUMMARY & FINANCIALS ---
    ws1 = wb.active
    ws1.title = "Proposal Summary"
    ws1.views.sheetView[0].showGridLines = True
    
    ws1["A1"] = "SPARKYTAKEOFF ENTERPRISE PROPOSAL"
    ws1["A1"].font = title_font
    
    ws1["A3"] = "Financial Metric"
    ws1["B3"] = "Calculated Value"
    for col in ["A", "B"]:
        cell = ws1[f"{col}3"]
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center")
    
    summary_metrics = [
        ("Base Material Subtotal", mat_cost),
        ("Base Labor Subtotal", labor_cost),
        ("Blended Labor Rate Configuration", rate),
        ("Applied Corporate Overhead / Profit Margin", overhead_pct),
        ("Total Estimated Target Contract Price", total_bid)
    ]
    
    for idx, (metric, val) in enumerate(summary_metrics, start=4):
        ws1[f"A{idx}"] = metric
        ws1[f"A{idx}"].font = regular_font
        ws1[f"B{idx}"] = val
        ws1[f"B{idx}"].font = bold_font if idx == 8 else regular_font
        
        # Formatting specifics
        if idx == 7: # Overhead percentage
            ws1[f"B{idx}"].number_format = '0.0%'
        else:
            ws1[f"B{idx}"].number_format = '$#,##0.00'
            
        ws1[f"A{idx}"].border = thin_border
        ws1[f"B{idx}"].border = thin_border
        
    # --- TAB 2: FIELD PURCHASE ORDER ---
    ws2 = wb.create_sheet(title="Field Purchase Order")
    ws2.views.sheetView[0].showGridLines = True
    
    headers = ["Item Name", "Project Phase", "Zone/Location", "Quantity Order", "Unit Material Cost"]
    for col_idx, text in enumerate(headers, start=1):
        cell = ws2.cell(row=1, column=col_idx, value=text)
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True)
        
    for row_idx, row_data in df_data.iterrows():
        ws2.cell(row=row_idx+2, column=1, value=row_data["Item Name"]).font = regular_font
        ws2.cell(row=row_idx+2, column=2, value=row_data["Phase"]).font = regular_font
        ws2.cell(row=row_idx+2, column=3, value=row_data["Zone/Location"]).font = regular_font
        
        qty_cell = ws2.cell(row=row_idx+2, column=4, value=row_data["Detected Qty"])
        qty_cell.font = regular_font
        qty_cell.number_format = '#,##0'
        
        cost_cell = ws2.cell(row=row_idx+2, column=5, value=row_data["Unit Cost ($)"])
        cost_cell.font = regular_font
        cost_cell.number_format = '$#,##0.00'
        
        for c in range(1, 6):
            ws2.cell(row=row_idx+2, column=c).border = thin_border

    # Auto-adjust column widths cleanly across sheets
    for sheet in [ws1, ws2]:
        for col in sheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 12)
            
    wb.save(output)
    return output.getvalue()

# --- RENDER EXPORT ACTIONS ---
st.write("### 📥 Document Distribution Panel")
excel_data = generate_excel_package(master_df, total_mat, total_labor, final_bid, overhead, labor_rate)

st.download_button(
    label="🚀 Export Enterprise Excel Package (.xlsx)",
    data=excel_data,
    file_name="SparkyTakeoff_Master_Estimate.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)