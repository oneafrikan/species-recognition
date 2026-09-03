## Routing

No specialist is pre-assigned to any task group below. The Tech Lead decides
routing at the point of actually starting the build — per task group, not
once for the whole change — based on what each group actually needs (e.g.
`grid-backend-dev` for application logic vs. `grid-data-engineer` if a task
turns out to be pipeline/warehousing-shaped, which none currently are).
Include `grid-ponytail` for a simplicity/de-bloat pass on the implementation
before QA sign-off — this project has an explicit "don't over-engineer"
mandate (see design.md's Goals/Non-Goals), so that check is load-bearing,
not optional. `grid-qa-engineer` is the release gate per the Tech Lead's
standard roster rules — it verifies against this change's specs/ acceptance
criteria, it doesn't implement.

7.3 and 7.4 (manual end-to-end runs against real photos and a live Ollama
instance) are the user's own verification once the build is done, not an
agent task — that's the point of shipping quickly: get it in front of real
testing.

## 1. Project scaffold

- [ ] 1.1 Create the `species_tag/` package with empty modules per design.md's layout (`__main__.py`, `config.py`, `discovery.py`, `backends/base.py`, `backends/ollama.py`, `tagging.py`, `exif.py`, `reporting.py`)
- [ ] 1.2 `requirements.txt` (pyexiftool, PyYAML, requests) and `config.example.yaml` matching the schema in design.md
- [ ] 1.3 `README.md`: exiftool + Ollama install steps per OS (macOS/Windows/Ubuntu), config walkthrough, usage example

## 2. Config loading

- [ ] 2.1 `config.py`: load and validate `config.yaml` (backend, ollama.host, ollama.active_model, ollama.models_to_test, region_context, min_confidence); clear error message and non-zero exit on a missing required field

## 3. Image discovery

- [ ] 3.1 `discovery.py`: recursive folder walk, filter to RAW (CR2/CR3/NEF/RAF/ARW) and JPEG/PNG by extension, skip everything else silently
- [ ] 3.2 `exif.py`: `extract_preview(raw_path) -> bytes` using pyexiftool
- [ ] 3.3 Wire discovery → preview extraction; a RAW file with no extractable preview is reported as a per-image error, not a crash

## 4. Species identification

- [ ] 4.1 `backends/base.py`: `VisionBackend` abstract base class + `SpeciesResult` dataclass (name, confidence)
- [ ] 4.2 `backends/ollama.py`: prompt template with `region_context` injected, requesting a simple parseable line format (species: confidence) from the model
- [ ] 4.3 `backends/ollama.py`: HTTP call to configured `host`/`active_model`, response parsed into `list[SpeciesResult]` (empty list = no detection)
- [ ] 4.4 Unreachable host or unparseable response is caught and surfaced as a per-image error, not a crash

## 5. Metadata tagging

- [ ] 5.1 `tagging.py`: pure function mapping a `list[SpeciesResult]` + `min_confidence` threshold to the correct keyword set (confident species keywords / species + `review_needed` / `no_detection` only)
- [ ] 5.2 `exif.py`: `write_keywords(image_path, keywords)` via pyexiftool — `-XMP-dc:Subject+=` and `-IPTC:Keywords+=` per keyword, no `-overwrite_original`
- [ ] 5.3 Wire tagging decision → `write_keywords` for each processed image

## 6. CLI and reporting

- [ ] 6.1 `__main__.py`: `python -m species_tag <folder> --config config.yaml` entry point, wires discovery → identification → tagging into one pipeline
- [ ] 6.2 `reporting.py`: per-image progress line (filename, outcome, model used) printed as each image completes; end-of-run summary tally (tagged / review_needed / no_detection / errors)
- [ ] 6.3 Per-image try/except at the pipeline level in `__main__.py` — one failure is logged and counted, batch continues

## 7. Verify

- [ ] 7.1 Unit tests for `tagging.py`'s confidence-bucket logic (pure function — high/medium/low across each threshold setting)
- [ ] 7.2 Unit tests for `config.py` validation (valid config loads; missing required field errors clearly)
- [ ] 7.3 Manual end-to-end run against a real small test folder (mixed RAW + JPEG) with a local Ollama instance — confirm written keywords are correct via `exiftool -XMP:Subject -IPTC:Keywords` and visible in Lightroom's keyword filter
- [ ] 7.4 Confirm the full pipeline runs on Ubuntu (primary use case, 3060 box) end to end; Windows/Mac Mini passes follow once the core loop is verified there
