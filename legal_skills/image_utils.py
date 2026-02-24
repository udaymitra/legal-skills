"""Shared image handling utilities for converting PDFs and images to base64."""

import base64
import io
from pathlib import Path

from pdf2image import convert_from_path
from PIL import Image, ImageOps


def _auto_orient(img: Image.Image, *, auto_rotate: bool = False) -> Image.Image:
    """Auto-orient an image based on EXIF data and optionally aspect ratio.

    Always applies EXIF transpose (handles phone photos with rotation metadata).
    When auto_rotate=True, also rotates portrait images to landscape if
    height > width * 1.2. This corrects PDFs that embed landscape document
    cards in portrait pages.
    """
    img = ImageOps.exif_transpose(img)

    if auto_rotate:
        width, height = img.size
        if height > width * 1.2:
            img = img.rotate(-90, expand=True)

    return img


def file_to_base64_image(
    file_path: str, *, auto_rotate: bool = False
) -> str:
    """Convert a PDF or image file to a base64-encoded PNG string.

    Applies EXIF orientation correction to all images. When auto_rotate=True,
    also rotates portrait images to landscape — useful for PDFs that render
    landscape document cards in portrait page orientation.
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix == ".pdf":
        images = convert_from_path(str(path), first_page=1, last_page=1)
        img = images[0]
    elif suffix in (".jpg", ".jpeg", ".png"):
        img = Image.open(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")

    img = _auto_orient(img, auto_rotate=auto_rotate)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")
