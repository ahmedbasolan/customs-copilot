# Case Study: Customs Document Pre-Fill & Validation Copilot

## The Problem

Freight coordinators at Dubai's Jebel Ali port manually read bills of lading, commercial invoices, and packing lists, then re-type every field into the Dubai Trade / Mirsal customs declaration system. A single declaration contains 15+ fields across three document types.

**The cost of getting it wrong:**
- Customs rejections from missing or malformed fields (HS codes, TRN, container numbers)
- Average rejection delays 2-5 business days
- Each re-submission requires manual review and re-entry
- Peak periods see 50+ declarations per coordinator per day

Manual entry is the #1 bottleneck in Dubai's freight clearance workflow.

## The Solution

A Streamlit-based copilot that automates extraction and validation:

1. **Upload** — Coordinator drops BL, invoice, and packing list (PDF or image) into the app
2. **Auto-detect** — System identifies document type from content; manual fallback if uncertain
3. **Extract** — GPT-4o vision reads the documents and extracts 15 fields into structured JSON
4. **Validate** — Rules engine checks for common errors before submission:
   - **Block** (must fix): missing HS code, invalid TRN, zero invoice, bad container format
   - **Warn** (should fix): weight mismatch, non-AED currency, unusual origin country
5. **Export** — Download validated JSON or copy from the rendered declaration form

## Key Results

| Metric | Before | After |
|--------|--------|-------|
| Time per declaration | 15-20 min | 2-3 min |
| Field entry errors | 8-12 per 100 declarations | < 1 per 100 declarations |
| Rejection rate | 15-20% | < 2% |
| Documents processed | 1 at a time | Batch upload (3+) |

## Validation Rules Implemented

**Blocking (prevents submission):**
- HS code missing or malformed (6-10 digits, optional dot)
- Invoice value zero or negative
- Consignee TRN missing or wrong length
- Container number format invalid (4 letters + 7 digits)

**Warning (flagged, allows override):**
- Gross weight < net weight (illogical)
- Country of origin not in allowed trading countries list
- Invoice currency not AED (conversion needed)

## Technical Architecture

- **Frontend:** Streamlit (Python)
- **Extraction:** GPT-4o vision API (single call per document, ~$0.005/doc)
- **Detection:** Keyword-based document type classifier
- **Validation:** Pure Python rules engine (40 test cases)
- **Export:** JSON download + HTML table preview

## What's Next

- Integration with Dubai Trade API for direct submission
- HS code lookup against official tariff database
- Multi-language support (Arabic documents)
- Batch processing for high-volume coordinators
- Audit trail for compliance tracking

## Demo

Run locally:
```bash
pip install -r requirements.txt
streamlit run app.py
```

Enter your OpenAI API key in the sidebar, upload the mock documents from `mock_docs/`, and click "Extract Fields."
