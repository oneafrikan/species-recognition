## Routing

Same convention as `species-tagging-cli-v1`: no specialist pre-assigned here.
The Tech Lead decides routing per task group when the build actually starts —
`grid-backend-dev` for the application-logic sections, `grid-ponytail` for a
simplicity pass before it's called done, `grid-qa-engineer` as the release
gate. This change is **not build-ready today** — it's picked up once the
Ubuntu 3060 box exists and Task 0 below is confirmed done.

## 0. Prerequisites (not code — confirm before starting)

- [ ] 0.1 Ubuntu box has NVIDIA drivers + a matching CUDA toolkit installed and verified (`nvidia-smi` works)
- [ ] 0.2 Confirm current, actually-installable MegaDetector and SpeciesNet package/weight sources against that machine (per design.md's "Model/package choice — deferred to build time")

## 1. Package scaffold

- [ ] 1.1 Create `species_tag_md/` package (`__main__.py`, `backends/megadetector.py`, `backends/speciesnet.py`) per design.md's module layout
- [ ] 1.2 `requirements-md.txt` (torch matched to the box's CUDA version, MegaDetector deps, SpeciesNet deps) and `config-md.example.yaml` (model weight paths, device, confidence threshold)
- [ ] 1.3 README section: setup for this backend specifically (GPU/CUDA prerequisites, weight downloads, how it differs from the Ollama tool's setup)

## 2. Blank-frame filtering

- [ ] 2.1 `backends/megadetector.py`: load MegaDetector, run inference, classify Animal/Human/Vehicle/Empty per `blank-frame-filtering` spec
- [ ] 2.2 Bounding-box cropping for each Animal detection (padded crop, per spec)
- [ ] 2.3 Non-Animal classifications short-circuit before species classification (per spec — no wasted classifier calls)

## 3. Species classification

- [ ] 3.1 `backends/speciesnet.py`: load SpeciesNet, classify a cropped region, return species name + confidence
- [ ] 3.2 Wrap per-crop results into the existing `SpeciesResult` shape (reuse `species_tag/backends/base.py`'s dataclass — don't redefine it)
- [ ] 3.3 Multiple animals per image: run classification per crop, combine into one `SpeciesResult` list per image

## 4. Pipeline wiring

- [ ] 4.1 `species_tag_md/__main__.py`: `python -m species_tag_md <folder> --config config-md.yaml`, reusing `discovery.py`, `exif.py`, `tagging.py`, `reporting.py` from `species_tag/` unchanged
- [ ] 4.2 Per-image error handling matches v1's shape (one failure doesn't halt the batch)

## 5. Verify

- [ ] 5.1 Unit tests for crop-geometry logic and config validation — the parts testable without a GPU or real model weights
- [ ] 5.2 Real end-to-end run on the 3060 against hundreds of real images — this is the actual point of building this backend, and it's the user's manual verification step, not an agent task (same pattern as v1's 7.3/7.4)
- [ ] 5.3 Side-by-side comparison against `qwen2.5vl` (the current best Ollama result) on the same image set, to answer the question this whole change exists to answer: does the accuracy gain justify the setup/maintenance cost
