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

```bash
python doc-validator/scripts/validate.py '<dl_json>' '<insurance_json>'
```

Or import as a module:

```python
from validate import validate_documents
from legal_skills.models import DriverLicenseData, InsuranceData

dl = DriverLicenseData.model_validate_json(dl_json_str)
ins = InsuranceData.model_validate_json(ins_json_str)
report = validate_documents(dl, ins)
```

### Step 3: Interpret results

- `name_match`: True if first_name + last_name match (case-insensitive)
- `dob_match`: True if date_of_birth matches, or if either is null
- `address_match`: True if address matches (case-insensitive, whitespace-stripped)
- `match_status`: `"match"` if all checks pass, `"discrepancy"` if any fail
- `discrepancies`: List of specific fields that differ, with values from both documents

## Examples

**All fields match:**

```json
{
  "person_name": "John Smith",
  "match_status": "match",
  "name_match": true,
  "dob_match": true,
  "address_match": true,
  "discrepancies": []
}
```

**Address mismatch:**

```json
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
```

## Troubleshooting

**DOB shows as matching when values differ**
If either document has a null date_of_birth, the comparison is skipped and `dob_match` returns true. This is by design — missing data is not treated as a discrepancy.

**Name mismatch for same person**
Name comparison is case-insensitive but exact. Nicknames (e.g., "John" vs "Jonathan") will be flagged as a discrepancy.

**Required packages**
This skill requires: `pydantic>=2.0`. Install with: `pip install pydantic`.
