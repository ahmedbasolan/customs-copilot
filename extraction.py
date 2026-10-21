import base64
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from detection import PDF_HINT


EXTRACTION_PROMPT = """You are a customs document extraction assistant. Extract the following fields from the shipping document image.

Return ONLY a JSON object with these fields (use null if a field cannot be extracted):

{
  "consignee_name": "string or null",
  "consignee_trn": "string or null (15-digit Tax Registration Number)",
  "shipper_name": "string or null",
  "shipper_country": "string or null",
  "container_numbers": ["array of strings, format: 4 letters + 7 digits"],
  "gross_weight": "number or null (in KGS)",
  "net_weight": "number or null (in KGS)",
  "invoice_value": "number or null",
  "invoice_currency": "string or null (e.g., USD, AED)",
  "hs_codes": ["array of strings, e.g., 9405.42"],
  "country_of_origin": "string or null",
  "port_of_loading": "string or null (IATA/unlocode, e.g., CNSHA)",
  "port_of_discharge": "string or null (IATA/unlocode, e.g., AEJEA)",
  "goods_description": "string or null",
  "package_count": "string or null (e.g., 120 PALLETS)",
  "marks_and_numbers": "string or null"
}

Rules:
- Return ONLY valid JSON, no markdown fences or explanation
- Extract exact values as they appear in the document
- For weights, extract numeric values only (remove commas, units)
- For container numbers, extract all that appear
- For HS codes, extract all that appear
- If a field is not found or illegible, set it to null"""


@dataclass
class ExtractionResult:
    consignee_name: Optional[str] = None
    consignee_trn: Optional[str] = None
    shipper_name: Optional[str] = None
    shipper_country: Optional[str] = None
    container_numbers: list[str] = field(default_factory=list)
    gross_weight: Optional[float] = None
    net_weight: Optional[float] = None
    invoice_value: Optional[float] = None
    invoice_currency: Optional[str] = None
    hs_codes: list[str] = field(default_factory=list)
    country_of_origin: Optional[str] = None
    port_of_loading: Optional[str] = None
    port_of_discharge: Optional[str] = None
    goods_description: Optional[str] = None
    package_count: Optional[str] = None
    marks_and_numbers: Optional[str] = None


PROVIDERS = {
    "openai": {
        "name": "OpenAI",
        "models": ["gpt-4o", "gpt-4o-mini", "gpt-4-turbo"],
        "default_model": "gpt-4o",
        "needs_base_url": False,
    },
    "anthropic": {
        "name": "Anthropic",
        "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20241022", "claude-3-opus-20240229"],
        "default_model": "claude-sonnet-4-20250514",
        "needs_base_url": False,
    },
    "google": {
        "name": "Google Gemini",
        "models": ["gemini-2.0-flash", "gemini-1.5-pro", "gemini-1.5-flash"],
        "default_model": "gemini-2.0-flash",
        "needs_base_url": False,
    },
    "ollama": {
        "name": "Ollama (Local)",
        "models": ["llava", "llava:13b", "bakllava", "moondream"],
        "default_model": "llava",
        "needs_base_url": True,
        "default_base_url": "http://localhost:11434",
        "needs_api_key": False,
    },
}


MAX_PDF_PAGES = 10
PDF_RENDER_DPI = 200
_PDF_MAGIC = b"%PDF"
_MAGIC_SCAN_BYTES = 1024
_PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
_JPEG_MAGIC = b"\xff\xd8\xff"


class DocumentRenderError(ValueError):
    """The upload could not be turned into image payloads for the model."""


def sniff_mime(raw: bytes) -> str:
    """Identify an upload from its magic bytes rather than its filename."""
    if _PDF_MAGIC in raw[:_MAGIC_SCAN_BYTES]:
        return "application/pdf"
    if raw.startswith(_PNG_MAGIC):
        return "image/png"
    if raw.startswith(_JPEG_MAGIC):
        return "image/jpeg"
    return "application/octet-stream"


def pdf_to_png_pages(
    raw: bytes,
    max_pages: int = MAX_PDF_PAGES,
    dpi: int = PDF_RENDER_DPI,
) -> list[bytes]:
    """Rasterise each PDF page to PNG bytes.

    Vision endpoints do not accept raw PDF bytes through their image inputs, so
    the demo's own mock documents (all PDFs) previously failed every extraction
    call. Rendering here also means scanned PDFs work without an OCR step.
    """
    try:
        import pymupdf
    except ImportError as exc:
        raise DocumentRenderError(
            f"Reading PDFs requires the 'pymupdf' package, which is not installed. {PDF_HINT}"
        ) from exc

    try:
        doc = pymupdf.open(stream=raw, filetype="pdf")
    except Exception as exc:
        raise DocumentRenderError(
            "This file could not be opened as a PDF. It may be corrupt or not a real PDF."
        ) from exc

    try:
        if getattr(doc, "needs_pass", False):
            raise DocumentRenderError(
                "This PDF is password-protected. Remove the password and upload again."
            )
        page_count = min(len(doc), max_pages)
        if page_count == 0:
            raise DocumentRenderError("This PDF contains no pages.")
        pages = [doc[index].get_pixmap(dpi=dpi).tobytes("png") for index in range(page_count)]
    except DocumentRenderError:
        raise
    except Exception as exc:
        raise DocumentRenderError(
            "The PDF opened but its pages could not be rendered to images."
        ) from exc
    finally:
        doc.close()

    return pages


