import base64
import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional


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
        "models": ["claude-sonnet-4-20250514", "claude-3-5-haiku-20251022", "claude-3-opus-20240229"],
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
    },
}


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


def _extract_openai(api_key: str, model: str, image_bytes: bytes, base_url: Optional[str] = None) -> str:
    from openai import OpenAI

    client = OpenAI(api_key=api_key)
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": EXTRACTION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{b64}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        max_tokens=2000,
        temperature=0,
    )
    return response.choices[0].message.content.strip()


def _extract_anthropic(api_key: str, model: str, image_bytes: bytes, base_url: Optional[str] = None) -> str:
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = client.messages.create(
        model=model,
        max_tokens=2000,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/png",
                            "data": b64,
                        },
                    },
                    {"type": "text", "text": EXTRACTION_PROMPT},
                ],
            }
        ],
    )
    return response.content[0].text.strip()


def _extract_google(api_key: str, model: str, image_bytes: bytes, base_url: Optional[str] = None) -> str:
    import google.generativeai as genai

    genai.configure(api_key=api_key)
    model_instance = genai.GenerativeModel(model)
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = model_instance.generate_content(
        [
            EXTRACTION_PROMPT,
            {"mime_type": "image/png", "data": b64},
        ],
        generation_config=genai.GenerationConfig(
            max_output_tokens=2000,
            temperature=0,
        ),
    )
    return response.text.strip()


def _extract_ollama(api_key: str, model: str, image_bytes: bytes, base_url: str = "http://localhost:11434") -> str:
    import httpx

    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = httpx.post(
        f"{base_url}/api/chat",
        json={
            "model": model,
            "messages": [
                {
                    "role": "user",
                    "content": EXTRACTION_PROMPT,
                    "images": [b64],
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
    if provider not in EXTRACTORS:
        raise ValueError(f"Unknown provider: {provider}")

    extractor = EXTRACTORS[provider]
    raw_text = extractor(api_key, model, image_bytes, base_url)

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
