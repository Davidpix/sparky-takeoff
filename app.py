import streamlit as st
import PyPDF2
import pandas as pd
import re  # Built-in Python Regular Expressions library

st.set_page_config(page_title="SparkyTakeoff AI", layout="wide")

st.title("⚡ SparkyTakeoff: Enterprise Regex Parser")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("Global Bid Settings")
    labor_rate = st.number_input("Hourly Labor Rate ($)", value=85.0)
    overhead = st.slider("Overhead/Profit Markup (%)", 10, 50, 20) / 100

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Blueprint PDF for Intelligent Scan", type="pdf")

if uploaded_file is not None:
    reader = PyPDF2.PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    st.success(f"Blueprint Loaded! Total Pages: {num_pages}")
    
    # Extract all text from the PDF
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text + "\n"

    # --- DEFINE OUR ADVANCED REGEX PATTERNS ---
    # This dictionary maps the item to a specialized search pattern
    # Example pattern: r"(\d+)\s*(?:-|x)?\s*gfci" looks for a number, optional spaces/dashes, and 'gfci'
    electrical_manifest = {
        "Main Panel": {"pattern": r"(\d+)\s*(?:-|x)?\s*(?:amp)?\s*(?:panel|load center)", "cost": 450.00, "mins": 120},
        "GFCI Receptacle": {"pattern": r"(\d+)\s*(?:-|x)?\s*gfci", "cost": 18.00, "mins": 20},
        "Disconnect Switch": {"pattern": r"(\d+)\s*(?:-|x)?\s*(?:phase)?\s*disconnect", "cost": 85.00, "mins": 45},
        "Single Pole Switch": {"pattern": r"(\d+)\s*(?:-|x)?\s*single pole", "cost": 1.50, "mins": 15}
    }

    scanned_data = []
    
    st.write("### 🧠 Intelligent Material Extraction")
    
    for item, info in electrical_manifest.items():
        # Find all matches of our pattern in the blueprint text
        # re.IGNORECASE makes sure it catches "GFCI", "gfci", or "Gfci"
        matches = re.findall(info["pattern"], full_text, re.IGNORECASE)
        
        # If matches are found, sum up the quantities extracted
        total_qty = 0
        for match in matches:
            try:
                total_qty += int(match)
            except ValueError:
                continue
        
        scanned_data.append({
            "Item Name": item,
            "Detected Qty": total_qty,
            "Unit Cost ($)": info["cost"],
            "Mins to Install": info["mins"]
        })

    # Convert to DataFrame
    df = pd.DataFrame(scanned_data)
    
    # Display editable table so the user can audit the AI's math
    st.caption("Review extracted quantities below. Double-click any cell to manually adjust.")
    edited_df = st.data_editor(df, num_rows="dynamic")

    # --- FINANCIAL MATH ---
    edited_df["Total Mat."] = edited_df["Detected Qty"] * edited_df["Unit Cost ($)"]
    edited_df["Total Labor"] = (edited_df["Detected Qty"] * edited_df["Mins to Install"] / 60) * labor_rate
    
    total_mat = edited_df["Total Mat."].sum()
    total_labor = edited_df["Total Labor"].sum()
    final_bid = (total_mat + total_labor) * (1 + overhead)

    # --- EXECUTIVE DASHBOARD ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Parsed Material Cost", f"${total_mat:,.2f}")
    c2.metric("Estimated Labor Cost", f"${total_labor:,.2f}")
    c3.metric("Total Suggested Bid", f"${final_bid:,.2f}", delta=f"{overhead*100}% Markup Included")