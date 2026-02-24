# Legal Document Processing Skills — Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build 4 Claude Skills (doc-classifier, dl-extractor, insurance-extractor, doc-validator) that process driver licenses and insurance documents using GPT-4o-mini vision, with importable Python scripts in each skill folder.

**Architecture:** Each skill is a folder with `SKILL.md` (YAML frontmatter + instructions) and `scripts/` containing Python modules that call GPT-4o-mini vision. A shared `models.py` at the project root defines all Pydantic data models. Scripts are importable functions so a web app can compose them later.

**Tech Stack:** Python 3.11, OpenAI SDK (GPT-4o-mini vision), Pydantic, pdf2image, Pillow, pytest, ruff, mypy

**Design doc:** `docs/plans/2026-02-23-legal-doc-skills-design.md`

**Skill scaffolding tool:** Use Anthropic's `skill-creator` scripts for all skill creation:
- `INIT_SKILL=/Users/uday/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts/init_skill.py`
- `PACKAGE_SKILL=/Users/uday/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts/package_skill.py`
- `VALIDATE_SKILL=/Users/uday/.claude/plugins/marketplaces/anthropic-agent-skills/skills/skill-creator/scripts/quick_validate.py`

---

## Progress Tracker

- [x] **Task 1:** Project Setup — CLAUDE.md, deps, shared models, tests (5 passing)
- [x] **Task 1b:** Git init, .gitignore, initial commit, push to GitHub
- [ ] **Task 2:** Skill 1 — doc-classifier (SKILL.md, classify.py, tests)
- [ ] **Task 3:** Skill 2 — dl-extractor (SKILL.md, extract_dl.py, tests)
- [ ] **Task 4:** Skill 3 — insurance-extractor (SKILL.md, extract_insurance.py, tests)
- [ ] **Task 5:** Skill 4 — doc-validator (SKILL.md, validate.py, tests)
- [ ] **Task 6:** Validate all skills, full test suite, package skills
- [ ] **Task 7:** Manual integration test with real docs
- [ ] **Task 8:** Build web UI integration test

---

### Task 1: Project Setup — Dependencies and Shared Models

**Files:**
- Create: `CLAUDE.md`
- Modify: `environment.yml`
- Create: `pyproject.toml`
- Create: `legal_skills/__init__.py`
- Create: `legal_skills/models.py`
- Create: `legal_skills/image_utils.py`
- Create: `tests/__init__.py`
- Create: `tests/test_models.py`

**Step 0: Create CLAUDE.md with project rules**

Create `CLAUDE.md` at the project root with the full project conventions document (see approved CLAUDE.md content from brainstorming session). This includes:
- Tech stack definition
- Architecture pattern (skill-based separation)
- File organization
- Naming conventions
- Commands
- Skill script conventions
- Error handling rules
- Code quality standards
- Testing requirements
- Pre-commit review process

**Step 1: Update environment.yml with all dependencies**

```yaml
name: legal_skills
dependencies:
  - python=3.11
  - pip
  - poppler
  - pip:
    - openai
    - pydantic>=2.0
    - pdf2image
    - Pillow
    - pytest
    - python-dotenv
    - ruff
    - mypy
```

**Step 2: Create pyproject.toml for the project**

```toml
[project]
name = "legal-skills"
version = "0.1.0"
requires-python = ">=3.11"

[tool.pytest.ini_options]
testpaths = ["tests"]
```

**Step 3: Create legal_skills/models.py with all Pydantic models**

```python
from __future__ import annotations
from typing import Literal
from pydantic import BaseModel


class ClassificationResult(BaseModel):
    file_path: str
    document_type: Literal["driver_license", "insurance", "unknown"]
    confidence: float


class DriverLicenseData(BaseModel):
    file_path: str
    first_name: str
    last_name: str
    license_number: str
    address: str
    state: str
    date_of_birth: str | None = None
    expiration_date: str | None = None


class InsuranceData(BaseModel):
    file_path: str
    first_name: str
    last_name: str
    date_of_birth: str | None = None
    address: str
    policy_number: str | None = None
    vehicle_make: str | None = None
    vehicle_model: str | None = None
    vehicle_year: str | None = None
    vin: str | None = None


class FieldDiscrepancy(BaseModel):
    field_name: str
    dl_value: str
    insurance_value: str


class ValidationReport(BaseModel):
    person_name: str
    name_match: bool
    dob_match: bool
    address_match: bool
    match_status: Literal["match", "discrepancy"]
    discrepancies: list[FieldDiscrepancy]
    dl_source: str
    insurance_source: str
```

