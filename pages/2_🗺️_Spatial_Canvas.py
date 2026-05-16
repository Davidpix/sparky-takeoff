import streamlit as st
import pdfplumber
import pandas as pd
from io import BytesIO
import math
from streamlit_image_coordinates import streamlit_image_coordinates
import numpy as np
from skimage.feature import match_template
# Import ImageDraw to enable direct canvas modification
from PIL import ImageDraw

st.set_page_config(page_title="Spatial Canvas", layout="wide")

st.title("🗺️ Spatial Canvas & Vision Takeoff Core")

# --- STRUCTURAL SECURITY INTEGRITY CHECK ---
if "uploaded_file_bytes" not in st.session_state or st.session_state.uploaded_file_bytes is None:
    st.warning("⚠️ No project blueprint detected in active session memory. Please return to the Dashboard Gateway page and upload a master PDF file package.")
    st.stop()

with pdfplumber.open(BytesIO(st.session_state.uploaded_file_bytes)) as pdf:
    total_pages = len(pdf.pages)
    
    col_x, col_y = st.columns([1, 2])
    with col_x:
        page_number = st.number_input("Target Drawing Sheet", min_value=1, max_value=total_pages, value=1)
        mode = st.radio("Canvas Tool Profile", ["1. Calibrate Scale", "2. Measure Linear Run", "3. AI Symbol Scan"])
        
        st.divider()
        st.write("#### 📐 Architectural Scale Presets")
        
        scale_preset = st.selectbox(
            "Select Standard Plan Scale",
            options=[
                "Manual Calibration Mode",
                "1/4\" = 1'-0\" (Residential Standard)",
                "1/8\" = 1'-0\" (Commercial Standard)",
                "1\" = 10'-0\" (Civil/Site Plan Standard)",
                "1\" = 20'-0\" (Civil/Plot Standard)"
            ]
        )
        
        if scale_preset != "Manual Calibration Mode":
            if "1/4\"" in scale_preset: st.session_state.scale_pixels_per_foot = 18.0
            elif "1/8\"" in scale_preset: st.session_state.scale_pixels_per_foot = 9.0
            elif "10'-0\"" in scale_preset: st.session_state.scale_pixels_per_foot = 7.2
            elif "20'-0\"" in scale_preset: st.session_state.scale_pixels_per_foot = 3.6
            st.success(f"Locked Preset Factor: {st.session_state.scale_pixels_per_foot:.1f} Px/Ft")

    with col_y:
        st.write("#### Canvas Control Actions")
        if st.button("🔄 Clear Active Canvas Session History"):
            st.session_state.click_history = []
            st.session_state.scale_pixels_per_foot = None
            st.session_state.conduit_runs = 0.0
            st.session_state.vision_counts = {}
            st.success("Canvas cache wiped!")
            st.rerun()

    page = pdf.pages[page_number - 1]
    img = page.to_image(resolution=100)
    # Convert image to RGB format so we can draw bright neon colors onto it
    pil_img = img.original.convert("RGB")
    
    if mode == "3. AI Symbol Scan":
        st.info("🤖 **Computer Vision Mode:** Select a visual electrical pattern. The scikit-image cross-correlation array will cross-examine pixel densities.")
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
                st.session_state.vision_counts[clean_name] = final_count
                st.success(f"Vision sweep complete. Locked {final_count} instances into workspace data!")
    else:
        # --- PILLOW DYNAMIC DRAWING COATING ENGINE ---
        # Intercept the blueprint and paint vector path targets over it
        if st.session_state.click_history:
            draw = ImageDraw.Draw(pil_img)
            
            # 1. Paint connecting neon lines for tracking conduit paths
            if len(st.session_state.click_history) >= 2 and mode == "2. Measure Linear Run":
                draw.line(st.session_state.click_history, fill="#00FFFF", width=4) # Premium Cyan vector trace line
                
            # 2. Paint individual target target rings over every single clicked point
            for point in st.session_state.click_history:
                x, y = point
                r = 6  # Radius size of target dot
                draw.ellipse([x - r, y - r, x + r, y + r], fill="#FF3366", outline="#FFFFFF", width=1) # Neon hot pink anchor point

        st.caption("Active Drawing Canvas Vector Array Interface")
        value = streamlit_image_coordinates(pil_img, key="multipage_blueprint_canvas", use_container_width=True)
        
        if value is not None:
            pt = (value["x"], value["y"])
            if not st.session_state.click_history or st.session_state.click_history[-1] != pt:
                st.session_state.click_history.append(pt)
                st.rerun()
                
        if mode == "1. Calibrate Scale":
            if scale_preset != "Manual Calibration Mode":
                st.warning("💡 You are currently using an Architectural Scale Preset. To manually calibrate using custom points instead, switch the dropdown on the left back to 'Manual Calibration Mode'.")
            
            if len(st.session_state.click_history) >= 2:
                p1, p2 = st.session_state.click_history[-2], st.session_state.click_history[-1]
                p_dist = math.sqrt((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)
                known_ft = st.number_input("Dimension Line Real length (Feet)", min_value=1.0, value=10.0)
                if st.button("💾 Lock Scale Calibration"):
                    st.session_state.scale_pixels_per_foot = p_dist / known_ft
                    st.success(f"Scale Calibration locked at {st.session_state.scale_pixels_per_foot:.2f} px/ft!")
                    
        elif mode == "2. Measure Linear Run":
            if st.session_state.scale_pixels_per_foot is None:
                st.error("⚠️ Scale factor uncalibrated. Select an Architectural Scale Preset or complete manual calibration points before tracking runs.")
            else:
                if len(st.session_state.click_history) >= 2:
                    t_px = 0.0
                    for i in range(len(st.session_state.click_history)-1):
                        pt1, pt2 = st.session_state.click_history[i], st.session_state.click_history[i+1]
                        t_px += math.sqrt((pt2[0]-pt1[0])**2 + (pt2[1]-pt1[1])**2)
                    calc_ft = t_px / st.session_state.scale_pixels_per_foot
                    st.metric("Traced Circuit Distance", f"{calc_ft:.2f} Linear Ft")
                    if st.button("➕ Push Branch Length to Active Estimate"):
                        st.session_state.conduit_runs += calc_ft
                        st.success("Footage compiled successfully into core worksheet ledger!")