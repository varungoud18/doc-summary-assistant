"""
Turns an uploaded file into plain text.
PDFs go through pdfplumber (text layer). Images go through Tesseract OCR.
No layout preservation attempted — summarization only needs clean text.
"""

import io
import pdfplumber
import pytesseract
from PIL import Image

SUPPORTED_PDF_TYPES = {"application/pdf"}
SUPPORTED_IMAGE_TYPES = {"image/png", "image/jpeg", "image/jpg", "image/webp"}


class ExtractionError(Exception):
    pass


def extract_text(file_bytes: bytes, content_type: str) -> str:
    if content_type in SUPPORTED_PDF_TYPES:
        return _extract_from_pdf(file_bytes)
    elif content_type in SUPPORTED_IMAGE_TYPES:
        return _extract_from_image(file_bytes)
    else:
        raise ExtractionError(
            f"Unsupported file type: {content_type}. Upload a PDF or an image (PNG/JPEG/WEBP)."
        )


def _extract_from_pdf(file_bytes: bytes) -> str:
    text_parts = []
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
    except Exception as e:
        raise ExtractionError(f"Could not parse PDF: {e}")

    text = "\n\n".join(text_parts).strip()
    if not text:
        raise ExtractionError(
            "No extractable text found in this PDF. It may be a scanned "
            "document — try uploading it as an image instead so OCR can run."
        )
    return text


def _extract_from_image(file_bytes: bytes) -> str:
    try:
        image = Image.open(io.BytesIO(file_bytes))
        text = pytesseract.image_to_string(image)
    except Exception as e:
        raise ExtractionError(f"Could not run OCR on this image: {e}")

    text = text.strip()
    if not text:
        raise ExtractionError("OCR found no readable text in this image.")
    return text
