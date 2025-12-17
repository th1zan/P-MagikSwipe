"""Utility functions."""
from slugify import slugify as python_slugify


def slugify(text: str) -> str:
    """Generate a URL-safe slug from text."""
    return python_slugify(text, separator="-", lowercase=True)


def get_mime_type(filename: str) -> str:
    """Get MIME type from filename extension."""
    import mimetypes
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or "application/octet-stream"
