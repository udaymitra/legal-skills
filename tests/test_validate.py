"""Tests for doc-validator validate_documents function."""

from validate import validate_documents

from legal_skills.models import DriverLicenseData, InsuranceData


def _make_dl(**overrides: object) -> DriverLicenseData:
    defaults: dict[str, object] = {
        "file_path": "/tmp/dl.jpg",
        "first_name": "John",
        "last_name": "Smith",
        "license_number": "D1234567",
        "address": "123 Main St, Springfield, IL 62701",
        "state": "IL",
        "date_of_birth": "1985-03-15",
        "expiration_date": "2027-03-15",
    }
    defaults.update(overrides)
    return DriverLicenseData(**defaults)


def _make_ins(**overrides: object) -> InsuranceData:
    defaults: dict[str, object] = {
        "file_path": "/tmp/ins.pdf",
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1985-03-15",
        "address": "123 Main St, Springfield, IL 62701",
        "policy_number": "POL-98765",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": "2022",
        "vin": "1HGBH41JXMN109186",
    }
    defaults.update(overrides)
    return InsuranceData(**defaults)


def test_all_fields_match() -> None:
    report = validate_documents(_make_dl(), _make_ins())
    assert report.match_status == "match"
    assert report.name_match is True
    assert report.dob_match is True
    assert report.address_match is True
    assert len(report.discrepancies) == 0


def test_address_mismatch() -> None:
    report = validate_documents(
        _make_dl(),
        _make_ins(address="456 Oak Ave, Springfield, IL 62702"),
    )
    assert report.match_status == "discrepancy"
    assert report.address_match is False
    assert report.name_match is True
    assert len(report.discrepancies) == 1
    assert report.discrepancies[0].field_name == "address"


def test_name_mismatch() -> None:
    report = validate_documents(
        _make_dl(),
        _make_ins(first_name="Jonathan"),
    )
    assert report.match_status == "discrepancy"
    assert report.name_match is False
    assert len(report.discrepancies) == 1
    assert report.discrepancies[0].field_name == "name"


def test_dob_mismatch() -> None:
    report = validate_documents(
        _make_dl(),
        _make_ins(date_of_birth="1985-04-20"),
    )
    assert report.match_status == "discrepancy"
    assert report.dob_match is False
    assert len(report.discrepancies) == 1
    assert report.discrepancies[0].field_name == "date_of_birth"


def test_dob_null_on_insurance_still_matches() -> None:
    report = validate_documents(
        _make_dl(),
        _make_ins(date_of_birth=None),
    )
    assert report.dob_match is True
    assert report.match_status == "match"


def test_multiple_discrepancies() -> None:
    report = validate_documents(
        _make_dl(),
        _make_ins(
            first_name="Jane",
            address="999 Different St",
            date_of_birth="1990-01-01",
        ),
    )
    assert report.match_status == "discrepancy"
    assert report.name_match is False
    assert report.dob_match is False
    assert report.address_match is False
    assert len(report.discrepancies) == 3


def test_case_insensitive_name_match() -> None:
    report = validate_documents(
        _make_dl(first_name="JOHN", last_name="SMITH"),
        _make_ins(first_name="john", last_name="smith"),
    )
    assert report.name_match is True


def test_case_insensitive_address_match() -> None:
    report = validate_documents(
        _make_dl(address="123 MAIN ST"),
        _make_ins(address="123 main st"),
    )
    assert report.address_match is True
