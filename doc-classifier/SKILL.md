---
name: doc-classifier
description: >
  This skill classifies uploaded PDF or image documents as either a Driver License
  or Insurance document using GPT-4o-mini vision. This skill should be used when
  a user uploads documents and asks to "classify these documents", "what type of
  document is this", "sort these documents", "identify document type", "is this a
  driver license or insurance card", or any request to categorize legal documents
  by type before extraction.
---

# Document Classifier

## Workflow

### Step 1: Prepare the document

Convert the input PDF or image to a base64-encoded image:

```python
from legal_skills.image_utils import file_to_base64_image
base64_img = file_to_base64_image("/path/to/document.pdf")
```

Supported formats: PDF, JPEG, PNG.

### Step 2: Classify with GPT-4o-mini vision

Run the classifier script:

```bash
python doc-classifier/scripts/classify.py <file_path>
```

Or import as a module:

```python
from classify import classify_document
result = classify_document("/path/to/document.pdf")
```

Output: JSON with `file_path`, `document_type` (`driver_license` | `insurance` | `unknown`), and `confidence` (0.0–1.0).

### Step 3: Route based on results

- `driver_license` → Route to **dl-extractor** skill for data extraction
- `insurance` → Route to **insurance-extractor** skill for data extraction
- `unknown` → Flag for manual review; document is not a recognized type

## Examples

**Classifying a driver license scan:**

Input: `classify_document("/input/doc.pdf")`
Output:
```json
{"file_path": "/input/doc.pdf", "document_type": "driver_license", "confidence": 0.97}
```

**Classifying an insurance card:**

Input: `classify_document("/input/card.png")`
Output:
```json
{"file_path": "/input/card.png", "document_type": "insurance", "confidence": 0.92}
```

## Troubleshooting

**"Unsupported file type" error**
The input file is not PDF, JPEG, or PNG. Convert to a supported format before classifying.

**"OpenAI API key not set" error**
Set the `OPENAI_API_KEY` environment variable or add it to a `.env` file in the project root.

**Required packages**
This skill requires: `openai`, `pydantic>=2.0`, `python-dotenv`, `pdf2image`, `Pillow`. The system package `poppler` is also required for PDF support. Install with: `pip install openai pydantic python-dotenv pdf2image Pillow`.
