import pytest

from detection import (
    PdfTextUnavailable,
    detect_document_type,
    detect_document_type_safe,
    pdf_support_available,
)


BL_TEXT = """
BILL OF LADING
B/L Number: SH-2026-00487
Shipper: Guangzhou Bright Electronics
Consignee: Al Noor Trading FZE
Container No: MSCU4567892
Port of Loading: Shanghai
Port of Discharge: Jebel Ali
"""

INVOICE_TEXT = """
COMMERCIAL INVOICE
Invoice No: INV-2026-GB-00892
Seller: Guangzhou Bright Electronics
Buyer: Al Noor Trading FZE
DESCRIPTION OF GOODS
Item | Description | HS Code | Qty | Unit Price | Amount
1 | LED Panel Light | 9405.42 | 500 | USD 28.50 | USD 14,250.00
TOTAL INVOICE VALUE: USD 36,850.00
"""

PL_TEXT = """
PACKING LIST
PL No: PL-2026-GB-00892
PACKING DETAILS
Item | Description | Qty | Packages | Gross Wt | Net Wt
1 | LED Panel Light | 500 | 50 pallets | 6,800.00 | 5,920.00
TOTALS
Total Packages: 120 PALLETS
Total Gross Weight: 18,500.00 KGS
Total Net Weight: 16,200.00 KGS
"""


class TestDetectDocumentType:
    def test_bill_of_lading(self):
        doc_type, confidence = detect_document_type(BL_TEXT.encode())
        assert doc_type == "bill_of_lading"
        assert confidence > 0.15

    def test_commercial_invoice(self):
        doc_type, confidence = detect_document_type(INVOICE_TEXT.encode())
        assert doc_type == "invoice"
        assert confidence > 0.15

    def test_packing_list(self):
        doc_type, confidence = detect_document_type(PL_TEXT.encode())
        assert doc_type == "packing_list"
        assert confidence > 0.15

    def test_unknown_document(self):
        text = b"This is a random document with no shipping information."
        doc_type, confidence = detect_document_type(text)
        assert doc_type == "unknown"

    def test_empty(self):
        doc_type, confidence = detect_document_type(b"")
        assert doc_type == "unknown"

    def test_case_insensitive(self):
        text = b"bill of lading\nShipper: Test"
        doc_type, confidence = detect_document_type(text)
        assert doc_type == "bill_of_lading"

    def test_pdf_bill_of_lading(self):
        with open("mock_docs/bill_of_lading.pdf", "rb") as f:
            raw = f.read()
        doc_type, confidence = detect_document_type(raw)
        assert doc_type == "bill_of_lading"

    def test_pdf_invoice(self):
        with open("mock_docs/commercial_invoice.pdf", "rb") as f:
            raw = f.read()
        doc_type, confidence = detect_document_type(raw)
        assert doc_type == "invoice"

    def test_pdf_packing_list(self):
        with open("mock_docs/packing_list.pdf", "rb") as f:
            raw = f.read()
        doc_type, confidence = detect_document_type(raw)
        assert doc_type == "packing_list"


class TestPdfDependency:
    """A missing pymupdf must fail loudly, not look like an unrecognised doc."""

    def test_pdf_support_available(self):
        ok, message = pdf_support_available()
        assert ok, (
            f"PDF support is broken: {message} "
            "The PDF tests below cannot pass without it."
        )

    def test_missing_dependency_raises_with_actionable_message(self, monkeypatch):
        import builtins

        real_import = builtins.__import__

        def fake_import(name, *args, **kwargs):
            if name == "pymupdf":
                raise ImportError("No module named 'pymupdf'")
            return real_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", fake_import)

        with open("mock_docs/bill_of_lading.pdf", "rb") as f:
            raw = f.read()

        with pytest.raises(PdfTextUnavailable) as excinfo:
            detect_document_type(raw)
        assert excinfo.value.reason == "missing_dependency"
        assert "pip install pymupdf" in str(excinfo.value)

    def test_safe_variant_reports_the_reason(self):
        with open("mock_docs/bill_of_lading.pdf", "rb") as f:
            raw = f.read()
        doc_type, confidence, warning = detect_document_type_safe(raw)
        assert warning is None, f"unexpected warning: {warning}"
        assert doc_type == "bill_of_lading"


class TestPdfFailureModes:
    """Each failure mode gets its own reason and its own message."""

    def test_corrupt_pdf_is_not_reported_as_unknown(self):
        doc_type, confidence, warning = detect_document_type_safe(b"%PDF-1.4 garbage")
        assert doc_type == "unknown"
        assert warning and "could not be opened" in warning.lower()

    def test_pdf_without_text_layer_explains_scanned_image(self, tmp_path):
        # Minimal hand-written PDF with a content stream of vector line
        # operators only: structurally valid, but no text-showing operators,
        # so pymupdf extracts nothing. Built by hand to avoid depending on
        # fpdf2, which is only needed to regenerate the mock documents.
        content = b"q 0 0 1 RG 2 w 10 10 m 200 10 l S Q"
        objects = [
            b"<< /Type /Catalog /Pages 2 0 R >>",
            b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
            b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 300 300] "
            b"/Resources << >> /Contents 4 0 R >>",
            b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n"
            + content
            + b"\nendstream",
        ]

        out = bytearray(b"%PDF-1.4\n")
        offsets = []
        for i, body in enumerate(objects, start=1):
            offsets.append(len(out))
            out += f"{i} 0 obj\n".encode() + body + b"\nendobj\n"

        xref_at = len(out)
        out += f"xref\n0 {len(objects) + 1}\n".encode()
        out += b"0000000000 65535 f \n"
        for off in offsets:
            out += f"{off:010d} 00000 n \n".encode()
        out += f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\nstartxref\n{xref_at}\n%%EOF\n".encode()

        doc_type, _, warning = detect_document_type_safe(bytes(out))
        assert doc_type == "unknown"
        assert warning and (
            "no embedded text" in warning.lower() or "scan" in warning.lower()
        ), f"unexpected warning: {warning}"

    def test_unrelated_text_file_still_returns_unknown_without_a_pdf_warning(self):
        doc_type, _, warning = detect_document_type_safe(
            b"This is a random document with no shipping information."
        )
        assert doc_type == "unknown"
        assert warning and "manually" in warning.lower()
