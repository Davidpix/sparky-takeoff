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
import math

st.set_page_config(page_title="Active Worksheet", layout="wide")

st.title("📊 Core Estimation Worksheet & Materializer Engine")
st.write("This sheet aggregates your blueprint text scans, multi-sheet vector tracings, and automatically calculates complete field material packages based on the NEC Code book.")

if "company_name" not in st.session_state:
    st.error("⚠️ Please return to the main Dashboard Gateway page to initialize your session parameters.")
    st.stop()

# Fallback crew logic
if "qty_journeymen" not in st.session_state: st.session_state.qty_journeymen = 1
if "rate_journeyman" not in st.session_state: st.session_state.rate_journeyman = 45.0
if "qty_helpers" not in st.session_state: st.session_state.qty_helpers = 1
if "rate_helper" not in st.session_state: st.session_state.rate_helper = 22.0
if "labor_burden_pct" not in st.session_state: st.session_state.labor_burden_pct = 0.30

total_crew_members = st.session_state.qty_journeymen + st.session_state.qty_helpers
raw_composite_rate = ((st.session_state.qty_journeymen * st.session_state.rate_journeyman) + (st.session_state.qty_helpers * st.session_state.rate_helper)) / total_crew_members
fully_burdened_labor_rate = raw_composite_rate * (1 + st.session_state.labor_burden_pct)

# --- READ LIVE DISTRIBUTOR PRICING OR USE FALLBACK MATRICES ---
if "vendor_pricing" not in st.session_state:
    st.session_state.vendor_pricing = {
        "Main Panel Enclosure": 450.00, "GFCI Receptacle": 18.00, 
        "Disconnect Switch": 85.00, "Single Pole Switch": 1.50,
        "3/4\" EMT Conduit Run (Linear Ft)": 1.25
    }

# Read live synced price modifiers from app.py, adjusting sub-components relative to base pricing indexes
conduit_base_cost = st.session_state.vendor_pricing.get("3/4\" EMT Conduit Run (Linear Ft)", 1.25)
price_ratio = conduit_base_cost / 1.25

# --- AUTOMATED MATERIALIZER & NEC COMPLIANCE LOGIC ---
total_raw_footage = 0.0
active_zone_tag = "General Branch Run"

if "sheet_ledger" in st.session_state:
    for sheet_id, data in st.session_state.sheet_ledger.items():
        total_raw_footage += data["conduit_runs"] + data["vertical_drops"]
        if data["conduit_runs"] > 0:
            active_zone_tag = data["active_zone"]

rows_to_compile = []

if total_raw_footage > 0:
    st.info(f"⚡ **NEC Takeoff Compliance Engine Active:** Exploding {total_raw_footage:.2f} Linear Feet of raw circuit tracing into code-compliant field material line items...")
    
    # 1. Compute 10-foot Conduit Factory Sticks
    conduit_sticks = math.ceil(total_raw_footage / 10.0)
    rows_to_compile.append({
        "Item Name": "3/4\" EMT Conduit (10ft Factory Sticks)", "Phase": "Rough-In", "Zone/Location": active_zone_tag,
        "Detected Qty": int(conduit_sticks), "Unit Cost ($)": round(6.50 * price_ratio, 2), "Mins to Install": 12
    })
    
    # 2. Compute 3/4" Set-Screw Couplings
    couplings_needed = max(conduit_sticks - 1, 0)
    if couplings_needed > 0:
        rows_to_compile.append({
            "Item Name": "3/4\" EMT Set-Screw Coupling", "Phase": "Rough-In", "Zone/Location": active_zone_tag,
            "Detected Qty": int(couplings_needed), "Unit Cost ($)": round(1.15 * price_ratio, 2), "Mins to Install": 3
        })
        
    # 3. Compute NEC-Compliant Conduit Support Straps (NEC 358.30)
    straps_needed = math.ceil(total_raw_footage / 8.0) + 2
    rows_to_compile.append({
        "Item Name": "3/4\" 1-Hole EMT Strap (NEC 358.30 Compliant)", "Phase": "Rough-In", "Zone/Location": active_zone_tag,
        "Detected Qty": int(straps_needed), "Unit Cost ($)": round(0.45 * price_ratio, 2), "Mins to Install": 2
    })

# --- PROCESS BLUEPRINT REGEX DATA TEXT SCANS ---
with st.sidebar:
    st.header("🔍 Custom Regex Profiles")
    panel_kw = st.text_input("Main Panel Keywords", value="panel, load center, mlo")
    gfci_kw = st.text_input("GFCI Keywords", value="gfci, gfi, ground fault")
    disc_kw = st.text_input("Disconnect Keywords", value="disconnect, safety switch")
    switch_kw = st.text_input("Switch Keywords", value="single pole, 1-pole switch")
    st.divider()
    st.metric("Active Burdened Billing Rate", f"${fully_burdened_labor_rate:,.2f}/hr")

