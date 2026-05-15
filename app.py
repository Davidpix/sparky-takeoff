import streamlit as st
import PyPDF2
import pypdfum2 as pdfium
import pandas as pd
import re
from io import BytesIO
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

st.set_page_config(page_title="SparkyTakeoff Enterprise", layout="wide")

st.title("⚡ SparkyTakeoff: Enterprise Visual Edition")

# --- SIDEBAR: GLOBAL SETTINGS & KEYWORD TUNING ---
with st.sidebar:
    st.header("💼 Executive Controls")
    company_name = st.text_input("Company Name", value="Shard Visuals & Electrical")
    labor_rate = st.number_input("Hourly Labor Rate ($)", value=85.0, step=5.0)
    overhead = st.slider("Overhead & Profit Markup (%)", 10, 50, 20) / 100
    
    st.divider()
    st.header("🔍 Custom Regex Tuning Profiles")
    panel_kw = st.text_input("Main Panel Keywords", value="panel, load center, mlo")
    gfci_kw = st.text_input("GFCI Keywords", value="gfci, gfi, ground fault")
    disc_kw = st.text_input("Disconnect Keywords", value="disconnect, safety switch")
    switch_kw = st.text_input("Switch Keywords", value="single pole, 1-pole switch")

# --- CACHING ENGINE WITH DYNAMIC PROFILES ---
@st.cache_data
def process_and_scan_blueprint(uploaded_file_bytes, p_kw, g_kw, d_kw, s_kw):
    # Read the PDF from raw bytes to keep memory footprint clean
    pdf_file = BytesIO(uploaded_file_bytes)
    reader = PyPDF2.PdfReader(pdf_file)
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"
            
    def clean_pattern(raw_input):
        parts = [p.strip() for p in raw_input.split(",")]
        return r"(\d+)\s*(?:-|x)?\s*(?:amp)?\s*(?:" + "|".join(parts) + ")"

    electrical_manifest = {
        "Main Panel Enclosure": {"pattern": clean_pattern(p_kw), "cost": 450.00, "mins": 120, "phase": "Rough-In", "zone": "Service Room"},
        "GFCI Receptacle": {"pattern": clean_pattern(g_kw), "cost": 18.00, "mins": 20, "phase": "Trim-Out", "zone": "Wet Areas (Kitchen/Bath)"},
        "Disconnect Switch": {"pattern": clean_pattern(d_kw), "cost": 85.00, "mins": 45, "phase": "Rough-In", "zone": "HVAC / Equipment"},
        "Single Pole Switch": {"pattern": clean_pattern(s_kw), "cost": 1.50, "mins": 15, "phase": "Trim-Out", "zone": "General Lighting"}
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

# --- FILE HANDLING ---
uploaded_file = st.file_uploader("Upload Blueprint PDF for Dynamic Scan & Visualization", type="pdf")

if uploaded_file is not None:
    # Read file once into raw bytes to pass safely into our cached functions
    file_bytes = uploaded_file.read()
    scanned_data = process_and_scan_blueprint(file_bytes, panel_kw, gfci_kw, disc_kw, switch_kw)
else:
    file_bytes = None
    scanned_data = [
        {"Item Name": "Main Panel Enclosure", "Phase": "Rough-In", "Zone/Location": "Service Room", "Detected Qty": 0, "Unit Cost ($)": 450.00, "Mins to Install": 120},
        {"Item Name": "Disconnect Switch", "Phase": "Rough-In", "Zone/Location": "HVAC / Equipment", "Detected Qty": 0, "Unit Cost ($)": 85.00, "Mins to Install": 45},
        {"Item Name": "GFCI Receptacle", "Phase": "Trim-Out", "Zone/Location": "Wet Areas (Kitchen/Bath)", "Detected Qty": 0, "Unit Cost ($)": 18.00, "Mins to Install": 20},
        {"Item Name": "Single Pole Switch", "Phase": "Trim-Out", "Zone/Location": "General Lighting", "Detected Qty": 0, "Unit Cost ($)": 1.50, "Mins to Install": 15}
    ]

master_df = pd.DataFrame(scanned_data)

# --- ENTERPRISE INTERFACE: TABULAR VIEWPORTS ---
tab1, tab2 = st.tabs(["📊 Estimation Worksheet", "🗺️ Interactive Blueprint Viewport"])

with tab1:
    st.write(r"### Active Estimation Workspace")
    edited_df = st.data_editor(
        master_df, 
        num_rows="dynamic",
        column_config={
            "Phase": st.column_config.SelectboxColumn("Phase", options=["Rough-In", "Trim-Out"], required=True),
            "Detected Qty": st.column_config.NumberColumn("Qty", min_value=0, step=1),
            "Unit Cost ($)": st.column_config.NumberColumn("Unit Cost", format="$%.2f"),
            "Mins to Install": st.column_config.NumberColumn("Labor Mins", format="%d mins")
        },
        use_container_width=True,
        key="workspace_editor"
    )

    # Calculations
    edited_df["Detected Qty"] = pd.to_numeric(edited_df["Detected Qty"]).fillna(0)
    edited_df["Unit Cost ($)"] = pd.to_numeric(edited_df["Unit Cost ($)"]).fillna(0)
    edited_df["Mins to Install"] = pd.to_numeric(edited_df["Mins to Install"]).fillna(0)

    total_mat = (edited_df["Detected Qty"] * edited_df["Unit Cost ($)"]).sum()
    total_labor = ((edited_df["Detected Qty"] * edited_df["Mins to Install"] / 60) * labor_rate).sum()
    final_bid = (total_mat + total_labor) * (1 + overhead)

    # --- LIVE FINANCIAL DASHBOARD ---
    st.divider()
    col1, col2, col3 = st.columns(3)
    col1.metric("Gross Material Allocation", f"${total_mat:,.2f}")
    col2.metric("Gross Labor Allocation", f"${total_labor:,.2f}")
    col3.metric("Target Contract Price", f"${final_bid:,.2f}", delta=f"{overhead*100:.0f}% Gross Margin")

with tab2:
    st.write("### 🗺️ Blueprint Document Viewport")
    if file_bytes is not None:
        # Load the blueprint dynamically using pdfium
        pdf = pdfium.PdfDocument(BytesIO(file_bytes))
        total_pages = len(pdf)
        
        col_ctrl1, col_ctrl2 = st.columns([1, 4])
        with col_ctrl1:
            page_number = st.number_input("Page Selector", min_value=1, max_value=total_pages, value=1, step=1)
        with col_ctrl2:
            st.info(f"Viewing sheet {page_number} of {total_pages}. Zoom and resolution are optimized for rendering speed.")
            
        # Render page to image instantly
        page = pdf[page_number - 1]
        # 1.5 scale provides an excellent balance between sharp visual details and processing speed
        bitmap = page.render(scale=1.5)
        pil_img = bitmap.to_pil()
        
        # Display the blueprint directly inside the web browser tab
        st.image(pil_img, use_container_width=True, caption=f"Page {page_number} - Visual Audit Layout")
    else:
        st.info("💡 Please upload a blueprint PDF document at the top to initialize the Interactive Blueprint Viewport.")

# --- EXPORT INTERFACE ---
st.write("### 📥 Document Distribution Panel")
# (Excel generation engine helper remains structured as designed previously)
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
    
    ws1 = wb.active
    ws1.title = "Executive Summary"
    ws1.views.sheetView[0].showGridLines = True
    ws1["A1"] = f"{comp_name.upper()}"
    ws1["A1"].font = title_font
    ws1["A2"] = "CONFIDENTIAL COMMERCIAL ESTIMATE & PROJECT PROPOSAL"
    ws1["A2"].font = Font(name=font_family, size=10, italic=True, color="595959")
    ws1.merge_cells("A4:B4")
    ws1["A4"] = "PROJECT FINANCIAL SUMMARY"
    ws1["A4"].fill = charcoal_fill
    ws1["A4"].font = section_font
    ws1["A4"].alignment = Alignment(horizontal="left", indent=1)
    
    metrics = [("Base Material Subtotal Cost", mat_cost), ("Base Labor Production Cost", labor_cost), ("Blended Labor Hourly Configuration", rate), ("Contractor Burden / Markup Percentage", overhead_pct)]
    for idx, (metric, val) in enumerate(metrics, start=5):
        ws1[f"A{idx}"] = metric
        ws1[f"A{idx}"].font = regular_font
        ws1[f"A{idx}"].border = thin_border
        ws1[f"B{idx}"] = val
        ws1[f"B{idx}"].font = regular_font
        ws1[f"B{idx}"].border = thin_border
        ws1[f"B{idx}"].number_format = '0.0%' if idx == 8 else '$#,##0.00'
        
    ws1["A10"] = "TOTAL TARGET CONTRACT BID"
    ws1["A10"].font = bold_font
    ws1["A10"].fill = gold_accent_fill
    ws1["A10"].border = thin_border
    ws1["B10"] = total_bid
    ws1["B10"].font = Font(name=font_family, size=12, bold=True, color="C00000")
    ws1["B10"].fill = gold_accent_fill
    ws1["B10"].border = thin_border
    ws1["B10"].number_format = '$#,##0.00'
    
    ws1["A13"] = "Client Acceptance Sign-Off"
    ws1["A13"].font = bold_font
    ws1["A14"] = "By signing below, the client authorizes execution of works detailed herein."
    ws1["A14"].font = Font(name=font_family, size=9, italic=True, color="595959")
    ws1["A16"] = "Signature: __________________________"
    ws1["A16"].font = regular_font
    ws1["B16"] = "Date: _______________"
    ws1["B16"].font = regular_font

    ws2 = wb.create_sheet(title="Itemized Bill of Materials")
    ws2.views.sheetView[0].showGridLines = True
    headers = ["Itemized Component Name", "Operational Phase", "Target Physical Zone", "Takeoff Qty", "Estimated Unit Cost"]
    for col_idx, text in enumerate(headers, start=1):
        cell = ws2.cell(row=1, column=col_idx, value=text)
        cell.fill = charcoal_fill
        cell.font = section_font
        cell.alignment = Alignment(horizontal="center", vertical="center")
        
    for row_idx, row_data in df_data.iterrows():
        r = row_idx + 2
        ws2.cell(row=r, column=1, value=row_data["Item Name"]).font = regular_font
        ws2.cell(row=r, column=2, value=row_data["Phase"]).font = regular_font
        ws2.cell(row=r, column=3, value=row_data["Zone/Location"]).font = regular_font
        q_cell = ws2.cell(row=r, column=4, value=row_data["Detected Qty"])
        q_cell.font = regular_font
        q_cell.number_format = '#,##0'
        c_cell = ws2.cell(row=r, column=5, value=row_data["Unit Cost ($)"])
        c_cell.font = regular_font
        c_cell.number_format = '$#,##0.00'
        
        if row_idx % 2 == 0:
            for col_c in range(1, 6):
                ws2.cell(row=r, column=col_c).fill = ice_fill
        for col_c in range(1, 6):
            ws2.cell(row=r, column=col_c).border = thin_border

    for sheet in [ws1, ws2]:
        for col in sheet.columns:
            vals = [str(cell.value or '') for cell in col]
            max_len = max(len(v) for v in vals) if vals else 10
            col_letter = get_column_letter(col[0].column)
            sheet.column_dimensions[col_letter].width = max(max_len + 3, 14)
            
    wb.save(output)
    return output.getvalue()

excel_data = generate_executive_excel(edited_df, total_mat, total_labor, final_bid, overhead, labor_rate, company_name)

st.download_button(
    label="🚀 Export Executive Proposal Package (.xlsx)",
    data=excel_data,
    file_name=f"Executive_Bid_{company_name.replace(' ', '_')}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)