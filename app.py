import sqlite3
from datetime import datetime, date, time
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st
from PIL import Image

DB_PATH = Path(__file__).with_name("carebridge.db")

st.set_page_config(page_title="CareBridge AI", page_icon="💙", layout="wide")

def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    with get_conn() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recorded_at TEXT NOT NULL,
                reading_type TEXT NOT NULL,
                value1 REAL NOT NULL,
                value2 REAL
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                medicine TEXT NOT NULL,
                instructions TEXT,
                reminder_time TEXT NOT NULL,
                active INTEGER NOT NULL DEFAULT 1
            )
        """)

def add_reading(recorded_at, reading_type, value1, value2=None):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO readings(recorded_at, reading_type, value1, value2) VALUES (?, ?, ?, ?)",
            (recorded_at, reading_type, value1, value2)
        )

def get_readings():
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM readings ORDER BY recorded_at", conn)

def add_reminder(medicine, instructions, reminder_time):
    with get_conn() as conn:
        conn.execute(
            "INSERT INTO reminders(medicine, instructions, reminder_time) VALUES (?, ?, ?)",
            (medicine, instructions, reminder_time)
        )

def get_reminders():
    with get_conn() as conn:
        return pd.read_sql_query("SELECT * FROM reminders WHERE active=1 ORDER BY reminder_time", conn)

def deactivate_reminder(reminder_id):
    with get_conn() as conn:
        conn.execute("UPDATE reminders SET active=0 WHERE id=?", (int(reminder_id),))

init_db()

st.title("💙 CareBridge AI")
st.caption("A patient-support prototype for organizing health readings, prescription text and medicine reminders.")
st.warning(
    "Prototype only — not a medical device and not a substitute for a doctor. "
    "It does not diagnose, recommend treatment, or decide medicine doses. "
    "Confirm all prescription details with a qualified healthcare professional."
)

with st.sidebar:
    st.header("Patient profile")
    patient_name = st.text_input("Display name", value="Demo Patient")
    st.caption("Demo profile only. Do not enter sensitive real patient information.")
    st.divider()
    st.header("Alert thresholds")
    st.caption("Demo settings only. Use thresholds provided by a clinician for real care.")
    glucose_low = st.number_input("Glucose low flag (mg/dL)", min_value=30, max_value=150, value=70)
    glucose_high = st.number_input("Glucose high flag (mg/dL)", min_value=100, max_value=500, value=180)
    systolic_high = st.number_input("Systolic BP flag (mmHg)", min_value=100, max_value=250, value=140)
    diastolic_high = st.number_input("Diastolic BP flag (mmHg)", min_value=60, max_value=160, value=90)

tabs = st.tabs(["Dashboard", "Add health reading", "Prescription reader", "Medicine reminders", "About & safety"])

with tabs[0]:
    st.subheader(f"Welcome, {patient_name}")
    df = get_readings()
    c1, c2, c3 = st.columns(3)
    c1.metric("Recorded readings", len(df))
    c2.metric("Active reminders", len(get_reminders()))
    c3.metric("Latest entry", df.iloc[-1]["recorded_at"][:10] if not df.empty else "—")

    if df.empty:
        st.info("No readings yet. Add a demo reading in the 'Add health reading' tab.")
    else:
        st.markdown("#### Reading history")
        st.dataframe(df[["recorded_at", "reading_type", "value1", "value2"]], use_container_width=True)
        glucose = df[df["reading_type"] == "Glucose"].copy()
        bp = df[df["reading_type"] == "Blood pressure"].copy()
        left, right = st.columns(2)
        with left:
            st.markdown("**Blood glucose trend**")
            if not glucose.empty:
                fig = px.line(glucose, x="recorded_at", y="value1", markers=True,
                              labels={"recorded_at": "Date/time", "value1": "Glucose (mg/dL)"})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No glucose readings recorded.")
        with right:
            st.markdown("**Blood pressure trend**")
            if not bp.empty:
                bp["Systolic"] = bp["value1"]
                bp["Diastolic"] = bp["value2"]
                fig = px.line(bp, x="recorded_at", y=["Systolic", "Diastolic"], markers=True,
                              labels={"recorded_at": "Date/time", "value": "mmHg"})
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.caption("No blood-pressure readings recorded.")

        st.markdown("#### Configured threshold flags")
        flags = []
        for _, row in df.iterrows():
            dt = row["recorded_at"]
            if row["reading_type"] == "Glucose":
                v = row["value1"]
                if v < glucose_low:
                    flags.append(f"{dt}: Glucose reading {v:g} mg/dL is below the demo flag threshold.")
                elif v > glucose_high:
                    flags.append(f"{dt}: Glucose reading {v:g} mg/dL is above the demo flag threshold.")
            elif row["reading_type"] == "Blood pressure":
                sys, dia = row["value1"], row["value2"]
                if sys >= systolic_high or dia >= diastolic_high:
                    flags.append(f"{dt}: BP reading {sys:g}/{dia:g} mmHg crossed a demo flag threshold.")
        if flags:
            for flag in flags[-8:]:
                st.warning(flag)
            st.caption("These are data flags, not diagnoses. Follow the care plan given by a clinician.")
        else:
            st.success("No readings crossed the configured demo thresholds.")

with tabs[1]:
    st.subheader("Record a health reading")
    kind = st.radio("Reading type", ["Glucose", "Blood pressure"], horizontal=True)
    with st.form("reading_form"):
        reading_date = st.date_input("Date", value=date.today())
        reading_time = st.time_input("Time", value=datetime.now().time().replace(second=0, microsecond=0))
        if kind == "Glucose":
            val1 = st.number_input("Blood glucose (mg/dL)", min_value=1.0, max_value=1000.0, value=100.0)
            val2 = None
        else:
            col1, col2 = st.columns(2)
            with col1:
                val1 = st.number_input("Systolic (mmHg)", min_value=1.0, max_value=300.0, value=120.0)
            with col2:
                val2 = st.number_input("Diastolic (mmHg)", min_value=1.0, max_value=200.0, value=80.0)
        submitted = st.form_submit_button("Save reading", type="primary")
        if submitted:
            stamp = datetime.combine(reading_date, reading_time).isoformat(timespec="minutes")
            add_reading(stamp, kind, val1, val2)
            st.success("Reading saved to this local demo database.")

with tabs[2]:
    st.subheader("Prescription text reader (OCR)")
    st.write("Upload a clear image of a prescription. OCR output may be inaccurate; verify every word with the prescriber or pharmacist.")
    uploaded = st.file_uploader("Choose prescription image", type=["png", "jpg", "jpeg"])
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Uploaded image", use_container_width=True)
        if st.button("Extract text with OCR"):
            try:
                import pytesseract
                extracted = pytesseract.image_to_string(image)
                st.text_area("Extracted text — review carefully", value=extracted, height=220)
                st.info("Do not use OCR output as medicine instructions until a qualified professional confirms it.")
            except ImportError:
                st.error("OCR package is not installed. Run: pip install pytesseract. You also need the Tesseract OCR system application.")
            except Exception as exc:
                st.error(f"OCR could not run: {exc}")
    else:
        st.caption("Tip: for the demo, use a sample/fake prescription image, not a real person's medical document.")

with tabs[3]:
    st.subheader("Medicine reminders")
    st.write("Add a schedule that has already been confirmed by a healthcare professional.")
    with st.form("reminder_form"):
        medicine = st.text_input("Medicine name (demo)")
        instructions = st.text_input("Instructions exactly as confirmed by clinician/pharmacist")
        reminder_time = st.time_input("Reminder time", value=time(8, 0))
        save = st.form_submit_button("Add reminder", type="primary")
        if save:
            if medicine.strip():
                add_reminder(medicine.strip(), instructions.strip(), reminder_time.strftime("%H:%M"))
                st.success("Reminder added.")
            else:
                st.error("Enter a medicine name.")
    reminders = get_reminders()
    if reminders.empty:
        st.info("No active reminders.")
    else:
        for _, r in reminders.iterrows():
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.markdown(f"**{r['reminder_time']} — {r['medicine']}**")
                st.caption(r["instructions"] or "No additional instructions entered.")
            with col_b:
                if st.button("Done", key=f"done_{r['id']}"):
                    deactivate_reminder(r["id"])
                    st.rerun()
    st.caption("This prototype displays reminder schedules; it does not send phone notifications or guarantee that a dose is taken.")

with tabs[4]:
    st.subheader("Project scope and safety")
    st.markdown("""
    **CareBridge AI** demonstrates a small patient-support workflow:
    - Local recording and visualization of patient-entered readings.
    - User-configured threshold flags for demonstration.
    - OCR text extraction from an uploaded image.
    - Manually entered medicine schedule reminders.

    **Limitations**
    - OCR can misread handwriting, medicine names, numbers and timing.
    - Thresholds shown here are demo values, not universal clinical guidance.
    - No diagnosis, treatment recommendation, dose calculation or emergency triage is provided.
    - No SMS, WhatsApp, email or caregiver alert is sent by this prototype.
    - Data is stored locally in `carebridge.db`; this demo is not hardened for real patient records.

    For a real deployment, obtain clinical review, security/privacy review, consent, access control,
    encryption, audit logs, validated clinical workflows and appropriate regulatory guidance.
    """)
    st.caption("Built as a hackathon prototype. Use synthetic/demo data only.")
