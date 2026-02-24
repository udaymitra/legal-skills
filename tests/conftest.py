"""Shared test configuration — adds skill script dirs to sys.path."""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent

# Add project root so `legal_skills` package is importable
sys.path.insert(0, str(project_root))

# Add each skill's scripts/ dir so tests can import by module name
for skill_dir in [
    "doc-classifier",
    "dl-extractor",
    "insurance-extractor",
    "doc-validator",
]:
    scripts_dir = project_root / skill_dir / "scripts"
    if scripts_dir.exists():
        sys.path.insert(0, str(scripts_dir))
