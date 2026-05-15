import streamlit as st
import pdfplumber
import pandas as pd
import re
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import random
import datetime

st.set_page_config(page_title="Active Worksheet", layout="wide")

st.title("📊 Core Estimation Worksheet")

# --- ENSURE PARENT INITIALIZATION ---
if "company_name" not in st.session_state:
    st.error("Please return to the main Dashboard page to initialize your session parameters.")
    st.stop()

# --- LIVE MARKET SIMULATOR LINK ---
today_str = datetime.date.today().strftime("%Y%m%d")
random.seed(int(today_str))
market_multiplier = 1.0 + random.uniform(-0.05, 0.12)

# --- SIDEBAR TUNING PROFILES ---
with st.sidebar:
    st.header("🔍 Custom Regex Profiles")
    panel_kw = st.text_input("Main Panel Keywords", value="panel, load center, mlo")
    gfci_kw = st.text_input("GFCI Keywords", value="gfci, gfi, ground fault")
    disc_kw = st.text_input("Disconnect Keywords", value="disconnect, safety switch")
    switch_kw = st.text_input("Switch Keywords", value="single pole, 1-pole switch")
    
    st.divider()
    st.metric("Live Market Cost Index Adjuster", f"{((market_multiplier - 1) * 100):.2f}%")

# --- TEXT SCANNING UTILITY ---
@st.cache_data
def process_and_scan_blueprint(uploaded_file_bytes, p_kw, g_kw, d_kw, s_kw, live_multiplier):
    pdf_file = BytesIO(uploaded_file_bytes)
    full_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += text + "\n"
            
    def clean_pattern(raw_input):
        parts = [p.strip() for p in raw_input.split(",")]
        return r"(\d+)\s*(?:-|x)?\s*(?:amp)?\s*(?:" + "|".join(parts) + ")"

    electrical_manifest = {
        "Main Panel Enclosure": {"pattern": clean_pattern(p_kw), "cost": round(450.00 * live_multiplier, 2), "mins": 120, "phase": "Rough-In", "zone": "Service Room"},
        "GFCI Receptacle": {"pattern": clean_pattern(g_kw), "cost": round(18.00 * live_multiplier, 2), "mins": 20, "phase": "Trim-Out", "zone": "Wet Areas (Kitchen/Bath)"},
        "Disconnect Switch": {"pattern": clean_pattern(d_kw), "cost": round(85.00 * live_multiplier, 2), "mins": 45, "phase": "Rough-In", "zone": "HVAC / Equipment"},
        "Single Pole Switch": {"pattern": clean_pattern(s_kw), "cost": round(1.50 * live_multiplier, 2), "mins": 15, "phase": "Trim-Out", "zone": "General Lighting"}
    }
    
    scanned_results = []
    for item, info in electrical_manifest.items():
        matches = re.findall(info["pattern"], full_text, re.IGNORECASE)
        total_qty = sum(int(match) for match in matches if match.isdigit())
        
        scanned_results.append({
            "Item Name": item, "Phase": info["phase"], "Zone/Location": info["zone"],
            "Detected Qty": total_qty, "Unit Cost ($)": info["cost"], "Mins to Install": info["mins"]
        })
    return scanned_results

# --- EXECUTE SCAN ---
if st.session_state.uploaded_file_bytes is not None:
    scanned_data = process_and_scan_blueprint(st.session_state.uploaded_file_bytes, panel_kw, gfci_kw, disc_kw, switch_kw, market_multiplier)
else:
    scanned_data = [
        {"Item Name": "Main Panel Enclosure", "Phase": "Rough-In", "Zone/Location": "Service Room", "Detected Qty": 0, "Unit Cost ($)": round(450.00 * market_multiplier, 2), "Mins to Install": 120},
        {"Item Name": "Disconnect Switch", "Phase": "Rough-In", "Zone/Location": "HVAC / Equipment", "Detected Qty": 0, "Unit Cost ($)": round(85.00 * market_multiplier, 2), "Mins to Install": 45},
        {"Item Name": "GFCI Receptacle", "Phase": "Trim-Out", "Zone/Location": "Wet Areas (Kitchen/Bath)", "Detected Qty": 0, "Unit Cost ($)": round(18.00 * market_multiplier, 2), "Mins to Install": 20},
        {"Item Name": "Single Pole Switch", "Phase": "Trim-Out", "Zone/Location": "General Lighting", "Detected Qty": 0, "Unit Cost ($)": round(1.50 * market_multiplier, 2), "Mins to Install": 15}
    ]

master_df = pd.DataFrame(scanned_data)

# Inject Conduit session results
if st.session_state.conduit_runs > 0:
    master_df = pd.concat([master_df, pd.DataFrame([{"Item Name": "3/4\" EMT Conduit Run (Linear Ft)", "Phase": "Rough-In", "Zone/Location": "Branch Run Takeoff", "Detected Qty": int(st.session_state.conduit_runs), "Unit Cost ($)": round(1.25 * market_multiplier, 2), "Mins to Install": 4}])], ignore_index=True)

# Inject Vision session results
for item_name, count in st.session_state.vision_counts.items():
    if count > 0:
        master_df = pd.concat([master_df, pd.DataFrame([{"Item Name": f"AI Scan: {item_name}", "Phase": "Trim-Out", "Zone/Location": "Vision Takeoff", "Detected Qty": count, "Unit Cost ($)": round(24.50 * market_multiplier, 2), "Mins to Install": 25}])], ignore_index=True)

