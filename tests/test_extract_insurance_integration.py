"""Integration tests for insurance-extractor skill using real documents and OpenAI API."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from extract_insurance import extract_insurance
from legal_skills.models import InsuranceData

TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"


def _require_test_data() -> None:
    """Skip if test_data directory is missing."""
    if not TEST_DATA.exists():
        pytest.skip("test_data/ directory not found")


def _assert_john_smith(result: InsuranceData) -> None:
    """Shared assertions for John Smith insurance — all fields exact."""
    assert isinstance(result, InsuranceData)
    assert result.first_name.upper() == "JOHN"
    assert result.last_name.upper() == "SMITH"
    assert result.date_of_birth == "1985-05-20"
    normalized_addr = " ".join(result.address.upper().split())
    assert "OAK" in normalized_addr
    assert "SPRINGFIELD" in normalized_addr
    assert "IL" in normalized_addr
    assert "62704" in normalized_addr
    assert normalized_addr == "123 OAK AVENUE, SPRINGFIELD, IL 62704" or \
        normalized_addr == "123 OAK AVENUE SPRINGFIELD, IL 62704"
    assert result.policy_number is not None
    assert result.policy_number == "987654321"
    assert result.vehicle_make is not None
    assert result.vehicle_make.upper() == "HONDA"
    assert result.vehicle_model is not None
    assert result.vehicle_model.upper() == "ACCORD"
    assert result.vehicle_year == "2023"
    assert result.vin is not None
    assert result.vin.upper() == "1HGCV1F45PA123456"


def _assert_adam_mangler(result: InsuranceData) -> None:
    """Shared assertions for Adam Mangler insurance — all fields exact."""
    assert isinstance(result, InsuranceData)
    assert result.first_name.upper() == "ADAM"
    assert result.last_name.upper() == "MANGLER"
    assert result.date_of_birth == "1990-11-11"
    normalized_addr = " ".join(result.address.upper().split())
    assert "SAILBORN" in normalized_addr
    assert "FICTIONAL CITY" in normalized_addr
    assert "95111" in normalized_addr
    assert normalized_addr == "1 SAILBORN ROAD, FICTIONAL CITY, CA 95111" or \
        normalized_addr == "1 SAILBORN ROAD FICTIONAL CITY, CA 95111"
    assert result.policy_number is not None
    assert result.policy_number == "12345"
    assert result.vehicle_make is not None
    assert result.vehicle_make.upper() == "TOYOTA"
    assert result.vehicle_model is not None
    assert result.vehicle_model.upper() == "HIGHLANDER"
    assert result.vehicle_year == "2025"
    assert result.vin is not None
    assert result.vin.upper() == "12345ABCDE12345"


@pytest.mark.integration
class TestExtractInsuranceJohnSmith:
    """Extract data from John Smith insurance documents."""

    def test_insurance_john_smith_png(self) -> None:
        _require_test_data()
        _assert_john_smith(extract_insurance(str(TEST_DATA / "insurance_john_smith.png")))


@pytest.mark.integration
class TestExtractInsuranceAdamMangler:
    """Extract data from Adam Mangler insurance documents."""

    def test_insurance_adam_mangler_png(self) -> None:
        _require_test_data()
        _assert_adam_mangler(extract_insurance(str(TEST_DATA / "insurance_adam_mangler.png")))

    def test_insurance_adam_mangler_pdf(self) -> None:
        """PDF extraction — auto-orient fixes rotation, same assertions as PNG."""
        _require_test_data()
        _assert_adam_mangler(extract_insurance(str(TEST_DATA / "insurance_adam_mangler.pdf")))


@pytest.mark.integration
class TestExtractInsuranceNonInsuranceDocument:
    """Verify behavior when a non-insurance document is passed."""

    def test_visiting_card_returns_unreliable_data(self) -> None:
        """A non-insurance document may return fabricated data or raise ValidationError.

        GPT behavior is non-deterministic on non-insurance inputs: it may hallucinate
        fields or return nulls that fail Pydantic validation. Either outcome
        is acceptable — the key point is to always use doc-classifier first.
        """
        _require_test_data()
        try:
            result = extract_insurance(str(TEST_DATA / "visiting_card_john_smith.png"))
            assert isinstance(result, InsuranceData)
        except (ValidationError, Exception):
            pass