**Step 4: Create legal_skills/image_utils.py — shared image handling**

```python
import base64
from pathlib import Path
from pdf2image import convert_from_path
from PIL import Image
import io


def file_to_base64_image(file_path: str) -> str:
    """Convert a PDF or image file to a base64-encoded PNG string."""
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        images = convert_from_path(str(path), first_page=1, last_page=1)
        img = images[0]
    elif suffix in (".jpg", ".jpeg", ".png"):
        img = Image.open(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
```

**Step 5: Create legal_skills/__init__.py**

```python
"""Legal Skills — document processing with GPT-4o-mini vision."""
```

**Step 6: Write tests for models**

```python
# tests/test_models.py
from legal_skills.models import (
    ClassificationResult,
    DriverLicenseData,
    InsuranceData,
    FieldDiscrepancy,
    ValidationReport,
)


def test_classification_result():
    result = ClassificationResult(
        file_path="/tmp/test.pdf",
        document_type="driver_license",
        confidence=0.95,
    )
    assert result.document_type == "driver_license"
    assert result.confidence == 0.95


def test_driver_license_data_optional_fields():
    dl = DriverLicenseData(
        file_path="/tmp/dl.pdf",
        first_name="John",
        last_name="Smith",
        license_number="D123",
        address="123 Main St",
        state="IL",
    )
    assert dl.date_of_birth is None
    assert dl.expiration_date is None


def test_insurance_data_optional_fields():
    ins = InsuranceData(
        file_path="/tmp/ins.pdf",
        first_name="John",
        last_name="Smith",
        address="123 Main St",
    )
    assert ins.date_of_birth is None
    assert ins.vehicle_make is None


def test_validation_report_with_discrepancy():
    report = ValidationReport(
        person_name="John Smith",
        name_match=True,
        dob_match=True,
        address_match=False,
        match_status="discrepancy",
        discrepancies=[
            FieldDiscrepancy(
                field_name="address",
                dl_value="123 Main St",
                insurance_value="456 Oak Ave",
            )
        ],
        dl_source="/tmp/dl.pdf",
        insurance_source="/tmp/ins.pdf",
    )
    assert report.match_status == "discrepancy"
    assert len(report.discrepancies) == 1


def test_validation_report_all_match():
    report = ValidationReport(
        person_name="Jane Doe",
        name_match=True,
        dob_match=True,
        address_match=True,
        match_status="match",
        discrepancies=[],
        dl_source="/tmp/dl.pdf",
        insurance_source="/tmp/ins.pdf",
    )
    assert report.match_status == "match"
    assert len(report.discrepancies) == 0
```

**Step 7: Run tests to verify models work**

Run: `cd /usr/local/code/legal_skills && python -m pytest tests/test_models.py -v`
Expected: All 5 tests PASS

**Step 8: Create tests/__init__.py**

Empty file.

**Step 9: Commit**

```bash
git add environment.yml pyproject.toml legal_skills/ tests/
git commit -m "feat: add project setup with shared Pydantic models and image utils"
```

---

### Task 2: Skill 1 — doc-classifier

**Files:**
- Create: `doc-classifier/SKILL.md`
- Create: `doc-classifier/scripts/__init__.py`
- Create: `doc-classifier/scripts/classify.py`
- Create: `tests/test_classify.py`

**Step 0: Scaffold the skill with init_skill.py**

```bash
$INIT_SKILL doc-classifier --path /usr/local/code/legal_skills
```

This creates the `doc-classifier/` folder with template SKILL.md, scripts/, references/, assets/. Delete any example files not needed (`references/`, `assets/` dirs if empty).

**Step 1: Edit doc-classifier/SKILL.md (replace template content)**

