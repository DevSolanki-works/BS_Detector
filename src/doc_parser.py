# src/doc_parser.py
# ─────────────────────────────────────────────────────────────────────────────
# Extracts plain text from uploaded PDF or DOCX files.
# Keeps file handling completely separate from LLM logic.
# ─────────────────────────────────────────────────────────────────────────────

import io
import pdfplumber
import docx


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract all text from a PDF file given its raw bytes."""
    text_parts = []
    with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text_parts.append(page_text)
    return "\n\n".join(text_parts)


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract all text from a .docx file given its raw bytes."""
    doc = docx.Document(io.BytesIO(file_bytes))
    return "\n".join(para.text for para in doc.paragraphs if para.text.strip())


def extract_text(uploaded_file) -> str:
    """
    Router: detect file type from Streamlit UploadedFile object
    and call the right extractor.
    """
    file_bytes = uploaded_file.read()
    name = uploaded_file.name.lower()

    if name.endswith(".pdf"):
        return extract_text_from_pdf(file_bytes)
    elif name.endswith(".docx"):
        return extract_text_from_docx(file_bytes)
    else:
        # Plain text / .txt fallback
        return file_bytes.decode("utf-8", errors="ignore")