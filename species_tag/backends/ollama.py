"""OllamaBackend: talks to a configured Ollama vision model over HTTP.

Uses `/api/generate` with `stream: false` and the image base64-encoded in
`images` — the documented shape for Ollama's vision models (llama3.2-vision,
llava, minicpm-v). Confirm against the installed Ollama version if this
starts failing; see design.md's "Ollama API surface varies by version" risk
note.

Asks the model for one `species: confidence` line per animal instead of
JSON-mode output, per design.md — not every candidate model reliably
supports structured output, and this format is regex-simple to parse.
Not every model call has been exercised against a live Ollama instance as
part of this build (see tasks.md 7.3); the request/response shape here
follows Ollama's documented API.
"""

import re
from base64 import b64encode
from typing import List

import requests

from .base import SpeciesResult, VisionBackend

# Generous timeout: CPU-served vision inference can take a while per image.
_REQUEST_TIMEOUT_SECONDS = 120

_LINE_RE = re.compile(r"^(?P<name>[^:]+):\s*(?P<confidence>low|medium|high)\s*$", re.IGNORECASE)


def _build_prompt(region_context: str) -> str:
    """Build the identification prompt, injecting the region hint (species-identification
    spec: no hardcoded species checklist — this free-text hint is the only geography input).
    """
    return (
        f"You are identifying wildlife species in a photo. Geographic context: {region_context}.\n"
        "Look at the image and identify every distinct animal species visible in it.\n"
        "Respond with exactly one line per animal, in this format:\n"
        "<common species name>: <confidence>\n"
        "where <confidence> is one of: low, medium, high.\n"
        "If no animal is visible in the image, respond with exactly: none\n"
        "Do not include any other text, explanation, or punctuation."
    )


def _parse_response(text: str) -> List[SpeciesResult]:
    """Parse the model's plain-text response into SpeciesResult objects.

    Raises ValueError if the response doesn't follow the requested format —
    the caller treats that as a per-image error (design.md's error-handling shape).
    """
    text = text.strip()
    if not text or text.lower() == "none":
        return []

    results = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        match = _LINE_RE.match(line)
        if not match:
            raise ValueError(f"unparseable response line from model: {line!r}")
        results.append(
            SpeciesResult(name=match.group("name").strip(), confidence=match.group("confidence").lower())
        )
    return results


class OllamaBackend(VisionBackend):
    def __init__(self, host: str, model: str):
        self.host = host.rstrip("/")
        self.model = model

    def identify(self, image_bytes: bytes, region_context: str) -> List[SpeciesResult]:
        payload = {
            "model": self.model,
            "prompt": _build_prompt(region_context),
            "images": [b64encode(image_bytes).decode("ascii")],
            "stream": False,
        }
        response = requests.post(
            f"{self.host}/api/generate", json=payload, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        return _parse_response(data.get("response", ""))
