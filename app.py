import streamlit as st

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
else:
    st.success("API key loaded. Upload documents to begin.")
