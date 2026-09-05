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


def _count_matches(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    count = 0
    for keyword in keywords:
        if keyword in text_lower:
            count += 1
    return count


def detect_document_type(text: str) -> tuple[str, float]:
    if not text or not text.strip():
        return "unknown", 0.0

    total_keywords = len(BILL_OF_LADING_KEYWORDS) + len(INVOICE_KEYWORDS) + len(PACKING_LIST_KEYWORDS)

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
