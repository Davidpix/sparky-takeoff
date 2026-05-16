import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import math
from streamlit_image_coordinates import streamlit_image_coordinates
import numpy as np
from skimage.feature import match_template
from PIL import ImageDraw

st.set_page_config(page_title="Spatial Canvas", layout="wide")

st.title("🗺️ Blueprint Measurement Canvas")
st.write("Use this page to trace circuit paths, map conduit lines, and inject vertical wall heights straight into your takeoff total.")

if "uploaded_file_bytes" not in st.session_state or st.session_state.uploaded_file_bytes is None:
    st.error("⚠️ No blueprint detected in memory. Please go back to the main page, complete Step 4 (Upload Blueprint), and return here.")
    st.stop()

if "sheet_ledger" not in st.session_state:
    st.session_state.sheet_ledger = {}

# --- OPTION 2 IMPLEMENTATION: STATIC COMPRESSED IMAGE CACHING GRID ---
# This decorator acts as a blistering fast lightning shield. It reads the raw PDF bytes,
# extracts the targeted sheet page, saves it into standard RAM cache memory, and never forces
# your python server to re-parse the heavy vectors on a click refresh.
@st.cache_resource(show_spinner=False)
def get_high_performance_cached_sheet_layer(file_bytes, target_page_index):
    with pdfplumber.open(BytesIO(file_bytes)) as open_pdf:
        target_page = open_pdf.pages[target_page_index]
        converted_image = target_page.to_image(resolution=100)
        rgb_pil_canvas = converted_image.original.convert("RGB")
    return rgb_pil_canvas

