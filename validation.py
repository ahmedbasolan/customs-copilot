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

# Documents rarely spell countries the way ALLOWED_COUNTRIES does: UAE arrives
# as "U.A.E.", "United Arab Emirates" or "uae". Matching used to run
# country.title(), which turned "UAE" into "Uae" and warned on the single most
# common origin in a Dubai declaration. Keys are pre-normalised by
# _country_key().
COUNTRY_ALIASES = {
    "uae": "UAE",
    "united arab emirates": "UAE",
    "usa": "United States",
    "us": "United States",
    "united states of america": "United States",
    "uk": "United Kingdom",
    "great britain": "United Kingdom",
    "england": "United Kingdom",
    "korea": "South Korea",
    "republic of korea": "South Korea",
    "viet nam": "Vietnam",
    "türkiye": "Turkey",
    "turkiye": "Turkey",
    "czechia": "Czech Republic",
    "russian federation": "Russia",
    "holland": "Netherlands",
    "ksa": "Saudi Arabia",
}


def _country_key(country: str) -> str:
    """Normalise a country name for lookup: no periods, single spaces, casefold."""
    return " ".join(str(country).replace(".", "").split()).casefold()


_COUNTRY_BY_KEY = {_country_key(c): c for c in ALLOWED_COUNTRIES}
_COUNTRY_BY_KEY.update({_country_key(k): v for k, v in COUNTRY_ALIASES.items()})


def _normalise_hs_code(hs_code: Any) -> str:
    """Reduce '9405.42' / '9403 20 00' / '9403.20.00' to bare digits."""
    return re.sub(r"[\s.\-]", "", str(hs_code)).upper()


def _normalise_container_number(container: Any) -> str:
    """Drop separators and upper-case, so 'mscu 4567892' matches the format."""
    return re.sub(r"[\s\-]", "", str(container)).upper()


def _normalise_trn(trn: Any) -> str:
    """Drop grouping separators, so '100 1234 5678 9012' is 15 digits."""
    return re.sub(r"[\s\-.()]", "", str(trn))


def ordered_unique(values) -> list:
    """De-duplicate while keeping first-seen order.

    list(set(...)) gave merged container numbers and HS codes a random order
    per run, which decided which value validation happened to see first.
    """
    seen = set()
    unique = []
    for value in values:
        if value not in seen:
            seen.add(value)
            unique.append(value)
    return unique


def validate_hs_code(hs_code: Optional[str]) -> ValidationResult:
    if not hs_code:
        return ValidationResult(
            field="hs_code",
            severity="block",
            message="HS code is missing",
            passed=False,
        )
    pattern = r"^\d{6,10}$"
    normalised = _normalise_hs_code(hs_code)
    if not re.match(pattern, normalised):
        return ValidationResult(
            field="hs_code",
            severity="block",
            message=f"HS code '{hs_code}' is malformed (expected 6-10 digits, optional dot after 4th)",
            passed=False,
        )
    return ValidationResult(
        field="hs_code",
        severity="block",
        message=f"HS code '{hs_code}' is valid",
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
        value = float(str(invoice_value).replace(",", "").strip())
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
    trn = _normalise_trn(trn)
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
    normalised = _normalise_container_number(container)
    if not re.match(pattern, normalised):
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
        gross = float(str(gross_weight).replace(",", "").strip())
        net = float(str(net_weight).replace(",", "").strip())
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
    if _country_key(country) not in _COUNTRY_BY_KEY:
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


def _validate_many(validator, values, field: str, label: str) -> list[ValidationResult]:
    """Validate every value in a list, reporting each failure separately.

    A shipment can carry several containers or HS codes. Validating only the
    first one (in whatever order the merged list happened to be in) let a
    malformed second container through. Passing values are collapsed into one
    row so a long shipment does not flood the UI with duplicates.
    """
    values = ordered_unique(values or [])
    if not values:
        return [validator(None)]

    results = [validator(value) for value in values]
    failures = [result for result in results if not result.passed]
    if failures:
        return failures
    if len(results) == 1:
        return results
    return [
        ValidationResult(
            field=field,
            severity=results[0].severity,
            message=f"All {len(results)} {label} are valid",
            passed=True,
        )
    ]


def _collect(data: dict, list_key: str, single_key: str) -> list:
    """Read the list form when present, else fall back to the scalar form."""
    values = data.get(list_key)
    if values:
        return list(values)
    single = data.get(single_key)
    return [single] if single else []


def validate_all(data: dict) -> list[ValidationResult]:
    results = []
    results.extend(
        _validate_many(
            validate_hs_code,
            _collect(data, "hs_codes", "hs_code"),
            "hs_code",
            "HS codes",
        )
    )
    results.append(validate_invoice_value(data.get("invoice_value")))
    results.append(validate_trn(data.get("trn")))
    results.extend(
        _validate_many(
            validate_container_number,
            _collect(data, "container_numbers", "container_number"),
            "container_number",
            "container numbers",
        )
    )
    results.append(validate_gross_weight(data.get("gross_weight"), data.get("net_weight")))
    results.append(validate_country_of_origin(data.get("country_of_origin")))
    results.append(validate_currency(data.get("currency")))
    return results