```markdown
---
name: doc-classifier
description: Classifies uploaded PDF or image documents as either a Driver License or Insurance document using GPT-4o-mini vision. Use when user uploads documents and says "classify", "what type of document is this", "sort these documents", or "identify document type".
---

# Document Classifier

## Instructions

### Step 1: Prepare the document
Convert the input PDF or image to a base64-encoded image using `legal_skills.image_utils.file_to_base64_image()`.

### Step 2: Classify with GPT-4o-mini vision
Run: `python doc-classifier/scripts/classify.py <file_path>`

Expected output: JSON with `file_path`, `document_type`, and `confidence`.

### Step 3: Interpret results
- `driver_license`: Route to dl-extractor skill
- `insurance`: Route to insurance-extractor skill
- `unknown`: Flag for manual review

## Examples

Example 1: Classifying a driver license scan
User says: "What type of document is this?"
Action: Run classify.py on the uploaded file
Result: `{"file_path": "/input/doc.pdf", "document_type": "driver_license", "confidence": 0.97}`

## Troubleshooting

Error: "Unsupported file type"
Cause: File is not PDF, JPEG, or PNG
Solution: Convert to a supported format first

Error: OpenAI API key not set
Cause: OPENAI_API_KEY environment variable missing
Solution: Set `export OPENAI_API_KEY=your-key` or add to `.env` file
```

**Step 2: Create doc-classifier/scripts/classify.py**

```python
"""Classify a document as Driver License, Insurance, or Unknown."""
import json
import sys
from pathlib import Path

from openai import OpenAI
from dotenv import load_dotenv

# Add project root to path so we can import shared modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from legal_skills.models import ClassificationResult
from legal_skills.image_utils import file_to_base64_image

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
                    "Respond with JSON: {\"document_type\": \"driver_license\" | \"insurance\" | \"unknown\", \"confidence\": 0.0-1.0}"
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
        print("Usage: python classify.py <file_path>")
        sys.exit(1)
    result = classify_document(sys.argv[1])
    print(result.model_dump_json(indent=2))
```

**Step 3: Create doc-classifier/scripts/__init__.py**

Empty file.

**Step 4: Write tests for classify (with mocked OpenAI)**

```python
# tests/test_classify.py
import json
from unittest.mock import patch, MagicMock

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from doc_classifier_scripts import classify_document
from legal_skills.models import ClassificationResult


def _mock_openai_response(document_type: str, confidence: float):
    """Create a mock OpenAI chat completion response."""
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        {"document_type": document_type, "confidence": confidence}
    )
    return mock_response


@patch("doc_classifier_scripts.file_to_base64_image", return_value="fake_base64")
@patch("doc_classifier_scripts.OpenAI")
def test_classify_driver_license(mock_openai_cls, mock_image):
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


@patch("doc_classifier_scripts.file_to_base64_image", return_value="fake_base64")
@patch("doc_classifier_scripts.OpenAI")
def test_classify_insurance(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_openai_response(
        "insurance", 0.88
    )

    result = classify_document("/tmp/test_ins.pdf")

    assert isinstance(result, ClassificationResult)
    assert result.document_type == "insurance"
    assert result.confidence == 0.88
```

> **Note on test imports:** Tests import from a `doc_classifier_scripts` module. We'll need a `conftest.py` that adds the script paths. Simpler approach: make `classify_document` importable by adding the scripts dir to `sys.path` in conftest. See Step 5.

**Step 5: Create tests/conftest.py for script import paths**

```python
# tests/conftest.py
import sys
from pathlib import Path

# Add each skill's scripts/ dir to sys.path so tests can import them
project_root = Path(__file__).resolve().parent.parent
for skill_dir in ["doc-classifier", "dl-extractor", "insurance-extractor", "doc-validator"]:
    scripts_dir = project_root / skill_dir / "scripts"
    if scripts_dir.exists():
        sys.path.insert(0, str(scripts_dir))

# Also make imports work with underscore names
# e.g., "from classify import classify_document"
```

> **Important:** Since Python can't import from paths with hyphens, the tests will import the script module directly by filename. Update tests to use `from classify import classify_document` instead of `doc_classifier_scripts`. The conftest adds script dirs to sys.path.

**Step 5b: Revise test imports to match conftest approach**

```python
# tests/test_classify.py
import json
from unittest.mock import patch, MagicMock

from classify import classify_document
from legal_skills.models import ClassificationResult


def _mock_openai_response(document_type: str, confidence: float):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps(
        {"document_type": document_type, "confidence": confidence}
    )
    return mock_response


@patch("classify.file_to_base64_image", return_value="fake_base64")
@patch("classify.OpenAI")
def test_classify_driver_license(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_openai_response(
        "driver_license", 0.95
    )
    result = classify_document("/tmp/test_dl.jpg")
    assert isinstance(result, ClassificationResult)
    assert result.document_type == "driver_license"
    assert result.confidence == 0.95


@patch("classify.file_to_base64_image", return_value="fake_base64")
@patch("classify.OpenAI")
def test_classify_insurance(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_openai_response(
        "insurance", 0.88
    )
    result = classify_document("/tmp/test_ins.pdf")
    assert result.document_type == "insurance"
    assert result.confidence == 0.88
```

