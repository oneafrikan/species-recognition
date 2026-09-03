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
_LEADING_MARKER_RE = re.compile(r"^\s*(?:[-*]|\d+[.)])\s*")


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
        "Example response for a photo with two animals:\n"
        "Lion: high\n"
        "Impala: medium\n"
        "If no animal is visible in the image, respond with exactly: none\n"
        "Do not include any other text, explanation, or punctuation."
    )


def _parse_response(text: str) -> List[SpeciesResult]:
    """Parse the model's plain-text response into SpeciesResult objects.

    Not every model reliably sticks to the requested "name: confidence" format even
    when told to (observed directly: bakllava frequently answers with a bare species
    name, a sentence, or commentary on some lines while getting others right). Rather
    than failing the whole image over one noisy line, this skips lines it can't parse
    and keeps whatever it can — an image only becomes an error if NOTHING parseable
    came back from a non-empty, non-"none" response.
    """
    text = text.strip()
    if not text or text.lower() == "none":
        return []

    results = []
    for line in text.splitlines():
        line = _LEADING_MARKER_RE.sub("", line.strip())
        if not line:
            continue
        match = _LINE_RE.match(line)
        if match:
            results.append(
                SpeciesResult(name=match.group("name").strip(), confidence=match.group("confidence").lower())
            )

    if not results:
        raise ValueError(f"no parseable species: confidence lines in model response: {text!r}")
    return results


class OllamaBackend(VisionBackend):
    def __init__(self, host: str, model: str, num_ctx: int):
        self.host = host.rstrip("/")
        self.model = model
        self.num_ctx = num_ctx

    def identify(self, image_bytes: bytes, region_context: str) -> List[SpeciesResult]:
        payload = {
            "model": self.model,
            "prompt": _build_prompt(region_context),
            "images": [b64encode(image_bytes).decode("ascii")],
            "stream": False,
            # Ollama's own default (2048) is too small for prompt + image tokens combined
            # — observed directly as silent context truncation (llava) and a hard 400
            # "exceeds the available context size" error (qwen2.5vl) in real testing.
            # Configurable per-machine (config.yaml ollama.num_ctx) since safe headroom
            # differs a lot between e.g. a 24GB unified-memory Mac and a fixed-VRAM GPU.
            "options": {"num_ctx": self.num_ctx},
        }
        response = requests.post(
            f"{self.host}/api/generate", json=payload, timeout=_REQUEST_TIMEOUT_SECONDS
        )
        response.raise_for_status()
        data = response.json()
        return _parse_response(data.get("response", ""))
