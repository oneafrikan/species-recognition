## Why

Wildlife and camera-trap photography produces a lot of motion-blurred or front/back-focused shots — a species ID being correct doesn't mean the photo is a keeper. The user wants photos automatically screened for focus quality so soft shots surface for review, the same way `review_needed` already surfaces low-confidence species IDs. Researched (not guessed): classical frame-level blur detection is cheap and well-understood; subject/eye-specific focus (the actually valuable check — is the *animal* sharp, not just some part of the frame) has no good lightweight existing solution and needs validation before committing to an approach.

## What Changes

- New: frame-level sharpness scoring using Laplacian variance (classical computer vision, no ML model, `opencv-python` the only new dependency) — flags a whole image as blurry/soft below a configurable threshold.
- New: a harder, explicitly pilot-first subject/eye-region focus check — compares sharpness inside a detected-animal region against the rest of the frame, to catch front/back-focus specifically. Two candidate approaches to validate before building for real (see design.md) — this is NOT a settled implementation like the rest of this repo's specs, it's a scoped experiment.
- Explicitly NOT using a vision-language model to directly judge "is this in focus" — researched and confirmed unreliable (VLMs benchmark close to random on blur judgments; they're good at semantic content, not pixel-level sharpness).
- **Spec only in this change — not implemented.** Per the user: build later.

## Capabilities

### New Capabilities
- `frame-blur-detection`: computes a sharpness score for a whole image and flags it below a configurable threshold — settled, ready to build.
- `subject-focus-detection`: compares sharpness in a detected-animal region against the frame background to catch front/back-focus — requires a pilot/validation task before full build-out, since the detection-method choice is genuinely unresolved (see design.md's Decisions).

### Modified Capabilities
(none formally — `species-tagging-cli-v1` isn't archived yet, so there's no canonical `metadata-tagging` spec in `openspec/specs/` to write a delta against. This change's capabilities describe new keyword outcomes that reuse v1's existing `exif.py` write path; see design.md.)

## Impact

- New dependency: `opencv-python` for `frame-blur-detection` (moderate size, CPU-only, no GPU/model download — the only new dependency this change definitely needs).
- `subject-focus-detection` may depend on either an Ollama VLM grounding-prompt call (untested for animal eyes — needs a pilot) or the `megadetector-speciesnet-backend` change's MegaDetector stage (heavier, GPU-oriented) — which one is used is an open decision, not a foregone conclusion.
- No change to existing species-identification or metadata-tagging behavior — this adds a new, independent keyword outcome, doesn't alter the existing confident/review_needed/no_detection logic.