**Step 6: Run tests**

Run: `cd /usr/local/code/legal_skills && python -m pytest tests/test_classify.py -v`
Expected: 2 tests PASS

**Step 7: Commit**

```bash
git add doc-classifier/ tests/test_classify.py tests/conftest.py
git commit -m "feat: add doc-classifier skill with SKILL.md and classify.py"
```

---

### Task 3: Skill 2 — dl-extractor

**Files:**
- Create: `dl-extractor/SKILL.md`
- Create: `dl-extractor/scripts/__init__.py`
- Create: `dl-extractor/scripts/extract_dl.py`
- Create: `tests/test_extract_dl.py`

**Step 0: Scaffold the skill with init_skill.py**

```bash
$INIT_SKILL dl-extractor --path /usr/local/code/legal_skills
```

Delete unused example files from references/ and assets/.

**Step 1: Edit dl-extractor/SKILL.md (replace template content)**

```markdown
---
name: dl-extractor
description: Extracts structured data from Driver License documents (PDF or image) using GPT-4o-mini vision. Outputs first name, last name, license number, address, state, DOB, expiration. Use when user says "extract driver license", "parse DL", "read this license", or after doc-classifier identifies a document as a driver license.
---

# Driver License Extractor

## Instructions

### Step 1: Prepare the document
Convert input to base64 image using `legal_skills.image_utils.file_to_base64_image()`.

### Step 2: Extract data with GPT-4o-mini vision
Run: `python dl-extractor/scripts/extract_dl.py <file_path>`

Expected output: JSON with first_name, last_name, license_number, address, state, date_of_birth, expiration_date.

## Examples

User says: "Extract the info from this driver license"
Result:
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

Error: "Unsupported file type"
Cause: File is not PDF, JPEG, or PNG
Solution: Convert to supported format

Error: Missing fields in output
Cause: Poor image quality or obscured text
Solution: Try with a clearer scan
```

**Step 2: Create dl-extractor/scripts/extract_dl.py**

```python
"""Extract structured data from a Driver License document."""
import json
import sys
from pathlib import Path

from openai import OpenAI
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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_dl.py <file_path>")
        sys.exit(1)
    data = extract_dl(sys.argv[1])
    print(data.model_dump_json(indent=2))
```

**Step 3: Create dl-extractor/scripts/__init__.py**

Empty file.

**Step 4: Write tests (mocked OpenAI)**

```python
# tests/test_extract_dl.py
import json
from unittest.mock import patch, MagicMock

from extract_dl import extract_dl
from legal_skills.models import DriverLicenseData


def _mock_dl_response():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "John",
        "last_name": "Smith",
        "license_number": "D1234567",
        "address": "123 Main St, Springfield, IL 62701",
        "state": "IL",
        "date_of_birth": "1985-03-15",
        "expiration_date": "2027-03-15",
    })
    return mock_response


@patch("extract_dl.file_to_base64_image", return_value="fake_base64")
@patch("extract_dl.OpenAI")
def test_extract_dl_full(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_dl_response()

    result = extract_dl("/tmp/dl.jpg")

    assert isinstance(result, DriverLicenseData)
    assert result.first_name == "John"
    assert result.last_name == "Smith"
    assert result.license_number == "D1234567"
    assert result.state == "IL"
    assert result.date_of_birth == "1985-03-15"


@patch("extract_dl.file_to_base64_image", return_value="fake_base64")
@patch("extract_dl.OpenAI")
def test_extract_dl_missing_optional_fields(mock_openai_cls, mock_image):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "Jane",
        "last_name": "Doe",
        "license_number": "D9999999",
        "address": "456 Oak Ave",
        "state": "CA",
        "date_of_birth": None,
        "expiration_date": None,
    })
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = mock_response

    result = extract_dl("/tmp/dl2.jpg")

    assert result.first_name == "Jane"
    assert result.date_of_birth is None
    assert result.expiration_date is None
```

**Step 5: Run tests**

Run: `cd /usr/local/code/legal_skills && python -m pytest tests/test_extract_dl.py -v`
Expected: 2 tests PASS

