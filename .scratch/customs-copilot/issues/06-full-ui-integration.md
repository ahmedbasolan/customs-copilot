# 06: Full UI integration

**What to build:** Complete upload → detect → extract → validate → display workflow in Streamlit. Shows extracted fields with color-coded status, validation warnings, and a Ready/Issues status indicator.

**Blocked by:** 03-extraction-pipeline, 04-document-type-detection, 05-validation-rules-engine

**Status:** ready-for-agent

- [ ] Streamlit file uploader accepting multiple PDFs/images
- [ ] Display uploaded documents with auto-detected type and manual override dropdowns
- [ ] "Extract" button that runs extraction pipeline on all documents
- [ ] Display extracted fields in a structured layout with color coding: green (extracted OK), yellow (unable to extract), red (validation block), orange (validation warning)
- [ ] Run validation rules on extracted data
- [ ] Show green "Ready to Submit" when all block-level validations pass
- [ ] Show red "Issues Found" when any block-level validation fails
- [ ] Show yellow warnings even when status is green
- [ ] End-to-end test with mock documents
