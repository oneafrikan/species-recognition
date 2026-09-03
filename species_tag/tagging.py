"""Confidence-bucket decision logic: turns identification results into a keyword set.

Pure function, no I/O — see metadata-tagging spec for the three outcomes this
implements (confident species / review_needed / no_detection).
"""

from typing import List

from .backends.base import SpeciesResult

_CONFIDENCE_RANK = {"low": 0, "medium": 1, "high": 2}


def build_keywords(results: List[SpeciesResult], min_confidence: str) -> List[str]:
    """Map identification results + threshold to the keyword set to write.

    - No results -> ["no_detection"], nothing else.
    - Each result's species name is always included.
    - If any result is below `min_confidence`, "review_needed" is appended once.
    """
    if not results:
        return ["no_detection"]

    threshold = _CONFIDENCE_RANK[min_confidence]
    keywords = [result.name for result in results]
    below_threshold = any(_CONFIDENCE_RANK[result.confidence] < threshold for result in results)
    if below_threshold:
        keywords.append("review_needed")
    return keywords