**Step 6: Commit**

```bash
git add dl-extractor/ tests/test_extract_dl.py
git commit -m "feat: add dl-extractor skill with SKILL.md and extract_dl.py"
```

---

### Task 4: Skill 3 — insurance-extractor

**Files:**
- Create: `insurance-extractor/SKILL.md`
- Create: `insurance-extractor/scripts/__init__.py`
- Create: `insurance-extractor/scripts/extract_insurance.py`
- Create: `tests/test_extract_insurance.py`

**Step 0: Scaffold the skill with init_skill.py**

```bash
$INIT_SKILL insurance-extractor --path /usr/local/code/legal_skills
```

Delete unused example files from references/ and assets/.

**Step 1: Edit insurance-extractor/SKILL.md (replace template content)**

```markdown
---
name: insurance-extractor
description: Extracts structured data from insurance documents (PDF or image) using GPT-4o-mini vision. Outputs first name, last name, DOB, address, policy number, vehicle details, VIN. Use when user says "extract insurance info", "parse insurance card", or after doc-classifier identifies a document as insurance.
---

# Insurance Document Extractor

## Instructions

### Step 1: Prepare the document
Convert input to base64 image using `legal_skills.image_utils.file_to_base64_image()`.

### Step 2: Extract data with GPT-4o-mini vision
Run: `python insurance-extractor/scripts/extract_insurance.py <file_path>`

Expected output: JSON with first_name, last_name, date_of_birth, address, policy_number, vehicle_make, vehicle_model, vehicle_year, vin.

## Examples

User says: "Extract info from this insurance card"
Result:
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

Error: Missing fields in output
Cause: Insurance cards vary widely in layout
Solution: Fields not found will be null. Review the source document manually if critical fields are missing.
```

**Step 2: Create insurance-extractor/scripts/extract_insurance.py**

```python
"""Extract structured data from an Insurance document."""
import json
import sys
from pathlib import Path

from openai import OpenAI
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
    "If a field is not visible, use null."
)


def extract_insurance(file_path: str) -> InsuranceData:
    """Extract structured data from an insurance document image."""
    base64_image = file_to_base64_image(file_path)
    client = OpenAI()

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


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python extract_insurance.py <file_path>")
        sys.exit(1)
    data = extract_insurance(sys.argv[1])
    print(data.model_dump_json(indent=2))
```

**Step 3: Create insurance-extractor/scripts/__init__.py**

Empty file.

**Step 4: Write tests (mocked OpenAI)**

```python
# tests/test_extract_insurance.py
import json
from unittest.mock import patch, MagicMock

from extract_insurance import extract_insurance
from legal_skills.models import InsuranceData


def _mock_insurance_response():
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1985-03-15",
        "address": "456 Oak Ave, Springfield, IL 62702",
        "policy_number": "POL-98765",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": "2022",
        "vin": "1HGBH41JXMN109186",
    })
    return mock_response


@patch("extract_insurance.file_to_base64_image", return_value="fake_base64")
@patch("extract_insurance.OpenAI")
def test_extract_insurance_full(mock_openai_cls, mock_image):
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = _mock_insurance_response()

    result = extract_insurance("/tmp/ins.pdf")

    assert isinstance(result, InsuranceData)
    assert result.first_name == "John"
    assert result.policy_number == "POL-98765"
    assert result.vehicle_make == "Toyota"
    assert result.vin == "1HGBH41JXMN109186"


@patch("extract_insurance.file_to_base64_image", return_value="fake_base64")
@patch("extract_insurance.OpenAI")
def test_extract_insurance_minimal(mock_openai_cls, mock_image):
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = json.dumps({
        "first_name": "Jane",
        "last_name": "Doe",
        "date_of_birth": None,
        "address": "789 Pine Rd",
        "policy_number": None,
        "vehicle_make": None,
        "vehicle_model": None,
        "vehicle_year": None,
        "vin": None,
    })
    mock_client = MagicMock()
    mock_openai_cls.return_value = mock_client
    mock_client.chat.completions.create.return_value = mock_response

    result = extract_insurance("/tmp/ins2.pdf")

    assert result.first_name == "Jane"
    assert result.policy_number is None
    assert result.vehicle_make is None
```

**Step 5: Run tests**

Run: `cd /usr/local/code/legal_skills && python -m pytest tests/test_extract_insurance.py -v`
Expected: 2 tests PASS

