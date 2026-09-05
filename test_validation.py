import pytest
from validation import (
    validate_hs_code,
    validate_invoice_value,
    validate_trn,
    validate_container_number,
    validate_gross_weight,
    validate_country_of_origin,
    validate_currency,
    validate_all,
)


class TestHSCodeValidation:
    def test_valid_hs_code(self):
        result = validate_hs_code("9405.42")
        assert result.passed is True
        assert result.severity == "block"

    def test_valid_hs_code_no_dot(self):
        result = validate_hs_code("940542")
        assert result.passed is True

    def test_valid_hs_code_long(self):
        result = validate_hs_code("9405420000")
        assert result.passed is True

    def test_missing_hs_code(self):
        result = validate_hs_code(None)
        assert result.passed is False
        assert result.severity == "block"

    def test_empty_hs_code(self):
        result = validate_hs_code("")
        assert result.passed is False

    def test_letters_in_hs_code(self):
        result = validate_hs_code("9405.AB")
        assert result.passed is False

    def test_too_short(self):
        result = validate_hs_code("9405")
        assert result.passed is False

    def test_too_long(self):
        result = validate_hs_code("94054200001")
        assert result.passed is False


class TestInvoiceValueValidation:
    def test_valid_invoice_value(self):
        result = validate_invoice_value(36850.00)
        assert result.passed is True
        assert result.severity == "block"

    def test_zero_invoice_value(self):
        result = validate_invoice_value(0)
        assert result.passed is False
        assert result.severity == "block"

    def test_negative_invoice_value(self):
        result = validate_invoice_value(-500.00)
        assert result.passed is False

    def test_missing_invoice_value(self):
        result = validate_invoice_value(None)
        assert result.passed is False

    def test_string_invoice_value(self):
        result = validate_invoice_value("36850")
        assert result.passed is True


class TestTRNValidation:
    def test_valid_trn(self):
        result = validate_trn("100234567800003")
        assert result.passed is True
        assert result.severity == "block"

    def test_missing_trn(self):
        result = validate_trn(None)
        assert result.passed is False
        assert result.severity == "block"

    def test_empty_trn(self):
        result = validate_trn("")
        assert result.passed is False

    def test_too_short_trn(self):
        result = validate_trn("1002345678")
        assert result.passed is False

    def test_letters_in_trn(self):
        result = validate_trn("10023ABC7800003")
        assert result.passed is False


class TestContainerNumberValidation:
    def test_valid_container(self):
        result = validate_container_number("MSCU4567892")
        assert result.passed is True
        assert result.severity == "block"

    def test_missing_container(self):
        result = validate_container_number(None)
        assert result.passed is False
        assert result.severity == "block"

    def test_letters_in_serial(self):
        result = validate_container_number("MSCU456789A")
        assert result.passed is False

    def test_too_short(self):
        result = validate_container_number("MSCU45678")
        assert result.passed is False

    def test_too_long(self):
        result = validate_container_number("MSCU45678901")
        assert result.passed is False

    def test_lowercase_letters(self):
        result = validate_container_number("mscu4567892")
        assert result.passed is False


class TestGrossWeightValidation:
    def test_valid_gross_weight(self):
        result = validate_gross_weight(18500.00, 16200.00)
        assert result.passed is True
        assert result.severity == "warn"

    def test_gross_less_than_net(self):
        result = validate_gross_weight(16000.00, 18500.00)
        assert result.passed is False
        assert result.severity == "warn"

    def test_equal_weights(self):
        result = validate_gross_weight(18500.00, 18500.00)
        assert result.passed is True

    def test_missing_gross_weight(self):
        result = validate_gross_weight(None, 16200.00)
        assert result.passed is True  # Can't validate, skip

    def test_missing_net_weight(self):
        result = validate_gross_weight(18500.00, None)
        assert result.passed is True  # Can't validate, skip


class TestCountryOfOriginValidation:
    def test_valid_country(self):
        result = validate_country_of_origin("China")
        assert result.passed is True
        assert result.severity == "warn"

    def test_invalid_country(self):
        result = validate_country_of_origin("Narnia")
        assert result.passed is False
        assert result.severity == "warn"

    def test_missing_country(self):
        result = validate_country_of_origin(None)
        assert result.passed is True  # Can't validate, skip

    def test_country_case_insensitive(self):
        result = validate_country_of_origin("china")
        assert result.passed is True


class TestCurrencyValidation:
    def test_valid_currency_aed(self):
        result = validate_currency("AED")
        assert result.passed is True
        assert result.severity == "warn"

    def test_non_aed_currency(self):
        result = validate_currency("USD")
        assert result.passed is False
        assert result.severity == "warn"

    def test_missing_currency(self):
        result = validate_currency(None)
        assert result.passed is True  # Can't validate, skip

    def test_currency_case_insensitive(self):
        result = validate_currency("aed")
        assert result.passed is True


class TestValidateAll:
    def test_all_pass(self):
        data = {
            "hs_code": "9405.42",
            "invoice_value": 36850.00,
            "trn": "100234567800003",
            "container_number": "MSCU4567892",
            "gross_weight": 18500.00,
            "net_weight": 16200.00,
            "country_of_origin": "China",
            "currency": "AED",
        }
        results = validate_all(data)
        assert all(r.passed for r in results)

    def test_blocks_present(self):
        data = {
            "hs_code": None,
            "invoice_value": 0,
            "trn": None,
            "container_number": "INVALID",
        }
        results = validate_all(data)
        blocks = [r for r in results if r.severity == "block" and not r.passed]
        assert len(blocks) >= 4

    def test_empty_data(self):
        results = validate_all({})
        assert len(results) > 0
        assert any(not r.passed for r in results)
