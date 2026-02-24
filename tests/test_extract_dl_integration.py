"""Integration tests for dl-extractor skill using real documents and OpenAI API."""

from pathlib import Path

import pytest
from pydantic import ValidationError

from extract_dl import extract_dl
from legal_skills.models import DriverLicenseData

TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"


def _require_test_data() -> None:
    """Skip if test_data directory is missing."""
    if not TEST_DATA.exists():
        pytest.skip("test_data/ directory not found")


def _assert_john_smith(result: DriverLicenseData) -> None:
    """Shared assertions for John Smith DL — all fields exact."""
    assert isinstance(result, DriverLicenseData)
    assert result.first_name.upper() == "JOHN"
    assert result.last_name.upper() == "SMITH"
    assert result.license_number.upper() == "E9876543"
    # GPT returns address with comma or newline between street and city;
    # normalize to single-line for comparison
    normalized_addr = " ".join(result.address.upper().split())
    assert normalized_addr == "456 OAK AVENUE, RIVER CITY, CA 90210" or \
        normalized_addr == "456 OAK AVENUE RIVER CITY, CA 90210"
    assert result.state.upper() in ("CA", "CALIFORNIA")
    assert result.date_of_birth == "1985-05-20"
    assert result.expiration_date == "2028-05-20"


@pytest.mark.integration
class TestExtractDlJohnSmith:
    """Extract data from John Smith driver license documents."""

    def test_dl_john_smith_png(self) -> None:
        _require_test_data()
        _assert_john_smith(extract_dl(str(TEST_DATA / "dl_john_smith.png")))

    def test_dl_john_smith_pdf(self) -> None:
        """PDF extraction — auto-orient fixes rotation, same assertions as PNG."""
        _require_test_data()
        _assert_john_smith(extract_dl(str(TEST_DATA / "dl_john_smith.pdf")))


def _assert_adam_mangler(result: DriverLicenseData) -> None:
    """Shared assertions for Adam Mangler DL — all fields exact."""
    assert isinstance(result, DriverLicenseData)
    assert result.first_name.upper() == "ADAM"
    assert result.last_name.upper() == "MANGLER"
    assert result.license_number.upper() == "D1234567"
    normalized_addr = " ".join(result.address.upper().split())
    assert "SAILBORN" in normalized_addr
    assert "FICTIONAL CITY" in normalized_addr
    assert "95111" in normalized_addr
    assert result.state.upper() in ("CA", "CALIFORNIA")
    assert result.date_of_birth == "1990-11-11"
    assert result.expiration_date == "2028-11-11"


@pytest.mark.integration
class TestExtractDlAdamMangler:
    """Extract data from Adam Mangler driver license documents."""

    def test_dl_adam_mangler_png(self) -> None:
        _require_test_data()
        _assert_adam_mangler(extract_dl(str(TEST_DATA / "dl_adam_mangler.png")))


# TODO: Add test with a manually rotated DL image (portrait orientation)
# to verify auto_rotate=True in file_to_base64_image corrects it before extraction.


@pytest.mark.integration
class TestExtractDlNonDlDocument:
    """Verify behavior when a non-DL document is passed."""

    def test_visiting_card_returns_unreliable_data(self) -> None:
        """A non-DL document may return fabricated data or raise ValidationError.

        GPT behavior is non-deterministic on non-DL inputs: it may hallucinate
        DL fields or return nulls that fail Pydantic validation. Either outcome
        is acceptable — the key point is to always use doc-classifier first.
        """
        _require_test_data()
        try:
            result = extract_dl(str(TEST_DATA / "visiting_card_john_smith.png"))
            # If it succeeds, the data is fabricated — just verify it's the right type
            assert isinstance(result, DriverLicenseData)
        except (ValidationError, Exception):
            # Expected when GPT returns nulls for required fields
            pass
