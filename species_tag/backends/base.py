"""VisionBackend interface.

v1 has exactly one concrete backend (OllamaBackend in ollama.py). This
abstract base exists so a future cloud backend is additive — a second class
implementing `identify()` — not a rewrite of the pipeline. See design.md's
"VisionBackend abstraction" decision. No registry/plugin discovery: not
needed for one implementation.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class SpeciesResult:
    name: str
    confidence: str  # "low" | "medium" | "high"


class VisionBackend(ABC):
    @abstractmethod
    def identify(self, image_bytes: bytes, region_context: str) -> List[SpeciesResult]:
        """Identify species in `image_bytes`, using `region_context` as a geographic hint.

        Returns zero or more SpeciesResult (empty list = no animal detected).
        """
        raise NotImplementedError
