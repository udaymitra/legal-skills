"""Classify a document as Driver License, Insurance, or Unknown."""

import json
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

# Add project root to path so we can import shared modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from legal_skills.image_utils import file_to_base64_image
from legal_skills.models import ClassificationResult

load_dotenv()


def classify_document(file_path: str) -> ClassificationResult:
    """Classify a document image as driver_license, insurance, or unknown."""
    base64_image = file_to_base64_image(file_path)
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a document classifier. Examine the image and determine "
                    "if it is a Driver License or an Insurance document. "
                    'Respond with JSON: {"document_type": "driver_license" | "insurance" | "unknown", "confidence": 0.0-1.0}'
                ),
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                        },
                    },
                    {
                        "type": "text",
                        "text": "Classify this document. Is it a driver license or insurance document?",
                    },
                ],
            },
        ],
        response_format={"type": "json_object"},
        max_tokens=100,
    )

    result = json.loads(response.choices[0].message.content)
    return ClassificationResult(
        file_path=file_path,
        document_type=result.get("document_type", "unknown"),
        confidence=result.get("confidence", 0.0),
    )


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python classify.py <file_path>", file=sys.stderr)
        sys.exit(1)
    result = classify_document(sys.argv[1])
    print(result.model_dump_json(indent=2))
