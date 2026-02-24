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
