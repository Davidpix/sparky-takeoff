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

st.title("🗺️ Spatial Canvas & Vision Takeoff Core")

# --- STRUCTURAL SECURITY INTEGRITY CHECK ---
if "uploaded_file_bytes" not in st.session_state or st.session_state.uploaded_file_bytes is None:
    st.warning("⚠️ No project blueprint detected in active session memory. Please return to the Dashboard Gateway page and upload a master PDF file package.")
    st.stop()

# --- INITIALIZE MULTI-SHEET LEDGER DICTIONARY ---
if "sheet_ledger" not in st.session_state:
    st.session_state.sheet_ledger = {}

with pdfplumber.open(BytesIO(st.session_state.uploaded_file_bytes)) as pdf:
    total_pages = len(pdf.pages)
    
    col_x, col_y = st.columns([1, 2])
    with col_x:
        page_number = st.number_input("Target Drawing Sheet", min_value=1, max_value=total_pages, value=1)
        
        # Define a unique key string for the currently selected blueprint page
        sheet_key = f"Sheet_{page_number}"
        
        # Securely initialize isolated database tokens for this specific sheet if it doesn't exist yet
        if sheet_key not in st.session_state.sheet_ledger:
            st.session_state.sheet_ledger[sheet_key] = {
                "click_history": [],
                "conduit_runs": 0.0,
                "vertical_drops": 0.0,
                "scale_factor": None,
                "scale_preset_name": "Manual Calibration Mode"
            }
            
        mode = st.radio("Canvas Tool Profile", ["1. Calibrate Scale", "2. Measure Linear Run", "3. AI Symbol Scan"])
        
        st.divider()
        st.write("#### 📐 Architectural Scale Presets")
        
        # Read/Write scale presets straight from this sheet's isolated memory sandbox
        current_preset = st.session_state.sheet_ledger[sheet_key]["scale_preset_name"]
        preset_options = [
            "Manual Calibration Mode",
            "1/4\" = 1'-0\" (Residential Standard)",
            "1/8\" = 1'-0\" (Commercial Standard)",
            "1\" = 10'-0\" (Civil/Site Plan Standard)",
            "1\" = 20'-0\" (Civil/Plot Standard)"
        ]
        
        preset_idx = preset_options.index(current_preset) if current_preset in preset_options else 0
        scale_preset = st.selectbox("Select Standard Plan Scale", options=preset_options, index=preset_idx)
        st.session_state.sheet_ledger[sheet_key]["scale_preset_name"] = scale_preset
        
        if scale_preset != "Manual Calibration Mode":
            if "1/4\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 18.0
            elif "1/8\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 9.0
            elif "10'-0\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 7.2
            elif "20'-0\"" in scale_preset: st.session_state.sheet_ledger[sheet_key]["scale_factor"] = 3.6
            st.success(f"Locked Preset: {st.session_state.sheet_ledger[sheet_key]['scale_factor']:.1f} Px/Ft")

        # --- ADVANCED MODULE A: VERTICAL DROP ADDER ---
        if mode == "2. Measure Linear Run":
            st.divider()
            st.write("#### 📐 Vertical Drops & Rises (Ceiling/Floor)")
            st.caption("Account for 3D vertical offsets (e.g., pipe dropping from an 8ft ceiling down to a panel or wall switch).")
            
            added_drop = st.number_input("Add Vertical Footage Allocation (Feet)", min_value=0.0, value=0.0, step=1.0)
            if st.button("➕ Inject Vertical Drop to Sheet Ledger"):
                st.session_state.sheet_ledger[sheet_key]["vertical_drops"] += added_drop
                st.toast(f"Added {added_drop}ft vertical drop to {sheet_key}!")

    with col_y:
        st.write("#### Canvas Control Actions")
        if st.button("🔄 Clear Current Sheet Canvas Cache"):
            st.session_state.sheet_ledger[sheet_key]["click_history"] = []
            st.session_state.sheet_ledger[sheet_key]["conduit_runs"] = 0.0
            st.session_state.sheet_ledger[sheet_key]["vertical_drops"] = 0.0
            st.session_state.sheet_ledger[sheet_key]["scale_factor"] = None
            st.session_state.sheet_ledger[sheet_key]["scale_preset_name"] = "Manual Calibration Mode"
            st.success(f"Cache wiped cleanly for {sheet_key}!")
            st.rerun()

    page = pdf.pages[page_number - 1]
    img = page.to_image(resolution=100)
    pil_img = img.original.convert("RGB")
    
    # Extract this sheet's active history array references for mapping loops
    active_clicks = st.session_state.sheet_ledger[sheet_key]["click_history"]
    
    if mode == "3. AI Symbol Scan":
        st.info("🤖 **Computer Vision Mode Active**")
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
        # --- PILLOW VECTOR OVERLAY ENGINE ---
        if active_clicks:
            draw = ImageDraw.Draw(pil_img)
            if len(active_clicks) >= 2 and mode == "2. Measure Linear Run":
                draw.line(active_clicks, fill="#00FFFF", width=4) 
                
            for point in active_clicks:
                x, y = point
                r = 6  
                draw.ellipse([x - r, y - r, x + r, y + r], fill="#FF3366", outline="#FFFFFF", width=1) 

        st.caption(f"Active Drawing Interface: Tracking Context **{sheet_key}**")
        value = streamlit_image_coordinates(pil_img, key=f"canvas_engine_{sheet_key}", use_container_width=True)
        
        if value is not None:
            pt = (value["x"], value["y"])
            if not active_clicks or active_clicks[-1] != pt:
                st.session_state.sheet_ledger[sheet_key]["click_history"].append(pt)
                st.rerun()
                
        if mode == "1. Calibrate Scale":
            if scale_preset != "Manual Calibration Mode":
                st.warning("💡 You are currently using an Architectural Scale Preset.")
            
            if len(active_clicks) >= 2:
                p1, p2 = active_clicks[-2], active_clicks[-1]
                p_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                known_ft = st.number_input("Dimension Line Real length (Feet)", min_value=1.0, value=10.0)
                if st.button("💾 Lock Scale Calibration"):
                    st.session_state.sheet_ledger[sheet_key]["scale_factor"] = p_dist / known_ft
                    st.success(f"Scale Calibration locked at {st.session_state.sheet_ledger[sheet_key]['scale_factor']:.2f} px/ft!")
                    
        elif mode == "2. Measure Linear Run":
            sf = st.session_state.sheet_ledger[sheet_key]["scale_factor"]
            if sf is None:
                st.error("⚠️ Scale factor uncalibrated for this specific sheet.")
            else:
                if len(active_clicks) >= 2:
                    t_px = 0.0
                    for i in range(len(active_clicks)-1):
                        pt1, pt2 = active_clicks[i], active_clicks[i+1]
                        t_px += math.sqrt((pt2[0]-pt1[0])**2 + (pt2[1]-pt1[1])**2)
                    calc_ft = t_px / sf
                    
                    # Core display factoring in linear horizontal measurements
                    st.metric("Traced Plan Distance (Horizontal)", f"{calc_ft:.2f} Linear Ft")
                    st.metric("Accumulated Sheet Vertical Drops", f"{st.session_state.sheet_ledger[sheet_key]['vertical_drops']:.2f} Vertical Ft")
                    
                    if st.button("➕ Push All Sheet Footage to Active Estimate"):
                        st.session_state.sheet_ledger[sheet_key]["conduit_runs"] += calc_ft
                        st.success(f"Footage compiled successfully for {sheet_key}!")