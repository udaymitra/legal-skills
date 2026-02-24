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
    "If a field is not visible, use null."
)


def extract_dl(file_path: str) -> DriverLicenseData:
    """Extract structured data from a driver license image."""
    base64_image = file_to_base64_image(file_path)
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
        print(f"OpenAI API error during DL extraction: {e}", file=sys.stderr)
        raise
    except json.JSONDecodeError as e:
        print(f"Failed to parse OpenAI response as JSON: {e}", file=sys.stderr)
        raise
    except ValidationError as e:
        print(f"Response validation failed: {e}", file=sys.stderr)
        raise


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_dl.py <file_path>")
        sys.exit(1)
    data = extract_dl(sys.argv[1])
    print(data.model_dump_json(indent=2))
