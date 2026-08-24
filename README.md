# Document Summary Assistant

Upload a PDF or scanned image, pick a summary length and a model (Gemini, GPT, or Grok), and get a summary with key points.

## Stack

- **Backend:** FastAPI, pdfplumber (PDF text), pytesseract (OCR for images)
- **Frontend:** React + Vite, no UI framework
- **Models:** Gemini (`google-generativeai`), GPT (`openai`), Grok (xAI's OpenAI-compatible API) — selected per request, with automatic fallback to Gemini if the chosen model's call fails

## Local setup

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # fill in the keys you have
uvicorn main:app --reload --port 8000
```

Tesseract must also be installed on your system (not a Python package):
- macOS: `brew install tesseract`
- Ubuntu: `sudo apt install tesseract-ocr`
- Windows: install from the [Tesseract UB Mannheim build](https://github.com/UB-Mannheim/tesseract/wiki)

### Frontend

```bash
cd frontend
npm install
echo "VITE_API_BASE_URL=http://localhost:8000" > .env
npm run dev
```

## Deployment

- **Backend → Render:** New Web Service from this repo, root directory `backend`, build command `pip install -r requirements.txt`, start command `uvicorn main:app --host 0.0.0.0 --port $PORT`. Add a build step or buildpack for Tesseract (Render's native runtime needs `apt-get install tesseract-ocr` via a `render-build.sh`, or use a Docker deploy with a Debian base image that installs it). Set the API keys and `ALLOWED_ORIGINS` as environment variables.
- **Frontend → Vercel:** import the repo, root directory `frontend`, framework preset Vite. Set `VITE_API_BASE_URL` to the deployed Render URL.

## Approach (write-up)

The app extracts text from uploads (pdfplumber for PDFs, Tesseract OCR for images), then sends it to one of three LLM providers behind a single adapter function, so switching models is a one-line change and adding a new one doesn't touch the API contract. Summary length is expressed as prompt guidance rather than three separate pipelines, keeping the surface area small. If a chosen provider fails (missing key, rate limit, outage), the backend retries once with Gemini so a demo doesn't break on a single flaky call. The frontend is one page: drag-and-drop upload, two pill selectors, a loading state, and a results view — no routing, auth, or persistence, since the brief doesn't call for any of that. Error handling surfaces specific, actionable messages (e.g. "this PDF has no text layer — try uploading it as an image") rather than generic failures.

## Known limitations

- Large PDFs are truncated to ~15k characters before summarization to stay within free-tier context limits.
- No persistence — summaries aren't saved between sessions.
- Grok access requires an xAI API key with available credit; the free tier has changed over time, worth checking current terms.
