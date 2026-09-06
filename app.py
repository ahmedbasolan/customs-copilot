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
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    .stApp { font-family: 'Inter', sans-serif; background: #f8fafc; }
    .main .block-container { padding-top: 2rem; padding-bottom: 2rem; max-width: 1200px; }

    .hero {
        background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f4c75 100%);
        color: white; padding: 2.5rem 3rem; border-radius: 16px;
        margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(15,23,42,0.2);
        position: relative; overflow: hidden;
    }
    .hero::before {
        content: ''; position: absolute; top: -50%; right: -10%;
        width: 400px; height: 400px; border-radius: 50%;
        background: radial-gradient(circle, rgba(59,130,246,0.15) 0%, transparent 70%);
    }
    .hero h1 { color: white; margin-bottom: 0.4rem; font-size: 2rem; font-weight: 700; position: relative; }
    .hero p { color: #94a3b8; margin: 0; font-size: 1rem; position: relative; }

    .steps-row {
        display: flex; gap: 1rem; margin-bottom: 2rem;
    }
    .step-card {
        flex: 1; background: white; border-radius: 12px; padding: 1.2rem;
        border: 1px solid #e2e8f0; position: relative; text-align: center;
    }
    .step-card.active { border-color: #3b82f6; background: #eff6ff; }
    .step-num {
        width: 32px; height: 32px; border-radius: 50%; background: #e2e8f0;
        display: inline-flex; align-items: center; justify-content: center;
        font-weight: 700; font-size: 0.85rem; color: #64748b; margin-bottom: 0.6rem;
    }
    .step-card.active .step-num { background: #3b82f6; color: white; }
    .step-title { font-weight: 600; font-size: 0.9rem; color: #1e293b; }
    .step-desc { font-size: 0.75rem; color: #64748b; margin-top: 0.2rem; }

    .stat-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
    .stat-card {
        flex: 1; background: white; border-radius: 12px; padding: 1rem 1.2rem;
        border: 1px solid #e2e8f0; display: flex; align-items: center; gap: 0.8rem;
    }
    .stat-icon {
        width: 44px; height: 44px; border-radius: 10px;
        display: flex; align-items: center; justify-content: center; font-size: 1.3rem;
    }
    .stat-icon.green { background: #dcfce7; }
    .stat-icon.yellow { background: #fef3c7; }
    .stat-icon.red { background: #fee2e2; }
    .stat-icon.blue { background: #dbeafe; }
    .stat-label { font-size: 0.75rem; color: #64748b; text-transform: uppercase; letter-spacing: 0.05em; }
    .stat-value { font-size: 1.4rem; font-weight: 700; color: #1e293b; }

    .doc-card {
        background: white; border: 1px solid #e2e8f0; border-radius: 12px;
        padding: 1rem 1.25rem; margin-bottom: 0.75rem;
        display: flex; align-items: center; gap: 1rem;
        transition: all 0.2s;
    }
    .doc-card:hover { border-color: #3b82f6; box-shadow: 0 2px 8px rgba(59,130,246,0.1); }
    .doc-icon { font-size: 2rem; }
    .doc-info { flex: 1; }
    .doc-name { font-weight: 600; color: #1e293b; font-size: 0.95rem; }
    .doc-meta { font-size: 0.78rem; color: #64748b; margin-top: 0.15rem; }

    .field-card {
        background: white; border-radius: 10px; padding: 0.85rem 1rem;
        margin-bottom: 0.5rem; border-left: 4px solid #22c55e;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        position: relative; transition: all 0.15s;
    }
    .field-card:hover { box-shadow: 0 2px 8px rgba(0,0,0,0.08); }
    .field-card.warn { border-left-color: #f59e0b; background: #fffbeb; }
    .field-card.error { border-left-color: #ef4444; background: #fef2f2; }
    .field-card.missing { border-left-color: #94a3b8; background: #f1f5f9; }
    .field-label { font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.06em; color: #64748b; margin-bottom: 0.2rem; font-weight: 500; }
    .field-value { font-size: 0.95rem; font-weight: 600; color: #1e293b; }
    .field-value.missing { color: #94a3b8; font-style: italic; font-weight: 400; }
    .copy-btn {
        position: absolute; top: 0.7rem; right: 0.7rem;
        background: none; border: 1px solid #e2e8f0; border-radius: 6px;
        padding: 0.2rem 0.5rem; font-size: 0.65rem; color: #64748b;
        cursor: pointer; opacity: 0; transition: opacity 0.15s;
    }
    .field-card:hover .copy-btn { opacity: 1; }
    .copy-btn:hover { background: #f1f5f9; border-color: #cbd5e1; }

    .status-badge {
        display: inline-flex; align-items: center; gap: 0.6rem;
        padding: 0.7rem 1.4rem; border-radius: 50px;
        font-weight: 600; font-size: 0.9rem;
    }
    .status-ready { background: #dcfce7; color: #166534; box-shadow: 0 2px 8px rgba(22,101,52,0.1); }
    .status-issues { background: #fee2e2; color: #991b1b; box-shadow: 0 2px 8px rgba(153,27,27,0.1); }

    .section-header {
        font-size: 0.8rem; font-weight: 700; text-transform: uppercase;
        letter-spacing: 0.1em; color: #64748b; margin: 1.5rem 0 0.75rem 0;
        padding-bottom: 0.5rem; border-bottom: 1px solid #e2e8f0;
        display: flex; align-items: center; gap: 0.5rem;
    }
    .section-header .count {
        background: #e2e8f0; color: #475569; font-size: 0.65rem;
        padding: 0.15rem 0.5rem; border-radius: 10px; font-weight: 600;
    }

    .validation-group { margin-bottom: 1rem; }
    .validation-group-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 0.5rem; }
    .validation-item {
        display: flex; align-items: flex-start; gap: 0.6rem;
        padding: 0.55rem 0.8rem; border-radius: 8px; margin-bottom: 0.3rem;
        font-size: 0.88rem;
    }
    .validation-item.pass { background: #f0fdf4; }
    .validation-item.fail-block { background: #fef2f2; }
    .validation-item.fail-warn { background: #fffbeb; }
    .validation-icon { font-size: 0.9rem; margin-top: 0.1rem; }
    .validation-text { color: #334155; }
    .validation-field { font-weight: 600; }

    .stTabs [data-baseweb="tab-list"] { gap: 0; background: white; border-radius: 10px; padding: 0.3rem; border: 1px solid #e2e8f0; }
    .stTabs [data-baseweb="tab"] {
        padding: 0.65rem 1.5rem; font-weight: 600; font-size: 0.9rem;
        border-radius: 8px; border: none;
    }
    .stTabs [aria-selected="true"] { background: #1e293b !important; color: white !important; }

    div[data-testid="stSidebar"] { background: #0f172a; }
    div[data-testid="stSidebar"] .stMarkdown { color: #e2e8f0; }
    div[data-testid="stSidebar"] label { color: #94a3b8 !important; }
    div[data-testid="stSidebar"] .stSelectbox label { color: #94a3b8 !important; }

    .sidebar-footer {
        position: fixed; bottom: 0; left: 0; width: 100%;
        padding: 1rem; text-align: center; font-size: 0.7rem;
        color: #475569; background: #0f172a;
    }

    .upload-zone {
        background: white; border: 2px dashed #cbd5e1; border-radius: 16px;
        padding: 4rem 2rem; text-align: center; margin: 1rem 0;
        transition: all 0.2s;
    }
    .upload-zone:hover { border-color: #3b82f6; background: #f8fafc; }

    .provider-badge {
        display: inline-flex; align-items: center; gap: 0.4rem;
        background: #1e293b; color: #94a3b8; padding: 0.3rem 0.8rem;
        border-radius: 6px; font-size: 0.75rem; font-weight: 500;
        margin-top: 0.5rem;
    }
    .provider-badge .dot { width: 6px; height: 6px; border-radius: 50%; background: #22c55e; }
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
    )

    preset_cols = st.columns(min(len(provider_info["models"]), 3))
    for i, m in enumerate(provider_info["models"][:3]):
        with preset_cols[i]:
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
    st.markdown(f"""
    <div class="provider-badge">
        <div class="dot"></div>
        {provider_info['name']} · {model}
    </div>
    """, unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>🚢 Customs Document Copilot</h1>
    <p>Extract, validate, and pre-fill customs declarations from shipping documents — powered by your AI provider.</p>
</div>
""", unsafe_allow_html=True)

current_step = 1
if api_key:
    current_step = 2
if st.session_state.get("extracted") and len(st.session_state["extracted"]) > 0:
    current_step = 3

st.markdown(f"""
<div class="steps-row">
    <div class="step-card {'active' if current_step == 1 else ''}">
        <div class="step-num">1</div>
        <div class="step-title">Configure</div>
        <div class="step-desc">Set provider & API key</div>
    </div>
    <div class="step-card {'active' if current_step == 2 else ''}">
        <div class="step-num">2</div>
        <div class="step-title">Upload</div>
        <div class="step-desc">Drop your documents</div>
    </div>
    <div class="step-card {'active' if current_step == 3 else ''}">
        <div class="step-num">3</div>
        <div class="step-title">Extract</div>
        <div class="step-desc">AI reads your docs</div>
    </div>
    <div class="step-card {'active' if current_step == 3 else ''}">
        <div class="step-num">4</div>
        <div class="step-title">Validate</div>
        <div class="step-desc">Review & export</div>
    </div>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.markdown("""
    <div style="background:white; border:1px solid #e2e8f0; border-radius:16px; padding:3rem; text-align:center; margin:1rem 0;">
        <div style="font-size:4rem; margin-bottom:1rem;">🔑</div>
        <h3 style="margin:0 0 0.5rem 0; color:#1e293b; font-size:1.3rem;">Connect your AI provider</h3>
        <p style="color:#64748b; margin:0; max-width:400px; margin:0 auto;">Select a provider in the sidebar and enter your API key. Your key stays in this session only.</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

uploaded_files = st.file_uploader(
    "Upload shipping documents",
    type=["pdf", "png", "jpg", "jpeg"],
    accept_multiple_files=True,
    label_visibility="collapsed",
)

if not uploaded_files:
    st.markdown("""
    <div class="upload-zone">
        <div style="font-size:4rem; margin-bottom:1rem;">📄</div>
        <h3 style="margin:0 0 0.5rem 0; color:#1e293b; font-size:1.2rem;">Drop your documents here</h3>
        <p style="color:#64748b; margin:0; font-size:0.9rem;">PDF, PNG, JPG — Bill of Lading, Invoices, Packing Lists</p>
        <p style="color:#94a3b8; margin:0.5rem 0 0 0; font-size:0.8rem;">Or click the uploader above</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

DOC_TYPE_LABELS = {
    "bill_of_lading": "🚢 Bill of Lading",
    "invoice": "💰 Commercial Invoice",
    "packing_list": "📦 Packing List",
    "unknown": "❓ Select Type",
}
DOC_TYPE_ICONS = {"bill_of_lading": "🚢", "invoice": "💰", "packing_list": "📦", "unknown": "❓"}

if "extracted" not in st.session_state:
    st.session_state.extracted = {}
if "doc_types" not in st.session_state:
    st.session_state.doc_types = {}

st.markdown(f'<div class="section-header">📄 Uploaded Documents <span class="count">{len(uploaded_files)}</span></div>', unsafe_allow_html=True)

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
        detected_type, _ = detect_document_type(text_chunk)
        st.session_state.doc_types[file_key] = detected_type

    icon = DOC_TYPE_ICONS.get(st.session_state.doc_types[file_key], "📄")
    col1, col2 = st.columns([5, 2])
    with col1:
        size_kb = file.size / 1024
        st.markdown(f"""
        <div class="doc-card">
            <div class="doc-icon">{icon}</div>
            <div class="doc-info">
                <div class="doc-name">{file.name}</div>
                <div class="doc-meta">{file.type.split('/')[-1].upper()} · {size_kb:.1f} KB</div>
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
col_btn, col_spacer = st.columns([2, 4])
with col_btn:
    extract_clicked = st.button("🔍 Extract Fields", type="primary", use_container_width=True)

if extract_clicked:
    st.session_state.extracted = {}
    status_text = st.empty()
    progress = st.progress(0)
    results_area = st.container()

    for i, file in enumerate(uploaded_files):
        file_key = f"{file.name}_{i}"
        progress.progress((i + 0.5) / len(uploaded_files))
        status_text.markdown(f"**Processing:** `{file.name}` ({i+1}/{len(uploaded_files)})")

        raw_bytes = file.read()
        file.seek(0)

        try:
            result = extract_from_image(
                provider=provider, api_key=api_key, model=model,
                image_bytes=raw_bytes, base_url=base_url,
            )
            st.session_state.extracted[file_key] = {
                "filename": file.name,
                "doc_type": st.session_state.doc_types[file_key],
                "result": result,
            }
            results_area.success(f"✓ `{file.name}` — extracted successfully")
        except Exception as e:
            results_area.error(f"✗ `{file.name}` — {e}")

    progress.progress(1.0)
    status_text.markdown("**Done!** All documents processed.")
    st.rerun()

if st.session_state.extracted:
    merged = ExtractionResult()
    for file_key, data in st.session_state.extracted.items():
        r = data["result"]
        if not merged.consignee_name and r.consignee_name: merged.consignee_name = r.consignee_name
        if not merged.consignee_trn and r.consignee_trn: merged.consignee_trn = r.consignee_trn
        if not merged.shipper_name and r.shipper_name: merged.shipper_name = r.shipper_name
        if not merged.shipper_country and r.shipper_country: merged.shipper_country = r.shipper_country
        if r.container_numbers: merged.container_numbers = list(set(merged.container_numbers + r.container_numbers))
        if merged.gross_weight is None and r.gross_weight is not None: merged.gross_weight = r.gross_weight
        if merged.net_weight is None and r.net_weight is not None: merged.net_weight = r.net_weight
        if merged.invoice_value is None and r.invoice_value is not None: merged.invoice_value = r.invoice_value
        if not merged.invoice_currency and r.invoice_currency: merged.invoice_currency = r.invoice_currency
        if r.hs_codes: merged.hs_codes = list(set(merged.hs_codes + r.hs_codes))
        if not merged.country_of_origin and r.country_of_origin: merged.country_of_origin = r.country_of_origin
        if not merged.port_of_loading and r.port_of_loading: merged.port_of_loading = r.port_of_loading
        if not merged.port_of_discharge and r.port_of_discharge: merged.port_of_discharge = r.port_of_discharge
        if not merged.goods_description and r.goods_description: merged.goods_description = r.goods_description
        if not merged.package_count and r.package_count: merged.package_count = r.package_count
        if not merged.marks_and_numbers and r.marks_and_numbers: merged.marks_and_numbers = r.marks_and_numbers

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
    passed_count = sum(1 for r in results if r.passed)
    total_count = len(results)
    fields_extracted = sum(1 for v in [
        merged.consignee_name, merged.consignee_trn, merged.shipper_name,
        merged.shipper_country, merged.gross_weight, merged.net_weight,
        merged.invoice_value, merged.invoice_currency, merged.country_of_origin,
        merged.port_of_loading, merged.port_of_discharge, merged.goods_description,
        merged.package_count, merged.marks_and_numbers,
    ] + merged.hs_codes + merged.container_numbers if v is not None)

    if has_blocks:
        st.markdown('<div class="status-badge status-issues">🔴 Issues Found — Fix blocking errors before submission</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-ready">🟢 Ready to Submit — All critical validations pass</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="stat-row">
        <div class="stat-card">
            <div class="stat-icon blue">📄</div>
            <div><div class="stat-label">Documents</div><div class="stat-value">{len(st.session_state.extracted)}</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon green">✓</div>
            <div><div class="stat-label">Fields Extracted</div><div class="stat-value">{fields_extracted}</div></div>
        </div>
        <div class="stat-card">
            <div class="stat-icon {'green' if passed_count == total_count else 'yellow' if not has_blocks else 'red'}">📋</div>
            <div><div class="stat-label">Validation</div><div class="stat-value">{passed_count}/{total_count}</div></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    def _get_field_class(field_name, value, results):
        if value is None or value == "":
            return "missing"
        for r in results:
            if r.field == field_name and not r.passed:
                return "error" if r.severity == "block" else "warn"
        return ""

    def _render_field(label, value, field_name, results, key=None):
        import html as html_mod
        cls = _get_field_class(field_name, value, results)
        is_missing = value is None or value == ""
        display = "Not extracted" if is_missing else value
        value_cls = "missing" if is_missing else ""
        escaped = html_mod.escape(str(display))
        uid = key or field_name or label.lower().replace(" ", "_")
        st.markdown(f"""
        <div class="field-card {cls}">
            <div class="field-label">{label}</div>
            <div class="field-value {value_cls}">{escaped}</div>
            <button class="copy-btn" onclick="navigator.clipboard.writeText(document.getElementById('fv-{uid}').textContent); this.textContent='Copied!'; setTimeout(()=>this.textContent='Copy',1000)">Copy</button>
            <span id="fv-{uid}" style="display:none">{escaped}</span>
        </div>
        """, unsafe_allow_html=True)

    tab_form, tab_valid, tab_json = st.tabs(["📋 Declaration Form", "✅ Validation", "📄 JSON"])

    with tab_form:
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('<div class="section-header">Consignee</div>', unsafe_allow_html=True)
            _render_field("Name", merged.consignee_name, "consignee_name", results)
            _render_field("TRN", merged.consignee_trn, "trn", results)

            st.markdown('<div class="section-header">Shipper</div>', unsafe_allow_html=True)
            _render_field("Name", merged.shipper_name, "shipper_name", results)
            _render_field("Country", merged.shipper_country, "shipper_country", results)

            st.markdown('<div class="section-header">Container</div>', unsafe_allow_html=True)
            containers = ", ".join(merged.container_numbers) if merged.container_numbers else None
            _render_field("Number(s)", containers, "container_number", results)

        with c2:
            st.markdown('<div class="section-header">Weight</div>', unsafe_allow_html=True)
            gw = f"{merged.gross_weight:,.2f} KGS" if merged.gross_weight is not None else None
            nw = f"{merged.net_weight:,.2f} KGS" if merged.net_weight is not None else None
            _render_field("Gross Weight", gw, "gross_weight", results)
            _render_field("Net Weight", nw, "net_weight", results)

            st.markdown('<div class="section-header">Invoice</div>', unsafe_allow_html=True)
            inv = f"{merged.invoice_currency} {merged.invoice_value:,.2f}" if merged.invoice_value is not None else None
            hs = ", ".join(merged.hs_codes) if merged.hs_codes else None
            _render_field("Value", inv, "invoice_value", results)
            _render_field("HS Code(s)", hs, "hs_code", results)

            st.markdown('<div class="section-header">Origin & Routing</div>', unsafe_allow_html=True)
            _render_field("Country of Origin", merged.country_of_origin, "country_of_origin", results)
            _render_field("Port of Loading", merged.port_of_loading, "port_of_loading", results)
            _render_field("Port of Discharge", merged.port_of_discharge, "port_of_discharge", results)

        st.markdown('<div class="section-header">Additional Details</div>', unsafe_allow_html=True)
        c3, c4, c5 = st.columns(3)
        with c3: _render_field("Goods Description", merged.goods_description, "goods_description", results)
        with c4: _render_field("Package Count", merged.package_count, "package_count", results)
        with c5: _render_field("Marks & Numbers", merged.marks_and_numbers, "marks_and_numbers", results)

    with tab_valid:
        blocks = [r for r in results if r.severity == "block"]
        warns = [r for r in results if r.severity == "warn"]

        if blocks:
            st.markdown(f'<div class="section-header">🔴 Blocking Errors <span class="count">{sum(1 for r in blocks if not r.passed)}</span></div>', unsafe_allow_html=True)
            for r in blocks:
                cls = "pass" if r.passed else "fail-block"
                icon = "✅" if r.passed else "🔴"
                st.markdown(f"""
                <div class="validation-item {cls}">
                    <span class="validation-icon">{icon}</span>
                    <span class="validation-text"><span class="validation-field">{r.field}</span> — {r.message}</span>
                </div>
                """, unsafe_allow_html=True)

        if warns:
            st.markdown(f'<div class="section-header">🟡 Warnings <span class="count">{sum(1 for r in warns if not r.passed)}</span></div>', unsafe_allow_html=True)
            for r in warns:
                cls = "pass" if r.passed else "fail-warn"
                icon = "✅" if r.passed else "🟡"
                st.markdown(f"""
                <div class="validation-item {cls}">
                    <span class="validation-icon">{icon}</span>
                    <span class="validation-text"><span class="validation-field">{r.field}</span> — {r.message}</span>
                </div>
                """, unsafe_allow_html=True)

        if all(r.passed for r in results):
            st.markdown("""
            <div style="text-align:center; padding:2rem; color:#166534;">
                <div style="font-size:3rem; margin-bottom:0.5rem;">✅</div>
                <h3 style="margin:0; color:#166534;">All validations passed</h3>
                <p style="color:#64748b; margin:0.3rem 0 0 0;">This declaration is ready to submit.</p>
            </div>
            """, unsafe_allow_html=True)

    with tab_json:
        export_data = {
            "consignee_name": merged.consignee_name, "consignee_trn": merged.consignee_trn,
            "shipper_name": merged.shipper_name, "shipper_country": merged.shipper_country,
            "container_numbers": merged.container_numbers, "gross_weight": merged.gross_weight,
            "net_weight": merged.net_weight, "invoice_value": merged.invoice_value,
            "invoice_currency": merged.invoice_currency, "hs_codes": merged.hs_codes,
            "country_of_origin": merged.country_of_origin, "port_of_loading": merged.port_of_loading,
            "port_of_discharge": merged.port_of_discharge, "goods_description": merged.goods_description,
            "package_count": merged.package_count, "marks_and_numbers": merged.marks_and_numbers,
        }
        json_str = json.dumps(export_data, indent=2, ensure_ascii=False)
        st.code(json_str, language="json")
        st.download_button("📥 Download JSON", data=json_str, file_name="customs_declaration.json", mime="application/json", use_container_width=True)

    st.markdown("---")
    st.markdown("""
    <div style="text-align:center; color:#94a3b8; font-size:0.75rem; padding:1rem 0;">
        Customs Document Copilot — Extract · Validate · Submit
    </div>
    """, unsafe_allow_html=True)
