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

    def test_two_dots_are_accepted(self):
        # '9403.20.00' is the common 8-digit presentation.
        assert validate_hs_code("9403.20.00").passed is True

    def test_spaces_and_hyphens_are_accepted(self):
        assert validate_hs_code("9403 20").passed is True
        assert validate_hs_code("9403-20-00").passed is True


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

    def test_thousands_separator_is_normalised(self):
        assert validate_invoice_value("36,850.00").passed is True


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

    def test_grouping_separators_are_normalised(self):
        assert validate_trn("100 1234 5678 9012").passed is True
        assert validate_trn("100-1234-5678-9012").passed is True


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

    def test_lowercase_is_normalised(self):
        # Document text often lower-cases the owner code; that is a formatting
        # difference, not a data-entry error.
        result = validate_container_number("mscu4567892")
        assert result.passed is True

    def test_spaces_and_dashes_are_normalised(self):
        assert validate_container_number("MSCU 4567892").passed is True
        assert validate_container_number("MSCU-4567892").passed is True

    def test_normalisation_does_not_hide_real_errors(self):
        result = validate_container_number("MSCU 456789A")
        assert result.passed is False
        assert "MSCU 456789A" in result.message  # report what the document said


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

    def test_uae_is_recognised_in_any_spelling(self):
        # The regression: .title() turned "UAE" into "Uae", so a Dubai
        # declaration warned about its own country of origin.
        for spelling in ["UAE", "uae", "U.A.E.", "United Arab Emirates"]:
            result = validate_country_of_origin(spelling)
            assert result.passed is True, f"{spelling!r} should be allowed"

    def test_common_aliases_are_recognised(self):
        for alias in ["USA", "U.S.A.", "UK", "Korea", "Türkiye", "Viet Nam"]:
            assert validate_country_of_origin(alias).passed is True, alias


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

    def test_all_containers_are_validated(self):
        data = {
            "hs_codes": ["9405.42"],
            "invoice_value": 36850.00,
            "trn": "100234567800003",
            "container_numbers": ["MSCU4567892", "TGHU1234567", "BAD"],
            "gross_weight": 18500.00,
            "net_weight": 16200.00,
            "country_of_origin": "China",
            "currency": "AED",
        }
        results = validate_all(data)
        container_failures = [
            r for r in results if r.field == "container_number" and not r.passed
        ]
        assert len(container_failures) == 1
        assert "'BAD'" in container_failures[0].message

    def test_all_valid_containers_collapse_to_one_row(self):
        data = {"container_numbers": ["MSCU4567892", "TGHU1234567"]}
        results = validate_all(data)
        container_results = [r for r in results if r.field == "container_number"]
        assert len(container_results) == 1
        assert container_results[0].passed is True
        assert "2" in container_results[0].message

    def test_list_keys_take_precedence_over_scalars(self):
        data = {"hs_code": "9405.42", "hs_codes": ["BAD1"]}
        results = validate_all(data)
        hs_results = [r for r in results if r.field == "hs_code"]
        assert len(hs_results) == 1
        assert hs_results[0].passed is False

    def test_empty_list_falls_back_to_scalar(self):
        data = {"hs_code": "9405.42", "hs_codes": []}
        results = validate_all(data)
        hs_results = [r for r in results if r.field == "hs_code"]
        assert len(hs_results) == 1
        assert hs_results[0].passed is True

    def test_duplicate_values_are_validated_once(self):
        data = {"container_numbers": ["MSCU4567892", "MSCU4567892"]}
        results = validate_all(data)
        container_results = [r for r in results if r.field == "container_number"]
        assert len(container_results) == 1
