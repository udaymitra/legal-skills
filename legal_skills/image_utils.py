"""Shared image handling utilities for converting PDFs and images to base64."""

import base64
import io
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image


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
