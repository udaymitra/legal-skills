"""Tests for dl-extractor skill."""
import json
from unittest.mock import patch, MagicMock

import pytest
from openai import OpenAIError

from extract_dl import extract_dl
from legal_skills.models import DriverLicenseData


def _mock_dl_response():
    """Create a mock OpenAI response with all DL fields."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "John",
        "last_name": "Smith",
        "license_number": "D1234567",
        "address": "123 Main St, Springfield, IL 62701",
        "state": "IL",
        "date_of_birth": "1985-03-15",
        "expiration_date": "2027-03-15",
    })
    return mock_response


@patch("extract_dl.file_to_base64_image", return_value="fake_base64")
@patch("extract_dl.OpenAI")
def test_extract_dl_full(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_dl_response()

    result = extract_dl("/tmp/dl.jpg")

    assert isinstance(result, DriverLicenseData)
    assert result.first_name == "John"
    assert result.last_name == "Smith"
    assert result.license_number == "D1234567"
    assert result.state == "IL"
    assert result.date_of_birth == "1985-03-15"
    assert result.expiration_date == "2027-03-15"
    assert result.file_path == "/tmp/dl.jpg"


@patch("extract_dl.file_to_base64_image", return_value="fake_base64")
@patch("extract_dl.OpenAI")
def test_extract_dl_missing_optional_fields(mock_openai_cls, mock_image):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "Jane",
        "last_name": "Doe",
        "license_number": "D9999999",
        "address": "456 Oak Ave",
        "state": "CA",
        "date_of_birth": None,
        "expiration_date": None,
    })
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = mock_response

    result = extract_dl("/tmp/dl2.jpg")

    assert result.first_name == "Jane"
    assert result.date_of_birth is None
    assert result.expiration_date is None


@patch("extract_dl.file_to_base64_image", return_value="fake_base64")
@patch("extract_dl.OpenAI")
def test_extract_dl_openai_error(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = OpenAIError("API error")

    with pytest.raises(OpenAIError, match="API error"):
        extract_dl("/tmp/dl.jpg")