# --- UI MATRIX WORKSPACE ---
edited_df = st.data_editor(master_df, num_rows="dynamic", use_container_width=True)

edited_df["Detected Qty"] = pd.to_numeric(edited_df["Detected Qty"]).fillna(0)
edited_df["Unit Cost ($)"] = pd.to_numeric(edited_df["Unit Cost ($)"]).fillna(0)
edited_df["Mins to Install"] = pd.to_numeric(edited_df["Mins to Install"]).fillna(0)

total_mat = (edited_df["Detected Qty"] * edited_df["Unit Cost ($)"]).sum()
total_labor = ((edited_df["Detected Qty"] * edited_df["Mins to Install"] / 60) * st.session_state.labor_rate).sum()
final_bid = (total_mat + total_labor) * (1 + st.session_state.overhead)

# --- LIVE METRIC STRIPS ---
st.divider()
colA, colB, colC = st.columns(3)
colA.metric("Material Cost Subtotal", f"${total_mat:,.2f}")
colB.metric("Labor Cost Subtotal", f"${total_labor:,.2f}")
colC.metric("Target Contract Price", f"${final_bid:,.2f}", delta=f"{st.session_state.overhead * 100:.0f}% Margin Configured")

# --- EXCEL COMPILATION HOOK ---
def generate_executive_excel(df_data, mat_cost, labor_cost, total_bid, overhead_pct, rate, comp_name):
    output = BytesIO()
    wb = openpyxl.Workbook()
    font_family = "Segoe UI"
    charcoal_fill = PatternFill(start_color="262626", end_color="262626", fill_type="solid")
    gold_accent_fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")
    ice_fill = PatternFill(start_color="F2F2F2", end_color="F2F2F2", fill_type="solid")
    title_font = Font(name=font_family, size=18, bold=True, color="262626")
    section_font = Font(name=font_family, size=12, bold=True, color="FFFFFF")
    bold_font = Font(name=font_family, size=11, bold=True)
    regular_font = Font(name=font_family, size=11)
    thin_border = Border(left=Side(style='thin', color='D9D9D9'), right=Side(style='thin', color='D9D9D9'), top=Side(style='thin', color='D9D9D9'), bottom=Side(style='thin', color='D9D9D9'))
    
    ws1 = wb.active; ws1.title = "Executive Summary"; ws1.views.sheetView[0].showGridLines = True
    ws1["A1"] = f"{comp_name.upper()} PROPOSAL"; ws1["A1"].font = title_font
    ws1.merge_cells("A4:B4"); ws1["A4"] = "PROJECT FINANCIAL SUMMARY"; ws1["A4"].fill = charcoal_fill; ws1["A4"].font = section_font
    
    metrics = [("Material Cost (Live Index)", mat_cost), ("Labor Cost Allocation", labor_cost), ("Labor Rate Configuration ($/hr)", rate), ("Markup Burden Percentage", overhead_pct)]
    for idx, (m, v) in enumerate(metrics, start=5):
        ws1[f"A{idx}"] = m; ws1[f"A{idx}"].font = regular_font; ws1[f"A{idx}"].border = thin_border
        ws1[f"B{idx}"] = v; ws1[f"B{idx}"].font = regular_font; ws1[f"B{idx}"].border = thin_border
        ws1[f"B{idx}"].number_format = '0.0%' if idx == 8 else '$#,##0.00'
        
    ws1["A10"] = "TOTAL TARGET CONTRACT BID"; ws1["A10"].font = bold_font; ws1["A10"].fill = gold_accent_fill; ws1["A10"].border = thin_border
    ws1["B10"] = total_bid; ws1["B10"].font = Font(name=font_family, size=12, bold=True, color="C00000"); ws1["B10"].fill = gold_accent_fill; ws1["B10"].border = thin_border; ws1["B10"].number_format = '$#,##0.00'
    
    ws2 = wb.create_sheet(title="Bill of Materials"); ws2.views.sheetView[0].showGridLines = True
    headers = ["Component Name", "Phase", "Target Zone", "Takeoff Qty", "Estimated Unit Cost"]
    for idx, t in enumerate(headers, start=1):
        cell = ws2.cell(row=1, column=idx, value=t); cell.fill = charcoal_fill; cell.font = section_font
        
    for r_idx, r_data in df_data.iterrows():
        r = r_idx + 2
        ws2.cell(row=r, column=1, value=r_data["Item Name"]).font = regular_font
        ws2.cell(row=r, column=2, value=r_data["Phase"]).font = regular_font
        ws2.cell(row=r, column=3, value=r_data["Zone/Location"]).font = regular_font
        ws2.cell(row=r, column=4, value=r_data["Detected Qty"]).number_format = '#,##0'
        ws2.cell(row=r, column=5, value=r_data["Unit Cost ($)"]).number_format = '$#,##0.00'
        for c in range(1, 6): ws2.cell(row=r, column=c).border = thin_border

    wb.save(output)
    return output.getvalue()

excel_data = generate_executive_excel(edited_df, total_mat, total_labor, final_bid, st.session_state.overhead, st.session_state.labor_rate, st.session_state.company_name)
st.download_button("🚀 Export Executive Proposal Package (.xlsx)", data=excel_data, file_name="Executive_Bid.xlsx")