import sys
import types
from pathlib import Path

import pytest

from extraction import (
    DocumentRenderError,
    ExtractionResult,
    extract_from_image,
    parse_extraction_response,
    prepare_document_images,
    sniff_mime,
)

MOCK_DOCS = Path(__file__).parent / "mock_docs"


class TestParseExtractionResponse:
    def test_full_response(self):
        raw = {
            "consignee_name": "Al Noor Trading FZE",
            "consignee_trn": "100234567800003",
            "shipper_name": "Guangzhou Bright Electronics Co., Ltd.",
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
            "goods_description": "LED Panel Light 600x600mm 48W",
            "package_count": "120 PALLETS",
            "marks_and_numbers": "ANT/DXB/2609-001",
        }
        result = parse_extraction_response(raw)
        assert isinstance(result, ExtractionResult)
        assert result.consignee_name == "Al Noor Trading FZE"
        assert result.consignee_trn == "100234567800003"
        assert result.container_numbers == ["MSCU4567892"]
        assert result.hs_codes == ["9405.42"]

    def test_partial_response(self):
        raw = {
            "consignee_name": "Al Noor Trading FZE",
            "consignee_trn": None,
            "shipper_name": "Guangzhou Bright Electronics",
            "shipper_country": "China",
            "container_numbers": [],
            "gross_weight": 18500.0,
            "net_weight": None,
            "invoice_value": 36850.0,
            "invoice_currency": "USD",
            "hs_codes": [],
            "country_of_origin": "China",
            "port_of_loading": "CNSHA",
            "port_of_discharge": "AEJEA",
            "goods_description": None,
            "package_count": None,
            "marks_and_numbers": None,
        }
        result = parse_extraction_response(raw)
        assert result.consignee_name == "Al Noor Trading FZE"
        assert result.consignee_trn is None
        assert result.container_numbers == []
        assert result.hs_codes == []
        assert result.goods_description is None

    def test_empty_response(self):
        raw = {}
        result = parse_extraction_response(raw)
        assert result.consignee_name is None
        assert result.hs_codes == []

    def test_string_weights(self):
        raw = {
            "gross_weight": "18,500.00",
            "net_weight": "16,200.00",
            "invoice_value": "USD 36,850.00",
        }
        result = parse_extraction_response(raw)
        assert result.gross_weight == 18500.0
        assert result.net_weight == 16200.0

    def test_container_string_to_list(self):
        raw = {
            "container_numbers": "MSCU4567892",
        }
        result = parse_extraction_response(raw)
        assert result.container_numbers == ["MSCU4567892"]


REAL_PNG = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d4944415478da63f8cfc0000003010100f7a9a4c10000000049454e44ae426082"
)
REAL_JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x00\x00\x01\x00\x01\x00\x00" + bytes.fromhex("ffd9")


class TestSniffMime:
    def test_png(self):
        assert sniff_mime(REAL_PNG) == "image/png"

    def test_jpeg(self):
        assert sniff_mime(REAL_JPEG) == "image/jpeg"

    def test_pdf(self):
        raw = (MOCK_DOCS / "bill_of_lading.pdf").read_bytes()
        assert sniff_mime(raw) == "application/pdf"

    def test_unknown(self):
        assert sniff_mime(b"just some text") == "application/octet-stream"


