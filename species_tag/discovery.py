"""Recursive folder walk and extension filtering.

Per image-discovery spec: finds RAW/JPEG/PNG at any depth, skips everything
else silently (no error, no count). RAW normalization (preview extraction)
lives in exif.py; this module only finds files and says whether a given one
is RAW.
"""

from pathlib import Path

RAW_EXTENSIONS = {".cr2", ".cr3", ".nef", ".raf", ".arw"}
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png"}
_ALL_EXTENSIONS = RAW_EXTENSIONS | IMAGE_EXTENSIONS


def find_images(folder: Path) -> list:
    """Recursively find every RAW/JPEG/PNG file under `folder`.

    Matching is case-insensitive on extension (spec: .CR2 as well as .cr2).
    Returned in a stable, sorted order so progress output is reproducible.
    """
    return sorted(
        path
        for path in Path(folder).rglob("*")
        if path.is_file() and path.suffix.lower() in _ALL_EXTENSIONS
    )


def is_raw(path: Path) -> bool:
    """True if `path` is one of the supported RAW formats (needs preview extraction)."""
    return Path(path).suffix.lower() in RAW_EXTENSIONS
