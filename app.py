import streamlit as st
from extraction import extract_from_image, ExtractionResult
from detection import detect_document_type
from validation import validate_all, ValidationResult

st.set_page_config(
    page_title="Customs Copilot",
    page_icon="🚢",
    layout="wide",
)

st.sidebar.header("Configuration")
api_key = st.sidebar.text_input(
    "OpenAI API Key",
    type="password",
    help="Your key is session-only and never stored.",
)

st.title("🚢 Customs Document Pre-Fill & Validation Copilot")
st.markdown(
    "Upload shipping documents (Bill of Lading, Invoice, Packing List) and let AI "
    "extract fields, pre-fill a customs declaration form, and validate before submission."
)

if not api_key:
    st.info("Enter your OpenAI API key in the sidebar to get started.")
    st.stop()

uploaded_files = st.file_uploader(
    "Upload documents",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    help="Upload Bill of Lading, Invoice, and/or Packing List",
)

if not uploaded_files:
    st.info("Upload documents to begin extraction.")
    st.stop()

DOC_TYPE_LABELS = {
    "bill_of_lading": "Bill of Lading",
    "invoice": "Commercial Invoice",
    "packing_list": "Packing List",
    "unknown": "Unknown - Select Type",
}

if "extracted" not in st.session_state:
    st.session_state.extracted = {}
if "doc_types" not in st.session_state:
    st.session_state.doc_types = {}

st.subheader("📄 Uploaded Documents")

doc_selections = {}
for i, file in enumerate(uploaded_files):
    file_key = f"{file.name}_{i}"

    if file_key not in st.session_state.doc_types:
        raw_bytes = file.read()
        file.seek(0)

        try:
            text_chunk = raw_bytes[:4000].decode("utf-8", errors="ignore")
        except Exception:
            text_chunk = ""

        detected_type, confidence = detect_document_type(text_chunk)
        st.session_state.doc_types[file_key] = detected_type

    col1, col2 = st.columns([3, 1])
    with col1:
        st.write(f"**{file.name}** ({file.type})")
    with col2:
        selected_type = st.selectbox(
            "Document type",
            options=list(DOC_TYPE_LABELS.keys()),
            format_func=lambda x: DOC_TYPE_LABELS[x],
            index=list(DOC_TYPE_LABELS.keys()).index(st.session_state.doc_types[file_key]),
            key=f"type_{file_key}",
        )
        doc_selections[file_key] = selected_type

st.session_state.doc_types.update(doc_selections)

if st.button("🔍 Extract Fields", type="primary"):
    st.session_state.extracted = {}
    progress = st.progress(0, text="Extracting fields...")

    for i, file in enumerate(uploaded_files):
        file_key = f"{file.name}_{i}"
        progress.progress(
            (i) / len(uploaded_files),
            text=f"Extracting from {file.name}...",
        )

        raw_bytes = file.read()
        file.seek(0)

        try:
            result = extract_from_image(api_key, raw_bytes)
            st.session_state.extracted[file_key] = {
                "filename": file.name,
                "doc_type": st.session_state.doc_types[file_key],
                "result": result,
            }
        except Exception as e:
            st.error(f"Extraction failed for {file.name}: {e}")

    progress.progress(1.0, text="Extraction complete!")
    st.rerun()

