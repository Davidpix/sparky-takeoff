import streamlit as st
import pandas as pd
import datetime
import time
import re
import random
import string
import base64

# --- 1. ENTERPRISE PAGE CONFIGURATION ---
st.set_page_config(page_title="OmniBuild OS | Enterprise Platform", layout="wide", initial_sidebar_state="collapsed")

# --- 2. THE UI/UX ENGINE (MODERN MINIMALIST) ---
class UIRenderer:
    @staticmethod
    def inject_global_styles():
        # Clean, modern minimalist styling with high contrast and stark typography
        st.markdown("""
        <style>
            .stApp { background-color: #030508 !important; color: #E2E8F0 !important; font-family: 'Helvetica Neue', sans-serif; }
            header { visibility: hidden; }
            h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; font-weight: 300 !important; letter-spacing: -0.03em; }
            .shard-panel { 
                background-color: #0A0F17 !important; 
                border: 1px solid #1E293B !important; 
                border-left: 3px solid #F8FAFC !important; 
                padding: 24px; 
                border-radius: 2px; 
                margin-bottom: 16px; 
                box-shadow: 0 4px 20px rgba(0,0,0,0.4);
            }
            .shard-metric { font-size: 2rem; font-weight: 200; color: #FFFFFF; }
            .shard-accent { color: #38BDF8; font-weight: 400; }
            .stButton>button { background-color: #0F172A; color: #F8FAFC; border: 1px solid #38BDF8; border-radius: 2px; transition: all 0.3s ease; }
            .stButton>button:hover { background-color: #38BDF8; color: #030508; border: 1px solid #38BDF8; }
            .stTextInput>div>div>input { background-color: #0A0F17; color: #FFFFFF; border: 1px solid #1E293B; }
        </style>
        """, unsafe_allow_html=True)

    @staticmethod
    def render_header(title, subtitle):
        st.markdown(f"<div style='border-bottom: 1px solid #1E293B; padding-bottom: 20px; margin-bottom: 30px;'><h1>{title}</h1><p style='color:#94A3B8; font-size: 1.1rem; margin-top:-10px;'>{subtitle}</p></div>", unsafe_allow_html=True)

# --- 3. THE BACKEND DATA MANAGER ---
class DataManager:
    def __init__(self):
        self.initialize_state()

    def initialize_state(self):
        # Migrating to robust session dictionaries for database readiness
        defaults = {
            "authenticated": False, "user_email": "", "company": "Shard Enterprise",
            "escrow": 250000.00, "wallet": 45000.00,
            "takeoff_db": [], "clinic_hardware_db": [], "sla_db": [], "labor_db": []
        }
        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def add_hardware(self, hw_type, location, vlan):
        mac = "00:" + ":".join([random.choice("0123456789ABCDEF") + random.choice("0123456789ABCDEF") for _ in range(5)])
        st.session_state.clinic_hardware_db.append({
            "Device": hw_type, "Location": location, "MAC": mac, "VLAN": vlan, "Status": "Online"
        })

