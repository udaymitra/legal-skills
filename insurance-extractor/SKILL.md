---
name: insurance-extractor
description: >
  This skill extracts structured data from insurance documents (PDF or image) using
  GPT-4o-mini vision. Outputs first name, last name, date of birth, address, policy
  number, vehicle make, model, year, and VIN. This skill should be used when a user
  says "extract insurance info", "parse insurance card", "read this insurance document",
  "get info from this policy", or after doc-classifier identifies a document as insurance.
---

# Insurance Document Extractor

## Workflow

### Step 1: Prepare the document

Convert the input PDF or image to a base64-encoded image:

```python
from legal_skills.image_utils import file_to_base64_image
base64_img = file_to_base64_image("/path/to/insurance.pdf")
```

Supported formats: PDF, JPEG, PNG.

### Step 2: Extract data with GPT-4o-mini vision

Run the extractor script:

```bash
python insurance-extractor/scripts/extract_insurance.py <file_path>
```

Or import as a module:

```python
from extract_insurance import extract_insurance
data = extract_insurance("/path/to/insurance.pdf")
```

Output: JSON with `file_path`, `first_name`, `last_name`, `date_of_birth` (YYYY-MM-DD or null), `address`, `policy_number` (or null), `vehicle_make` (or null), `vehicle_model` (or null), `vehicle_year` (or null), `vin` (or null).

### Step 3: Handle results

Required fields (`first_name`, `last_name`, `address`) will always be populated. All other fields may be null if not visible in the document. Insurance cards vary widely in layout, so null fields are common.

## Examples

**Extracting from an insurance card:**

Input: `extract_insurance("/input/ins.pdf")`
Output:
```json
{
  "file_path": "/input/ins.pdf",
  "first_name": "John",
  "last_name": "Smith",
  "date_of_birth": "1985-03-15",
  "address": "456 Oak Ave, Springfield, IL 62702",
  "policy_number": "POL-98765",
  "vehicle_make": "Toyota",
  "vehicle_model": "Camry",
  "vehicle_year": "2022",
  "vin": "1HGBH41JXMN109186"
}
```

## Troubleshooting

**Missing fields in output**
Insurance cards vary widely in layout. Fields not found will be null. Review the source document manually if critical fields are missing.

**"Unsupported file type" error**
The input file is not PDF, JPEG, or PNG. Convert to a supported format before extracting.

**"OpenAI API key not set" error**
Set the `OPENAI_API_KEY` environment variable or add it to a `.env` file in the project root.
