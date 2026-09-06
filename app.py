import json
import streamlit as st
from extraction import extract_from_image, ExtractionResult, PROVIDERS
from detection import detect_document_type
from validation import validate_all, ValidationResult

st.set_page_config(
    page_title="Customs Copilot",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .stApp { background: #f8fafc; }
    .main .block-container { padding-top: 2rem; max-width: 1200px; }

    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 100%);
        color: white;
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
    .hero h1 { color: white; margin-bottom: 0.3rem; font-size: 1.8rem; }
    .hero p { color: #94a3b8; margin: 0; font-size: 0.95rem; }

    .doc-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 1rem;
        transition: border-color 0.2s;
    }
    .doc-card:hover { border-color: #3b82f6; }
    .doc-icon { font-size: 2rem; }
    .doc-info { flex: 1; }
    .doc-name { font-weight: 600; color: #1e293b; }
    .doc-meta { font-size: 0.8rem; color: #64748b; }

    .field-card {
        background: white;
        border-radius: 10px;
        padding: 0.9rem 1.1rem;
        margin-bottom: 0.5rem;
        border-left: 4px solid #22c55e;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    }
    .field-card.warn { border-left-color: #f59e0b; background: #fffbeb; }
    .field-card.error { border-left-color: #ef4444; background: #fef2f2; }
    .field-card.missing { border-left-color: #94a3b8; background: #f1f5f9; }
    .field-label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.05em; color: #64748b; margin-bottom: 0.2rem; }
    .field-value { font-size: 1rem; font-weight: 600; color: #1e293b; }
    .field-value.missing { color: #94a3b8; font-style: italic; }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.6rem 1.2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 0.9rem;
    }
    .status-ready { background: #dcfce7; color: #166534; }
    .status-issues { background: #fee2e2; color: #991b1b; }

    .section-header {
        font-size: 0.85rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.4rem;
        border-bottom: 1px solid #e2e8f0;
    }

    .validation-item {
        display: flex;
        align-items: flex-start;
        gap: 0.6rem;
        padding: 0.5rem 0;
        font-size: 0.9rem;
    }
    .validation-icon { font-size: 1rem; margin-top: 0.1rem; }
    .validation-text { color: #334155; }
    .validation-field { font-weight: 600; }

    .stTabs [data-baseweb="tab-list"] { gap: 0; }
    .stTabs [data-baseweb="tab"] {
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        border-bottom: 3px solid transparent;
    }
    .stTabs [aria-selected="true"] { border-bottom-color: #3b82f6; color: #1e293b; }

    div[data-testid="stSidebar"] { background: #0f172a; }
    div[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0; }
    div[data-testid="stSidebar"] label { color: #94a3b8 !important; }
</style>
""", unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    provider = st.selectbox(
        "AI Provider",
        options=list(PROVIDERS.keys()),
        format_func=lambda x: PROVIDERS[x]["name"],
        key="provider",
    )

    provider_info = PROVIDERS[provider]

    if "custom_model" not in st.session_state:
        st.session_state.custom_model = provider_info["default_model"]
    if "current_provider" not in st.session_state:
        st.session_state.current_provider = provider
    if st.session_state.current_provider != provider:
        st.session_state.custom_model = provider_info["default_model"]
        st.session_state.current_provider = provider

    model = st.text_input(
        "Model",
        value=st.session_state.custom_model,
        key="custom_model",
        placeholder="Type any model name",
        help="Enter any model — the presets below are suggestions.",
    )

    st.markdown(
        f'<div style="margin-top:-0.5rem; margin-bottom:0.5rem;">'
        f'<span style="font-size:0.75rem; color:#64748b;">Quick pick:</span></div>',
        unsafe_allow_html=True,
    )
    cols = st.columns(len(provider_info["models"]))
    for i, m in enumerate(provider_info["models"]):
        with cols[i]:
            if st.button(m, key=f"preset_{m}", use_container_width=True):
                st.session_state.custom_model = m
                st.rerun()

    base_url = None
    if provider_info["needs_base_url"]:
        base_url = st.text_input(
            "Ollama URL",
            value=provider_info["default_base_url"],
            key="base_url",
        )

    api_key = st.text_input(
        "API Key",
        type="password",
        key="api_key",
        help="Your key is session-only, never stored or transmitted elsewhere.",
        placeholder="sk-..." if provider == "openai" else "Enter your API key",
    )

    st.markdown("---")
    st.markdown(
        f"**Provider:** {provider_info['name']}  \n"
        f"**Model:** `{model}`"
    )

st.markdown("""
<div class="hero">
    <h1>🚢 Customs Document Copilot</h1>
    <p>Upload shipping documents — extract, validate, and pre-fill customs declarations instantly.</p>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div style="background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 2rem; text-align: center; margin: 2rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">🔑</div>
        <h3 style="margin: 0 0 0.5rem 0; color: #1e293b;">Enter your API key to begin</h3>
        <p style="color: #64748b; margin: 0;">Add your API key in the sidebar to start extracting document fields.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

uploaded_files = st.file_uploader(
    "Upload shipping documents",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    label_visibility="collapsed",
    help="Upload Bill of Lading, Invoice, and/or Packing List",
)

if not uploaded_files:
    st.markdown("""
    <div style="background: white; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 3rem; text-align: center; margin: 1rem 0;">
        <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
        <h3 style="margin: 0 0 0.5rem 0; color: #1e293b;">Drop your documents here</h3>
        <p style="color: #64748b; margin: 0;">Supports PDF, PNG, JPG — Bill of Lading, Invoices, Packing Lists</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

DOC_TYPE_LABELS = {
    "bill_of_lading": "🚢 Bill of Lading",
    "invoice": "💰 Commercial Invoice",
    "packing_list": "📦 Packing List",
    "unknown": "❓ Unknown — Select Type",
}

DOC_TYPE_ICONS = {
    "bill_of_lading": "🚢",
    "invoice": "💰",
    "packing_list": "📦",
    "unknown": "❓",
}

if "extracted" not in st.session_state:
    st.session_state.extracted = {}
if "doc_types" not in st.session_state:
    st.session_state.doc_types = {}

st.markdown('<div class="section-header">Uploaded Documents</div>', unsafe_allow_html=True)

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

    icon = DOC_TYPE_ICONS.get(st.session_state.doc_types[file_key], "📄")
    col1, col2 = st.columns([5, 2])
    with col1:
        st.markdown(f"""
        <div class="doc-card">
            <div class="doc-icon">{icon}</div>
            <div class="doc-info">
                <div class="doc-name">{file.name}</div>
                <div class="doc-meta">{file.type} · {(file.size / 1024):.1f} KB</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        selected_type = st.selectbox(
            "Type",
            options=list(DOC_TYPE_LABELS.keys()),
            format_func=lambda x: DOC_TYPE_LABELS[x],
            index=list(DOC_TYPE_LABELS.keys()).index(st.session_state.doc_types[file_key]),
            key=f"type_{file_key}",
            label_visibility="collapsed",
        )
        doc_selections[file_key] = selected_type

st.session_state.doc_types.update(doc_selections)

st.markdown("")
col_btn, col_status = st.columns([1, 3])
with col_btn:
    extract_clicked = st.button("🔍 Extract Fields", type="primary", use_container_width=True)

if extract_clicked:
    st.session_state.extracted = {}
    progress = st.progress(0, text="Extracting fields...")

    for i, file in enumerate(uploaded_files):
        file_key = f"{file.name}_{i}"
        progress.progress(
            i / len(uploaded_files),
            text=f"Processing {file.name}...",
        )

        raw_bytes = file.read()
        file.seek(0)

        try:
            result = extract_from_image(
                provider=provider,
                api_key=api_key,
                model=model,
                image_bytes=raw_bytes,
                base_url=base_url,
            )
            st.session_state.extracted[file_key] = {
                "filename": file.name,
                "doc_type": st.session_state.doc_types[file_key],
                "result": result,
            }
        except Exception as e:
            st.error(f"Extraction failed for {file.name}: {e}")

    progress.progress(1.0, text="Done!")
    st.rerun()

if st.session_state.extracted:
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
            merged.container_numbers = list(set(merged.container_numbers + r.container_numbers))
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
        st.markdown('<div class="status-badge status-issues">🔴 Issues Found — Fix before submission</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-ready">🟢 Ready to Submit</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-header">Extracted Fields</div>', unsafe_allow_html=True)

    def _get_field_class(field_name: str, value, results: list[ValidationResult]) -> str:
        if value is None:
            return "missing"
        for r in results:
            if r.field == field_name and not r.passed:
                return "error" if r.severity == "block" else "warn"
        return ""

    def _render_field_card(label: str, value, field_name: str, results: list[ValidationResult]):
        cls = _get_field_class(field_name, value, results)
        display = value if value is not None else "Not extracted"
        value_cls = "missing" if value is None else ""
        st.markdown(f"""
        <div class="field-card {cls}">
            <div class="field-label">{label}</div>
            <div class="field-value {value_cls}">{display}</div>
        </div>
        """, unsafe_allow_html=True)

    tab_form, tab_raw = st.tabs(["📋 Declaration Form", "📄 Raw Data"])

    with tab_form:
        c1, c2 = st.columns(2)

        with c1:
            st.markdown('<div class="section-header">Consignee</div>', unsafe_allow_html=True)
            _render_field_card("Name", merged.consignee_name, "consignee_name", results)
            _render_field_card("TRN", merged.consignee_trn, "trn", results)

            st.markdown('<div class="section-header">Shipper</div>', unsafe_allow_html=True)
            _render_field_card("Name", merged.shipper_name, "shipper_name", results)
            _render_field_card("Country", merged.shipper_country, "shipper_country", results)

            st.markdown('<div class="section-header">Container</div>', unsafe_allow_html=True)
            containers = ", ".join(merged.container_numbers) if merged.container_numbers else None
            _render_field_card("Container Number(s)", containers, "container_number", results)

        with c2:
            st.markdown('<div class="section-header">Weight</div>', unsafe_allow_html=True)
            gw = f"{merged.gross_weight:,.2f} KGS" if merged.gross_weight else None
            nw = f"{merged.net_weight:,.2f} KGS" if merged.net_weight else None
            _render_field_card("Gross Weight", gw, "gross_weight", results)
            _render_field_card("Net Weight", nw, "net_weight", results)

            st.markdown('<div class="section-header">Invoice</div>', unsafe_allow_html=True)
            inv = f"{merged.invoice_currency} {merged.invoice_value:,.2f}" if merged.invoice_value else None
            hs = ", ".join(merged.hs_codes) if merged.hs_codes else None
            _render_field_card("Value", inv, "invoice_value", results)
            _render_field_card("HS Code(s)", hs, "hs_code", results)

            st.markdown('<div class="section-header">Origin & Routing</div>', unsafe_allow_html=True)
            _render_field_card("Country of Origin", merged.country_of_origin, "country_of_origin", results)
            _render_field_card("Port of Loading", merged.port_of_loading, "port_of_loading", results)
            _render_field_card("Port of Discharge", merged.port_of_discharge, "port_of_discharge", results)

        st.markdown('<div class="section-header">Additional Details</div>', unsafe_allow_html=True)
        c3, c4, c5 = st.columns(3)
        with c3:
            _render_field_card("Goods Description", merged.goods_description, "goods_description", results)
        with c4:
            _render_field_card("Package Count", merged.package_count, "package_count", results)
        with c5:
            _render_field_card("Marks & Numbers", merged.marks_and_numbers, "marks_and_numbers", results)

    with tab_raw:
        st.markdown('<div class="section-header">Validation Rules</div>', unsafe_allow_html=True)
        for r in results:
            icon = "✅" if r.passed else ("🔴" if r.severity == "block" else "🟡")
            st.markdown(f"""
            <div class="validation-item">
                <span class="validation-icon">{icon}</span>
                <span class="validation-text"><span class="validation-field">{r.field}</span> — {r.message}</span>
            </div>
            """, unsafe_allow_html=True)

        st.markdown('<div class="section-header">JSON Export</div>', unsafe_allow_html=True)
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
        }
        st.code(json.dumps(export_data, indent=2, ensure_ascii=False), language="json")

        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(export_data, indent=2, ensure_ascii=False),
            file_name="customs_declaration.json",
            mime="application/json",
            use_container_width=True,
        )
