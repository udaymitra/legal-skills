# Corrected SKILL.md templates for remaining skills
# Following Anthropic best practices: third-person description, imperative body,
# specific trigger phrases, progressive disclosure

---

## dl-extractor/SKILL.md

```markdown
---
name: dl-extractor
description: >
  This skill extracts structured data from Driver License documents (PDF or image)
  using GPT-4o-mini vision. Outputs first name, last name, license number, address,
  state, date of birth, and expiration date. This skill should be used when a user
  says "extract driver license", "parse DL", "read this license", "get info from
  this license", "what does this driver license say", or after doc-classifier
  identifies a document as a driver license.
---

# Driver License Extractor

## Workflow

### Step 1: Prepare the document

Convert the input PDF or image to a base64-encoded image:

\```python
from legal_skills.image_utils import file_to_base64_image
base64_img = file_to_base64_image("/path/to/dl.pdf")
\```

Supported formats: PDF, JPEG, PNG.

### Step 2: Extract data with GPT-4o-mini vision

Run the extractor script:

\```bash
python dl-extractor/scripts/extract_dl.py <file_path>
\```

Or import as a module:

\```python
from extract_dl import extract_dl
data = extract_dl("/path/to/dl.pdf")
\```

Output: JSON with `file_path`, `first_name`, `last_name`, `license_number`, `address`, `state`, `date_of_birth` (YYYY-MM-DD or null), `expiration_date` (YYYY-MM-DD or null).

### Step 3: Handle results

All required fields (`first_name`, `last_name`, `license_number`, `address`, `state`) will always be populated. Optional fields (`date_of_birth`, `expiration_date`) may be null if not visible in the document.

## Examples

**Extracting from a clear driver license scan:**

Input: `extract_dl("/input/dl.jpg")`
Output:
\```json
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
\```

## Troubleshooting

**"Unsupported file type" error**
The input file is not PDF, JPEG, or PNG. Convert to a supported format before extracting.

**Missing fields in output**
Poor image quality or obscured text may prevent extraction. Try with a clearer scan.

**"OpenAI API key not set" error**
Set the `OPENAI_API_KEY` environment variable or add it to a `.env` file in the project root.
```

---

## insurance-extractor/SKILL.md

```markdown
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

\```python
from legal_skills.image_utils import file_to_base64_image
base64_img = file_to_base64_image("/path/to/insurance.pdf")
\```

Supported formats: PDF, JPEG, PNG.

### Step 2: Extract data with GPT-4o-mini vision

Run the extractor script:

\```bash
python insurance-extractor/scripts/extract_insurance.py <file_path>
\```

Or import as a module:

\```python
from extract_insurance import extract_insurance
data = extract_insurance("/path/to/insurance.pdf")
\```

Output: JSON with `file_path`, `first_name`, `last_name`, `date_of_birth` (YYYY-MM-DD or null), `address`, `policy_number` (or null), `vehicle_make` (or null), `vehicle_model` (or null), `vehicle_year` (or null), `vin` (or null).

### Step 3: Handle results

Required fields (`first_name`, `last_name`, `address`) will always be populated. All other fields may be null if not visible in the document. Insurance cards vary widely in layout, so null fields are common.

## Examples

**Extracting from an insurance card:**

Input: `extract_insurance("/input/ins.pdf")`
Output:
\```json
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
\```

## Troubleshooting

**Missing fields in output**
Insurance cards vary widely in layout. Fields not found will be null. Review the source document manually if critical fields are missing.

**"Unsupported file type" error**
The input file is not PDF, JPEG, or PNG. Convert to a supported format before extracting.

**"OpenAI API key not set" error**
Set the `OPENAI_API_KEY` environment variable or add it to a `.env` file in the project root.
```

---

## doc-validator/SKILL.md

```markdown
---
name: doc-validator
description: >
  This skill compares extracted Driver License and Insurance data for discrepancies
  in name, date of birth, and address. Takes two pre-paired JSON documents as input
  (pairing is done by the calling application, not this skill). This skill should be
  used when a user says "validate documents", "check for mismatches", "compare DL and
  insurance", "find discrepancies", "do these documents match", or after extraction
  is complete for a paired set of documents.
---

# Document Validator

## Workflow

### Step 1: Prepare inputs

Provide two JSON objects: one `DriverLicenseData` and one `InsuranceData`, already paired by the calling application. This skill does NOT perform matching or pairing — it only compares pre-paired data.

### Step 2: Run validation

Run the validator script:

\```bash
python doc-validator/scripts/validate.py '<dl_json>' '<insurance_json>'
\```

Or import as a module:

\```python
from validate import validate_documents
from legal_skills.models import DriverLicenseData, InsuranceData

dl = DriverLicenseData.model_validate_json(dl_json_str)
ins = InsuranceData.model_validate_json(ins_json_str)
report = validate_documents(dl, ins)
\```

### Step 3: Interpret results

- `name_match`: True if first_name + last_name match (case-insensitive)
- `dob_match`: True if date_of_birth matches, or if either is null
- `address_match`: True if address matches (case-insensitive, whitespace-stripped)
- `match_status`: `"match"` if all checks pass, `"discrepancy"` if any fail
- `discrepancies`: List of specific fields that differ, with values from both documents

## Examples

**All fields match:**

\```json
{
  "person_name": "John Smith",
  "match_status": "match",
  "name_match": true,
  "dob_match": true,
  "address_match": true,
  "discrepancies": []
}
\```

**Address mismatch:**

\```json
{
  "person_name": "John Smith",
  "match_status": "discrepancy",
  "name_match": true,
  "dob_match": true,
  "address_match": false,
  "discrepancies": [
    {"field_name": "address", "dl_value": "123 Main St", "insurance_value": "456 Oak Ave"}
  ]
}
\```

## Troubleshooting

**DOB shows as matching when values differ**
If either document has a null date_of_birth, the comparison is skipped and `dob_match` returns true. This is by design — missing data is not treated as a discrepancy.

**Name mismatch for same person**
Name comparison is case-insensitive but exact. Nicknames (e.g., "John" vs "Jonathan") will be flagged as a discrepancy.
```
