# species-recognition

Batch-tags a folder of wildlife photos with species keywords, using a local vision model served by [Ollama](https://ollama.com) — no cloud, no per-image cost. Built for camera-trap, wildlife-photography, and drone-footage workflows across any geography.

**Status:** spec complete, implementation not started. See [Status](#status) below.

## What it does

Point it at a folder of photos (RAW or JPEG/PNG, any depth of subfolders). For each image it:

1. Extracts a usable JPEG (the embedded preview, for RAW files).
2. Sends it to a vision model running in Ollama, with a geographic hint (e.g. "Southern African safari wildlife") to help the model narrow down plausible species.
3. Writes the result into the image's own metadata as a keyword — filterable in Lightroom's keyword list, no separate database or log file:
   - Confident ID → the species name(s) as keywords (an image can have more than one species).
   - Low-confidence ID → the guess plus a `review_needed` keyword.
   - No animal in frame → a `no_detection` keyword.

Every run reprocesses every image found — there's no "already tagged, skip it" logic. exiftool's automatic backup (`<file>_original`) is left in place on every write, so a bad tag is always reversible.

## Requirements

- Python 3.10+
- [exiftool](https://exiftool.org) — used both to pull the embedded preview out of RAW files and to write the keywords back.
  - macOS: `brew install exiftool`
  - Ubuntu: `sudo apt install libimage-exiftool-perl`
  - Windows: download the installer from [exiftool.org](https://exiftool.org) (or `choco install exiftool`)
- [Ollama](https://ollama.com) running somewhere reachable — locally, or on another machine on your network (e.g. a GPU box) — with at least one vision-capable model pulled:
  ```bash
  ollama pull llama3.2-vision
  ollama pull llava
  ollama pull minicpm-v
  ```

## Setup

```bash
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp config.example.yaml config.yaml
# edit config.yaml: Ollama host, active model, region_context, min_confidence
```

## Usage

```bash
python -m species_tag /path/to/photos --config config.yaml
```

Progress prints per image as it runs, with a summary tally at the end (tagged / review_needed / no_detection / errors).

## Config

See `config.example.yaml`. Key fields:

| Field | Purpose |
|---|---|
| `ollama.host` | Where Ollama is running — can point at a different machine than the one running this script |
| `ollama.active_model` | Which pulled model to use for this run |
| `ollama.models_to_test` | Reference list of models you're comparing — swap `active_model` between runs to A/B them |
| `region_context` | Free-text geographic hint injected into the model prompt (e.g. "South American Pantanal wildlife") — no hardcoded species list, this is how the tool adapts to any region |
| `min_confidence` | `low` / `medium` / `high` — results below this are tagged `review_needed` instead of trusted outright |

## Status

This repo is spec'd via [OpenSpec](https://github.com/Fission-AI/OpenSpec) — see `openspec/changes/species-tagging-cli-v1/` for the full proposal, capability specs, architecture design, and build task list. Implementation hasn't started yet; `tasks.md` in that folder is the build checklist.

## v1 scope

Local/remote Ollama only. A cloud API backend is architected as an extension point but not implemented. Also deferred to a later version: a GUI, blank-frame pre-filtering, scientific names, hierarchical keywords, a results database, and pip-installable packaging — see the proposal for the full list.

## License

Private repo, personal project. No license file yet — treat as all-rights-reserved until one is added.
