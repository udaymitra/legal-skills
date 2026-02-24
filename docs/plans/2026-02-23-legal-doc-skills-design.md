# Legal Document Processing Skills — Design Document

**Date:** 2026-02-23
**Status:** Approved

## Overview

Build 4 Claude Skills that process driver licenses and insurance documents using GPT-4o-mini vision. Each skill is a standalone folder with `SKILL.md` + `scripts/`, following Anthropic's skill best practices. A web UI (built separately via Claude Code) will orchestrate the skills as an integration test.

## Architecture

```
Files (PDF/JPEG) → Skill 1: Classify → Route by type
                                         ├─ DL → Skill 2: Extract DL data
                                         └─ Insurance → Skill 3: Extract insurance data
                                                          │
                    Web app pairs DL + Insurance ◄────────┘
                              │
                              ▼
                    Skill 4: Validate pair → Discrepancy report
```

### Project Structure

```
legal_skills/
├── environment.yml
├── doc-classifier/
│   ├── SKILL.md
│   └── scripts/
│       └── classify.py
├── dl-extractor/
│   ├── SKILL.md
│   └── scripts/
│       └── extract_dl.py
├── insurance-extractor/
│   ├── SKILL.md
│   └── scripts/
│       └── extract_insurance.py
├── doc-validator/
│   ├── SKILL.md
│   └── scripts/
│       └── validate.py
└── docs/
    └── plans/
        └── 2026-02-23-legal-doc-skills-design.md
```

### Shared Dependencies (environment.yml)

- `python=3.11`
- `openai` — GPT-4o-mini API calls
- `pdf2image` + `poppler` — PDF to image conversion
- `Pillow` — image handling
- `pydantic` — structured output models

## Skills

### Skill 1: doc-classifier

**Frontmatter:**
```yaml
---
name: doc-classifier
description: Classifies uploaded PDF or image documents as either a Driver License or Insurance document using GPT-4o-mini vision. Use when user uploads documents and says "classify", "what type of document is this", "sort these documents", or "identify document type".
---
```

**Input:** File path to a PDF or image (JPEG/PNG)

**Process:** Convert PDF to image if needed, base64-encode, send to GPT-4o-mini vision with classification prompt.

**Output:**
```json
{
  "file_path": "/input/doc1.pdf",
  "document_type": "driver_license",
  "confidence": 0.97
}
```

**Data Model:**
```python
class ClassificationResult(BaseModel):
    file_path: str
    document_type: Literal["driver_license", "insurance", "unknown"]
    confidence: float
```

---

### Skill 2: dl-extractor

**Frontmatter:**
```yaml
---
name: dl-extractor
description: Extracts structured data from Driver License documents (PDF or image) using GPT-4o-mini vision. Outputs first name, last name, license number, address, state, DOB, expiration. Use when user says "extract driver license", "parse DL", "read this license", or after doc-classifier identifies a document as a driver license.
---
```

**Input:** File path to a driver license PDF or image.

**Process:** Send image to GPT-4o-mini vision with structured extraction prompt.

**Output:**
```json
{
  "file_path": "/input/doc1.pdf",
  "first_name": "John",
  "last_name": "Smith",
  "license_number": "D1234567",
  "address": "123 Main St, Springfield, IL 62701",
  "state": "IL",
  "date_of_birth": "1985-03-15",
  "expiration_date": "2027-03-15"
}
```

**Data Model:**
```python
class DriverLicenseData(BaseModel):
    file_path: str
    first_name: str
    last_name: str
    license_number: str
    address: str
    state: str
    date_of_birth: str | None
    expiration_date: str | None
```

---

### Skill 3: insurance-extractor

**Frontmatter:**
```yaml
---
name: insurance-extractor
description: Extracts structured data from insurance documents (PDF or image) using GPT-4o-mini vision. Outputs first name, last name, DOB, address, policy number, vehicle details, VIN. Use when user says "extract insurance info", "parse insurance card", or after doc-classifier identifies a document as insurance.
---
```

**Input:** File path to an insurance document PDF or image.

**Process:** Send image to GPT-4o-mini vision with structured extraction prompt.

**Output:**
```json
{
  "file_path": "/input/doc2.pdf",
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

**Data Model:**
```python
class InsuranceData(BaseModel):
    file_path: str
    first_name: str
    last_name: str
    date_of_birth: str | None
    address: str
    policy_number: str | None
    vehicle_make: str | None
    vehicle_model: str | None
    vehicle_year: str | None
    vin: str | None
```

---

### Skill 4: doc-validator

**Frontmatter:**
```yaml
---
name: doc-validator
description: Compares extracted Driver License and Insurance data for discrepancies in name, date of birth, and address. Takes two pre-paired JSON documents as input. Use when user says "validate documents", "check for mismatches", "compare DL and insurance", or after extraction is complete.
---
```

**Input:** One `DriverLicenseData` JSON + one `InsuranceData` JSON (already paired by the caller/orchestration layer).

**Process:** Compare name, DOB, and address fields. No matching/pairing logic — that belongs to the orchestration layer.

**Output:**
```json
{
  "person_name": "John Smith",
  "name_match": true,
  "dob_match": true,
  "address_match": false,
  "match_status": "discrepancy",
  "discrepancies": [
    {
      "field_name": "address",
      "dl_value": "123 Main St, Springfield, IL 62701",
      "insurance_value": "456 Oak Ave, Springfield, IL 62702"
    }
  ],
  "dl_source": "/input/doc1.pdf",
  "insurance_source": "/input/doc2.pdf"
}
```

**Data Models:**
```python
class FieldDiscrepancy(BaseModel):
    field_name: str
    dl_value: str
    insurance_value: str

class ValidationReport(BaseModel):
    person_name: str
    name_match: bool
    dob_match: bool
    address_match: bool
    match_status: Literal["match", "discrepancy", "unmatched"]
    discrepancies: list[FieldDiscrepancy]
    dl_source: str
    insurance_source: str
```

## Integration Test: Web UI

After Skills 1-4 are built, use Claude Code to build a web app that:

1. Accepts file uploads (drag-and-drop PDF/JPEG)
2. Runs Skill 1 to classify each document
3. Routes DLs to Skill 2, insurance docs to Skill 3
4. Lets the user pair DL + insurance results (or auto-pairs by name)
5. Runs Skill 4 on each pair
6. Displays the full validation report with discrepancies highlighted

This validates that all skills are truly modular and composable.

## Design Decisions

- **GPT-4o-mini vision** chosen for cost efficiency on structured documents
- **Pydantic models** for type-safe structured output via OpenAI's `response_format`
- **No orchestrator skill** — the web app handles pairing and routing, keeping skills single-responsibility
- **Scripts are importable modules** — each script exposes a function (e.g., `classify_document(file_path) -> ClassificationResult`) so the web app can call them directly
- **PDF handling** via `pdf2image` + `poppler` — converts PDF pages to images before sending to vision API
