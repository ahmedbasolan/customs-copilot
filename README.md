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

Open [http://localhost:8501](http://localhost:8501), enter your OpenAI API key in the sidebar, and upload a shipping document.

## Tech Stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit |
| Extraction | OpenAI GPT-4o (vision) — single API call does OCR + structuring |
| Validation | Python rules engine (block + warn severity) |
| Document parsing | Python `ast` module for function/class boundary detection |
| Deployment | Streamlit Cloud (no containers needed) |

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
4. Enter your OpenAI API key in the sidebar

## Validation Rules

| Rule | Severity | What It Checks |
|------|----------|---------------|
| HS Code missing/malformed | Block | Must be 6-10 digits, optionally dotted after 4th |
| Invoice value ≤ 0 | Block | Must be positive |
| TRN missing | Block | Required on all customs declarations |
| Container number format | Block | 4 uppercase + 7 digits |
| Gross < Net weight | Warn | Data entry error |
| Country of origin not allowed | Warn | Not in allowed list for Dubai imports |
| Currency not AED | Warn | Conversion may be needed |

**Block** rules prevent submission. **Warn** rules flag issues but allow override.

## Project Structure

```
customs-copilot/
├── app.py              # Streamlit UI + Gemini generation
├── detection.py        # Document type auto-detection
├── extraction.py       # Prompt construction + response parsing
├── validation.py       # Block/warn validation rules
├── mock_docs/          # Sample shipping documents for demos
├── docs/               # Agent instructions and ADRs
├── tests/              # Unit + integration tests
└── requirements.txt
```

## Limitations

- No real Dubai Trade / Mirsal 2 API integration (mock form only)
- No OCR preprocessing — relies entirely on GPT-4o vision
- No persistence (session-only)
- Single-user demo, not production-grade

## License

MIT
