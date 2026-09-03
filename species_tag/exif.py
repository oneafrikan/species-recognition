"""Thin wrapper around pyexiftool.

Exposes exactly two functions: extract_preview() and write_keywords() — see
design.md's "exiftool wrapper" decision. Both share one persistent exiftool
process (`-stay_open`, via pyexiftool's low-level ExifTool class) for the
life of the run, since spinning up a fresh exiftool subprocess per image
would dominate runtime over a batch of thousands of images. The process is
started lazily on first use and torn down automatically at interpreter exit
— callers never need to manage it.
"""

import atexit
from pathlib import Path
from typing import List, Union

import exiftool

_et = None  # module-level singleton, lazily started


def _get_exiftool() -> "exiftool.ExifTool":
    global _et
    if _et is None:
        _et = exiftool.ExifTool()
        _et.run()
        atexit.register(_et.terminate)
    return _et


def extract_preview(raw_path: Union[str, Path]) -> bytes:
    """Extract the embedded preview JPEG from a RAW file.

    Raises ValueError if the file has no extractable preview (image-discovery
    spec: this must be reported as a per-image error, not a crash — the caller
    is expected to catch it).
    """
    et = _get_exiftool()
    preview = et.execute("-b", "-PreviewImage", str(raw_path), raw_bytes=True)
    if not preview:
        raise ValueError(f"no embedded preview image in '{raw_path}'")
    return preview


def write_keywords(image_path: Union[str, Path], keywords: List[str]) -> None:
    """Append each keyword to the image's XMP dc:Subject and IPTC Keywords fields.

    Uses exiftool's `+=` append syntax (metadata-tagging spec: species/review/
    no_detection keywords are added, not a full-list overwrite) and never
    passes -overwrite_original, so exiftool's automatic `<file>_original`
    backup is always left in place.
    """
    et = _get_exiftool()
    args = []
    for keyword in keywords:
        args.append(f"-XMP-dc:Subject+={keyword}")
        args.append(f"-IPTC:Keywords+={keyword}")
    args.append(str(image_path))
    et.execute(*args)