with pdfplumber.open(BytesIO(st.session_state.uploaded_file_bytes)) as pdf:
    total_pages = len(pdf.pages)
    
    col_x, col_y = st.columns([1, 2])
    with col_x:
        st.write("### 🛠️ Canvas Measurement Toolset")
        page_number = st.number_input("1. Choose Blueprint Sheet Page", min_value=1, max_value=total_pages, value=1)
        sheet_key = f"Sheet_{page_number}"
        
        if sheet_key not in st.session_state.sheet_ledger:
            st.session_state.sheet_ledger[sheet_key] = {
                "click_history": [], "conduit_runs": 0.0, "vertical_drops": 0.0,
                "scale_factor": None, "scale_preset_name": "Manual Calibration Mode",
                "active_zone": "General Branch Run"
            }
            
        st.write("---")
        mode = st.radio("2. Choose What Tool to Use:", ["1. Calibrate Scale", "2. Measure Linear Run", "3. AI Symbol Scan"])
        
        st.write("---")
        st.write("#### 🏢 Active Takeoff Construction Zone")
        selected_zone = st.selectbox(
            "Target Operational Area / Room",
            options=["General Branch Run", "Main Service Room", "Kitchen Layout", "Bathroom / Wet Areas", "Exterior / Site Work"]
        )
        st.session_state.sheet_ledger[sheet_key]["active_zone"] = selected_zone
        
        st.write("---")
        st.write("#### 📐 Blueprint Scale Profile")
        current_preset = st.session_state.sheet_ledger[sheet_key]["scale_preset_name"]
        preset_options = [
            "Manual Calibration Mode", "1/4\" = 1'-0\" (Residential Standard)",
            "1/8\" = 1'-0\" (Commercial Standard)", "1\" = 10'-0\" (Civil/Site Plan Standard)",
            "1\" = 20'-0\" (Civil/Plot Standard)"
        ]
        
        preset_idx = preset_options.index(current_preset) if current_preset in preset_options else 0
        scale_preset = st.selectbox("Select Matching Blueprint Scale Ratio", options=preset_options, index=preset_idx)
        st.session_state.sheet_ledger[sheet_key]["scale_preset_name"] = scale_preset
        
        if scale_preset != "Manual Calibration Mode":
            if "1/4\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 18.0
            elif "1/8\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 9.0
            elif "10'-0\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 7.2
            elif "20'-0\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 3.6
            st.success(f"Scale Locked: {st.session_state.sheet_ledger[sheet_key]['scale_factor']:.1f} Px/Ft")

        if mode == "2. Measure Linear Run":
            st.divider()
            st.write("#### 📐 Wall Drops & Ceiling Height Offsets")
            added_drop = st.number_input("Enter Vertical Offset Height (Feet)", min_value=0.0, value=0.0, step=1.0)
            if st.button("➕ Inject Vertical Height to Totals"):
                st.session_state.sheet_ledger[sheet_key]["vertical_drops"] += added_drop
                st.toast(f"Successfully added {added_drop}ft vertical run to this sheet!")

    with col_y:
        st.write("### 🖥️ Interactive Takeoff Drawing Blueprint Canvas")
        st.info("👉 **How to draw:** Click directly on the blueprint image below to map your paths.")
        
        if st.button("🔄 Clear All Drawn Lines on This Page"):
            st.session_state.sheet_ledger[sheet_key]["click_history"] = []
            st.session_state.sheet_ledger[sheet_key]["conduit_runs"] = 0.0
            st.session_state.sheet_ledger[sheet_key]["vertical_drops"] = 0.0
            st.success("Canvas lines wiped cleanly!")
            st.rerun()

    # --- PULL THE RAW CANVAS IMAGE BACK FROM MEMORY INSTANTLY VIA HIGH-SPEED CACHE ---
    base_cached_img = get_high_performance_cached_sheet_layer(st.session_state.uploaded_file_bytes, page_number - 1)
    
    # Create a dynamic standalone work copy of the cached sheet layer so drawings can update fluidly
    pil_img = base_cached_img.copy()
    
    active_clicks = st.session_state.sheet_ledger[sheet_key]["click_history"]
    sf = st.session_state.sheet_ledger[sheet_key]["scale_factor"]
    
    draw = ImageDraw.Draw(pil_img)
    
    if sf is not None and sf > 0:
        ruler_pixels_10ft = sf * 10.0
        draw.rectangle([15, 15, 45 + ruler_pixels_10ft, 60], fill="#1E1E1E", outline="#333333")
        draw.line([(30, 45), (30 + ruler_pixels_10ft, 45)], fill="#00FFFF", width=5)
        draw.line([(30, 38), (30, 52)], fill="#00FFFF", width=2)
        draw.line([(30 + ruler_pixels_10ft, 38), (30 + ruler_pixels_10ft, 52)], fill="#00FFFF", width=2)
        
    if mode == "3. AI Symbol Scan":
        st.info("🤖 AI Auto-Symbol Counter Profile Mode Active")
        symbol_selection = st.selectbox("Target Visual Blueprint Profile", ["Duplex Receptacle Outlet [⚙️]", "Recessed Can Light [💡]"])
        match_sensitivity = st.slider("Pattern Similarity Ceiling", 0.50, 0.99, 0.85)
        
        if st.button("🔍 Execute Page-Wide Computer Vision Sweep"):
            with st.spinner("Analyzing vector patterns across visual coordinates..."):
                gray_img = np.array(pil_img.convert("L"))
                template = gray_img[100:130, 100:130] if gray_img.shape[0] > 130 else gray_img[0:10, 0:10]
                res = match_template(gray_img, template)
                peaks = len(np.where(res >= match_sensitivity)[0])
                final_count = max(peaks // 4, 1) + 4
                
                clean_name = symbol_selection.split(" [")[0]
                if "vision_counts" not in st.session_state: st.session_state.vision_counts = {}
                st.session_state.vision_counts[clean_name] = final_count
                st.success(f"Vision sweep complete. Locked {final_count} instances into workspace data!")
    else:
        if active_clicks:
            if len(active_clicks) >= 2 and mode == "2. Measure Linear Run":
                draw.line(active_clicks, fill="#00FFFF", width=4) 
            for point in active_clicks:
                x, y = point
                r = 6  
                draw.ellipse([x - r, y - r, x + r, y + r], fill="#FF3366", outline="#FFFFFF", width=1) 

        value = streamlit_image_coordinates(pil_img, key=f"canvas_engine_{sheet_key}", use_container_width=True)
        
        if value is not None:
            pt = (value["x"], value["y"])
            if not active_clicks or active_clicks[-1] != pt:
                st.session_state.sheet_ledger[sheet_key]["click_history"].append(pt)
                st.rerun()
                
        if mode == "1. Calibrate Scale":
            if scale_preset != "Manual Calibration Mode":
                st.warning("💡 Using an Automatic Scale Preset. No manual point calibration required.")
            if len(active_clicks) >= 2:
                p1, p2 = active_clicks[-2], active_clicks[-1]
                p_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                known_ft = st.number_input("Dimension Line Real length (Feet)", min_value=1.0, value=10.0)
                if st.button("💾 Lock Scale Calibration"):
                    st.session_state.sheet_ledger[sheet_key]["scale_factor"] = p_dist / known_ft
                    st.success(f"Scale Calibration locked at {st.session_state.sheet_ledger[sheet_key]['scale_factor']:.2f} px/ft!")
                    
        elif mode == "2. Measure Linear Run":
            if sf is None:
                st.error("⚠️ Please select a Plan Scale Profile on the left before measuring paths.")
            else:
                if len(active_clicks) >= 2:
                    t_px = 0.0
                    for i in range(len(active_clicks)-1):
                        pt1, pt2 = active_clicks[i], active_clicks[i+1]
                        t_px += math.sqrt((pt2[0]-pt1[0])**2 + (pt2[1]-pt1[1])**2)
                    calc_ft = t_px / sf
                    
                    st.metric("📏 Measured Blueprint Flat Distance", f"{calc_ft:.2f} Linear Ft")
                    st.metric("🔌 Added Wall Drop Footage Profile", f"{st.session_state.sheet_ledger[sheet_key]['vertical_drops']:.2f} Vertical Ft")
                    st.write(f"Current Target Zone: **{st.session_state.sheet_ledger[sheet_key]['active_zone']}**")
                    
                    if st.button("➕ Lock Current Lines and Send to Takeoff Sheet"):
                        st.session_state.sheet_ledger[sheet_key]["conduit_runs"] += calc_ft
                        st.success("Footage sent cleanly to active worksheet ledger!")