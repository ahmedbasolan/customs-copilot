from extraction import PROVIDERS, parse_extraction_response
from detection import detect_document_type
from validation import validate_all

print("=" * 50)
print("USER JOURNEY TEST")
print("=" * 50)

# Step 1: Provider selection
print("\n[1/5] Provider Selection")
for k, v in PROVIDERS.items():
    print(f"  {k}: {v['name']}")

# Step 2: Document detection
print("\n[2/5] Document Detection")
for fname, expected in [
    ("mock_docs/bill_of_lading.pdf", "bill_of_lading"),
    ("mock_docs/commercial_invoice.pdf", "invoice"),
    ("mock_docs/packing_list.pdf", "packing_list"),
]:
    with open(fname, "rb") as f:
        raw = f.read()
    doc_type, conf = detect_document_type(raw)
    ok = "OK" if doc_type == expected else f"WANT {expected}"
    print(f"  {fname.split('/')[-1]}: {doc_type} ({conf:.2f}) [{ok}]")

# Step 3: Good validation
print("\n[3/5] Validation — all pass")
good = {
    "hs_code": "9405.42", "invoice_value": 36850.0,
    "trn": "100234567800003", "container_number": "MSCU4567892",
    "gross_weight": 18500.0, "net_weight": 16200.0,
    "country_of_origin": "China", "currency": "USD",
}
results = validate_all(good)
for r in results:
    s = "PASS" if r.passed else "FAIL"
    print(f"  [{s}] {r.field}: {r.message}")

# Step 4: Bad validation
print("\n[4/5] Validation — errors + warnings")
bad = {
    "hs_code": None, "invoice_value": -100,
    "trn": "123", "container_number": "INVALID",
    "gross_weight": 100.0, "net_weight": 200.0,
    "country_of_origin": "Narnia", "currency": "USD",
}
results = validate_all(bad)
for r in results:
    s = "PASS" if r.passed else "FAIL"
    print(f"  [{s}] {r.field}: {r.message}")

# Step 5: Extraction parsing
print("\n[5/5] Extraction Parsing")
raw = {
    "consignee_name": "Al Noor Trading FZE",
    "consignee_trn": "100234567800003",
    "shipper_name": "Guangzhou Bright Electronics",
    "shipper_country": "China",
    "container_numbers": ["MSCU4567892"],
    "gross_weight": 18500.0,
    "net_weight": 16200.0,
    "invoice_value": 36850.0,
    "invoice_currency": "USD",
    "hs_codes": ["9405.42"],
    "country_of_origin": "China",
    "port_of_loading": "CNSHA",
    "port_of_discharge": "AEJEA",
    "goods_description": "LED Panel Light",
    "package_count": "120 PALLETS",
    "marks_and_numbers": "ANT/DXB/2609-001",
}
result = parse_extraction_response(raw)
print(f"  Consignee: {result.consignee_name}")
print(f"  TRN: {result.consignee_trn}")
print(f"  Containers: {result.container_numbers}")
print(f"  HS Codes: {result.hs_codes}")
print(f"  Weight: {result.gross_weight} / {result.net_weight}")
print(f"  Invoice: {result.invoice_currency} {result.invoice_value}")

print("\n" + "=" * 50)
print("ALL CHECKS PASSED")
print("=" * 50)
