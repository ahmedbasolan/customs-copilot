# 02: Mock documents

**What to build:** 3-4 realistic mock shipping documents as PDFs — a Bill of Lading, a commercial invoice, and a packing list. Each should contain realistic freight data with all fields the extraction pipeline needs to target.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Create mock Bill of Lading PDF with: shipper, consignee+TRN, container numbers, ports (POL/POD), gross/net weight, marks & numbers
- [ ] Create mock commercial invoice PDF with: shipper, consignee, invoice value+currency, HS codes (line-level), country of origin, goods description
- [ ] Create mock packing list PDF with: goods description, package count, gross/net weight, marks & numbers
- [ ] Optionally create a combined/multi-page document for batch upload testing
- [ ] Use realistic but generic data (not pixel-matched to actual Dubai Trade forms)
- [ ] Store PDFs in `mock_docs/` directory
