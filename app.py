# app.py
import streamlit as st
import json, os, base64
from blockchain_ledger import Blockchain
from qr_generator import generate_qr_for_data
from report_generator import generate_report
from emailer import send_email_with_attachments

# Constants
LEDGER_FILE = "data/ledger.json"
ASSETS_DIR = "assets"
DOCS_DIR = "docs"

# ensure folders
os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
os.makedirs(ASSETS_DIR, exist_ok=True)
os.makedirs(DOCS_DIR, exist_ok=True)

# Load or init ledger
if os.path.exists(LEDGER_FILE):
    try:
        with open(LEDGER_FILE, "r") as f:
            ledger_data = json.load(f)
    except Exception:
        ledger_data = None
else:
    ledger_data = None

blockchain = Blockchain()
if ledger_data and isinstance(ledger_data, list) and len(ledger_data) > 1:
    for entry in ledger_data[1:]:
        blockchain.add_block(entry.get("data", {}))

def save_ledger():
    os.makedirs(os.path.dirname(LEDGER_FILE), exist_ok=True)
    with open(LEDGER_FILE, "w") as f:
        json.dump(blockchain.export_chain(), f, indent=4)

# Streamlit UI
st.set_page_config(page_title="AyurChain", layout="wide")
st.title("🌿 AyurChain - Blockchain Traceability for Ayurvedic Herbs")

menu = ["Farmer", "Lab", "Processor", "Consumer", "Ledger"]
choice = st.sidebar.radio("Role", menu)

# Farmer
if choice == "Farmer":
    st.header("👨‍🌾 Farmer - Record Harvest")
    farmer = st.text_input("Farmer Name")
    herb = st.text_input("Herb / Crop")
    gps = st.text_input("GPS Location (lat,long)")
    batch_id = st.text_input("Batch ID")
    if st.button("Submit Harvest"):
        if not (farmer and herb and gps and batch_id):
            st.error("Fill all fields.")
        else:
            event = {
                "role": "Farmer",
                "farmer": farmer,
                "herb": herb,
                "gps": gps,
                "batch_id": batch_id
            }
            blockchain.add_block(event)
            save_ledger()
            st.success(f"Harvest recorded for batch {batch_id}")

# Lab
elif choice == "Lab":
    st.header("🔬 Lab - Add Quality Test")
    batch_id = st.text_input("Batch ID")
    lab_name = st.text_input("Lab Name")
    dna = st.selectbox("DNA Verified", ["Yes", "No"])
    pesticide = st.text_input("Pesticide Level/Notes")
    if st.button("Submit Test"):
        if not (batch_id and lab_name):
            st.error("Provide Batch ID and Lab name.")
        else:
            event = {
                "role": "Lab",
                "batch_id": batch_id,
                "lab": lab_name,
                "dna_verified": dna,
                "pesticide_level": pesticide
            }
            blockchain.add_block(event)
            save_ledger()
            st.success(f"Lab record added for batch {batch_id}")

# Processor
elif choice == "Processor":
    st.header("🏭 Processor - Processing Step")
    batch_id = st.text_input("Batch ID")
    step = st.text_input("Processing Step (Drying / Grinding / Packaging)")
    notes = st.text_area("Notes")
    if st.button("Submit Processing"):
        if not (batch_id and step):
            st.error("Provide Batch ID and step.")
        else:
            event = {
                "role": "Processor",
                "batch_id": batch_id,
                "process": step,
                "notes": notes
            }
            blockchain.add_block(event)
            save_ledger()
            st.success(f"Processing step recorded for batch {batch_id}")
            qrpath = generate_qr_for_data(
                {"batch_id": batch_id, "event": event},
                filename=f"{batch_id}_latest_qr.png",
                save_path=ASSETS_DIR
            )
            st.image(qrpath, caption="QR for this batch (latest event)")

# Consumer
elif choice == "Consumer":
    st.header("🛒 Consumer Verification & Report")
    batch_id = st.text_input("Enter Batch ID to verify")
    recipient_email = st.text_input("Notification email (optional)")

    # Session state to persist PDF + view state
    if "show_report" not in st.session_state:
        st.session_state.show_report = False
        st.session_state.pdf_path = None

    if st.button("Verify & Generate Report"):
        if not batch_id:
            st.error("Provide Batch ID.")
        else:
            chain = blockchain.export_chain()
            matches = [entry for entry in chain if entry.get("data", {}).get("batch_id") == batch_id]

            if not matches:
                st.error("No records for this batch.")
                st.session_state.show_report = False
            else:
                st.success(f"Found {len(matches)} records for batch {batch_id}")

                # generate PDF
                pdf_path = generate_report(batch_id, matches, save_path=DOCS_DIR)
                st.session_state.pdf_path = pdf_path
                st.session_state.show_report = False  # wait until "View" clicked

                # Download option
                with open(pdf_path, "rb") as f:
                    st.download_button("⬇️ Download PDF Report", f, file_name=os.path.basename(pdf_path))

                # Email sending
                if recipient_email:
                    try:
                        subject = f"AyurChain Report for Batch {batch_id}"
                        body = (f"Please find attached the AyurChain PDF report for batch {batch_id}.\n\n"
                                "This email was sent automatically by AyurChain.")
                        attachments = [pdf_path]
                        send_email_with_attachments(subject, body, recipient_email, attachments=attachments)
                        st.success(f"Email sent to {recipient_email}")
                    except Exception as e:
                        st.error(f"Failed to send email: {e}")

    # Show "View Report" button if a PDF exists
    if st.session_state.pdf_path:
        if st.button("📖 View Report"):
            st.session_state.show_report = True

    # If "View Report" pressed → display PDF
    if st.session_state.show_report and st.session_state.pdf_path:
        pdf_path = st.session_state.pdf_path
        st.markdown("### 📖 View Report")

        with open(pdf_path, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode('utf-8')

        # Safer: link to open in new tab
        href = f'<a href="data:application/pdf;base64,{base64_pdf}" target="_blank">📖 Open Report in New Tab</a>'
        st.markdown(href, unsafe_allow_html=True)


# Ledger
elif choice == "Ledger":
    st.header("📜 Ledger Access (Admin Only)")
    password = st.text_input("Enter Admin Password", type="password")
    if st.button("Unlock Ledger"):
        if password == "admin123":  # 🔒 Replace with env var later
            st.success("Access Granted")
            st.write("Total blocks:", len(blockchain.export_chain()))
            st.json(blockchain.export_chain())
            st.write("Ledger valid:", blockchain.is_chain_valid())
        else:
            st.error("Invalid password. Access denied.")
