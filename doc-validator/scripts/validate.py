"""Compare Driver License and Insurance data for discrepancies."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from legal_skills.models import (
    DriverLicenseData,
    FieldDiscrepancy,
    InsuranceData,
    ValidationReport,
)


def _normalize(value: str | None) -> str:
    """Normalize a string for case-insensitive, whitespace-stripped comparison."""
    if value is None:
        return ""
    return value.strip().lower()


def validate_documents(
    dl: DriverLicenseData, insurance: InsuranceData
) -> ValidationReport:
    """Compare DL and insurance data, returning a validation report.

    Checks name, date of birth, and address for discrepancies.
    Name and address comparisons are case-insensitive.
    DOB comparison is skipped if either value is None.
    """
    discrepancies: list[FieldDiscrepancy] = []

    # Name comparison
    dl_name = _normalize(f"{dl.first_name} {dl.last_name}")
    ins_name = _normalize(f"{insurance.first_name} {insurance.last_name}")
    name_match = dl_name == ins_name
    if not name_match:
        discrepancies.append(
            FieldDiscrepancy(
                field_name="name",
                dl_value=f"{dl.first_name} {dl.last_name}",
                insurance_value=f"{insurance.first_name} {insurance.last_name}",
            )
        )

    # DOB comparison (match if either is None)
    if dl.date_of_birth is not None and insurance.date_of_birth is not None:
        dob_match = _normalize(dl.date_of_birth) == _normalize(
            insurance.date_of_birth
        )
    else:
        dob_match = True
    if not dob_match:
        discrepancies.append(
            FieldDiscrepancy(
                field_name="date_of_birth",
                dl_value=dl.date_of_birth or "",
                insurance_value=insurance.date_of_birth or "",
            )
        )

    # Address comparison
    address_match = _normalize(dl.address) == _normalize(insurance.address)
    if not address_match:
        discrepancies.append(
            FieldDiscrepancy(
                field_name="address",
                dl_value=dl.address,
                insurance_value=insurance.address,
            )
        )

    all_match = name_match and dob_match and address_match

    return ValidationReport(
        person_name=f"{dl.first_name} {dl.last_name}",
        name_match=name_match,
        dob_match=dob_match,
        address_match=address_match,
        match_status="match" if all_match else "discrepancy",
        discrepancies=discrepancies,
        dl_source=dl.file_path,
        insurance_source=insurance.file_path,
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate.py '<dl_json>' '<insurance_json>'")
        sys.exit(1)
    dl = DriverLicenseData.model_validate_json(sys.argv[1])
    ins = InsuranceData.model_validate_json(sys.argv[2])
    report = validate_documents(dl, ins)
    print(report.model_dump_json(indent=2))
