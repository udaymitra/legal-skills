# CLAUDE.md - Project Rules for Legal Skills

## Tech Stack
- **Language**: Python 3.11+
- **Environment**: conda (legal_skills)
- **LLM**: OpenAI GPT-4o-mini vision via `openai` SDK
- **Models**: Pydantic 2.0+
- **Image Processing**: pdf2image + Pillow
- **Linting**: ruff
- **Type Checking**: mypy (strict)
- **Testing**: pytest

## Architecture Pattern — Skill-Based Separation

**Each skill is an independent, composable unit.** Skills do NOT import from each other. They share only the common `legal_skills/` package.

### 1. Shared Package (`legal_skills/`)
- Pydantic data models (`models.py`)
- Image utilities (`image_utils.py`)
- NO business logic
- NO OpenAI calls
- Pure data definitions and utilities

### 2. Skill Folders (`<skill-name>/`)
- `SKILL.md` — YAML frontmatter + instructions (Anthropic skill format)
- `scripts/` — Python modules callable as CLI or importable functions
- `references/` — optional docs for progressive disclosure
- Skill folders use kebab-case: `doc-classifier/`
- Each script exposes ONE public function as its interface
- Scripts import from `legal_skills/` only — never from other skills

### 3. Tests (`tests/`)
- Mirror skill structure: `tests/test_classify.py` for `doc-classifier/scripts/classify.py`
- Mock ALL external APIs (OpenAI)
- `conftest.py` manages sys.path for skill script imports

## File Organization

```
legal_skills/
  legal_skills/              # Shared package
    __init__.py
    models.py                # All Pydantic models
    image_utils.py           # PDF/image -> base64
  doc-classifier/            # Skill 1
    SKILL.md
    scripts/
      __init__.py
      classify.py
  dl-extractor/              # Skill 2
    SKILL.md
    scripts/
      __init__.py
      extract_dl.py
  insurance-extractor/       # Skill 3
    SKILL.md
    scripts/
      __init__.py
      extract_insurance.py
  doc-validator/             # Skill 4
    SKILL.md
    scripts/
      __init__.py
      validate.py
  tests/
    __init__.py
    conftest.py
    test_models.py
    test_classify.py
    test_extract_dl.py
    test_extract_insurance.py
    test_validate.py
  docs/plans/
```

## Naming Conventions
- **Skill folders**: `kebab-case` (required by Anthropic skill spec)
- **Python modules**: `snake_case.py`
- **Classes**: `PascalCase` (Pydantic models)
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Test files**: `test_<module_name>.py`
- **Test functions**: `test_<behavior_description>`

## Commands
- `conda activate legal_skills` — Activate environment
- `pytest` — Run all tests
- `pytest --cov=legal_skills --cov-report=term-missing` — Tests with coverage
- `ruff check .` — Lint
- `ruff format .` — Format
- `ruff check --fix .` — Auto-fix lint issues
- `mypy legal_skills/` — Type check shared package
- `python <skill>/scripts/<script>.py <args>` — Run a skill script

## Skill Script Conventions
- Every script exposes ONE public function as its entry point
- Function signature: `def <verb>_<noun>(file_path: str) -> <PydanticModel>`
- Scripts are both importable modules AND CLI-runnable via `if __name__ == "__main__"`
- CLI mode: reads args, calls the function, prints JSON to stdout
- All OpenAI calls happen in skill scripts — NOT in the shared package
- Use `response_format={"type": "json_object"}` for structured outputs

## Error Handling
- Handle errors in skill scripts
- Return typed Pydantic models (not raw dicts)
- Use try-except for OpenAI API calls
- Raise `ValueError` for unsupported file types
- Never let unhandled exceptions reach the caller
- Log errors to stderr, output to stdout

## Code Quality
- Keep functions small and focused (single responsibility)
- Use descriptive variable and function names
- Remove print/debug statements before committing
- Handle edge cases (None checks, empty lists, missing data)
- DRY — flag repetition aggressively
- Explicit over clever
- "Engineered enough" — not fragile/hacky, not over-abstracted
- Type hints on ALL function signatures
- Docstrings on ALL public functions

## Testing
- pytest with 80%+ coverage target
- Mock ALL external APIs (OpenAI)
- Test structure: `tests/test_<script_name>.py`
- Unit tests run after every commit
- Test edge cases and error paths thoroughly
- Use fixtures in `conftest.py` for shared test helpers
- Test both happy path and null/missing field scenarios

## Planning & Execution
- Before executing any non-trivial task, write a plan to `docs/plans/`
- Include a progress tracker with checkboxes for each phase/step
- Update checkboxes in the plan file after completing each phase/step
- End every plan with a "## Unresolved Questions" section

## Git Workflow
- Branch from `main` for features
- Use descriptive branch names: `feature/`, `fix/`, `chore/`
- Keep commits focused and well-described
- Do NOT include "Co-Authored-By" or any other AI/Claude attribution in commit messages

## Pre-Commit Review Process

**MANDATORY before EVERY commit.** No exceptions.

### Step 1: Automated Checks
Run these first. Do not proceed if any fail:
- `pytest` — all tests passing
- `ruff check .` — lint passing
- `mypy legal_skills/` — type check passing

### Step 2: Diff Review
- Run `git diff` and `git status` — verify every changed line is intentional
- No debug code, no unrelated changes, no secrets
- Plan alignment: confirm changes match the spec, update checkboxes
- TODO tracking: when taking a shortcut or deferring work, add `# TODO:` in the code file AND a corresponding entry in the active plan file (if one exists). Both locations must be updated — never one without the other.

### Step 2b: SKILL.md Template Compliance (when adding/modifying a skill)
If the commit includes a new or modified SKILL.md, verify it matches the approved template in `docs/plans/skill-templates.md`:
- [ ] YAML frontmatter has `name` and `description` (third-person, with trigger phrases)
- [ ] Body follows: `## Workflow` (Step 1: Prepare, Step 2: Run, Step 3: Handle results) → `## Examples` → `## Troubleshooting`
- [ ] Imperative voice in body instructions
- [ ] Both CLI (`python <skill>/scripts/<script>.py <args>`) and module import examples in Step 2
- [ ] Step 3 documents required vs optional fields
- [ ] Troubleshooting covers: unsupported file type, missing fields, API key errors (as applicable)

### Step 3: Structured Code Review
Walk through all 4 sections. For SMALL changes: 1 top issue per section. For BIG changes: up to 4 per section.

1. **Architecture** — skill boundaries, coupling, data flow
2. **Code quality** — DRY violations, error handling, edge cases
3. **Tests** — coverage gaps, assertion strength, missing edge cases
4. **Performance** — unnecessary API calls, image processing efficiency

For each issue: describe concretely, present options, recommend one, ask user before proceeding.

### Step 4: Commit
Only after user approves the review.
