"""Tests for shared Pydantic data models."""

from legal_skills.models import (
    ClassificationResult,
    DriverLicenseData,
    FieldDiscrepancy,
    InsuranceData,
    ValidationReport,
)


def test_classification_result() -> None:
    result = ClassificationResult(
        file_path="/tmp/test.pdf",
        document_type="driver_license",
        confidence=0.95,
    )
    assert result.document_type == "driver_license"
    assert result.confidence == 0.95


def test_driver_license_data_optional_fields() -> None:
    dl = DriverLicenseData(
        file_path="/tmp/dl.pdf",
        first_name="John",
        last_name="Smith",
        license_number="D123",
        address="123 Main St",
        state="IL",
    )
    assert dl.date_of_birth is None
    assert dl.expiration_date is None


def test_insurance_data_optional_fields() -> None:
    ins = InsuranceData(
        file_path="/tmp/ins.pdf",
        first_name="John",
        last_name="Smith",
        address="123 Main St",
    )
    assert ins.date_of_birth is None
    assert ins.vehicle_make is None


def test_validation_report_with_discrepancy() -> None:
    report = ValidationReport(
        person_name="John Smith",
        name_match=True,
        dob_match=True,
        address_match=False,
        match_status="discrepancy",
        discrepancies=[
            FieldDiscrepancy(
                field_name="address",
                dl_value="123 Main St",
                insurance_value="456 Oak Ave",
            )
        ],
        dl_source="/tmp/dl.pdf",
        insurance_source="/tmp/ins.pdf",
    )
    assert report.match_status == "discrepancy"
    assert len(report.discrepancies) == 1


def test_validation_report_all_match() -> None:
    report = ValidationReport(
        person_name="Jane Doe",
        name_match=True,
        dob_match=True,
        address_match=True,
        match_status="match",
        discrepancies=[],
        dl_source="/tmp/dl.pdf",
        insurance_source="/tmp/ins.pdf",
    )
    assert report.match_status == "match"
    assert len(report.discrepancies) == 0
