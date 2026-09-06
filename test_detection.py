import pytest
from detection import detect_document_type


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
