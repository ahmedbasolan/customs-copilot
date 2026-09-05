# Customs Document Pre-Fill & Validation Copilot

## Problem Statement

Freight coordinators manually read bills of lading, invoices, and packing lists, then re-type data into Dubai Trade / Mirsal. Typos and missing fields cause rejections and delays. The process is slow, error-prone, and requires deep domain knowledge to catch mistakes before submission.

## Solution

A Streamlit app that:
1. Accepts uploaded shipping documents (PDFs/images of BL, invoice, packing list)
2. Auto-detects document type from content (with manual fallback)
3. Extracts key fields using GPT-4o vision (no separate OCR step)
4. Pre-fills a mock customs declaration form with extracted data
5. Runs validation rules and highlights issues (block or warn) before submission
6. Outputs a JSON download and rendered HTML form ready for manual entry

## User Stories

1. As a freight coordinator, I want to upload multiple documents at once (BL, invoice, packing list), so that I don't have to classify each document manually
2. As a freight coordinator, I want the system to auto-detect which document is which, so that upload is fast and intuitive
3. As a freight coordinator, I want to manually assign document type when auto-detection fails, so that I'm not stuck on blurry or unusual documents
4. As a freight coordinator, I want to see extracted consignee name and TRN, so that I can verify the receiver details
5. As a freight coordinator, I want to see extracted shipper name and country, so that I can verify the sender details
6. As a freight coordinator, I want to see extracted container number(s), so that I can verify routing information
7. As a freight coordinator, I want to see extracted gross weight and net weight, so that I can verify weight accuracy
8. As a freight coordinator, I want to see extracted invoice value and currency, so that I can verify financial details
9. As a freight coordinator, I want to see extracted HS codes at line level, so that I can verify commodity classification
10. As a freight coordinator, I want to see extracted country of origin, so that I can verify origin compliance
11. As a freight coordinator, I want to see extracted port of loading and port of discharge, so that I can verify routing
12. As a freight coordinator, I want to see extracted goods description, number of packages, and marks & numbers, so that I have complete declaration data
13. As a freight coordinator, I want the system to block submission when HS code is missing or malformed, so that customs won't reject the declaration
14. As a freight coordinator, I want the system to block submission when invoice value is zero or negative, so that financial data is valid
15. As a freight coordinator, I want the system to block submission when consignee TRN is missing, so that the declaration is complete
16. As a freight coordinator, I want the system to block submission when container number format is invalid, so that container tracking works
17. As a freight coordinator, I want the system to warn when gross weight is less than net weight, so that I can catch data entry errors
18. As a freight coordinator, I want the system to warn when country of origin is not in the allowed list, so that I can flag compliance risks
19. As a freight coordinator, I want the system to warn when invoice currency is not AED, so that I'm aware of currency conversion needs
20. As a freight coordinator, I want fields that couldn't be extracted to show as "Unable to extract" in yellow, so that I know what to fill manually
21. As a freight coordinator, I want a rendered HTML table showing all declaration fields, so that I can visually confirm the form before manual entry
22. As a freight coordinator, I want a JSON download of all extracted and validated data, so that I can import it into other systems
23. As a freight coordinator, I want to enter my OpenAI API key in the sidebar, so that the app works without storing secrets
24. As a freight coordinator, I want the app to work locally and deploy to Streamlit Cloud, so that I can demo it to colleagues
25. As a freight coordinator, I want the app to handle multiple container numbers in a single shipment, so that consolidated shipments work
26. As a freight coordinator, I want to see all uploaded documents listed with their auto-detected types, so that I can confirm classification before extraction
27. As a freight coordinator, I want a green "Ready to Submit" indicator when all block-level validations pass, so that I know the declaration is safe to submit
28. As a freight coordinator, I want a red "Issues Found" indicator when block-level validations fail, so that I know fixes are required
29. As a freight coordinator, I want yellow warnings visible even when the declaration is "ready," so that I can make informed decisions about edge cases
30. As a demo viewer, I want the case study written after the demo works, so that it references a working system

## Implementation Decisions

### Architecture
- **Single Streamlit app** — no separate FastAPI backend. Streamlit handles file uploads, OpenAI API calls, validation logic, and rendering. A backend adds deployment complexity for a 2-3 day demo with no benefit.

### Extraction Pipeline
- **LLM vision over OCR** — GPT-4o reads document images directly and returns structured JSON. No Tesseract, no Google Vision, no OCR preprocessing. Single API call does OCR + structuring. Cost: ~$0.005/doc, negligible for demo volume.
- **Extraction prompt** — sends the image with a system prompt listing all target fields (consignee, shipper, TRN, containers, weights, invoice, HS codes, origin, ports, description, packages, marks). Returns a JSON object with null for unextractable fields.
- **Fallback** — when auto-detection confidence is low, show document list with manual type assignment dropdowns.

### Validation Rules
Mixed severity model:
- **Block** (submission impossible): HS code missing/malformed, invoice value ≤ 0, TRN missing, container number format invalid
- **Warn** (flagged, allow submission): gross weight < net weight, country of origin not in allowed list, currency not AED

### HS Code Validation
Format check only: must be 6-10 digits, optionally with a dot after the 4th digit (e.g., `9403.20`). No reference lookup against a full HS database.

### Country of Origin
Hardcoded list of ~30 common trading countries (GCC states, India, China, US, EU majors, etc.) in a config constant. Not a compliance database.

### UI Output
- HTML table rendered in Streamlit showing all declaration fields with validation status colors (green/red/yellow)
- JSON download button for structured data export
- Green "Ready to Submit" / red "Issues Found" status indicator

### API Key
Streamlit sidebar text input. Session-only, never stored. Works on Streamlit Cloud with user-provided key.

### Mock Documents
Generic but realistic shipping documents (correct fields, realistic data) not pixel-matched to actual Dubai Trade forms. Content covers BL, invoice, and packing list with realistic freight data.

### Deployment
Start local (Streamlit localhost), deploy to Streamlit Cloud at end. No containerization needed.

## Testing Decisions

### Test Strategy
- Unit tests for validation rules (each rule tested independently)
- Unit tests for document type detection (auto-classify logic)
- Unit tests for HS code format validation
- Integration test for extraction pipeline (mock OpenAI response, verify JSON structure)
- Manual test with mock documents (end-to-end upload → extract → validate → render)

### What Makes a Good Test
- Test external behavior (does validation block when HS code is missing?) not implementation details
- Use realistic mock data (sample BL text, sample invoice text)
- Each validation rule gets its own test case

### Modules to Test
- `validation.py` — all block/warn rules
- `detection.py` — document type auto-detection
- `extraction.py` — prompt construction and response parsing

## Out of Scope

- Real Dubai Trade / Mirsal API integration
- Authentication or multi-user support
- Database persistence (session-only)
- PDF generation of filled forms
- OCR preprocessing pipeline
- HS code reference database lookup
- Real compliance rule engine
- Production-grade error handling for API rate limits
- Multi-language document support

## Further Notes

- The 3-day timeline is aggressive but achievable: Day 1 (mock docs + extraction), Day 2 (validation + UI), Day 3 (polish + deploy + case study)
- The case study is a deliverable but not a gate — write it after the demo works
- This is a prototype/demo, not production code. Architectural decisions favor speed over robustness.
