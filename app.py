import streamlit as st
import PyPDF2
import pandas as pd

st.set_page_config(page_title="SparkyTakeoff AI", layout="wide")

st.title("⚡ SparkyTakeoff: Blueprint Scanner")

# --- SIDEBAR: SETTINGS ---
with st.sidebar:
    st.header("Bid Settings")
    labor_rate = st.number_input("Hourly Labor Rate ($)", value=85.0)
    overhead = st.slider("Overhead/Profit Markup (%)", 10, 50, 20) / 100

# --- FILE UPLOADER ---
uploaded_file = st.file_uploader("Upload Blueprint PDF for Scan", type="pdf")

if uploaded_file is not None:
    reader = PyPDF2.PdfReader(uploaded_file)
    num_pages = len(reader.pages)
    st.success(f"Blueprint Loaded! Total Pages: {num_pages}")
    
    # Extract all text from the PDF once to search through it efficiently
    full_text = ""
    for page in reader.pages:
        text = page.extract_text()
        if text:
            full_text += text.lower() + "\n"

    # --- DEFINE OUR SEARCH KEYWORDS & DEFAULT PRICES ---
    # The app will look for these words in the blueprint notes/schedules
    electrical_items = {
        "Main Panel": {"keywords": ["panel", "load center", "mlo", "mcbs"], "cost": 450.00, "mins": 120},
        "GFCI Receptacle": {"keywords": ["gfci", "gfi", "ground fault"], "cost": 18.00, "mins": 20},
        "AFCI Breaker": {"keywords": ["afci", "arc fault"], "cost": 45.00, "mins": 15},
        "Disconnect Switch": {"keywords": ["disconnect", "safety switch", "fused disc"], "cost": 85.00, "mins": 45},
        "Single Pole Switch": {"keywords": ["single pole", "1-pole switch"], "cost": 1.50, "mins": 15}
    }

    # --- AUTOMATED COUNTING LOGIC ---
    scanned_data = []
    
    st.write("### 🔍 Scan Results from Technical Schedules/Notes")
    
    for item, info in electrical_items.items():
        # Count how many times any of the keywords appear in the PDF text
        item_count = 0
        for keyword in info["keywords"]:
            item_count += full_text.count(keyword)
        
        # Add to our list for the table
        scanned_data.append({
            "Item Name": item,
            "Detected Qty": item_count,
            "Unit Cost ($)": info["cost"],
            "Mins to Install": info["mins"]
        })

    # Convert to DataFrame so user can view/edit
    df = pd.DataFrame(scanned_data)
    
    # Display editable table so user can override data if the scan missed something
    edited_df = st.data_editor(df, num_rows="dynamic")

    # --- MATH ENGINE ---
    edited_df["Total Mat."] = edited_df["Detected Qty"] * edited_df["Unit Cost ($)"]
    edited_df["Total Labor"] = (edited_df["Detected Qty"] * edited_df["Mins to Install"] / 60) * labor_rate
    
    total_mat = edited_df["Total Mat."].sum()
    total_labor = edited_df["Total Labor"].sum()
    final_bid = (total_mat + total_labor) * (1 + overhead)

    # --- RESULTS DASHBOARD ---
    st.divider()
    c1, c2, c3 = st.columns(3)
    c1.metric("Scanned Material Cost", f"${total_mat:,.2f}")
    c2.metric("Estimated Labor Cost", f"${total_labor:,.2f}")
    c3.metric("Total Suggested Bid", f"${final_bid:,.2f}", delta=f"{overhead*100}% Margin Incl.")

    st.write("#### 📋 Detailed Line Breakdown")
    st.dataframe(edited_df)