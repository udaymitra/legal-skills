"""Pydantic data models for all legal document processing skills."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ClassificationResult(BaseModel):
    """Result of classifying a document as DL, insurance, or unknown."""

    file_path: str
    document_type: Literal["driver_license", "insurance", "unknown"]
    confidence: float


class DriverLicenseData(BaseModel):
    """Structured data extracted from a driver license document."""

    file_path: str
    first_name: str
    last_name: str
    license_number: str
    address: str
    state: str
    date_of_birth: str | None = None
    expiration_date: str | None = None


class InsuranceData(BaseModel):
    """Structured data extracted from an insurance document."""

    file_path: str
    first_name: str
    last_name: str
    date_of_birth: str | None = None
    address: str
    policy_number: str | None = None
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    vehicle_year: str | None = None
    vin: str | None = None


class FieldDiscrepancy(BaseModel):
    """A single field that differs between DL and insurance data."""

    field_name: str
    dl_value: str
    insurance_value: str


class ValidationReport(BaseModel):
    """Result of comparing DL and insurance data for a single person."""

    person_name: str
    name_match: bool
    dob_match: bool
    address_match: bool
    match_status: Literal["match", "discrepancy"]
    discrepancies: list[FieldDiscrepancy]
    dl_source: str
    insurance_source: str
