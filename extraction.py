import json
import re
from dataclasses import dataclass, field
from typing import Any, Optional

from openai import OpenAI


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


def extract_from_image(api_key: str, image_bytes: bytes) -> ExtractionResult:
    client = OpenAI(api_key=api_key)

    base64_image = __import__("base64").b64encode(image_bytes).decode("utf-8")

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": EXTRACTION_PROMPT},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "high",
                        },
                    },
                ],
            }
        ],
        max_tokens=2000,
        temperature=0,
    )

    content = response.choices[0].message.content.strip()

    content = re.sub(r"```json\n?", "", content)
    content = re.sub(r"\n?```", "", content)
    content = content.strip()

    raw = json.loads(content)
    return parse_extraction_response(raw)
