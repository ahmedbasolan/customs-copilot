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

PDF_HINT = "Install it with: pip install pymupdf"


class PdfTextUnavailable(Exception):
    """PDF text extraction failed. `reason` is a short machine-readable slug."""

    def __init__(self, reason: str, message: str):
        self.reason = reason
        super().__init__(message)


def _import_pymupdf():
    """Import pymupdf, or explain clearly that it is missing.

    Swallowing this import error is what previously made a missing dependency
    look identical to an unreadable document: auto-detect just returned
    "unknown" and the coordinator was never told why.
    """
    try:
        import pymupdf
    except ImportError as exc:
        raise PdfTextUnavailable(
            "missing_dependency",
            f"PDF support requires the 'pymupdf' package, which is not installed. {PDF_HINT}",
        ) from exc
    return pymupdf


def pdf_support_available() -> tuple[bool, str]:
    """Whether PDF auto-detect can run. Returns (ok, message)."""
    try:
        _import_pymupdf()
    except PdfTextUnavailable as exc:
        return False, str(exc)
    return True, "pymupdf available"


def _extract_text_from_pdf(raw_bytes: bytes) -> str:
    """Extract embedded text from a PDF.

    Raises PdfTextUnavailable with a distinct reason for each failure mode:
    missing dependency, unreadable/encrypted file, or a scanned image with no
    text layer. All three used to return "" and surface as "unknown".
    """
    pymupdf = _import_pymupdf()

    try:
        doc = pymupdf.open(stream=raw_bytes, filetype="pdf")
    except Exception as exc:
        raise PdfTextUnavailable(
            "unreadable_pdf",
            "This file could not be opened as a PDF. It may be corrupt, "
            "password-protected, or not a real PDF.",
        ) from exc

    try:
        if getattr(doc, "needs_pass", False):
            raise PdfTextUnavailable(
                "encrypted_pdf",
                "This PDF is password-protected, so its text cannot be read. "
                "Remove the password and upload again, or set the document type manually.",
            )
        pages = list(doc)
        text = "".join(page.get_text() for page in pages)
    except PdfTextUnavailable:
        raise
    except Exception as exc:
        raise PdfTextUnavailable(
            "unreadable_pdf",
            "The PDF opened but its text could not be read.",
        ) from exc
    finally:
        doc.close()

    if not text.strip():
        raise PdfTextUnavailable(
            "no_text_layer",
            "This PDF has no embedded text — it is most likely a scan or photo. "
            "Auto-detect needs a text-based PDF; set the document type manually.",
        )
    return text


def _extract_text(raw_bytes: bytes) -> str:
    if raw_bytes[:4] == b"%PDF":
        return _extract_text_from_pdf(raw_bytes)
    return raw_bytes[:8000].decode("utf-8", errors="ignore")


def _count_matches(text: str, keywords: list[str]) -> int:
    text_lower = text.lower()
    count = 0
    for keyword in keywords:
        if keyword in text_lower:
            count += 1
    return count


def detect_document_type(raw_bytes: bytes) -> tuple[str, float]:
    """Classify a document as bill_of_lading / invoice / packing_list / unknown.

    Returns ("unknown", 0.0) when the content is readable but does not match
    any keyword profile. Raises PdfTextUnavailable when a PDF could not be
    read at all, so the caller can tell the user why.
    """
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


def detect_document_type_safe(raw_bytes: bytes) -> tuple[str, float, str | None]:
    """Like detect_document_type, but never raises.

    Returns (doc_type, confidence, warning). `warning` is None on success, or
    a user-facing message explaining why auto-detect could not run.
    """
    try:
        doc_type, confidence = detect_document_type(raw_bytes)
    except PdfTextUnavailable as exc:
        return "unknown", 0.0, str(exc)
    if doc_type == "unknown":
        return doc_type, confidence, (
            "Could not identify this document automatically. Set the type manually."
        )
    return doc_type, confidence, None
