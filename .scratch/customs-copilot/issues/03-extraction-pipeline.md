# 03: Extraction pipeline

**What to build:** GPT-4o vision extraction — send a document image to OpenAI and get back structured JSON with all target fields. Returns null for fields that couldn't be extracted.

**Blocked by:** 01-project-scaffold

**Status:** ready-for-agent

- [ ] Create extraction module with a function that accepts an image (bytes/PIL) and returns structured JSON
- [ ] Design the extraction prompt listing all target fields: consignee+TRN, shipper+country, container numbers, gross/net weight, invoice value+currency, HS codes, country of origin, ports, goods description, package count, marks & numbers
- [ ] Parse GPT-4o response into a Pydantic model with optional fields (null for unextractable)
- [ ] Handle API errors gracefully (rate limits, invalid key, network errors)
- [ ] Test extraction against mock documents from Ticket 02
