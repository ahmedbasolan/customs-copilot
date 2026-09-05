# 04: Document type detection

**What to build:** Auto-classify uploaded documents as BL, invoice, or packing list based on content. Provide manual fallback dropdowns when detection confidence is low.

**Blocked by:** 01-project-scaffold

**Status:** ready-for-agent

- [ ] Create detection module with a function that accepts document text/image and returns detected type (BL, invoice, packing list) with confidence score
- [ ] Use keyword/structural heuristics: BL has "Bill of Lading" header, invoice has totals/pricing, packing list has weight/package details
- [ ] When confidence is below threshold, return "unknown" to trigger manual fallback
- [ ] Create UI component: list of uploaded documents with auto-detected type and manual override dropdown
- [ ] Test detection against mock documents from Ticket 02
