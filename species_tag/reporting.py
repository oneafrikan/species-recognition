"""Per-image progress line + end-of-run summary tally.

The console is the only window into a run (no log files, per CLAUDE.md), so
this module owns all of the tool's stdout.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Union

OUTCOMES = ("tagged", "review_needed", "no_detection", "error")


def classify_outcome(keywords: List[str]) -> str:
    """Map a keyword set from tagging.build_keywords() to a reporting outcome."""
    if "no_detection" in keywords:
        return "no_detection"
    if "review_needed" in keywords:
        return "review_needed"
    return "tagged"


@dataclass
class Tally:
    counts: Dict[str, int] = field(default_factory=lambda: {outcome: 0 for outcome in OUTCOMES})

    def record(self, outcome: str) -> None:
        self.counts[outcome] += 1


def print_progress(
    image_path: Union[str, Path], outcome: str, model: str, detail: Optional[str] = None
) -> None:
    """Print one progress line for a completed image (filename, outcome, model used)."""
    line = f"{Path(image_path).name}: {outcome} (model: {model})"
    if detail:
        line += f" — {detail}"
    print(line)


def print_summary(tally: Tally) -> None:
    """Print the end-of-run summary tally across all four outcome categories."""
    print(
        "Summary: "
        f"tagged={tally.counts['tagged']} "
        f"review_needed={tally.counts['review_needed']} "
        f"no_detection={tally.counts['no_detection']} "
        f"errors={tally.counts['error']}"
    )
