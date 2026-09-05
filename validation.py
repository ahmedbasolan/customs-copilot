import re
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ValidationResult:
    field: str
    severity: str  # "block" or "warn"
    message: str
    passed: bool


ALLOWED_COUNTRIES = {
    "Afghanistan", "Albania", "Algeria", "Argentina", "Australia",
    "Austria", "Bahrain", "Bangladesh", "Belgium", "Brazil",
    "Canada", "China", "Cyprus", "Czech Republic", "Denmark",
    "Egypt", "Finland", "France", "Germany", "Greece",
    "India", "Indonesia", "Iran", "Iraq", "Ireland",
    "Italy", "Japan", "Jordan", "Kuwait", "Lebanon",
    "Libya", "Malaysia", "Mexico", "Morocco", "Netherlands",
    "New Zealand", "Nigeria", "Norway", "Oman", "Pakistan",
    "Philippines", "Poland", "Portugal", "Qatar", "Romania",
    "Russia", "Saudi Arabia", "Singapore", "South Africa", "South Korea",
    "Spain", "Sri Lanka", "Sweden", "Switzerland", "Syria",
    "Taiwan", "Thailand", "Tunisia", "Turkey", "UAE",
    "Ukraine", "United Kingdom", "United States", "Vietnam", "Yemen",
}


def validate_hs_code(hs_code: Optional[str]) -> ValidationResult:
    if not hs_code:
        return ValidationResult(
            field="hs_code",
            severity="block",
            message="HS code is missing",
            passed=False,
        )
    pattern = r"^\d{4}\.?\d{2,6}$"
    if not re.match(pattern, hs_code):
        return ValidationResult(
            field="hs_code",
            severity="block",
            message=f"HS code '{hs_code}' is malformed (expected 6-10 digits, optional dot after 4th)",
            passed=False,
        )
    return ValidationResult(
        field="hs_code",
        severity="block",
        message="HS code is valid",
        passed=True,
    )


def validate_invoice_value(invoice_value: Any) -> ValidationResult:
    if invoice_value is None:
        return ValidationResult(
            field="invoice_value",
            severity="block",
            message="Invoice value is missing",
            passed=False,
        )
    try:
        value = float(invoice_value)
    except (ValueError, TypeError):
        return ValidationResult(
            field="invoice_value",
            severity="block",
            message=f"Invoice value '{invoice_value}' is not a valid number",
            passed=False,
        )
    if value <= 0:
        return ValidationResult(
            field="invoice_value",
            severity="block",
            message=f"Invoice value must be positive (got {value})",
            passed=False,
        )
    return ValidationResult(
        field="invoice_value",
        severity="block",
        message="Invoice value is valid",
        passed=True,
    )


def validate_trn(trn: Optional[str]) -> ValidationResult:
    if not trn:
        return ValidationResult(
            field="trn",
            severity="block",
            message="TRN (Tax Registration Number) is missing",
            passed=False,
        )
    if not trn.isdigit() or len(trn) != 15:
        return ValidationResult(
            field="trn",
            severity="block",
            message=f"TRN '{trn}' is invalid (expected exactly 15 digits)",
            passed=False,
        )
    return ValidationResult(
        field="trn",
        severity="block",
        message="TRN is valid",
        passed=True,
    )


def validate_container_number(container: Optional[str]) -> ValidationResult:
    if not container:
        return ValidationResult(
            field="container_number",
            severity="block",
            message="Container number is missing",
            passed=False,
        )
    pattern = r"^[A-Z]{4}\d{7}$"
    if not re.match(pattern, container):
        return ValidationResult(
            field="container_number",
            severity="block",
            message=f"Container number '{container}' is invalid (expected 4 uppercase letters + 7 digits)",
            passed=False,
        )
    return ValidationResult(
        field="container_number",
        severity="block",
        message="Container number is valid",
        passed=True,
    )


def validate_gross_weight(gross_weight: Any, net_weight: Any) -> ValidationResult:
    if gross_weight is None or net_weight is None:
        return ValidationResult(
            field="gross_weight",
            severity="warn",
            message="Cannot validate weight relationship (missing data)",
            passed=True,
        )
    try:
        gross = float(gross_weight)
        net = float(net_weight)
    except (ValueError, TypeError):
        return ValidationResult(
            field="gross_weight",
            severity="warn",
            message="Cannot validate weight relationship (invalid data)",
            passed=True,
        )
    if gross < net:
        return ValidationResult(
            field="gross_weight",
            severity="warn",
            message=f"Gross weight ({gross}) is less than net weight ({net})",
            passed=False,
        )
    return ValidationResult(
        field="gross_weight",
        severity="warn",
        message="Weight relationship is valid",
        passed=True,
    )


def validate_country_of_origin(country: Optional[str]) -> ValidationResult:
    if not country:
        return ValidationResult(
            field="country_of_origin",
            severity="warn",
            message="Country of origin is missing",
            passed=True,
        )
    if country.title() not in ALLOWED_COUNTRIES:
        return ValidationResult(
            field="country_of_origin",
            severity="warn",
            message=f"Country '{country}' is not in the allowed trading countries list",
            passed=False,
        )
    return ValidationResult(
        field="country_of_origin",
        severity="warn",
        message="Country of origin is valid",
        passed=True,
    )


def validate_currency(currency: Optional[str]) -> ValidationResult:
    if not currency:
        return ValidationResult(
            field="currency",
            severity="warn",
            message="Invoice currency is missing",
            passed=True,
        )
    if currency.upper() != "AED":
        return ValidationResult(
            field="currency",
            severity="warn",
            message=f"Invoice currency is {currency}, not AED (conversion may be needed)",
            passed=False,
        )
    return ValidationResult(
        field="currency",
        severity="warn",
        message="Currency is AED",
        passed=True,
    )


def validate_all(data: dict) -> list[ValidationResult]:
    results = []
    results.append(validate_hs_code(data.get("hs_code")))
    results.append(validate_invoice_value(data.get("invoice_value")))
    results.append(validate_trn(data.get("trn")))
    results.append(validate_container_number(data.get("container_number")))
    results.append(validate_gross_weight(data.get("gross_weight"), data.get("net_weight")))
    results.append(validate_country_of_origin(data.get("country_of_origin")))
    results.append(validate_currency(data.get("currency")))
    return results
