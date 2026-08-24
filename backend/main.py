import os
from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from extractors import extract_text, ExtractionError
from summarizers import summarize, SummarizationError, VALID_PROVIDERS, VALID_LENGTHS

app = FastAPI(title="Document Summary Assistant")

allowed_origins_env = os.environ.get("ALLOWED_ORIGINS", "*")
allowed_origins = [o.strip() for o in allowed_origins_env.split(",") if o.strip()] if allowed_origins_env != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_FILE_SIZE_MB = 10


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/summarize")
async def summarize_document(
    file: UploadFile = File(...),
    length: str = Form("medium"),
    provider: str = Form("groq"),
):
    if length not in VALID_LENGTHS:
        raise HTTPException(400, f"length must be one of {sorted(VALID_LENGTHS)}")
    if provider not in VALID_PROVIDERS:
        raise HTTPException(400, f"provider must be one of {sorted(VALID_PROVIDERS)}")

    file_bytes = await file.read()
    if len(file_bytes) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(400, f"File exceeds {MAX_FILE_SIZE_MB}MB limit")
    if not file_bytes:
        raise HTTPException(400, "Uploaded file is empty")

    try:
        text = extract_text(file_bytes, file.content_type)
    except ExtractionError as e:
        raise HTTPException(422, str(e))

    try:
        result = summarize(text, length, provider)
    except SummarizationError as e:
        # Fall back to Gemini if the chosen provider fails and it wasn't already Gemini
        if provider != "gemini" and os.environ.get("GEMINI_API_KEY"):
            try:
                result = summarize(text, length, "gemini")
                return {
                    "summary": result,
                    "provider_used": "gemini",
                    "fallback": True,
                    "original_error": str(e),
                }
            except SummarizationError:
                pass
        raise HTTPException(502, str(e))

    return {"summary": result, "provider_used": provider, "fallback": False}
