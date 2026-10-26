# Customs Copilot

A Streamlit app that pre-fills Dubai customs declarations from shipping documents (Bill of Lading, Invoice, Packing List) using GPT-4o vision — then validates every field before submission.

## What It Does

1. **Upload** — PDFs/images of BL, Invoice, or Packing List
2. **Auto-detect** — Identifies document type from content (with manual fallback)
3. **Extract** — GPT-4o reads the image and returns structured JSON (no separate OCR step)
4. **Pre-fill** — Populates a mock Dubai Trade / Mirsal 2 customs declaration form
5. **Validate** — Runs block/warn rules and highlights issues before submission
6. **Export** — JSON download of extracted data + rendered HTML preview

## Demo

```
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501), pick a provider and enter its API key in the sidebar, and upload a shipping document.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit |
| Extraction | Vision LLM — GPT-4o by default; Claude, Gemini, or a local Ollama model (llava) also supported. A single call does OCR + structuring |
| Validation | Python rules engine (block + warn severity) |
| Document detection | PyMuPDF text extraction + keyword scoring to identify BL / Invoice / Packing List |
| Deployment | Runs locally with `streamlit run`; no hosted demo |

## Getting Started

1. Clone the repo:
   ```bash
   git clone https://github.com/ahmedbasolan/customs-copilot.git
   cd customs-copilot
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run:
   ```bash
   streamlit run app.py
   ```
4. Pick a provider (OpenAI, Anthropic, Google, or Ollama) and enter its API key in the sidebar

## Validation Rules

| Rule | Severity | What It Checks |
|------|----------|---------------|
| HS Code missing/malformed | Block | 6-10 digits once dots, spaces and hyphens are removed |
| Invoice value ≤ 0 | Block | Must be positive |
| TRN missing or invalid | Block | Must be 15 digits |
| Container number format | Block | 4 uppercase + 7 digits |
| Gross < Net weight | Warn | Data entry error |
| Country of origin not in list | Warn | Outside the app's hardcoded list of 65 common trading partners (a sanity check, not an official import rule) |
| Currency not AED | Warn | Conversion may be needed |

**Block** rules prevent submission. **Warn** rules flag issues but allow override.

## Project Structure

```
customs-copilot/
├── app.py              # Streamlit UI + provider settings
├── detection.py        # Document type auto-detection
├── extraction.py       # Prompt construction, provider calls, response parsing
├── validation.py       # Block/warn validation rules
├── generate_mock_docs.py  # Builds the sample PDFs in mock_docs/
├── mock_docs/          # Sample shipping documents for demos
├── docs/adr/           # Architecture decision records
├── test_*.py           # 87 unit tests (run with `pytest`)
└── requirements.txt
```

## Limitations

- No real Dubai Trade / Mirsal 2 API integration (mock form only)
- Extraction accuracy has not been measured: the tests cover rendering, request payloads, parsing and validation, not whether a model reads a document correctly. See [CASE_STUDY.md](CASE_STUDY.md)
- Tested only on three synthetic documents (`mock_docs/`)
- No OCR preprocessing: relies on a vision LLM to read documents
- No persistence (session-only)
- Single-user demo, not production-grade

## License

MIT