**Step 6: Commit**

```bash
git add insurance-extractor/ tests/test_extract_insurance.py
git commit -m "feat: add insurance-extractor skill with SKILL.md and extract_insurance.py"
```

---

### Task 5: Skill 4 — doc-validator

**Files:**
- Create: `doc-validator/SKILL.md`
- Create: `doc-validator/scripts/__init__.py`
- Create: `doc-validator/scripts/validate.py`
- Create: `tests/test_validate.py`

**Step 0: Scaffold the skill with init_skill.py**

```bash
$INIT_SKILL doc-validator --path /usr/local/code/legal_skills
```

Delete unused example files from references/ and assets/.

**Step 1: Edit doc-validator/SKILL.md (replace template content)**

```markdown
---
name: doc-validator
description: Compares extracted Driver License and Insurance data for discrepancies in name, date of birth, and address. Takes two pre-paired JSON documents as input. Use when user says "validate documents", "check for mismatches", "compare DL and insurance", or after extraction is complete.
---

# Document Validator

## Instructions

### Step 1: Prepare inputs
You need two JSON objects: one `DriverLicenseData` and one `InsuranceData`, already paired by the calling application.

### Step 2: Run validation
Run: `python doc-validator/scripts/validate.py '<dl_json>' '<insurance_json>'`

Or import as a module:
```python
from validate import validate_documents
report = validate_documents(dl_data, insurance_data)
```

### Step 3: Interpret results
- `name_match`: True if first_name + last_name match (case-insensitive)
- `dob_match`: True if date_of_birth matches, or if either is null
- `address_match`: True if address matches (case-insensitive, stripped)
- `match_status`: "match" if all checks pass, "discrepancy" if any fail
- `discrepancies`: list of specific fields that differ

## Examples

Matching documents:
```json
{"match_status": "match", "name_match": true, "dob_match": true, "address_match": true, "discrepancies": []}
```

Address mismatch:
```json
{"match_status": "discrepancy", "address_match": false, "discrepancies": [{"field_name": "address", "dl_value": "123 Main St", "insurance_value": "456 Oak Ave"}]}
```
```

**Step 2: Create doc-validator/scripts/validate.py**

```python
"""Compare Driver License and Insurance data for discrepancies."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from legal_skills.models import (
    DriverLicenseData,
    InsuranceData,
    FieldDiscrepancy,
    ValidationReport,
)


def _normalize(value: str | None) -> str:
    """Normalize a string for comparison."""
    if value is None:
        return ""
    return value.strip().lower()


def validate_documents(
    dl: DriverLicenseData, insurance: InsuranceData
) -> ValidationReport:
    """Compare DL and insurance data, returning a validation report."""
    discrepancies: list[FieldDiscrepancy] = []

    # Name comparison
    dl_name = _normalize(f"{dl.first_name} {dl.last_name}")
    ins_name = _normalize(f"{insurance.first_name} {insurance.last_name}")
    name_match = dl_name == ins_name
    if not name_match:
        discrepancies.append(
            FieldDiscrepancy(
                field_name="name",
                dl_value=f"{dl.first_name} {dl.last_name}",
                insurance_value=f"{insurance.first_name} {insurance.last_name}",
            )
        )

    # DOB comparison (match if either is None)
    if dl.date_of_birth is not None and insurance.date_of_birth is not None:
        dob_match = _normalize(dl.date_of_birth) == _normalize(insurance.date_of_birth)
    else:
        dob_match = True
    if not dob_match:
        discrepancies.append(
            FieldDiscrepancy(
                field_name="date_of_birth",
                dl_value=dl.date_of_birth or "",
                insurance_value=insurance.date_of_birth or "",
            )
        )

    # Address comparison
    address_match = _normalize(dl.address) == _normalize(insurance.address)
    if not address_match:
        discrepancies.append(
            FieldDiscrepancy(
                field_name="address",
                dl_value=dl.address,
                insurance_value=insurance.address,
            )
        )

    all_match = name_match and dob_match and address_match

    return ValidationReport(
        person_name=f"{dl.first_name} {dl.last_name}",
        name_match=name_match,
        dob_match=dob_match,
        address_match=address_match,
        match_status="match" if all_match else "discrepancy",
        discrepancies=discrepancies,
        dl_source=dl.file_path,
        insurance_source=insurance.file_path,
    )


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python validate.py '<dl_json>' '<insurance_json>'")
        sys.exit(1)
    dl = DriverLicenseData.model_validate_json(sys.argv[1])
    ins = InsuranceData.model_validate_json(sys.argv[2])
    report = validate_documents(dl, ins)
    print(report.model_dump_json(indent=2))
```