@st.cache_data
def process_and_scan_blueprint(uploaded_file_bytes, p_kw, g_kw, d_kw, s_kw, prices_dict):
    pdf_file = BytesIO(uploaded_file_bytes)
    full_text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text: full_text += text + "\n"
            
    def clean_pattern(raw_input):
        parts = [p.strip() for p in raw_input.split(",")]
        return r"(\d+)\s*(?:-|x)?\s*(?:amp)?\s*(?:" + "|".join(parts) + ")"

    electrical_manifest = {
        "Main Panel Enclosure": {"pattern": clean_pattern(p_kw), "cost": prices_dict["Main Panel Enclosure"], "mins": 120, "phase": "Rough-In", "zone": "Service Room"},
        "GFCI Receptacle": {"pattern": clean_pattern(g_kw), "cost": prices_dict["GFCI Receptacle"], "mins": 20, "phase": "Trim-Out", "zone": "Wet Areas (Kitchen/Bath)"},
        "Disconnect Switch": {"pattern": clean_pattern(d_kw), "cost": prices_dict["Disconnect Switch"], "mins": 45, "phase": "Rough-In", "zone": "HVAC / Equipment"},
        "Single Pole Switch": {"pattern": clean_pattern(s_kw), "cost": prices_dict["Single Pole Switch"], "mins": 15, "phase": "Trim-Out", "zone": "General Lighting"}
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

if st.session_state.uploaded_file_bytes is not None:
    base_data = process_and_scan_blueprint(st.session_state.uploaded_file_bytes, panel_kw, gfci_kw, disc_kw, switch_kw, st.session_state.vendor_pricing)
else:
    base_data = []

master_df = pd.DataFrame(base_data)
if rows_to_compile:
    canvas_df = pd.DataFrame(rows_to_compile)
    master_df = pd.concat([master_df, canvas_df], ignore_index=True)

# Inject Vision Computer Vision rows
for item_name, count in st.session_state.vision_counts.items():
    if count > 0:
        vision_row = pd.DataFrame([{
            "Item Name": f"AI Scan: {item_name}", "Phase": "Trim-Out", "Zone/Location": "Vision Takeoff Area", 
            "Detected Qty": count, "Unit Cost ($)": 24.50, "Mins to Install": 25
        }])
        master_df = pd.concat([master_df, vision_row], ignore_index=True)

st.caption("Review compiled data metrics below. Double-click any quantity cell to adjust.")
edited_df = st.data_editor(master_df, num_rows="dynamic", use_container_width=True)

edited_df["Detected Qty"] = pd.to_numeric(edited_df["Detected Qty"]).fillna(0)
edited_df["Unit Cost ($)"] = pd.to_numeric(edited_df["Unit Cost ($)"]).fillna(0)
edited_df["Mins to Install"] = pd.to_numeric(edited_df["Mins to Install"]).fillna(0)

total_mat = (edited_df["Detected Qty"] * edited_df["Unit Cost ($)"]).sum()
total_labor = ((edited_df["Detected Qty"] * edited_df["Mins to Install"] / 60) * fully_burdened_labor_rate).sum()
final_bid = (total_mat + total_labor) * (1 + st.session_state.overhead)

st.divider()
colA, colB, colC = st.columns(3)
colA.metric("Material Cost Subtotal", f"${total_mat:,.2f}")
colB.metric("Fully Burdened Labor Subtotal", f"${total_labor:,.2f}")
colC.metric("Target Contract Price", f"${final_bid:,.2f}", delta=f"{st.session_state.overhead * 100:.0f}% Gross Margin Linked")

# --- HIGH-FIDELITY EXCEL COMPILATION HOOK ---
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
    
    metrics = [("Material Cost Subtotal", mat_cost), ("Burdened Labor Allocation", labor_cost), ("Blended Crew Composite Rate ($/hr)", rate), ("Markup Burden Percentage", overhead_pct)]
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
        
        if r_idx % 2 == 0:
            for col_c in range(1, 6): ws2.cell(row=r, column=col_c).fill = ice_fill
        for col_c in range(1, 6): ws2.cell(row=r, column=col_c).border = thin_border

    for sheet in [ws1, ws2]:
        for col in sheet.columns:
            vals = [str(cell.value or '') for cell in col]
            max_len = max(len(v) for v in vals) if vals else 10
            col_letter = get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 14)

    wb.save(output)
    return output.getvalue()

st.write("### 📥 Document Distribution Panel")
excel_data = generate_executive_excel(edited_df, total_mat, total_labor, final_bid, st.session_state.overhead, fully_burdened_labor_rate, st.session_state.company_name)
st.download_button("🚀 Export Executive Proposal Package (.xlsx)", data=excel_data, file_name="Executive_Bid.xlsx")