---
name: dl-extractor
description: >
  This skill extracts structured data from Driver License documents (PDF or image)
  using GPT-4o-mini vision. It outputs first name, last name, license number, address,
  state, date of birth, and expiration date. This skill should be used when a user
  says "extract driver license", "parse DL", "read this license", "get info from
  this license", "what does this driver license say", or after doc-classifier
  identifies a document as a driver license.
---

# Driver License Extractor

## Workflow

### Step 1: Prepare the document

Convert the input PDF or image to a base64-encoded image:

```python
from legal_skills.image_utils import file_to_base64_image
base64_img = file_to_base64_image("/path/to/dl.pdf")
```

Supported formats: PDF, JPEG, PNG.

### Step 2: Extract data with GPT-4o-mini vision

Run the extractor script:

```bash
python dl-extractor/scripts/extract_dl.py <file_path>
```

Or import as a module:

```python
from extract_dl import extract_dl
data = extract_dl("/path/to/dl.pdf")
```

Output: JSON with `file_path`, `first_name`, `last_name`, `license_number`, `address`, `state`, `date_of_birth` (YYYY-MM-DD or null), `expiration_date` (YYYY-MM-DD or null).

### Step 3: Handle results

All required fields (`first_name`, `last_name`, `license_number`, `address`, `state`) will always be populated. Optional fields (`date_of_birth`, `expiration_date`) may be null if not visible in the document.

## Examples

**Extracting from a driver license scan:**

Input: `extract_dl("/input/dl.jpg")`
Output:
```json
{
  "file_path": "/input/dl.jpg",
  "first_name": "John",
  "last_name": "Smith",
  "license_number": "D1234567",
  "address": "123 Main St, Springfield, IL 62701",
  "state": "IL",
  "date_of_birth": "1985-03-15",
  "expiration_date": "2027-03-15"
}
```

## Troubleshooting

**"Unsupported file type" error**
The input file is not PDF, JPEG, or PNG. Convert to a supported format before extracting.

**Missing fields in output**
Poor image quality or obscured text may prevent extraction. Try with a clearer scan.

**"OpenAI API key not set" error**
Set the `OPENAI_API_KEY` environment variable or add it to a `.env` file in the project root.

**Required packages**
This skill requires: `openai`, `pydantic>=2.0`, `python-dotenv`, `pdf2image`, `Pillow`. The system package `poppler` is also required for PDF support. Install with: `pip install openai pydantic python-dotenv pdf2image Pillow`.
