## Why

Wildlife photographers and camera-trap operators manually keyword thousands of images per shoot to make them filterable in Lightroom. This is repetitive, time-consuming, and skippable — most photos never get properly tagged. A local vision model can do the species identification automatically, using hardware the user already owns, with no cloud dependency or per-image cost.

## What Changes

- New CLI tool: recursively scans a folder of images (RAW + JPEG/PNG), identifies wildlife species per image using a vision-language model served by Ollama, and writes the result into the image's own EXIF/XMP/IPTC metadata as keywords.
- RAW files (Canon CR2/CR3, Nikon NEF, Fuji RAF, Sony ARW) are handled by extracting the embedded preview JPEG rather than a full RAW decode.
- Vision backend is config-driven: local or remote Ollama host, with a choice of models for A/B testing. The backend is architected as a pluggable interface so a cloud API backend can be added later without touching the rest of the tool (not implemented in v1).
- A free-text `region_context` config value is injected into the model prompt as a geographic hint (no hardcoded species checklist — must work across continents via config alone).
- Tagging outcome per image is one of three states, each written as a flat keyword with no external log files: confident species name(s), a low-confidence guess plus `review_needed`, or `no_detection` for empty frames.
- Every run reprocesses every image in the target folder — no idempotency/skip tracking.
- Runs on macOS, Windows, and Ubuntu via a standard `venv` + `requirements.txt` workflow.

## Capabilities

### New Capabilities
- `image-discovery`: recursively finds RAW/JPEG/PNG files under a target folder and produces a normalized JPEG for each (embedded preview extraction for RAW).
- `species-identification`: sends a normalized image to a configured Ollama vision model, with a region-hint prompt, and returns species name(s) plus a confidence level.
- `metadata-tagging`: converts an identification result into the correct keyword set for an image's confidence bucket (confident / review_needed / no_detection) and writes it into the image's XMP/IPTC metadata via exiftool, preserving the automatic `_original` backup.
- `cli-reporting`: loads YAML config, drives the discovery → identification → tagging pipeline over a folder, and prints live per-image progress plus an end-of-run summary tally.

### Modified Capabilities
(none — first change in this repo)

## Impact

- New repo, no existing code to affect.
- New runtime dependencies: `pyexiftool` (BSD terms) wrapping the user-installed `exiftool` binary; an HTTP client for the Ollama API; `PyYAML` for config.
- New external dependency the user must install themselves: `exiftool` (documented per-OS in README).
- New external service dependency: a running Ollama instance (local or remote), with vision-capable models pulled (`llama3.2-vision`, `llava`, `minicpm-v` as v1 candidates).