class TestPrepareDocumentImages:
    def test_pdf_is_rasterised_to_png_pages(self):
        raw = (MOCK_DOCS / "bill_of_lading.pdf").read_bytes()
        images = prepare_document_images(raw)

        assert images, "a PDF must produce at least one image"
        for mime_type, data in images:
            assert mime_type == "image/png"
            assert data.startswith(b"\x89PNG")

    def test_every_mock_document_renders(self):
        for name in ["bill_of_lading", "commercial_invoice", "packing_list"]:
            images = prepare_document_images((MOCK_DOCS / f"{name}.pdf").read_bytes())
            assert len(images) >= 1

    def test_png_passes_through_with_real_mime(self):
        assert prepare_document_images(REAL_PNG) == [("image/png", REAL_PNG)]

    def test_jpeg_passes_through_with_real_mime(self):
        assert prepare_document_images(REAL_JPEG) == [("image/jpeg", REAL_JPEG)]

    def test_multipage_pdf_renders_each_page(self):
        pymupdf = pytest.importorskip("pymupdf")
        doc = pymupdf.open()
        for _ in range(2):
            doc.new_page().insert_text((72, 72), "BILL OF LADING")
        raw = doc.tobytes()
        doc.close()

        assert len(prepare_document_images(raw)) == 2

    def test_empty_upload_is_rejected(self):
        with pytest.raises(DocumentRenderError):
            prepare_document_images(b"")

    def test_unsupported_type_is_rejected(self):
        with pytest.raises(DocumentRenderError, match="Unsupported file type"):
            prepare_document_images(b"GIF89a not really supported")


class _FakeChatCompletions:
    def __init__(self, captured):
        self._captured = captured

    def create(self, **kwargs):
        self._captured.update(kwargs)
        message = types.SimpleNamespace(content='{"consignee_name": "Al Noor Trading FZE"}')
        return types.SimpleNamespace(choices=[types.SimpleNamespace(message=message)])


def _install_fake_openai(monkeypatch, captured):
    module = types.ModuleType("openai")

    class FakeOpenAI:
        def __init__(self, **kwargs):
            self.chat = types.SimpleNamespace(
                completions=_FakeChatCompletions(captured)
            )

    module.OpenAI = FakeOpenAI
    monkeypatch.setitem(sys.modules, "openai", module)


class TestProviderPayloads:
    """The original bug: raw PDF bytes were sent as data:image/png, so every
    demo document failed at the provider. These assert the payload shape."""

    def test_pdf_reaches_openai_as_rendered_png(self, monkeypatch):
        captured = {}
        _install_fake_openai(monkeypatch, captured)

        raw = (MOCK_DOCS / "bill_of_lading.pdf").read_bytes()
        result = extract_from_image("openai", "sk-test", "gpt-4o", raw)

        assert result.consignee_name == "Al Noor Trading FZE"
        parts = captured["messages"][0]["content"]
        urls = [p["image_url"]["url"] for p in parts if p["type"] == "image_url"]
        assert urls, "the prompt must include at least one image"
        assert all(url.startswith("data:image/png;base64,") for url in urls)
        assert not any("application/pdf" in url for url in urls)

    def test_jpeg_reaches_openai_as_jpeg(self, monkeypatch):
        captured = {}
        _install_fake_openai(monkeypatch, captured)

        extract_from_image("openai", "sk-test", "gpt-4o", REAL_JPEG)

        parts = captured["messages"][0]["content"]
        urls = [p["image_url"]["url"] for p in parts if p["type"] == "image_url"]
        assert len(urls) == 1
        assert urls[0].startswith("data:image/jpeg;base64,")

    def test_pdf_reaches_anthropic_as_png(self, monkeypatch):
        captured = {}

        class FakeMessages:
            def create(self, **kwargs):
                captured.update(kwargs)
                block = types.SimpleNamespace(text='{"shipper_name": "Guangzhou"}')
                return types.SimpleNamespace(content=[block])

        class FakeAnthropic:
            def __init__(self, **kwargs):
                self.messages = FakeMessages()

        module = types.ModuleType("anthropic")
        module.Anthropic = FakeAnthropic
        monkeypatch.setitem(sys.modules, "anthropic", module)

        raw = (MOCK_DOCS / "commercial_invoice.pdf").read_bytes()
        extract_from_image("anthropic", "sk-ant-test", "claude-sonnet-4-20250514", raw)

        blocks = captured["messages"][0]["content"]
        media_types = {
            b["source"]["media_type"]
            for b in blocks
            if b["type"] == "image"
        }
        assert media_types == {"image/png"}

