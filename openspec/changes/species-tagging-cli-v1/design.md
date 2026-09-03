## Context

Greenfield repo — no existing code or patterns to match. See proposal.md for motivation. Constraints from the user: three-OS support (macOS/Windows/Ubuntu) with no fragile native deps, no CSV/log files, and no over-engineering — this design favors the smallest structure that satisfies the four capability specs, not a general-purpose framework.

## Goals / Non-Goals

**Goals:**
- A `VisionBackend` boundary clean enough that adding a cloud provider later is additive, not a rewrite.
- All exiftool interaction (RAW preview extraction and metadata writing) behind one thin wrapper.
- Config is the only thing that changes between machines/deployments (Ubuntu 3060 box vs. Mac Mini vs. future region/model changes).

**Non-Goals:**
- No cloud backend implementation (interface only).
- No plugin/registry system for backends — v1 has exactly one concrete backend (`OllamaBackend`); a second backend is added by writing a second class, not by building a discovery mechanism.
- No packaging (setup.py/pyproject wheel) — stays a clone + venv repo.
- No test framework scaffolding beyond what's needed to verify the spec scenarios (pytest, unit-level, no CI setup in this change).

## Decisions

### Module layout

```
species_tag/
  __main__.py          # CLI entry point: argparse, wires the pipeline together
  config.py             # loads + validates config.yaml (PyYAML), dataclass/TypedDict shape
  discovery.py           # recursive folder walk, extension filtering, RAW preview extraction
  backends/
    base.py             # VisionBackend abstract base
    ollama.py            # OllamaBackend: prompt building (region-hint injection) + HTTP call
  tagging.py             # confidence-bucket decision logic + keyword-set construction
  exif.py                 # thin wrapper around pyexiftool: extract_preview(), write_keywords()
  reporting.py            # progress line + summary tally printing
config.example.yaml
requirements.txt
```

One module per capability spec (`discovery.py` ↔ image-discovery, `backends/` ↔ species-identification, `tagging.py` + `exif.py` ↔ metadata-tagging, `reporting.py` + `__main__.py` ↔ cli-reporting). Keeps the spec-to-code mapping obvious for whoever picks this up next.

### VisionBackend abstraction

```python
class VisionBackend(ABC):
    def identify(self, image_bytes: bytes, region_context: str) -> list[SpeciesResult]: ...

@dataclass
class SpeciesResult:
    name: str
    confidence: Literal["low", "medium", "high"]
```

`OllamaBackend` is the only implementation in v1: builds the prompt (species-identification spec's region-hint requirement), POSTs to `{host}/api/generate` (or `/api/chat`, whichever the target Ollama version's vision endpoint is — confirm against installed Ollama version during implementation) with the image base64-encoded, and parses the model's response into `SpeciesResult` list. Parsing asks the model for a small structured format (e.g. one `species: confidence` pair per line) rather than free prose, so parsing stays regex-simple — no JSON-mode dependency on model support.

Alternative considered: pass a JSON schema via Ollama's structured-output support. Rejected for v1 — not every candidate model (`llava`, `minicpm-v`) reliably supports it, and a plain-text line format is trivial to parse and easy to debug by eye in the progress log.

### exiftool wrapper

Use `pyexiftool` (the `sylikc/pyexiftool` package, BSD terms) rather than hand-rolled subprocess calls — it manages a persistent exiftool process (`-stay_open`), which matters for batch throughput over thousands of images. `exif.py` exposes exactly two functions: `extract_preview(raw_path) -> bytes` and `write_keywords(image_path, keywords: list[str])`. `write_keywords` calls exiftool with `-XMP-dc:Subject+=` and `-IPTC:Keywords+=` for each keyword, without `-overwrite_original` (metadata-tagging spec's backup requirement).

### icewall905/image-tagger: write fresh, don't vendor

Evaluated per the prior-art research as a possible submodule (MIT, close architectural match). Decision: write `backends/ollama.py` and `exif.py` directly instead of vendoring it. Rationale: it's a 3-star project with no independent code-quality signal beyond its README, the actual logic needed (HTTP call + prompt template + exiftool write) is small enough that a submodule adds more indirection (submodule pin/update overhead, an extra license to track) than it saves. This keeps the dependency surface to two vendored packages (`pyexiftool`, an HTTP client) instead of three.

### Config schema (`config.yaml`)

```yaml
backend: ollama              # only valid value in v1; reserved for future cloud backends
ollama:
  host: http://localhost:11434
  active_model: llama3.2-vision
  models_to_test:            # documentation/reference list for the user's own A/B testing
    - llama3.2-vision
    - llava
    - minicpm-v
region_context: "Southern African safari wildlife"
min_confidence: medium        # low | medium | high
```

`config.example.yaml` is tracked; `config.yaml` is gitignored (may contain a private network host).

### Error handling shape

Per-image try/except at the pipeline level in `__main__.py` — a failure in discovery, identification, or writing for one image is caught, printed as that image's progress line (`ERROR: <reason>`), counted in the summary, and the loop continues. No retry logic — a single failed image is cheap to re-run, and the design goal is "don't halt the batch," not "recover automatically."

## Risks / Trade-offs

- **Ollama API surface varies by version.** Vision endpoint shape (`/api/generate` vs `/api/chat` with images) has shifted across Ollama releases. Mitigation: pin against the version installed during implementation, note it in README, treat as a known upgrade risk rather than building version-detection logic (out of scope for v1's "boring tech, smallest footprint" mandate).
- **Plain-text response parsing is less robust than structured output.** A model that ignores the requested format produces an unparseable response. Mitigation: treat a parse failure as a per-image error (falls under existing error handling), not a crash.
- **Embedded RAW previews vary in resolution by camera/generation.** A very low-res preview could hurt identification accuracy. Accepted trade-off per the proposal — full RAW decode was explicitly rejected for the dependency cost.
