"""Tests for doc-classifier skill."""

import json
from unittest.mock import MagicMock, patch

import pytest
from openai import OpenAIError

from classify import classify_document
from legal_skills.models import ClassificationResult


def _mock_openai_response(document_type: str, confidence: float) -> MagicMock:
    """Create a mock OpenAI chat completion response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        {"document_type": document_type, "confidence": confidence}
    )
    return mock_response


@patch("classify.file_to_base64_image", return_value="fake_base64")
@patch("classify.OpenAI")
def test_classify_driver_license(mock_openai_cls: MagicMock, mock_image: MagicMock) -> None:
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_openai_response(
        "driver_license", 0.95
    )

    result = classify_document("/tmp/test_dl.jpg")

    assert isinstance(result, ClassificationResult)
    assert result.document_type == "driver_license"
    assert result.confidence == 0.95
    assert result.file_path == "/tmp/test_dl.jpg"


@patch("classify.file_to_base64_image", return_value="fake_base64")
@patch("classify.OpenAI")
def test_classify_insurance(mock_openai_cls: MagicMock, mock_image: MagicMock) -> None:
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_openai_response(
        "insurance", 0.88
    )

    result = classify_document("/tmp/test_ins.pdf")

    assert isinstance(result, ClassificationResult)
    assert result.document_type == "insurance"
    assert result.confidence == 0.88


@patch("classify.file_to_base64_image", return_value="fake_base64")
@patch("classify.OpenAI")
def test_classify_unknown(mock_openai_cls: MagicMock, mock_image: MagicMock) -> None:
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_openai_response(
        "unknown", 0.4
    )

    result = classify_document("/tmp/test_random.png")

    assert isinstance(result, ClassificationResult)
    assert result.document_type == "unknown"
    assert result.confidence == 0.4


@patch("classify.file_to_base64_image", return_value="fake_base64")
@patch("classify.OpenAI")
def test_classify_openai_error(mock_openai_cls: MagicMock, mock_image: MagicMock) -> None:
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.side_effect = OpenAIError("API error")

    with pytest.raises(OpenAIError, match="API error"):
        classify_document("/tmp/test.jpg")
