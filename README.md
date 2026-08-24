# Document Summary Assistant

Upload a PDF or scanned image, pick a summary length, and get a fast summary with key points powered by Groq (Llama 3.3 70B) with Gemini fallback.

## Stack

- **Backend:** FastAPI, pdfplumber (PDF text extraction), Cloud Vision OCR via Gemini (images & scanned PDFs)
- **Frontend:** React + Vite, clean styling (no external CSS framework)
- **Model:** Groq (`llama-3.3-70b-versatile`) as Primary, Gemini (`gemini-1.5-flash`) as Fallback

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

> **Note:** No local Tesseract installation or OS-level binaries are required! Image OCR and scanned PDF processing are handled natively via Cloud Vision (Gemini / OpenAI), making it 100% portable for any device, serverless platform, or cloud deployment.

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
  - Environment Variables: Set `GROQ_API_KEY`, `GEMINI_API_KEY`, and `ALLOWED_ORIGINS=*`.

- **Frontend → Vercel:** Import this repository.
  - Root directory: `frontend`
  - Framework preset: `Vite`
  - Environment Variable: Set `VITE_API_BASE_URL` to your live Backend URL.

## Approach & Design

The application extracts text from uploaded documents (using `pdfplumber` for text PDFs and Cloud Vision AI for image OCR / scanned PDFs), then generates structured summaries with key bullet points.

* **Length Options:** Summary length is handled through dynamic system prompts rather than separate processing pipelines.
* **Modern Interface:** Built with a professional, dark-mode design system following human-crafted SaaS layouts (Linear/Stripe style) featuring optimized contrasts, smooth drag-and-drop actions, and a copy-to-clipboard utility.
* **Error Handling:** Actionable user feedback is provided for failed extractions (e.g. empty files, unreadable formats).

## Known Limitations

- Large PDFs are truncated to stay within free-tier context limits.
- No session persistence — summaries are not saved between browser refreshes.