**Step 3: Create doc-validator/scripts/__init__.py**

Empty file.

**Step 4: Write tests for validator**

```python
# tests/test_validate.py
from validate import validate_documents
from legal_skills.models import DriverLicenseData, InsuranceData


def _make_dl(**overrides) -> DriverLicenseData:
    defaults = {
        "file_path": "/tmp/dl.jpg",
        "first_name": "John",
        "last_name": "Smith",
        "license_number": "D1234567",
        "address": "123 Main St, Springfield, IL 62701",
        "state": "IL",
        "date_of_birth": "1985-03-15",
        "expiration_date": "2027-03-15",
    }
    defaults.update(overrides)
    return DriverLicenseData(**defaults)


def _make_ins(**overrides) -> InsuranceData:
    defaults = {
        "file_path": "/tmp/ins.pdf",
        "first_name": "John",
        "last_name": "Smith",
        "date_of_birth": "1985-03-15",
        "address": "123 Main St, Springfield, IL 62701",
        "policy_number": "POL-98765",
        "vehicle_make": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_year": "2022",
        "vin": "1HGBH41JXMN109186",
    }
    defaults.update(overrides)
    return InsuranceData(**defaults)


def test_all_fields_match():
    report = validate_documents(_make_dl(), _make_ins())
    assert report.match_status == "match"
    assert report.name_match is True
    assert report.dob_match is True
    assert report.address_match is True
    assert len(report.discrepancies) == 0


def test_address_mismatch():
    report = validate_documents(
        _make_dl(),
        _make_ins(address="456 Oak Ave, Springfield, IL 62702"),
    )
    assert report.match_status == "discrepancy"
    assert report.address_match is False
    assert report.name_match is True
    assert len(report.discrepancies) == 1
    assert report.discrepancies[0].field_name == "address"


def test_name_mismatch():
    report = validate_documents(
        _make_dl(),
        _make_ins(first_name="Jonathan"),
    )
    assert report.match_status == "discrepancy"
    assert report.name_match is False
    assert len(report.discrepancies) == 1
    assert report.discrepancies[0].field_name == "name"


def test_dob_mismatch():
    report = validate_documents(
        _make_dl(),
        _make_ins(date_of_birth="1985-04-20"),
    )
    assert report.match_status == "discrepancy"
    assert report.dob_match is False
    assert len(report.discrepancies) == 1
    assert report.discrepancies[0].field_name == "date_of_birth"


def test_dob_null_on_insurance_still_matches():
    report = validate_documents(
        _make_dl(),
        _make_ins(date_of_birth=None),
    )
    assert report.dob_match is True
    assert report.match_status == "match"


def test_multiple_discrepancies():
    report = validate_documents(
        _make_dl(),
        _make_ins(
            first_name="Jane",
            address="999 Different St",
            date_of_birth="1990-01-01",
        ),
    )
    assert report.match_status == "discrepancy"
    assert report.name_match is False
    assert report.dob_match is False
    assert report.address_match is False
    assert len(report.discrepancies) == 3


def test_case_insensitive_name_match():
    report = validate_documents(
        _make_dl(first_name="JOHN", last_name="SMITH"),
        _make_ins(first_name="john", last_name="smith"),
    )
    assert report.name_match is True


def test_case_insensitive_address_match():
    report = validate_documents(
        _make_dl(address="123 MAIN ST"),
        _make_ins(address="123 main st"),
    )
    assert report.address_match is True
```

**Step 5: Run tests**

Run: `cd /usr/local/code/legal_skills && python -m pytest tests/test_validate.py -v`
Expected: 8 tests PASS

**Step 6: Commit**

```bash
git add doc-validator/ tests/test_validate.py
git commit -m "feat: add doc-validator skill with SKILL.md and validate.py"
```

---

### Task 6: Run Full Test Suite and Initialize Git

**Files:**
- Create: `.gitignore`
- Create: `.env.example`

**Step 1: Create .gitignore**

```
__pycache__/
*.pyc
.env
*.egg-info/
dist/
build/
.pytest_cache/
```

**Step 2: Create .env.example**

```
OPENAI_API_KEY=your-openai-api-key-here
```