def prepare_document_images(raw: bytes) -> list[tuple[str, bytes]]:
    """Return [(mime_type, image_bytes), ...] ready for a vision model.

    PDFs are rasterised page by page; images pass through with their real MIME
    type so the provider is never handed PNG-labelled PDF data.
    """
    if not raw:
        raise DocumentRenderError("The uploaded file is empty.")

    mime = sniff_mime(raw)
    if mime == "application/pdf":
        return [("image/png", page) for page in pdf_to_png_pages(raw)]
    if mime in ("image/png", "image/jpeg"):
        return [(mime, raw)]
    raise DocumentRenderError(
        "Unsupported file type. Upload a PDF, PNG, or JPG."
    )


def _parse_number(value: Any) -> Optional[float]:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        cleaned = re.sub(r"[^\d.\-]", "", value)
        try:
            return float(cleaned)
        except ValueError:
            return None
    return None


def _parse_string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value if v]
    if isinstance(value, str):
        return [value] if value else []
    return []


def parse_extraction_response(raw: dict) -> ExtractionResult:
    return ExtractionResult(
        consignee_name=raw.get("consignee_name"),
        consignee_trn=raw.get("consignee_trn"),
        shipper_name=raw.get("shipper_name"),
        shipper_country=raw.get("shipper_country"),
        container_numbers=_parse_string_list(raw.get("container_numbers")),
        gross_weight=_parse_number(raw.get("gross_weight")),
        net_weight=_parse_number(raw.get("net_weight")),
        invoice_value=_parse_number(raw.get("invoice_value")),
        invoice_currency=raw.get("invoice_currency"),
        hs_codes=_parse_string_list(raw.get("hs_codes")),
        country_of_origin=raw.get("country_of_origin"),
        port_of_loading=raw.get("port_of_loading"),
        port_of_discharge=raw.get("port_of_discharge"),
        goods_description=raw.get("goods_description"),
        package_count=raw.get("package_count"),
        marks_and_numbers=raw.get("marks_and_numbers"),
    )


def _extract_openai(api_key: str, model: str, images: list[tuple[str, bytes]], base_url: Optional[str] = None) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    content = [{"type": "text", "text": EXTRACTION_PROMPT}]
    for mime_type, image in images:
        b64 = base64.b64encode(image).decode("utf-8")
        content.append(
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime_type};base64,{b64}",
                    "detail": "high",
                },
            }
        )

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": content}],
        max_tokens=2000,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def _extract_anthropic(api_key: str, model: str, images: list[tuple[str, bytes]], base_url: Optional[str] = None) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    content = []
    for mime_type, image in images:
        content.append(
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": mime_type,
                    "data": base64.b64encode(image).decode("utf-8"),
                },
            }
        )
    content.append({"type": "text", "text": EXTRACTION_PROMPT})

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[{"role": "user", "content": content}],
    )
    return response.content[0].text.strip()


def _extract_google(api_key: str, model: str, images: list[tuple[str, bytes]], base_url: Optional[str] = None) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)

    parts = [EXTRACTION_PROMPT]
    for mime_type, image in images:
        parts.append(
            {"mime_type": mime_type, "data": base64.b64encode(image).decode("utf-8")}
        )

    response = model_instance.generate_content(
        parts,
        generation_config=genai.GenerationConfig(
            max_output_tokens=2000,
            temperature=0,
        ),
    )
    return response.text.strip()


def _extract_ollama(api_key: str, model: str, images: list[tuple[str, bytes]], base_url: Optional[str] = None) -> str:
    import httpx

    if not base_url:
        raise ValueError("Ollama needs a base URL (default: http://localhost:11434)")

    response = httpx.post(
        f"{base_url.rstrip('/')}/api/chat",
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT,
                    "images": [
                        base64.b64encode(image).decode("utf-8")
                        for _, image in images
                    ],
                }
            ],
            "stream": False,
        },
        timeout=120,
    )
    response.raise_for_status()
    return response.json()["message"]["content"].strip()



EXTRACTORS = {
    "openai": _extract_openai,
    "anthropic": _extract_anthropic,
    "google": _extract_google,
    "ollama": _extract_ollama,
}


def extract_from_image(
    provider: str,
    api_key: str,
    model: str,
    image_bytes: bytes,
    base_url: Optional[str] = None,
) -> ExtractionResult:
    """Extract declaration fields from an uploaded PDF or image.

    The parameter keeps its historical name; `image_bytes` may be a PDF, which
    is rasterised before it reaches the provider.
    """
    if provider not in EXTRACTORS:
        raise ValueError(f"Unknown provider: {provider}")

    images = prepare_document_images(image_bytes)
    extractor = EXTRACTORS[provider]
    raw_text = extractor(api_key, model, images, base_url)

    raw_text = re.sub(r"```json\n?", "", raw_text)
    raw_text = re.sub(r"\n?```", "", raw_text)
    raw_text = raw_text.strip()

    try:
        raw = json.loads(raw_text)
    except json.JSONDecodeError as e:
        raise ValueError(
            f"Model returned invalid JSON. Response preview: {raw_text[:200]}..."
        ) from e

    return parse_extraction_response(raw)
