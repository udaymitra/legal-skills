"""Tests for insurance-extractor skill."""
import json
from unittest.mock import patch, MagicMock

import pytest
from openai import OpenAIError

from extract_insurance import extract_insurance
from legal_skills.models import InsuranceData


def _mock_insurance_response():
    """Create a mock OpenAI response with all insurance fields."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1985-03-15",
        "address": "456 Oak Ave, Springfield, IL 62702",
        "policy_number": "POL-98765",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": "2022",
        "vin": "1HGBH41JXMN109186",
    })
    return mock_response


@patch("extract_insurance.file_to_base64_image", return_value="fake_base64")
@patch("extract_insurance.OpenAI")
def test_extract_insurance_full(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_insurance_response()

    result = extract_insurance("/tmp/ins.pdf")

    assert isinstance(result, InsuranceData)
    assert result.first_name == "John"
    assert result.last_name == "Smith"
    assert result.policy_number == "POL-98765"
    assert result.vehicle_make == "Toyota"
    assert result.vehicle_model == "Camry"
    assert result.vehicle_year == "2022"
    assert result.vin == "1HGBH41JXMN109186"
    assert result.file_path == "/tmp/ins.pdf"


@patch("extract_insurance.file_to_base64_image", return_value="fake_base64")
@patch("extract_insurance.OpenAI")
def test_extract_insurance_minimal(mock_openai_cls, mock_image):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": None,
        "address": "789 Pine Rd",
        "policy_number": None,
        "vehicle_make": None,
        "vehicle_model": None,
        "vehicle_year": None,
        "vin": None,
    })
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = mock_response

    result = extract_insurance("/tmp/ins2.pdf")

    assert result.first_name == "Jane"
    assert result.policy_number is None
    assert result.vehicle_make is None
    assert result.vin is None


@patch("extract_insurance.file_to_base64_image", return_value="fake_base64")
@patch("extract_insurance.OpenAI")
def test_extract_insurance_openai_error(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = OpenAIError("API error")

    with pytest.raises(OpenAIError, match="API error"):
        extract_insurance("/tmp/ins.pdf")
