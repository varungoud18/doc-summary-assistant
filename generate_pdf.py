import os
import sys

def build_pdf():
    pdf_filename = "Document_Summary_Assistant_Overview.pdf"
    
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
        )
    except ImportError:
        print("reportlab library not found. Installing via pip...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "reportlab"])
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.platypus import (
            SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
        )

    doc = SimpleDocTemplate(
        pdf_filename,
        pagesize=letter,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    styles = getSampleStyleSheet()

    # Custom styles
    primary_color = colors.HexColor("#1e293b")
    secondary_color = colors.HexColor("#0f766e")
    accent_color = colors.HexColor("#0284c7")
    dark_text = colors.HexColor("#334155")
    bg_light = colors.HexColor("#f8fafc")

    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=primary_color,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubtitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=secondary_color,
        spaceAfter=15
    )

    h2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=primary_color,
        spaceBefore=14,
        spaceAfter=6
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14,
        textColor=dark_text,
        spaceAfter=8
    )

    bullet_style = ParagraphStyle(
        'BulletCustom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=11,
        textColor=colors.white
    )

    table_cell_style = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11,
        textColor=dark_text
    )

    story = []

    # Title Banner
    story.append(Paragraph("Document Summary Assistant", title_style))
    story.append(Paragraph("Project Architecture, Technical Overview, & Technical Limitations Report", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=secondary_color, spaceBefore=0, spaceAfter=15))

    # Section 1: Executive Overview
    story.append(Paragraph("1. Executive Overview & Theme", h2_style))
    exec_text = (
        "<b>Document Summary Assistant</b> is an AI-powered document processing and summarization platform. "
        "It accepts PDFs and scanned document images, extracts textual content using high-speed text layers or "
        "cloud-native vision OCR, and produces clean, structured Markdown summaries paired with actionable key bullet points. "
        "The project emphasizes <b>zero local binary dependencies</b> (removing OS-level Tesseract installations), "
        "high performance via <b>Groq inference</b>, and ultimate reliability with <b>Google Gemini fallback</b>."
    )
    story.append(Paragraph(exec_text, body_style))

    # Features
    story.append(Paragraph("<b>Key System Highlights:</b>", body_style))
    highlights = [
        "<b>Multi-Format Ingestion:</b> Supports PDFs and raster document images (.png, .jpg, .jpeg, .webp) up to 50 MB.",
        "<b>Dual AI Engine Architecture:</b> Primary high-speed LLM processing via Groq with seamless automatic failover to Google Gemini 3.",
        "<b>Cloud-Native Multimodal OCR:</b> Automatically transcribes text from scanned image PDFs and standalone image uploads without local Tesseract dependencies.",
        "<b>Interactive UX:</b> Dynamic summary length switching (Short, Medium, Long), single-click Markdown copying, dark/light glassmorphic theme.",
        "<b>Clean Output Pipeline:</b> Regex sanitization strips model reasoning tags (<think>...</think>) and preamble thoughts."
    ]
    for h in highlights:
        story.append(Paragraph(f"• {h}", bullet_style))

    story.append(Spacer(1, 10))

    # Section 2: Technology Stack
    story.append(Paragraph("2. Technical Stack & Components", h2_style))

    tech_data = [
        [Paragraph("Layer", table_header_style), Paragraph("Technologies", table_header_style), Paragraph("Purpose / Highlights", table_header_style)],
        [Paragraph("Frontend UI", table_cell_style), Paragraph("React 18, Vite, Vanilla CSS", table_cell_style), Paragraph("Fast SPA with custom CSS design tokens, glassmorphism, responsive theme switching.", table_cell_style)],
        [Paragraph("Backend API", table_cell_style), Paragraph("FastAPI, Python 3.11+, Uvicorn", table_cell_style), Paragraph("Asynchronous RESTful framework, file validation, CORS handling, provider orchestration.", table_cell_style)],
        [Paragraph("Text Extraction", table_cell_style), Paragraph("pdfplumber", table_cell_style), Paragraph("Parses embedded PDF text layers directly with high fidelity.", table_cell_style)],
        [Paragraph("Cloud OCR", table_cell_style), Paragraph("Google Gemini Vision API, OpenAI Vision API", table_cell_style), Paragraph("Cloud-native multimodal transcription for scanned PDFs and image files.", table_cell_style)],
        [Paragraph("Primary LLM Engine", table_cell_style), Paragraph("Groq API (Llama-3.3-70B, Qwen3.6-27B, GPT-OSS)", table_cell_style), Paragraph("Ultra-low latency inference with dynamic model availability lookup.", table_cell_style)],
        [Paragraph("Fallback LLM Engine", table_cell_style), Paragraph("Google Gemini 3 (3.7-flash, 3.6-flash)", table_cell_style), Paragraph("Automatic secondary provider if Groq encounters limits or API errors.", table_cell_style)],
        [Paragraph("Deployment Target", table_cell_style), Paragraph("Render (Backend), Vercel (Frontend)", table_cell_style), Paragraph("Hosted cloud deployment setup with environment variable configuration.", table_cell_style)]
    ]

    t = Table(tech_data, colWidths=[100, 160, 270])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), primary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t)

    story.append(Spacer(1, 12))

    # Section 3: Architecture & Data Flow
    story.append(Paragraph("3. System Architecture & Ingestion Flow", h2_style))
    flow_text = (
        "1. <b>File Reception:</b> Client uploads document (PDF/Image) to <code>POST /summarize</code> along with requested length and provider.<br/>"
        "2. <b>Size & Type Validation:</b> FastAPI verifies file size is within 50MB and validates content type headers.<br/>"
        "3. <b>Text Extraction Routing:</b> For PDFs, <i>pdfplumber</i> extracts selectable text layers. If no text layer exists or an image is uploaded, it routes to Cloud Vision (Gemini/OpenAI).<br/>"
        "4. <b>LLM Summarization:</b> Text is dispatched to Groq API. If Groq fails or rate limits, request transparently falls back to Gemini.<br/>"
        "5. <b>Output Sanitization:</b> The response passes through <code>_clean_summary()</code> regex filters before returning formatted JSON to the React frontend."
    )
    story.append(Paragraph(flow_text, body_style))

    story.append(Spacer(1, 10))

    # Section 4: Technical Limitations
    story.append(Paragraph("4. Technical Limitations & Constraints", h2_style))

    limitations_data = [
        [Paragraph("Constraint / Area", table_header_style), Paragraph("Current Limitation", table_header_style), Paragraph("Impact & Details", table_header_style)],
        [Paragraph("Context Window Limit", table_cell_style), Paragraph("60,000 Characters (~15,000 words)", table_cell_style), Paragraph("Document text is hard-truncated at 60k chars. Large multi-chapter books are cut off rather than processed via RAG.", table_cell_style)],
        [Paragraph("Stateless Architecture", table_cell_style), Paragraph("No persistent database or auth", table_cell_style), Paragraph("Summaries are generated in-memory. Reloading the browser page resets state. No user account management.", table_cell_style)],
        [Paragraph("Supported File Formats", table_cell_style), Paragraph("PDF, PNG, JPG, JPEG, WEBP", table_cell_style), Paragraph("Office documents (.docx, .pptx, .xlsx) and plain markdown (.md) are not supported directly without prior conversion.", table_cell_style)],
        [Paragraph("Cloud API Reliance", table_cell_style), Paragraph("Third-party API key dependency", table_cell_style), Paragraph("Requires active GROQ_API_KEY and GEMINI_API_KEY. Rate limits or service outages on third-party APIs affect service.", table_cell_style)],
        [Paragraph("Upload Payload Cap", table_cell_style), Paragraph("50 Megabytes maximum file size", table_cell_style), Paragraph("Protects server memory on free tier deployments (Render free tier memory caps).", table_cell_style)]
    ]

    t_limit = Table(limitations_data, colWidths=[120, 160, 250])
    t_limit.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), secondary_color),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, bg_light]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    story.append(t_limit)

    story.append(Spacer(1, 10))


    doc.build(story)
    print(f"Successfully generated PDF: {pdf_filename}")

if __name__ == "__main__":
    build_pdf()
