# 05: Validation rules engine

**What to build:** All validation rules as standalone pure functions. Each rule returns pass/block/warn status with a message. No UI dependency — pure logic that can be tested independently.

**Blocked by:** None (can start immediately)

**Status:** ready-for-agent

- [ ] Create `validation.py` module with rule functions
- [ ] Block rules (submission impossible): HS code missing/malformed (6-10 digits, optional dot after 4th), invoice value ≤ 0, TRN missing, container number format invalid (4 letters + 7 digits)
- [ ] Warn rules (flagged, allow submission): gross weight < net weight, country of origin not in allowed list (~30 common trading countries), invoice currency not AED
- [ ] Each rule takes extracted JSON and returns: field name, severity (block/warn), message, passed (bool)
- [ ] Create a runner function that applies all rules and returns a list of results
- [ ] Unit test every rule with passing and failing cases
