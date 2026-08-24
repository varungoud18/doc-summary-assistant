# Document Summary Assistant

Upload a PDF or scanned image, pick a summary length, and get a summary with key points powered by Gemini.

## Stack

- **Backend:** FastAPI, pdfplumber (PDF text extraction), pytesseract (OCR for scanned images)
- **Frontend:** React + Vite, clean styling (no external CSS framework)
- **Model:** Gemini (`google-generativeai`)

## Local Setup

### Backend

```bash
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

pip install -r requirements.txt
cp .env.example .env   # Fill in your GEMINI_API_KEY
uvicorn main:app --reload --port 8000
```

Tesseract must also be installed on your system (not a Python package):
- Windows: Install from the [Tesseract UB Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki)
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt install tesseract-ocr`

### Frontend

```bash
cd frontend
npm install
# Create local env file:
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

### Run Everything Together (Windows)
Double-click the `run.bat` script in the root directory to launch both the backend and frontend at the same time.

## Deployment

- **Backend → Render:** New Web Service from this repo.
  - Root directory: `backend`
  - Build command: `pip install -r requirements.txt`
  - Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Environment Variables: Set `GEMINI_API_KEY` and `ALLOWED_ORIGINS=*`.
  *(Note: Render's native environment requires a build script to install the tesseract-ocr system package for OCR support, or a Docker deploy).*

- **Frontend → Vercel:** Import this repository.
  - Root directory: `frontend`
  - Framework preset: `Vite`
  - Environment Variable: Set `VITE_API_BASE_URL` to your Render backend URL.

## Approach & Design

The application extracts text from uploaded documents (using `pdfplumber` for text PDFs and `pytesseract` for image OCR), then sends the text to the Google Gemini API to generate structured summaries.

* **Length Options:** Summary length is handled through dynamic system prompts rather than separate processing pipelines.
* **Modern Interface:** Built with a professional, dark-mode design system following human-crafted SaaS layouts (Linear/Stripe style) featuring optimized contrasts, smooth drag-and-drop actions, and a copy-to-clipboard utility.
* **Error Handling:** Actionable user feedback is provided for failed extractions (e.g. empty files, unreadable formats).

## Known Limitations

- Large PDFs are truncated to stay within free-tier context limits.
- No session persistence — summaries are not saved between browser refreshes.

