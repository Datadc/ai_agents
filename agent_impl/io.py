from pathlib import Path

import pdfplumber
import pytesseract


def extract_text_from_pdf(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)

    # Text extraction via pdfplumber first
    text_chunks = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            t = page.extract_text() or ""
            text_chunks.append(t)

    extracted = "\n".join(text_chunks).strip()
    if extracted:
        return extracted

    # Fallback OCR for scanned PDF
    ocr_chunks = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            page_image = page.to_image(resolution=300).original
            ocr_text = pytesseract.image_to_string(page_image)
            ocr_chunks.append(ocr_text)

    return "\n".join(ocr_chunks).strip()


def load_policy_text(path: Path) -> str:
    if not path.exists():
        raise FileNotFoundError(path)
    if path.suffix.lower() == ".pdf":
        return extract_text_from_pdf(path)
    return path.read_text(encoding="utf-8", errors="ignore")
