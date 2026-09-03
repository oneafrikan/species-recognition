# species-recognition

Batch-tags a folder of wildlife photos with species keywords, using a local vision model served by [Ollama](https://ollama.com) — no cloud, no per-image cost. Built for camera-trap, wildlife-photography, and drone-footage workflows across any geography.

**Status:** implemented and tested against real photos. See [Status](#status) below.

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
  ollama pull qwen2.5vl        # recommended — best result in real testing, see Status below
  ollama pull llama3.2-vision
  ollama pull llava
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
| `ollama.num_ctx` | Context window size, default 8192. Ollama's own default (2048) silently truncates prompt+image context on most vision models — this is the single biggest accuracy lever, see Status below. Raise it if you have RAM/VRAM headroom; lower it on a tight-VRAM GPU box |
| `region_context` | Free-text geographic hint injected into the model prompt (e.g. "South American Pantanal wildlife") — no hardcoded species list, this is how the tool adapts to any region |
| `min_confidence` | `low` / `medium` / `high` — results below this are tagged `review_needed` instead of trusted outright |

## Status

Built and manually tested against 26 real photos, across all five practical Ollama vision models (`qwen2.5vl`, `llama3.2-vision`, `llava`, `bakllava`, `moondream`).

- **`qwen2.5vl` is the clear best** — 25/26 correct, 0 false negatives, one slow timeout on a single image (not a detection failure). Recommended default.
- **A real bug, not model weakness, was the majority cause of early poor results**: Ollama's default `num_ctx` (2048 tokens) was silently truncating prompt+image context. Fixing it (raising `ollama.num_ctx`, see Config below) took `llava` from 13/26 correctly-tagged to 20/26 in direct testing.
- `llama3.2-vision` may hit an `unknown model architecture: 'mllama'` error depending on your Ollama install/version — a real install issue seen in testing, not a code bug; `qwen2.5vl` doesn't have this problem.
- `bakllava` sees animals correctly but often won't follow the requested output format; `moondream` is too small (1.8B, hard 2048-token context ceiling) for reliable results.

Full proposal, capability specs, architecture design, and build task list: `openspec/changes/species-tagging-cli-v1/`. Not yet archived — a wider real-photo run and a Ubuntu pass (`tasks.md` 7.3/7.4) are still open.

## v2: MegaDetector + SpeciesNet

A specced-but-not-built alternate backend using a purpose-trained detect-then-classify pipeline (MegaDetector + SpeciesNet) instead of a general vision-language model — see `openspec/changes/megadetector-speciesnet-backend/`. Deliberately deferred until real GPU hardware is available to build and test it against, rather than guessing.

## v1 scope

Local/remote Ollama only. A cloud API backend is architected as an extension point but not implemented. Also deferred: a GUI, scientific names, hierarchical keywords, a results database, and pip-installable packaging — see the proposal for the full list.

## License

No license file yet — treat as all-rights-reserved until one is added.
