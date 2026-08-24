"""
Turns an uploaded file into plain text.
PDFs go through pdfplumber (text layer) with AI Vision fallback for scanned PDFs.
Images are processed using cloud-native Multimodal Vision (Gemini / OpenAI)
with local pytesseract as an optional fallback.
No OS-level Tesseract installation required.
"""

import io
import os
import base64
from typing import Optional
import pdfplumber
from PIL import Image

SUPPORTED_PDF_TYPES = {"application/pdf"}
SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


class ExtractionError(Exception):
    pass


def extract_text(file_bytes: bytes, content_type: Optional[str] = None) -> str:
    # Normalize content type if missing or generic
    if not content_type or content_type == "application/octet-stream":
        # Basic sniffing
        if file_bytes.startswith(b"%PDF"):
            content_type = "application/pdf"
        elif file_bytes.startswith(b"\x89PNG"):
            content_type = "image/png"
        elif file_bytes.startswith(b"\xff\xd8\xff"):
            content_type = "image/jpeg"
        elif file_bytes.startswith(b"RIFF") and b"WEBP" in file_bytes[:16]:
            content_type = "image/webp"

    if content_type in SUPPORTED_PDF_TYPES:
        return _extract_from_pdf(file_bytes)
    elif content_type in SUPPORTED_IMAGE_TYPES:
        return _extract_from_image(file_bytes, content_type)
    else:
        raise ExtractionError(
            f"Unsupported file type: {content_type or 'unknown'}. Upload a PDF or an image (PNG/JPEG/WEBP)."
        )


def _extract_with_gemini_vision(file_bytes: bytes, mime_type: Optional[str] = None) -> str:
    """Extracts text using Gemini's cloud-native multimodal vision API."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return ""

    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")

        # Standardize mime_type for Gemini
        if not mime_type or mime_type == "application/octet-stream":
            mime_type = "image/jpeg"
        elif mime_type == "image/jpg":
            mime_type = "image/jpeg"

        prompt = (
            "Extract and transcribe all readable text, tables, and contents from this document or image accurately. "
            "Maintain the original document wording, structure, and order. "
            "Output only the transcribed document text without conversational comments or introductions."
        )

        response = model.generate_content([
            {"mime_type": mime_type, "data": file_bytes},
            prompt,
        ])
        if response and response.text:
            return response.text.strip()
    except Exception:
        pass
    return ""


def _extract_with_openai_vision(file_bytes: bytes, mime_type: Optional[str] = None) -> str:
    """Extracts text using OpenAI's vision API as a secondary cloud fallback."""
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return ""

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        if not mime_type or mime_type == "application/octet-stream":
            mime_type = "image/jpeg"
        elif mime_type == "image/jpg":
            mime_type = "image/jpeg"
        b64_data = base64.b64encode(file_bytes).decode("utf-8")
        data_url = f"data:{mime_type};base64,{b64_data}"

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                "Extract and transcribe all text, tables, and content from this document image. "
                                "Return only the extracted text with no conversational remarks."
                            ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {"url": data_url},
                        },
                    ],
                }
            ],
        )
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
    except Exception:
        pass
    return ""


def _extract_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception:
        pass

    text = "\n\n".join(text_parts).strip()
    if text:
        return text

    # If pdfplumber found no text layer (e.g. scanned PDF), use Gemini Multimodal Vision on the PDF
    cloud_text = _extract_with_gemini_vision(file_bytes, "application/pdf")
    if cloud_text:
        return cloud_text

    raise ExtractionError(
        "No extractable text found in this PDF. If this is a scanned document, please ensure your GEMINI_API_KEY is configured in backend/.env for Cloud Vision OCR."
    )


def _extract_from_image(file_bytes: bytes, content_type: Optional[str] = None) -> str:
    # 1. Primary: Cloud Vision OCR via Gemini (no local binaries required)
    text = _extract_with_gemini_vision(file_bytes, content_type)
    if text:
        return text

    # 2. Secondary Cloud Vision via OpenAI if configured
    text = _extract_with_openai_vision(file_bytes, content_type)
    if text:
        return text

    # 3. Optional local Tesseract OCR (if installed on host OS)
    try:
        import pytesseract
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image).strip()
        if text:
            return text
    except Exception:
        pass

    raise ExtractionError(
        "Could not extract text from this image. Please ensure your GEMINI_API_KEY is configured in backend/.env for Cloud Vision OCR."
    )
