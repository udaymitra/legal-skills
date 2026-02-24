"""Extract structured data from a Driver License document."""
import json
import sys
from pathlib import Path

import openai
from openai import OpenAI
from pydantic import ValidationError
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from legal_skills.models import DriverLicenseData
from legal_skills.image_utils import file_to_base64_image

load_dotenv()

EXTRACTION_PROMPT = (
    "Extract the following fields from this Driver License image. "
    "Return JSON with these exact keys: "
    "first_name, last_name, license_number, address, state, date_of_birth (YYYY-MM-DD or null), "
    "expiration_date (YYYY-MM-DD or null). "
    "IMPORTANT: Only extract values that are clearly visible in the document. "
    "If a field is not visible, partially obscured, or you are not confident in the value, use null. "
    "Do NOT guess or fabricate any values. Accuracy is more important than completeness."
)


def extract_dl(file_path: str) -> DriverLicenseData:
    """Extract structured data from a driver license image."""
    base64_image = file_to_base64_image(file_path, auto_rotate=True)
    client = OpenAI()

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": EXTRACTION_PROMPT},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                        },
                        {"type": "text", "text": "Extract all fields from this driver license."},
                    ],
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=300,
        )
        result = json.loads(response.choices[0].message.content)
        return DriverLicenseData(file_path=file_path, **result)
    except openai.OpenAIError as e:
        print(f"OpenAI API call failed: {e}", file=sys.stderr)
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse OpenAI response as JSON: {e}", file=sys.stderr)
        raise
    except ValidationError as e:
        print(f"OpenAI response failed Pydantic validation: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_dl.py <file_path>")
        sys.exit(1)
    data = extract_dl(sys.argv[1])
    print(data.model_dump_json(indent=2))