**Step 3: Initialize git repo**

```bash
cd /usr/local/code/legal_skills
git init
```

**Step 4: Validate all skills with skill-creator's validator**

```bash
$VALIDATE_SKILL /usr/local/code/legal_skills/doc-classifier
$VALIDATE_SKILL /usr/local/code/legal_skills/dl-extractor
$VALIDATE_SKILL /usr/local/code/legal_skills/insurance-extractor
$VALIDATE_SKILL /usr/local/code/legal_skills/doc-validator
```

Expected: All 4 skills pass validation (proper frontmatter, naming, description).

**Step 5: Run the full test suite**

Run: `cd /usr/local/code/legal_skills && python -m pytest tests/ -v`
Expected: All tests PASS (5 model tests + 2 classify + 2 dl + 2 insurance + 8 validate = 19 tests)

**Step 6: Package all skills**

```bash
$PACKAGE_SKILL /usr/local/code/legal_skills/doc-classifier
$PACKAGE_SKILL /usr/local/code/legal_skills/dl-extractor
$PACKAGE_SKILL /usr/local/code/legal_skills/insurance-extractor
$PACKAGE_SKILL /usr/local/code/legal_skills/doc-validator
```

Expected: 4 `.skill` files created, ready for distribution.

**Step 7: Commit everything**

```bash
git add .
git commit -m "feat: legal-skills project with 4 Claude Skills for document processing

- doc-classifier: classifies PDFs/images as DL or insurance
- dl-extractor: extracts structured data from driver licenses
- insurance-extractor: extracts structured data from insurance docs
- doc-validator: compares DL and insurance data for discrepancies
- shared Pydantic models and image utilities
- full test suite with mocked OpenAI calls"
```

---

### Task 7: Manual Integration Test with Real Documents

> This task requires an `OPENAI_API_KEY` set in `.env`.

**Step 1: Create .env with your API key**

```bash
cp .env.example .env
# Edit .env and add your actual OPENAI_API_KEY
```

**Step 2: Test classifier with a real DL image**

Run: `cd /usr/local/code/legal_skills && python doc-classifier/scripts/classify.py <path-to-dl-image>`
Expected: JSON output with `"document_type": "driver_license"`

**Step 3: Test classifier with a real insurance image**

Run: `cd /usr/local/code/legal_skills && python doc-classifier/scripts/classify.py <path-to-insurance-image>`
Expected: JSON output with `"document_type": "insurance"`

**Step 4: Test DL extractor**

Run: `cd /usr/local/code/legal_skills && python dl-extractor/scripts/extract_dl.py <path-to-dl-image>`
Expected: JSON with extracted name, license number, address, etc.

**Step 5: Test insurance extractor**

Run: `cd /usr/local/code/legal_skills && python insurance-extractor/scripts/extract_insurance.py <path-to-insurance-image>`
Expected: JSON with extracted name, address, policy number, vehicle details

**Step 6: Test validator with extracted JSON**

Take the JSON outputs from Steps 4 and 5 and pass them to the validator:
Run: `cd /usr/local/code/legal_skills && python doc-validator/scripts/validate.py '<dl_json>' '<insurance_json>'`
Expected: Validation report showing matches/discrepancies

---

### Task 8: Build Web UI (Integration Test)

> This is the composability validation. Use Claude Code with the frontend-design skill to build a web app that orchestrates all 4 skills.

**This task is intentionally left as a high-level spec.** The point is to use Claude Code to build it, proving the skills are composable.

**Web app requirements:**
1. File upload area (drag-and-drop PDF/JPEG)
2. On upload: run `classify.py` → display document type
3. Route to appropriate extractor → display extracted JSON
4. User selects DL + insurance pair → run `validate.py`
5. Display validation report with discrepancies highlighted

**Framework suggestion:** Streamlit (simplest for Python, single file) or FastAPI + vanilla HTML.

**How to invoke:** Open a new Claude Code session and say:
> "Build a web app that uses the skills in this project to process uploaded documents. See docs/plans/2026-02-23-legal-doc-skills-design.md for the full design."

---

## Unresolved Questions

1. No unit test for `image_utils.py` yet — requires mocking pdf2image/PIL. Add in Task 6?
2. Task 6 originally included git init steps — already done in Task 1b. Task 6 should focus on validation/packaging only.
3. `.env.example` — create in Task 6 or earlier?
