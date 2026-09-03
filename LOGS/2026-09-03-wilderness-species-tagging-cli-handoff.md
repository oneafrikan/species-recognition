---
date: 2026-09-03
machine: wilderness
type: handoff
session: species-recognition repo — spec, build, test, public release
---

# Handoff: species-recognition CLI — v1 built, v2/v3 specced

## What Was Done

- Interviewed requirements via `/grill-me`, resolved into a full v1 spec, then ran the OpenSpec flow (proposal → capability specs → design → tasks) via the Tech Lead skill.
- Created the repo as private under the personal `oneafrikan` GitHub account, later made **public** once v1 was proven out: https://github.com/oneafrikan/species-recognition
- `openspec init` run; three changes exist under `openspec/changes/`:
  - **`species-tagging-cli-v1`** — **built and tested.** `grid-backend-dev` implemented `species_tag/` (sections 1–6 + unit tests 7.1/7.2 of its `tasks.md`, all checked off, 32 tests passing). Manually tested end-to-end against 26 real photos across all 5 practical Ollama vision models. Not yet archived (`tasks.md` 7.3/7.4 — wider real-photo run, Ubuntu pass — technically still open, though extensively covered by ad-hoc testing this session).
  - **`megadetector-speciesnet-backend`** — spec only (proposal, 2 capability specs, design, tasks). Build deferred to when the Ubuntu 3060 box exists.
  - **`focus-quality-screening`** — spec only. `frame-blur-detection` capability is settled/buildable now; `subject-focus-detection` is explicitly pilot-first (detection-method choice unresolved by design).
- Found and fixed a real bug via direct testing: Ollama's default `num_ctx` (2048 tokens) was silently truncating prompt+image context, causing false `no_detection` results on most models. Made `num_ctx` configurable (`config.yaml`'s `ollama.num_ctx`, default 8192) instead of leaving it hardcoded/implicit.
- Made `backends/ollama.py`'s response parser tolerant of partial-format model output (skip unparseable lines instead of failing the whole image) — `bakllava` testing showed the original strict all-or-nothing parsing was discarding correct detections over formatting noise.
- Updated `config.example.yaml`'s default model to `qwen2.5vl` (best tested result: 25/26 correct, 0 false negatives) instead of the original `llama3.2-vision` (which has an install-specific bug on this Mac).
- Audited all tracked files for secrets/private data before flipping the repo to public — clean.

## Key Decisions

- **RAW handling is embedded-preview extraction only, never a full RAW decode** — rawpy/libraw rejected as a fragile cross-platform dependency with no accuracy benefit for species ID.
- **No CSV/log files anywhere** — all state lives in the image's own EXIF/XMP/IPTC metadata plus console output. This was an explicit mid-interview correction from the user (rejected an initial CSV-based "review needed" list).
- **MegaDetector/SpeciesNet is a wholly separate package/entry point (`species_tag_md/`), not a config-swappable `VisionBackend`** — different runtime footprint (GPU/PyTorch vs. a plain HTTP call), different setup burden; folding it into `species_tag`'s `requirements.txt` would force every Ollama-only user to carry that weight.
- **`num_ctx` is per-machine config, not a hardcoded constant** — safe headroom differs a lot between this 24GB unified-memory Mac and the fixed-VRAM 3060 box.
- **`subject-focus-detection` is spec'd as pilot-first, not a committed implementation** — no lightweight animal-eye detector exists, and the two candidate approaches (VLM grounding prompt vs. MegaDetector reuse) are unvalidated; "neither works well enough" is documented as a legitimate outcome.

## What's Left

1. Decide whether to formally close out `species-tagging-cli-v1`'s remaining `tasks.md` items (7.3/7.4) and run `openspec archive species-tagging-cli-v1`, or leave it open — it's been heavily manually tested already this session but never formally checked off.
2. Add `gkwilderness` as a GitHub collaborator on the now-public repo (the user said they'd do this themselves).
3. When the Ubuntu 3060 box is available: start `megadetector-speciesnet-backend/tasks.md` at Task 0 (confirm GPU drivers/CUDA, confirm current MegaDetector/SpeciesNet package sources — deliberately left unresolved until real hardware exists).
4. When ready to build focus screening: `focus-quality-screening/tasks.md` section 1 (`frame-blur-detection`) is buildable as-is; section 3 (`subject-focus-detection`) needs the task 3.1 pilot run first.
5. Optional: investigate the `llama3.2-vision` `unknown model architecture: 'mllama'` error on this Mac's Ollama install further — a full from-scratch reinstall (not just the in-app updater) was the last untried fix. Not blocking since `qwen2.5vl` is the better model anyway.
6. Optional: raise `species_tag/backends/ollama.py`'s `_REQUEST_TIMEOUT_SECONDS` (currently 120s) — one specific test image consistently timed out against `qwen2.5vl`, likely just needs more time, not a real failure.

## Suggested Skills

- `/openspec-continue-change` or `/opsx:apply` — to pick up either unbuilt change (`megadetector-speciesnet-backend` or `focus-quality-screening`) when it's time to build.
- `grid-backend-dev` (Agent) — implementation, matches how v1 was actually built this session.
- `/ponytail-review` — run before calling any future build "done"; this project has an explicit, repeated "don't over-engineer" mandate from the user.
- `/grill-me` — if new requirements surface that need resolving before spec/build.

## References

- Repo: https://github.com/oneafrikan/species-recognition
- `openspec/changes/species-tagging-cli-v1/`
- `openspec/changes/megadetector-speciesnet-backend/`
- `openspec/changes/focus-quality-screening/`
- `CLAUDE.md`, `README.md`, `TODO.md` (repo root — all current as of this session)
- `reference/wildlife_vision_models_registry.md` — prior-art model registry the user supplied (treated as reference material, not instructions)