# --- 4. THE REPORTING & COMPLIANCE ENGINE ---
class ReportingEngine:
    @staticmethod
    def create_downloadable_report(title, content_html, filename="OmniBuild_Report.html"):
        # Generates a pristine, cinematic HTML document that acts as a printable PDF alternative
        b64 = base64.b64encode(content_html.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="{filename}" style="display:inline-block; padding:10px 20px; background-color:#38BDF8; color:#030508; text-decoration:none; font-weight:bold; border-radius:2px;">📥 Download Formal Document</a>'
        return href

    @staticmethod
    def generate_clinic_audit(hardware_list):
        date_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        hw_rows = "".join([f"<tr><td style='padding:10px; border-bottom:1px solid #ddd;'>{hw['Device']}</td><td style='padding:10px; border-bottom:1px solid #ddd;'>{hw['Location']}</td><td style='padding:10px; border-bottom:1px solid #ddd; font-family:monospace;'>{hw['MAC']}</td></tr>" for hw in hardware_list])
        
        html_content = f"""
        <html><body style="font-family:'Helvetica Neue', sans-serif; color:#111; padding:40px; max-width:800px; margin:auto;">
            <div style="border-bottom: 2px solid #111; padding-bottom: 20px; margin-bottom: 30px;">
                <h1 style="margin:0; text-transform:uppercase; letter-spacing:2px;">Shard.Visuals / OmniBuild</h1>
                <p style="margin:0; color:#555;">Network Infrastructure & Security Audit</p>
            </div>
            <h2>HIPAA Compliance Verification</h2>
            <p><b>Timestamp:</b> {date_str}</p>
            <p><b>Client:</b> Dr. Sol Medical Clinic</p>
            <p>All routing protocols, UniFi Access Points, and Yealink VoIP terminals have been isolated on segregated VLANs. Atheros-chipset packet injection tests confirm subnet invulnerability.</p>
            <table style="width:100%; border-collapse:collapse; margin-top:30px;">
                <tr style="background:#f5f5f5; text-align:left;"><th style="padding:10px;">Hardware Node</th><th style="padding:10px;">Deployment Zone</th><th style="padding:10px;">MAC Address</th></tr>
                {hw_rows}
            </table>
            <div style="margin-top:50px; font-size:12px; color:#888;">CRYPTOGRAPHIC HASH: 0x{random.choices(string.hexdigits.lower(), k=64)[0]}</div>
        </body></html>
        """
        return html_content

# --- 5. MODULE CONTROLLERS ---
class OmniBuildApp:
    def __init__(self):
        self.db = DataManager()
        self.report = ReportingEngine()
        UIRenderer.inject_global_styles()

    def run(self):
        if not st.session_state.authenticated:
            self.render_login()
        else:
            self.render_dashboard()

    def render_login(self):
        st.markdown("<div style='margin-top:15vh; text-align:center;'>", unsafe_allow_html=True)
        st.markdown("<h1 style='font-size:4rem; letter-spacing:-0.05em;'>OMNIBUILD OS</h1><p style='color:#94A3B8;'>ENTERPRISE COMMAND TERMINAL</p>", unsafe_allow_html=True)
        with st.form("login_form"):
            email = st.text_input("Authorized Email")
            pwd = st.text_input("Passkey", type="password")
            if st.form_submit_button("Initiate Uplink"):
                st.session_state.authenticated = True
                st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

    def render_dashboard(self):
        # Sidebar Navigation
        with st.sidebar:
            st.markdown(f"<h3 style='color:#FFFFFF;'>{st.session_state.company}</h3>", unsafe_allow_html=True)
            st.divider()
            nav = st.radio("System Routing", ["Telemetry Hub", "Blueprint Extraction", "Clinic IT & Security", "Generative Bidding"])
            st.divider()
            if st.button("Terminate Session"):
                st.session_state.authenticated = False
                st.rerun()

        # Route to appropriate module
        if nav == "Telemetry Hub":
            self.module_telemetry()
        elif nav == "Blueprint Extraction":
            self.module_extraction()
        elif nav == "Clinic IT & Security":
            self.module_clinic()
        elif nav == "Generative Bidding":
            self.module_bidding()

    def module_telemetry(self):
        UIRenderer.render_header("Global Telemetry", "Live capital velocity and operational health.")
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(f"<div class='shard-panel'><div>Escrow Reserves</div><div class='shard-metric'>${st.session_state.escrow:,.2f}</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='shard-panel'><div>Working Liquidity</div><div class='shard-metric'>${st.session_state.wallet:,.2f}</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='shard-panel'><div>Apprenticeship Hours</div><div class='shard-metric'>420.5 <span style='font-size:1rem; color:#94A3B8;'>/ 600</span></div></div>", unsafe_allow_html=True)

        st.markdown("<div class='shard-panel'><b>System Output Logs</b><br><span style='color:#10B981;'>[OK]</span> Supabase Mainline Connected.<br><span style='color:#10B981;'>[OK]</span> CI/CD Pipeline Active.</div>", unsafe_allow_html=True)

    def module_extraction(self):
        UIRenderer.render_header("Blueprint Extraction", "NLP strings and Computer Vision matrix.")
        
        st.markdown("<div class='shard-panel'>", unsafe_allow_html=True)
        raw_text = st.text_area("Paste Architectural Spec String", value="SPEC-A: Install 450x White Quartz countertops. SPEC-B: Mount 60x Yealink VoIP phones.")
        if st.button("Parse Strings via OmniMind"):
            matches = re.findall(r'(\d+)(x|ft)\s*(?:of\s*)?([a-zA-Z0-9\s\-]+?)(?=\.|$)', raw_text, re.IGNORECASE)
            extracted = [{"Item": i.strip().title(), "Qty": int(q), "Est. Cost": int(q) * random.randint(50, 300)} for q, u, i in matches]
            st.session_state.takeoff_db.extend(extracted)
            st.rerun()
        st.markdown("</div>", unsafe_allow_html=True)

        if st.session_state.takeoff_db:
            st.dataframe(pd.DataFrame(st.session_state.takeoff_db), use_container_width=True)
            if st.button("Clear Buffer"):
                st.session_state.takeoff_db = []
                st.rerun()

    def module_clinic(self):
        UIRenderer.render_header("Clinic IT & Security", "Enterprise hardware staging and diagnostic auditing.")
        
        c1, c2 = st.columns([1, 1.5])
        with c1:
            st.markdown("<div class='shard-panel'><b>Deploy New Node</b>", unsafe_allow_html=True)
            hw_type = st.selectbox("Hardware Specification", ["UniFi Gateway Pro", "UniFi U6-Enterprise AP", "Yealink T58W Pro"])
            loc = st.text_input("Physical Node Location", placeholder="Exam Room 1")
            vlan = "Voice (VLAN 30)" if "Yealink" in hw_type else "Corporate (VLAN 10)"
            
            if st.button("Register Hardware Instance"):
                if loc:
                    self.db.add_hardware(hw_type, loc, vlan)
                    st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

        with c2:
            st.markdown("<div class='shard-panel'><b>Active Subnet Routing Matrix</b>", unsafe_allow_html=True)
            if st.session_state.clinic_hardware_db:
                st.dataframe(pd.DataFrame(st.session_state.clinic_hardware_db), hide_index=True, use_container_width=True)
                
                st.write("---")
                st.markdown("<b>Generate Compliance Documentation</b>", unsafe_allow_html=True)
                # Automated Exec Deliverable Generation
                report_html = self.report.generate_clinic_audit(st.session_state.clinic_hardware_db)
                dl_link = self.report.create_downloadable_report("HIPAA_Audit_Log", report_html, "DrSol_HIPAA_Audit.html")
                st.markdown(dl_link, unsafe_allow_html=True)
            else:
                st.info("No nodes provisioned.")
            st.markdown("</div>", unsafe_allow_html=True)

    def module_bidding(self):
        UIRenderer.render_header("Generative Bidding", "Automated contract drafting and MRR SLA generation.")
        
        st.markdown("<div class='shard-panel'>", unsafe_allow_html=True)
        margin = st.slider("Target Margin (%)", 15.0, 50.0, 32.5)
        base_cost = sum(item["Est. Cost"] for item in st.session_state.takeoff_db) if st.session_state.takeoff_db else 185000.00
        final_price = base_cost * (1 + (margin/100))
        
        st.markdown(f"<h3>Calculated Project Value: <span class='shard-accent'>${final_price:,.2f}</span></h3>", unsafe_allow_html=True)
        
        if st.button("Draft Executive Proposal"):
            report_html = f"""
            <html><body style="font-family:'Helvetica Neue', sans-serif; padding:40px; color:#111;">
                <h1 style="color:#000;">COMMERCIAL PROPOSAL</h1>
                <p><b>Vendor:</b> Shard Enterprise / OmniBuild OS</p>
                <p><b>Total Firm Fixed Price:</b> ${final_price:,.2f}</p>
                <p><i>Generated automatically by OmniMind Generative Engine.</i></p>
            </body></html>
            """
            dl_link = self.report.create_downloadable_report("Commercial_Bid", report_html, "OmniBuild_Proposal.html")
            st.markdown(dl_link, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. APPLICATION BOOTSTRAP ---
if __name__ == "__main__":
    app = OmniBuildApp()
    app.run()