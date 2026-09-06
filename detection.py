import re
from typing import Optional


BILL_OF_LADING_KEYWORDS = [
    "bill of lading",
    "b/l number",
    "bl number",
    "shipper",
    "consignee",
    "container no",
    "port of loading",
    "port of discharge",
    "vessel",
    "voyage",
    "marks & numbers",
    "marks and numbers",
]

INVOICE_KEYWORDS = [
    "commercial invoice",
    "invoice no",
    "invoice number",
    "seller",
    "buyer",
    "unit price",
    "amount",
    "total invoice value",
    "payment terms",
    "description of goods",
    "hs code",
]

PACKING_LIST_KEYWORDS = [
    "packing list",
    "pl no",
    "packing details",
    "packages",
    "gross wt",
    "gross weight",
    "net wt",
    "net weight",
    "total packages",
    "cbm",
    "pallets",
]

CONFIDENCE_THRESHOLD = 0.15


def _extract_text_from_pdf(raw_bytes: bytes) -> str:
    try:
        import pymupdf
        doc = pymupdf.open(stream=raw_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except Exception:
        return ""


def _extract_text(raw_bytes: bytes) -> str:
    if raw_bytes[:4] == b"%PDF":
        return _extract_text_from_pdf(raw_bytes)
    try:
        return raw_bytes[:8000].decode("utf-8", errors="ignore")
    except Exception:
        return ""


def _count_matches(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    count = 0
    for keyword in keywords:
        if keyword in text_lower:
            count += 1
    return count


def detect_document_type(raw_bytes: bytes) -> tuple[str, float]:
    text = _extract_text(raw_bytes)

    if not text or not text.strip():
        return "unknown", 0.0

    bl_matches = _count_matches(text, BILL_OF_LADING_KEYWORDS)
    invoice_matches = _count_matches(text, INVOICE_KEYWORDS)
    pl_matches = _count_matches(text, PACKING_LIST_KEYWORDS)

    scores = {
        "bill_of_lading": bl_matches / len(BILL_OF_LADING_KEYWORDS),
        "invoice": invoice_matches / len(INVOICE_KEYWORDS),
        "packing_list": pl_matches / len(PACKING_LIST_KEYWORDS),
    }

    best_type = max(scores, key=scores.get)
    best_score = scores[best_type]

    if best_score < CONFIDENCE_THRESHOLD:
        return "unknown", best_score

    return best_type, best_score
