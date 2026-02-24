"""Integration tests for doc-classifier skill using real documents and OpenAI API."""

from pathlib import Path

import pytest

from classify import classify_document

TEST_DATA = Path(__file__).resolve().parent.parent / "test_data"


def _require_test_data() -> None:
    """Skip if test_data directory is missing."""
    if not TEST_DATA.exists():
        pytest.skip("test_data/ directory not found")


@pytest.mark.integration
class TestClassifyDriverLicenses:
    """Classify real driver license documents."""

    def test_dl_john_smith_png(self) -> None:
        _require_test_data()
        result = classify_document(str(TEST_DATA / "dl_john_smith.png"))
        assert result.document_type == "driver_license"
        assert result.confidence >= 0.7

    def test_dl_john_smith_pdf(self) -> None:
        _require_test_data()
        result = classify_document(str(TEST_DATA / "dl_john_smith.pdf"))
        assert result.document_type == "driver_license"
        assert result.confidence >= 0.7

    def test_dl_adam_mangler_png(self) -> None:
        _require_test_data()
        result = classify_document(str(TEST_DATA / "dl_adam_mangler.png"))
        assert result.document_type == "driver_license"
        assert result.confidence >= 0.7


@pytest.mark.integration
class TestClassifyInsurance:
    """Classify real insurance documents."""

    def test_insurance_adam_mangler_pdf(self) -> None:
        _require_test_data()
        result = classify_document(str(TEST_DATA / "insurance_adam_mangler.pdf"))
        assert result.document_type == "insurance"
        assert result.confidence >= 0.7

    def test_insurance_john_smith_png(self) -> None:
        _require_test_data()
        result = classify_document(str(TEST_DATA / "insurance_john_smith.png"))
        assert result.document_type == "insurance"
        assert result.confidence >= 0.7

    def test_insurance_adam_mangler_png(self) -> None:
        _require_test_data()
        result = classify_document(str(TEST_DATA / "insurance_adam_mangler.png"))
        assert result.document_type == "insurance"
        assert result.confidence >= 0.7


@pytest.mark.integration
class TestClassifyNegative:
    """Classify documents that are neither DL nor insurance."""

    def test_visiting_card_is_unknown(self) -> None:
        _require_test_data()
        result = classify_document(str(TEST_DATA / "visiting_card_john_smith.png"))
        assert result.document_type == "unknown"
