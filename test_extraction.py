import pytest
from extraction import parse_extraction_response, ExtractionResult


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
