# Customs Document Pre-Fill & Validation Copilot

A Streamlit app that extracts fields from shipping documents (BL, invoice, packing list) using GPT-4o vision, pre-fills a mock customs declaration form, and validates fields before submission.

## Language

**Bill of Lading (BL)**:
A document issued by a carrier acknowledging receipt of cargo for shipment. Contains shipper, consignee, container details, ports, and marks & numbers.
_Avoid_: B/L, shipping bill

**Packing List**:
A document listing the contents, weight, and packaging details of each shipment item. Source for goods description, package count, gross/net weight.
_Aavoid_: packing slip, contents list

**Invoice**:
A commercial document issued by the seller to the buyer stating the value of goods. Source for invoice value, currency, and HS codes.
_Avoid_: commercial invoice, proforma

**Consignee**:
The party receiving the goods. Identified by name and Tax Registration Number (TRN) for Dubai customs.
_Avoid_: receiver, recipient

**Shipper**:
The party sending the goods. Identified by name and country of origin.
_Avoid_: sender, exporter

**HS Code (Harmonized System Code)**:
A 6-10 digit numeric classification code for traded goods. Required on all customs declarations. Format: optionally dotted after 4th digit (e.g., `9403.20`).
_Aavoid_: tariff code, commodity code

**TRN (Tax Registration Number)**:
A 15-digit unique identifier for VAT-registered entities in UAE/GCC. Required on customs declarations for the consignee.
_Avoid_: VAT number, tax ID

**Container Number**:
A unique identifier for shipping containers. Format: 4 uppercase letters (owner code) + 7 digits (serial + check digit). Example: `MSCU1234567`.
_Avoid_: container ID, box number

**Gross Weight**:
Total weight of goods including packaging and container. Must be ≥ net weight.
_Avoid_: total weight

**Net Weight**:
Weight of goods only, excluding packaging. Must be ≤ gross weight.
_Avoid_: goods weight

**Country of Origin**:
The country where the goods were manufactured or produced. Must be from an allowed list for Dubai imports.
_Avoid_: origin country, made in

**Port of Loading (POL)**:
The port where goods are loaded onto the vessel. IATA/unlocode format (e.g., `CNSHA` for Shanghai).
_Avoid_: departure port, origin port

**Port of Discharge (POD)**:
The port where goods are unloaded from the vessel. For Dubai: `AEJEA` (Jebel Ali) or `AEDXB` (Dubai).
_Avoid_: destination port, arrival port

**Declaration Type**:
The category of customs declaration. For this copilot: always "Import".
_Aavoid_: decl type, entry type

**Validation Rule**:
A check applied to extracted fields before submission. Rules either **block** (must fix) or **warn** (should fix). Block rules prevent submission; warn rules flag issues but allow override.
_Avoid_: error, check

**Auto-Detect**:
System behavior that identifies document type (BL, invoice, packing list) from content without user input. Falls back to manual assignment when confidence is low.
_Avoid_: OCR classification, document detection
