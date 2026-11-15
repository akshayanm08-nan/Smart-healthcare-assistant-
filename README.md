# Smart-healthcare-assistant-
Easy and very smartest healthcare assistant 
CareBridge AI — VibeX Codes Track 2

A Streamlit hackathon prototype for organizing patient-entered health readings, extracting text from prescription images using OCR, and displaying medicine reminder schedules.

## Features
- Local SQLite storage for demo health readings and reminders
- Blood glucose and blood-pressure trend charts
- User-configurable demo threshold flags
- Optional prescription image OCR using Tesseract
- Manually entered medicine reminders
- Safety and limitations page

## Important safety note
This is an educational prototype, not a medical device or clinical decision-support system. It does not diagnose, prescribe, calculate doses, or send emergency alerts. OCR output must be checked by a qualified healthcare professional. Use synthetic/demo data only; do not upload real patient records.

## Run locally

### 1. Install Python
Use Python 3.10 or newer.

### 2. Create and activate a virtual environment (recommended)
```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
```

### 3. Install packages
```bash
pip install -r requirements.txt
```

### 4. Optional: install Tesseract OCR
The prescription reader uses `pytesseract`, which also requires the Tesseract OCR application installed on your computer.
- Windows: install the Tesseract OCR application and ensure `tesseract.exe` is on PATH.
- Ubuntu/Debian: `sudo apt install tesseract-ocr`
- macOS with Homebrew: `brew install tesseract`

If Tesseract is not installed, the rest of the application still works; OCR will show an explanatory error.

### 5. Start the app
```bash
streamlit run app.py
```
Open the local URL shown in the terminal (usually http://localhost:8501).

## Demo walkthrough
1. Open **Add health reading** and save a glucose value.
2. Save a blood-pressure value.
3. Open **Dashboard** to see history, charts and configured demo flags.
4. Open **Prescription reader** and upload a sample/fake prescription image.
5. Open **Medicine reminders** and add a schedule using instructions already confirmed by a clinician/pharmacist.