if st.session_state.extracted:
    st.subheader("📋 Extracted Declaration Fields")

    merged = ExtractionResult()
    for file_key, data in st.session_state.extracted.items():
        r = data["result"]
        if r.consignee_name:
            merged.consignee_name = r.consignee_name
        if r.consignee_trn:
            merged.consignee_trn = r.consignee_trn
        if r.shipper_name:
            merged.shipper_name = r.shipper_name
        if r.shipper_country:
            merged.shipper_country = r.shipper_country
        if r.container_numbers:
            merged.container_numbers = list(
                set(merged.container_numbers + r.container_numbers)
            )
        if r.gross_weight is not None:
            merged.gross_weight = r.gross_weight
        if r.net_weight is not None:
            merged.net_weight = r.net_weight
        if r.invoice_value is not None:
            merged.invoice_value = r.invoice_value
        if r.invoice_currency:
            merged.invoice_currency = r.invoice_currency
        if r.hs_codes:
            merged.hs_codes = list(set(merged.hs_codes + r.hs_codes))
        if r.country_of_origin:
            merged.country_of_origin = r.country_of_origin
        if r.port_of_loading:
            merged.port_of_loading = r.port_of_loading
        if r.port_of_discharge:
            merged.port_of_discharge = r.port_of_discharge
        if r.goods_description:
            merged.goods_description = r.goods_description
        if r.package_count:
            merged.package_count = r.package_count
        if r.marks_and_numbers:
            merged.marks_and_numbers = r.marks_and_numbers

    validation_data = {
        "hs_code": merged.hs_codes[0] if merged.hs_codes else None,
        "invoice_value": merged.invoice_value,
        "trn": merged.consignee_trn,
        "container_number": merged.container_numbers[0] if merged.container_numbers else None,
        "gross_weight": merged.gross_weight,
        "net_weight": merged.net_weight,
        "country_of_origin": merged.country_of_origin,
        "currency": merged.invoice_currency,
    }
    results = validate_all(validation_data)

    has_blocks = any(r.severity == "block" and not r.passed for r in results)

    if has_blocks:
        st.error("🔴 **Issues Found** — Fix blocking errors before submission")
    else:
        st.success("🟢 **Ready to Submit** — All critical validations pass")

    st.markdown("---")

    def _field_status(field_name: str, results: list[ValidationResult]) -> str:
        for r in results:
            if r.field == field_name and not r.passed:
                return "block" if r.severity == "block" else "warn"
        return "ok"

    def _color(status: str) -> str:
        return {"ok": "green", "warn": "orange", "block": "red"}.get(status, "gray")

    def _render_field(label: str, value, field_name: str, results: list[ValidationResult]):
        status = _field_status(field_name, results)
        color = _color(status)
        display_value = value if value is not None else "Unable to extract"
        if value is None:
            status = "warn"
            color = "orange"
        st.markdown(f"**{label}:** :{color}[{display_value}]")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("### Consignee")
        _render_field("Name", merged.consignee_name, "consignee_name", results)
        _render_field("TRN", merged.consignee_trn, "trn", results)

        st.markdown("### Shipper")
        st.markdown(f"**Name:** {merged.shipper_name or 'Unable to extract'}")
        st.markdown(f"**Country:** {merged.shipper_country or 'Unable to extract'}")

        st.markdown("### Containers")
        containers = ", ".join(merged.container_numbers) if merged.container_numbers else "Unable to extract"
        _render_field("Container Number(s)", containers, "container_number", results)

    with col_right:
        st.markdown("### Weights")
        _render_field("Gross Weight", f"{merged.gross_weight:,.2f} KGS" if merged.gross_weight else None, "gross_weight", results)
        _render_field("Net Weight", f"{merged.net_weight:,.2f} KGS" if merged.net_weight else None, "net_weight", results)

        st.markdown("### Invoice")
        _render_field("Value", f"{merged.invoice_currency} {merged.invoice_value:,.2f}" if merged.invoice_value else None, "invoice_value", results)
        _render_field("HS Code(s)", ", ".join(merged.hs_codes) if merged.hs_codes else None, "hs_code", results)

        st.markdown("### Origin & Routing")
        _render_field("Country of Origin", merged.country_of_origin, "country_of_origin", results)
        st.markdown(f"**Port of Loading:** {merged.port_of_loading or 'Unable to extract'}")
        st.markdown(f"**Port of Discharge:** {merged.port_of_discharge or 'Unable to extract'}")

    st.markdown("---")
    st.markdown("### Additional Details")
    st.markdown(f"**Goods Description:** {merged.goods_description or 'Unable to extract'}")
    st.markdown(f"**Package Count:** {merged.package_count or 'Unable to extract'}")
    st.markdown(f"**Marks & Numbers:** {merged.marks_and_numbers or 'Unable to extract'}")

    st.markdown("---")
    st.markdown("### Validation Results")
    for r in results:
        icon = "✅" if r.passed else ("🔴" if r.severity == "block" else "🟡")
        st.markdown(f"{icon} **{r.field}:** {r.message}")

    st.markdown("---")
    st.subheader("📤 Export")

    export_data = {
        "consignee_name": merged.consignee_name,
        "consignee_trn": merged.consignee_trn,
        "shipper_name": merged.shipper_name,
        "shipper_country": merged.shipper_country,
        "container_numbers": merged.container_numbers,
        "gross_weight": merged.gross_weight,
        "net_weight": merged.net_weight,
        "invoice_value": merged.invoice_value,
        "invoice_currency": merged.invoice_currency,
        "hs_codes": merged.hs_codes,
        "country_of_origin": merged.country_of_origin,
        "port_of_loading": merged.port_of_loading,
        "port_of_discharge": merged.port_of_discharge,
        "goods_description": merged.goods_description,
        "package_count": merged.package_count,
        "marks_and_numbers": merged.marks_and_numbers,
        "validation": [
            {"field": r.field, "severity": r.severity, "message": r.message, "passed": r.passed}
            for r in results
        ],
    }

    import json

    json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
    st.download_button(
        label="📥 Download JSON",
        data=json_str,
        file_name="customs_declaration.json",
        mime="application/json",
    )

    st.markdown("---")
    st.subheader("📊 Declaration Form Preview")

    def _status_color(field_name: str) -> str:
        for r in results:
            if r.field == field_name and not r.passed:
                return "#ffcccc" if r.severity == "block" else "#fff3cd"
        return "#d4edda"

    fields = [
        ("Consignee Name", merged.consignee_name, "consignee_name"),
        ("Consignee TRN", merged.consignee_trn, "trn"),
        ("Shipper Name", merged.shipper_name, None),
        ("Shipper Country", merged.shipper_country, None),
        ("Container Number(s)", ", ".join(merged.container_numbers) if merged.container_numbers else None, "container_number"),
        ("Gross Weight (KGS)", f"{merged.gross_weight:,.2f}" if merged.gross_weight else None, "gross_weight"),
        ("Net Weight (KGS)", f"{merged.net_weight:,.2f}" if merged.net_weight else None, "net_weight"),
        ("Invoice Value", f"{merged.invoice_currency} {merged.invoice_value:,.2f}" if merged.invoice_value else None, "invoice_value"),
        ("HS Code(s)", ", ".join(merged.hs_codes) if merged.hs_codes else None, "hs_code"),
        ("Country of Origin", merged.country_of_origin, "country_of_origin"),
        ("Port of Loading", merged.port_of_loading, None),
        ("Port of Discharge", merged.port_of_discharge, None),
        ("Goods Description", merged.goods_description, None),
        ("Package Count", merged.package_count, None),
        ("Marks & Numbers", merged.marks_and_numbers, None),
    ]

    html = '<table style="width:100%; border-collapse: collapse;">'
    html += '<tr style="background-color: #f8f9fa;"><th style="text-align:left; padding:8px; border:1px solid #ddd;">Field</th><th style="text-align:left; padding:8px; border:1px solid #ddd;">Value</th></tr>'
    for label, value, field_name in fields:
        bg = _status_color(field_name) if field_name else "#ffffff"
        display = value if value else "—"
        html += f'<tr style="background-color: {bg};"><td style="padding:8px; border:1px solid #ddd; font-weight:bold;">{label}</td><td style="padding:8px; border:1px solid #ddd;">{display}</td></tr>'
    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)
