"""Extract structured data from an Insurance document."""
import json
import sys
from pathlib import Path

import openai
from openai import OpenAI
from pydantic import ValidationError
from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from legal_skills.models import InsuranceData
from legal_skills.image_utils import file_to_base64_image

load_dotenv()

EXTRACTION_PROMPT = (
    "Extract the following fields from this insurance document image. "
    "Return JSON with these exact keys: "
    "first_name, last_name, date_of_birth (YYYY-MM-DD or null), address, "
    "policy_number (or null), vehicle_make (or null), vehicle_model (or null), "
    "vehicle_year (or null), vin (or null). "
    "IMPORTANT: Only extract values that are clearly visible in the document. "
    "If a field is not visible, partially obscured, or you are not confident in the value, use null. "
    "Do NOT guess or fabricate any values. Accuracy is more important than completeness."
)


def extract_insurance(file_path: str) -> InsuranceData:
    """Extract structured data from an insurance document image."""
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
                        {"type": "text", "text": "Extract all fields from this insurance document."},
                    ],
                },
            ],
            response_format={"type": "json_object"},
            max_tokens=300,
        )
        result = json.loads(response.choices[0].message.content)
        return InsuranceData(file_path=file_path, **result)
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
        print("Usage: python extract_insurance.py <file_path>")
        sys.exit(1)
    data = extract_insurance(sys.argv[1])
    print(data.model_dump_json(indent=2))
