# Case Study: Customs Document Pre-Fill & Validation Copilot

**Status: working prototype, tested on three synthetic documents. No real declarations
have been processed and extraction accuracy has not been measured.**

## The Problem

Freight coordinators read bills of lading, commercial invoices and packing lists, then
re-type the fields into the Dubai Trade / Mirsal customs declaration system. One
declaration draws on 16 fields spread across the three documents. A missing or
malformed HS code, TRN or container number gets the declaration rejected and means a
manual fix and resubmission.

## The Solution

A Streamlit copilot that reads the documents and checks the result before anything is
typed into the customs system:

1. **Upload**: BL, invoice and packing list, as PDF or image, several at once
2. **Auto-detect**: identifies each document type from its text; manual fallback when it can't
3. **Extract**: a vision LLM (GPT-4o by default; Claude, Gemini or a local Ollama model
   also work) reads each document and returns 16 fields as JSON. PDFs are rendered to
   PNG pages first, because vision endpoints don't accept raw PDF bytes.
4. **Validate**: a rules engine flags errors before submission
   - **Block** (must fix): missing or malformed HS code, missing or invalid TRN, zero or
     negative invoice value, bad container number format
   - **Warn** (should fix): gross weight below net weight, non-AED currency, origin
     country outside the app's list
5. **Export**: JSON download, or copy from the rendered declaration form

## What Has Been Verified

87 automated tests, all passing:

| Area | Tests | What they check |
|------|------:|-----------------|
| Validation | 53 | Every block and warn rule, including normalisation of the formats documents really use (`9403.20.00`, `mscu4567892`, TRNs with spaces, "UAE" vs "United Arab Emirates") |
| Detection | 15 | Document-type detection on the three mock PDFs and on text; a corrupt file, a PDF with no text layer and a missing pymupdf are each reported instead of returning "unknown" |
| Extraction | 19 | PDF-to-PNG rendering of every mock document; the request payload sent to OpenAI and Anthropic, built from the real mock PDFs; parsing of full, partial and empty model responses |

## What Has Not Been Measured

- **Extraction accuracy.** No provider's output has been scored against labelled
  documents. The extraction tests check what is sent to the model and how its reply is
  parsed, not whether the reply is right.
- **Time saved, error rates or rejection rates.** The app has not been used on real
  declarations, so there is no before-and-after to report.
- **Real documents.** The three demo documents in `mock_docs/` are synthetic, generated
  by `generate_mock_docs.py`.

The next step that would turn this into evidence is a labelled set of real (redacted)
documents and a field-level accuracy score per provider.

## Validation Rules

**Blocking (prevents submission):**
- HS code missing or malformed (6-10 digits after removing dots, spaces and hyphens)
- Invoice value zero or negative
- Consignee TRN missing or not 15 digits
- Container number not 4 letters + 7 digits

**Warning (flagged, allows override):**
- Gross weight below net weight
- Country of origin not in the app's hardcoded list of 65 common trading partners (a
  sanity check, not an official import rule)
- Invoice currency not AED

## Technical Architecture

- **Frontend:** Streamlit (Python)
- **Extraction:** one vision-LLM call per document. Cost is roughly $0.005 per document
  with GPT-4o (an estimate from token pricing, not measured).
- **Detection:** keyword scoring over text extracted with pymupdf
- **Validation:** pure Python rules engine with value normalisation
- **Export:** JSON download + HTML table preview

### Auto-detect failure modes

Auto-detect needs a text-based PDF. Each way that can fail is reported distinctly
rather than collapsing into "unknown", so a coordinator is never left guessing why a
document was not classified:

| Cause | What the user sees |
|---|---|
| `pymupdf` not installed | App-level warning with the install command; manual type selection still works |
| Corrupt / not really a PDF | Per-file note that the file could not be opened |
| Password-protected PDF | Per-file note to remove the password |
| Scanned image with no text layer | Per-file note that auto-detect needs a text-based PDF |

## Known Limitations

- Extraction accuracy is unmeasured (see above).
- PDFs are rendered up to 10 pages at 200 dpi; longer documents are truncated.
- Auto-detect only reads text-based PDFs. Scanned PDFs and JPG/PNG uploads always need
  the document type set manually, although extraction itself works on them.
- Uploaded file names are inserted into the page's HTML without escaping, and the
  weight check reports a pass when it cannot run (missing or invalid weights).
- The password-protected PDF message has no test.
- No hosted demo: it runs locally.
- No Dubai Trade / Mirsal integration: the declaration form is a mock.

## What's Next

- Measure extraction accuracy per provider on labelled documents
- Fix the two rendering issues above
- HS code lookup against the official tariff
- Arabic documents
- Dubai Trade API integration for direct submission

## Demo

Run locally:
```bash
pip install -r requirements.txt
streamlit run app.py
```

Pick a provider and enter its API key in the sidebar (Ollama runs locally and needs no
key), upload the documents in `mock_docs/`, and click "Extract Fields".
