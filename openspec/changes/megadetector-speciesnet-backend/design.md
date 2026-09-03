## Context

See `proposal.md` for motivation. This design assumes the target machine is the Ubuntu box with an RTX 3060, not this Mac — build and validation are explicitly deferred until that hardware exists (per the user). This document fixes the shape of the work so build day is "implement against a plan," not "start from zero."

## Goals / Non-Goals

**Goals:**
- A second, standalone backend that reuses v1's non-backend-specific modules (`discovery.py`, `exif.py`, `tagging.py`, `reporting.py`) rather than duplicating them.
- Keep it genuinely separate from the Ollama tool at the entry-point level, per the user's explicit "two files" direction — different runtime footprint (PyTorch + GPU vs. an HTTP client), different setup instructions, different failure modes. Not forced through the same `VisionBackend`-swap-via-config mechanism v1 uses for Ollama models.
- Produce output in the exact same `SpeciesResult` shape v1 already defines, so `tagging.py`/`exif.py`/`reporting.py` don't need to know or care which backend produced it.

**Non-Goals:**
- No implementation in this change — proposal/specs/design/tasks only. Tasks are written to be picked up cold once the 3060 box exists.
- No attempt to unify this with `species_tag`'s `config.yaml`/`backend:` field — that field stays Ollama-only for now; a true multi-backend config could be a later cleanup once both paths are proven, not before.
- No CUDA/driver/Ubuntu-setup instructions here — that's machine setup, not application design, and belongs to whoever provisions that box.

## Decisions

### Module layout

```
species_tag_md/                    # separate top-level package — the "second file"
  __main__.py                       # own CLI entry point: python -m species_tag_md <folder> --config config.yaml
  backends/
    megadetector.py                  # blank-frame-filtering: wraps MegaDetector, returns crops
    speciesnet.py                    # species-classification-local: wraps SpeciesNet, returns SpeciesResult
requirements-md.txt                  # separate requirements file — torch, MegaDetector/YOLO deps, SpeciesNet deps
config-md.example.yaml               # separate config: model weight paths, device (cuda/cpu), confidence threshold
```

Reused from `species_tag/` (the existing v1 package) without modification: `discovery.py`, `exif.py`, `tagging.py`, `reporting.py`, and the `SpeciesResult` dataclass from `backends/base.py`. `species_tag_md/__main__.py` imports these directly — same package tree, no duplication, just a different `backends/` implementation and its own entry point.

### Why a separate entry point instead of another `VisionBackend` config option

v1's `OllamaBackend` swap works because every Ollama model shares one runtime shape: an HTTP call to a server that's either running or not, with no special hardware setup. MegaDetector+SpeciesNet is a different category of dependency — GPU drivers, multi-GB model weight downloads, a PyTorch install that needs to match the machine's CUDA version exactly. Bundling that into `species_tag`'s `requirements.txt` would force every user (including this Mac, running Ollama-only) to carry that weight. A separate package/entry point/requirements file keeps the Ollama tool exactly as lightweight as it is today.

### Pipeline shape (two stages, not one call)

```
image → extract_preview/read bytes (reused from v1)
       → MegaDetector: classify Animal/Human/Vehicle/Empty, get bounding boxes
       → if not Animal: SpeciesResult = [] (same shape as v1's "no animal detected")
       → if Animal: crop each box
              → SpeciesNet: classify each crop → SpeciesResult per animal
       → tagging.py / exif.py (reused from v1, unchanged)
```

This mirrors `OllamaBackend.identify()`'s contract exactly (bytes in, `List[SpeciesResult]` out) even though internally it's two model calls instead of one — `tagging.py` never needs to know the difference.

### Model/package choice — deferred to build time

MegaDetector has shifted from the original `microsoft/CameraTraps` repo toward newer YOLOv9/v10-based community packages, and SpeciesNet's exact pip-installable package and weight-hosting has its own moving parts. Pinning exact package names/versions now, without a machine to install and test them on, risks locking in something already stale by build day. Resolve the concrete dependency versions at implementation time against whatever's current then.

## Risks / Trade-offs

- **Heavy setup burden.** Multi-GB model downloads, CUDA-matched PyTorch install — real friction compared to `ollama pull`. Accepted trade-off for the accuracy ceiling this exists to test.
- **Global taxonomy vs. regional accuracy.** SpeciesNet's species coverage may be uneven outside its best-represented regions (per `species-classification-local`'s spec) — validate against real regional test volume once the 3060 is up, don't assume parity with the Ollama backend's region-hint approach.
- **Two codebases to maintain.** Deliberate, not accidental — see "Why a separate entry point" above. Revisit only if this backend proves clearly superior and worth the unification effort.

## Open Questions

- Exact MegaDetector/SpeciesNet package versions and weight sources — resolve when the 3060 box exists and can actually install/test candidates, per "Model/package choice" above. Doesn't change the specs or task breakdown, only which specific package name lands in `requirements-md.txt`.
